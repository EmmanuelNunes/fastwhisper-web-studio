import os
import time
from typing import Generator, Dict, Any, List, Optional
from core.utils import get_device_info, format_timestamp

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

AVAILABLE_MODELS = ["tiny", "base", "small", "medium", "large-v3-turbo"]
DEFAULT_MODEL = "large-v3-turbo"

class TranscriberManager:
    """
    Gerenciador singleton com cache para instâncias do WhisperModel.
    Oferece streaming progressivo de transcrição e filtragem de silêncio (VAD).
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TranscriberManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.models: Dict[str, Any] = {}
        self.current_model_name: Optional[str] = None
        self._initialized = True

    def clear_cache(self):
        """Limpa o cache de modelos carregados na memória."""
        self.models.clear()
        self.current_model_name = None

    def get_model(self, model_name: str = DEFAULT_MODEL):
        if WhisperModel is None:
            raise RuntimeError("O pacote faster-whisper não está instalado.")

        if model_name not in AVAILABLE_MODELS:
            model_name = DEFAULT_MODEL

        if model_name in self.models:
            self.current_model_name = model_name
            return self.models[model_name]

        device_info = get_device_info()
        device = device_info["device"]
        compute_type = device_info["compute_type"]

        try:
            model = WhisperModel(model_name, device=device, compute_type=compute_type)
        except Exception as e:
            # Fallback seguro para CPU com int8 caso CUDA falhe na inicialização
            if device != "cpu":
                model = WhisperModel(model_name, device="cpu", compute_type="int8")
            else:
                raise e

        self.models[model_name] = model
        self.current_model_name = model_name
        return model

    def transcribe_stream(
        self,
        audio_path: str,
        model_name: str = DEFAULT_MODEL,
        language: Optional[str] = "pt",
        beam_size: int = 5,
        vad_filter: bool = True
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Transcreve o áudio emitindo atualizações progressivas a cada segmento identificado.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {audio_path}")

        model = self.get_model(model_name)
        
        # language=None ativa auto-detecção
        lang = language if (language and language.lower() != "auto") else None

        segments_generator, info = model.transcribe(
            audio_path,
            beam_size=beam_size,
            language=lang,
            vad_filter=vad_filter,
            vad_parameters=dict(min_silence_duration_ms=500) if vad_filter else None
        )

        detected_language = getattr(info, 'language', 'pt')
        language_prob = getattr(info, 'language_probability', 1.0)
        total_duration = getattr(info, 'duration', 0.0)

        accumulated_text = []
        collected_segments: List[Dict[str, Any]] = []

        start_time = time.time()

        for seg in segments_generator:
            seg_dict = {
                "start": float(seg.start),
                "end": float(seg.end),
                "timestamp": f"{format_timestamp(seg.start)} - {format_timestamp(seg.end)}",
                "text": seg.text.strip()
            }
            collected_segments.append(seg_dict)
            accumulated_text.append(f"{seg_dict['timestamp']}  {seg_dict['text']}")

            # Emite atualização parcial para o frontend
            yield {
                "status": "transcribing",
                "partial_text": "\n".join(accumulated_text),
                "last_segment": seg_dict,
                "segments_count": len(collected_segments),
                "language": detected_language,
                "language_probability": language_prob,
                "elapsed_time": round(time.time() - start_time, 2)
            }

        # Emite resultado final completo
        full_text_clean = "\n".join([s["text"] for s in collected_segments])
        yield {
            "status": "completed",
            "full_text": full_text_clean,
            "full_text_with_timestamps": "\n".join(accumulated_text),
            "segments": collected_segments,
            "language": detected_language,
            "language_probability": language_prob,
            "duration": total_duration,
            "total_time": round(time.time() - start_time, 2)
        }
