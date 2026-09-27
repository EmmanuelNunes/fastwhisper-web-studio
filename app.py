import os
import time
from datetime import datetime
import gradio as gr

from core.utils import get_device_info, check_ffmpeg_available, format_timestamp
from core.downloader import WebAudioDownloader, DownloadError
from core.transcriber import TranscriberManager, AVAILABLE_MODELS, DEFAULT_MODEL
from core.exporter import export_all
from core.pdf_reader import PDFReader, AVAILABLE_VOICES_PTBR, DEFAULT_VOICE, synthesize_speech_ptbr

# Informações de inicialização de hardware
device_info = get_device_info()
ffmpeg_ok = check_ffmpeg_available()

def _run_transcription_pipeline(
    audio_path: str,
    title: str,
    duration: float,
    model_name: str,
    language: str,
    include_timestamps: bool,
    vad_filter: bool
):
    """
    Função geradora central para streaming da transcrição e exportação em .docx, .md e .txt.
    """
    if not audio_path or not os.path.exists(audio_path):
        yield "❌ Arquivo de áudio não encontrado ou inválido.", "", audio_path, None, None, None
        return

    yield (
        f"🎙️ Carregando modelo `{model_name}` e preparando áudio: **{title}**...",
        "",
        audio_path,
        None,
        None,
        None
    )

    manager = TranscriberManager()
    start_time = time.time()

    try:
        for event in manager.transcribe_stream(
            audio_path=audio_path,
            model_name=model_name,
            language=language,
            vad_filter=vad_filter
        ):
            if event["status"] == "transcribing":
                status_msg = (
                    f"⚡ **Processando áudio...**\n\n"
                    f"- **Segmentos identificados:** `{event['segments_count']}`\n"
                    f"- **Tempo decorrido:** `{event['elapsed_time']}s`\n"
                    f"- **Idioma detectado:** `{event['language'].upper()}` ({int(event['language_probability'] * 100)}% confiança)"
                )
                yield status_msg, event["partial_text"], audio_path, None, None, None

            elif event["status"] == "completed":
                total_elapsed = event["total_time"]
                audio_dur = duration if duration > 0 else event["duration"]
                speedup = round(audio_dur / total_elapsed, 1) if (total_elapsed > 0 and audio_dur > 0) else 1.0

                # Metadados para exportação
                metadata = {
                    "title": title,
                    "language": event["language"],
                    "language_probability": event["language_probability"],
                    "model": model_name,
                    "duration": audio_dur
                }

                timestamp_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')])[:40].strip() or "transcricao"
                base_filename = f"{timestamp_prefix}_{safe_title}"

                exported_files = export_all(
                    segments=event["segments"],
                    metadata=metadata,
                    output_dir="outputs",
                    base_filename=base_filename,
                    include_timestamps=include_timestamps
                )

                final_text = event["full_text_with_timestamps"] if include_timestamps else event["full_text"]

                summary_msg = (
                    f"### 🎉 Transcrição Concluída com Sucesso!\n\n"
                    f"| Métrica | Valor |\n"
                    f"| :--- | :--- |\n"
                    f"| **Fonte** | {title} |\n"
                    f"| **Duração do Áudio** | {audio_dur:.1f}s |\n"
                    f"| **Tempo de Execução** | {total_elapsed}s |\n"
                    f"| **Fator de Aceleração** | **{speedup}x mais rápido** que o tempo real |\n"
                    f"| **Idioma** | {event['language'].upper()} ({int(event['language_probability'] * 100)}% de certeza) |\n"
                    f"| **Modelo Utilizado** | `{model_name}` |"
                )

                yield summary_msg, final_text, audio_path, exported_files["docx"], exported_files["md"], exported_files["txt"]

    except Exception as e:
        yield f"❌ **Erro durante o processamento:** {str(e)}", "", audio_path, None, None, None


def handle_url_transcribe(url, model_name, language, include_timestamps, vad_filter):
    if not url or not url.strip():
        yield "⚠️ Por favor, insira o link de um site ou vídeo (ex: YouTube, Twitter/X, etc.).", "", None, None, None, None
        return

    yield "🌐 Conectando à URL e extraindo áudio via yt-dlp...", "", None, None, None, None
    downloader = WebAudioDownloader(output_dir="temp_audio")
    
    try:
        download_info = downloader.download_audio(url.strip())
    except Exception as e:
        yield f"❌ **Falha ao baixar áudio da URL:** {str(e)}", "", None, None, None, None
        return

    yield from _run_transcription_pipeline(
        audio_path=download_info["file_path"],
        title=download_info["title"],
        duration=download_info["duration"],
        model_name=model_name,
        language=language,
        include_timestamps=include_timestamps,
        vad_filter=vad_filter
    )


def handle_file_transcribe(file_obj, model_name, language, include_timestamps, vad_filter):
    if not file_obj:
        yield "⚠️ Por favor, selecione ou arraste um arquivo de áudio ou vídeo.", "", None, None, None, None
        return

    audio_path = file_obj if isinstance(file_obj, str) else getattr(file_obj, 'name', None)
    if not audio_path or not os.path.exists(audio_path):
        yield "❌ Arquivo inválido ou não encontrado.", "", None, None, None, None
        return

    title = os.path.splitext(os.path.basename(audio_path))[0]
    yield from _run_transcription_pipeline(
        audio_path=audio_path,
        title=title,
        duration=0.0,
        model_name=model_name,
        language=language,
        include_timestamps=include_timestamps,
        vad_filter=vad_filter
    )


def handle_mic_transcribe(audio_file, model_name, language, include_timestamps, vad_filter):
    if not audio_file:
        yield "⚠️ Nenhuma gravação de áudio encontrada. Grave algo no microfone antes de transcrever.", "", None, None, None, None
        return

    title = f"Gravacao_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    yield from _run_transcription_pipeline(
        audio_path=audio_file,
        title=title,
        duration=0.0,
        model_name=model_name,
        language=language,
        include_timestamps=include_timestamps,
        vad_filter=vad_filter
    )


def handle_pdf_process(pdf_file, voice_choice, speech_rate, max_pages):
    if not pdf_file:
        yield "⚠️ Por favor, selecione ou envie um arquivo PDF.", "", None, None, None, None
        return

    pdf_path = pdf_file if isinstance(pdf_file, str) else getattr(pdf_file, 'name', None)
    if not pdf_path or not os.path.exists(pdf_path):
        yield "❌ Arquivo PDF inválido ou não encontrado.", "", None, None, None, None
        return

    title = os.path.splitext(os.path.basename(pdf_path))[0]
    yield f"📑 Extraindo texto do PDF **{title}**...", "", None, None, None, None

    try:
        pdf_data = PDFReader.extract(pdf_path, max_pages=int(max_pages) if max_pages else None)
        full_text = pdf_data["full_text"]
        total_pages = pdf_data["total_pages"]
        processed_pages = pdf_data["processed_pages"]

        if not full_text.strip():
            yield f"⚠️ Nenhum texto legível encontrado no PDF **{title}** (o arquivo pode ser uma imagem escaneada).", "", None, None, None, None
            return

        yield (
            f"⚡ **Texto extraído com sucesso!** ({processed_pages} de {total_pages} páginas).\n\n"
            f"🎙️ Gerando narração em voz alta pt-BR com a voz `{AVAILABLE_VOICES_PTBR.get(voice_choice, voice_choice)}`...",
            full_text,
            None,
            None,
            None,
            None
        )

        # Gera o áudio falado via Edge TTS
        os.makedirs("outputs", exist_ok=True)
        timestamp_prefix = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '_', '-')])[:40].strip() or "pdf_audio"
        audio_output_path = os.path.join("outputs", f"{timestamp_prefix}_{safe_title}_narracao.mp3")

        synthesize_speech_ptbr(
            text=full_text,
            output_path=audio_output_path,
            voice=voice_choice,
            rate=speech_rate
        )

        # Monta os segmentos para o exportador docx, md, txt
        segments = []
        for p_info in pdf_data["pages"]:
            if p_info["text"]:
                segments.append({
                    "start": float(p_info["page"]),
                    "end": float(p_info["page"]),
                    "timestamp": f"[Pág. {p_info['page']}]",
                    "text": p_info["text"]
                })

        metadata = {
            "title": f"Leitura de PDF: {title}",
            "language": "pt-BR",
            "language_probability": 1.0,
            "model": f"Edge TTS ({voice_choice})",
            "duration": float(processed_pages)
        }

        exported_files = export_all(
            segments=segments,
            metadata=metadata,
            output_dir="outputs",
            base_filename=f"{timestamp_prefix}_{safe_title}",
            include_timestamps=True
        )

        success_msg = (
            f"### 🎉 Leitura e Narração do PDF Concluídas!\n\n"
            f"| Detalhe | Informação |\n"
            f"| :--- | :--- |\n"
            f"| **Documento** | {title}.pdf |\n"
            f"| **Páginas Lidas** | {processed_pages} de {total_pages} |\n"
            f"| **Voz Utilizada** | {AVAILABLE_VOICES_PTBR.get(voice_choice, voice_choice)} |\n"
            f"| **Áudio Gerado** | Pronto para ouvir e baixar no player abaixo! |\n"
            f"| **Arquivos Exportados** | .docx, .md e .txt disponíveis para download |"
        )

        yield success_msg, full_text, audio_output_path, exported_files["docx"], exported_files["md"], exported_files["txt"]

    except Exception as e:
        yield f"❌ **Erro no processamento do PDF:** {str(e)}", "", None, None, None, None


# Construção da Interface Gradio
custom_theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="indigo",
    neutral_hue="slate"
)

with gr.Blocks(title="FastWhisper Web Studio") as demo:
    gr.HTML("""
    <div style="text-align: center; padding: 18px 0 10px 0;">
        <h1 style="font-size: 2.3rem; font-weight: 800; margin-bottom: 4px; background: linear-gradient(90deg, #1d4ed8, #4f46e5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🎙️ FastWhisper Web Studio
        </h1>
        <p style="font-size: 1.05rem; color: #64748b; margin-top: 0;">
            Transcrição Ultra-Rápida de Áudio de Sites, Arquivos e Microfone para <b>.docx</b>, <b>.md</b> e <b>.txt</b>
        </p>
    </div>
    """)

    # Badges de Status do Sistema
    dev_color = "#16a34a" if device_info["device"] == "cuda" else "#0284c7"
    dev_label = f"⚡ Aceleração: GPU NVIDIA ({device_info['compute_type']})" if device_info["device"] == "cuda" else f"⚙️ Modo CPU Otimizado ({device_info['compute_type']} CTranslate2 AVX2/512)"
    ffmpeg_badge = "🟢 FFmpeg Pronto" if ffmpeg_ok else "🔴 FFmpeg Não Detectado"

    gr.HTML(f"""
    <div style="display: flex; gap: 10px; justify-content: center; margin-bottom: 18px;">
        <span style="background-color: {dev_color}; color: white; padding: 4px 12px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600;">
            {dev_label}
        </span>
        <span style="background-color: #334155; color: white; padding: 4px 12px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600;">
            {ffmpeg_badge}
        </span>
    </div>
    """)

    with gr.Row():
        # Painel Esquerdo: Entradas e Controles
        with gr.Column(scale=5):
            with gr.Accordion("⚙️ Configurações do Motor e Formatação", open=True):
                with gr.Row():
                    model_dropdown = gr.Dropdown(
                        choices=AVAILABLE_MODELS,
                        value=DEFAULT_MODEL,
                        label="Modelo Whisper",
                        info="Recomendado: large-v3-turbo (máxima fidelidade e rapidez)"
                    )
                    language_dropdown = gr.Dropdown(
                        choices=[
                            ("Português (pt)", "pt"),
                            ("Inglês (en)", "en"),
                            ("Espanhol (es)", "es"),
                            ("Detectar Automaticamente", "auto")
                        ],
                        value="pt",
                        label="Idioma do Áudio"
                    )
                with gr.Row():
                    include_timestamps_cb = gr.Checkbox(
                        label="Incluir Marcas de Tempo [00:00:00]",
                        value=True
                    )
                    vad_filter_cb = gr.Checkbox(
                        label="Filtrar Silêncios e Ruídos (Silero VAD)",
                        value=True
                    )

            with gr.Tabs():
                # Aba 1: Links da Web
                with gr.TabItem("🌐 Link da Web (YouTube, etc.)"):
                    url_input = gr.Textbox(
                        label="URL do Vídeo ou Áudio",
                        placeholder="Cole a URL do YouTube, podcast, Twitter/X, SoundCloud...",
                        lines=1
                    )
                    btn_transcribe_url = gr.Button("🚀 Baixar e Transcrever", variant="primary", size="lg")
                    url_audio_preview = gr.Audio(label="Áudio Baixado", type="filepath", interactive=False)

                # Aba 2: Upload de Arquivos
                with gr.TabItem("📁 Upload de Arquivo Local"):
                    file_input = gr.File(
                        label="Selecione ou Arraste o Arquivo (.mp3, .wav, .m4a, .mp4, .mkv, .ogg, etc.)",
                        file_types=["audio", "video"]
                    )
                    btn_transcribe_file = gr.Button("🚀 Transcrever Arquivo", variant="primary", size="lg")
                    file_audio_preview = gr.Audio(label="Prévia do Áudio", type="filepath", interactive=False)

                # Aba 3: Gravação ao Vivo
                with gr.TabItem("🎙️ Gravação ao Vivo"):
                    mic_input = gr.Audio(
                        label="Grave Áudio do Microfone",
                        sources=["microphone"],
                        type="filepath"
                    )
                    btn_transcribe_mic = gr.Button("🚀 Transcrever Gravação", variant="primary", size="lg")

                # Aba 4: Leitura de PDF (pt-BR)
                with gr.TabItem("📑 Leitura de PDF (pt-BR)"):
                    pdf_input = gr.File(
                        label="Selecione ou Arraste o Arquivo PDF",
                        file_types=[".pdf"]
                    )
                    with gr.Row():
                        pdf_voice_dropdown = gr.Dropdown(
                            choices=[(label, key) for key, label in AVAILABLE_VOICES_PTBR.items()],
                            value=DEFAULT_VOICE,
                            label="Voz Neural pt-BR"
                        )
                        pdf_rate_dropdown = gr.Dropdown(
                            choices=[
                                ("Velocidade Normal (+0%)", "+0%"),
                                ("Rápida (+20%)", "+20%"),
                                ("Mais Rápida (+40%)", "+40%"),
                                ("Lenta (-15%)", "-15%")
                            ],
                            value="+0%",
                            label="Velocidade"
                        )
                    pdf_max_pages_slider = gr.Slider(
                        minimum=1,
                        maximum=100,
                        value=20,
                        step=1,
                        label="Limite de Páginas a Processar",
                        info="Para síntese rápida de documentos extensos"
                    )
                    btn_process_pdf = gr.Button("🚀 Extrair Texto e Narrar em Áudio pt-BR", variant="primary", size="lg")
                    pdf_audio_preview = gr.Audio(label="🎧 Narração Gerada (.mp3)", type="filepath", interactive=False)

        # Painel Direito: Resultados e Downloads
        with gr.Column(scale=6):
            status_box = gr.Markdown("💡 *Selecione uma fonte à esquerda e clique em Transcrever para iniciar.*")
            transcription_text = gr.Textbox(
                label="Texto Transcrito em Tempo Real",
                placeholder="A transcrição aparecerá aqui conforme os blocos de áudio forem processados...",
                lines=15,
                autoscroll=True
            )

            gr.Markdown("### 📥 Arquivos Exportados para Download")
            with gr.Row():
                download_docx = gr.File(label="📄 Word (.docx)", interactive=False)
                download_md = gr.File(label="📝 Markdown (.md)", interactive=False)
                download_txt = gr.File(label="📃 Texto (.txt)", interactive=False)

    # Eventos de clique
    btn_transcribe_url.click(
        fn=handle_url_transcribe,
        inputs=[url_input, model_dropdown, language_dropdown, include_timestamps_cb, vad_filter_cb],
        outputs=[status_box, transcription_text, url_audio_preview, download_docx, download_md, download_txt]
    )

    btn_transcribe_file.click(
        fn=handle_file_transcribe,
        inputs=[file_input, model_dropdown, language_dropdown, include_timestamps_cb, vad_filter_cb],
        outputs=[status_box, transcription_text, file_audio_preview, download_docx, download_md, download_txt]
    )

    btn_transcribe_mic.click(
        fn=handle_mic_transcribe,
        inputs=[mic_input, model_dropdown, language_dropdown, include_timestamps_cb, vad_filter_cb],
        outputs=[status_box, transcription_text, mic_input, download_docx, download_md, download_txt]
    )

    btn_process_pdf.click(
        fn=handle_pdf_process,
        inputs=[pdf_input, pdf_voice_dropdown, pdf_rate_dropdown, pdf_max_pages_slider],
        outputs=[status_box, transcription_text, pdf_audio_preview, download_docx, download_md, download_txt]
    )

if __name__ == "__main__":
    demo.queue()
    demo.launch(server_name="127.0.0.1", server_port=7860, theme=custom_theme, show_error=True)
