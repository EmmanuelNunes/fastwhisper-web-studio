import os
import asyncio
from typing import Dict, Any, List, Optional

try:
    import pypdf
except ImportError:
    pypdf = None

try:
    import edge_tts
except ImportError:
    edge_tts = None

AVAILABLE_VOICES_PTBR = {
    "pt-BR-FranciscaNeural": "Francisca (Feminina - Fluida e Natural)",
    "pt-BR-AntonioNeural": "Antonio (Masculino - Firme e Profissional)",
    "pt-BR-ThalitaNeural": "Thalita (Feminina - Expressiva e Amigável)"
}

DEFAULT_VOICE = "pt-BR-FranciscaNeural"

class PDFReader:
    """
    Responsável pela extração e processamento de texto de documentos PDF.
    """
    @staticmethod
    def extract(pdf_path: str, max_pages: Optional[int] = None) -> Dict[str, Any]:
        if not pdf_path or not os.path.exists(pdf_path):
            raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")

        if pypdf is None:
            raise RuntimeError("O pacote pypdf não está instalado. Instale-o com: pip install pypdf")

        reader = pypdf.PdfReader(pdf_path)
        total_pages = len(reader.pages)
        pages_to_process = min(total_pages, max_pages) if max_pages else total_pages

        pages_data = []
        full_text_parts = []

        for i in range(pages_to_process):
            page = reader.pages[i]
            extracted = page.extract_text() or ""
            cleaned_text = extracted.strip()
            
            pages_data.append({
                "page": i + 1,
                "text": cleaned_text
            })
            if cleaned_text:
                full_text_parts.append(f"--- Página {i + 1} ---\n{cleaned_text}")

        return {
            "total_pages": total_pages,
            "processed_pages": pages_to_process,
            "pages": pages_data,
            "full_text": "\n\n".join(full_text_parts)
        }


def extract_text_from_pdf(pdf_path: str, max_pages: Optional[int] = None) -> Dict[str, Any]:
    """Helper funcional para extração de texto de PDF."""
    return PDFReader.extract(pdf_path, max_pages=max_pages)


async def _synthesize_async(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = "+0%") -> str:
    if edge_tts is None:
        raise RuntimeError("O pacote edge-tts não está instalado.")

    if voice not in AVAILABLE_VOICES_PTBR:
        voice = DEFAULT_VOICE

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate)
    await communicate.save(output_path)
    return output_path


def synthesize_speech_ptbr(text: str, output_path: str, voice: str = DEFAULT_VOICE, rate: str = "+0%") -> str:
    """
    Sintetiza texto em áudio falado natural em português brasileiro (Edge TTS)
    e salva no caminho de saída especificado (.mp3).
    """
    if not text or not text.strip():
        raise ValueError("O texto para síntese de voz não pode estar vazio.")

    try:
        return asyncio.run(_synthesize_async(text, output_path, voice, rate))
    except RuntimeError:
        # Se chamado de dentro de um loop asyncio ativo (ex: workers assíncronos do Gradio/Uvicorn)
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(lambda: asyncio.run(_synthesize_async(text, output_path, voice, rate)))
            return future.result()
