import os
import shutil
import math

def format_timestamp(seconds: float) -> str:
    """
    Converte segundos em uma string formatada de timestamp [HH:MM:SS].
    Exemplo: 135.8 -> [00:02:15]
    """
    total_seconds = int(math.floor(seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"[{hours:02d}:{minutes:02d}:{secs:02d}]"

def get_device_info() -> dict:
    """
    Detecta se há GPU NVIDIA compatível com CUDA para aceleração float16,
    ou seleciona CPU com quantização int8 para alta eficiência no faster-whisper.
    """
    device = "cpu"
    compute_type = "int8"
    
    try:
        import torch
        if torch.cuda.is_available():
            device = "cuda"
            compute_type = "float16"
    except Exception:
        # Fallback seguro para CPU
        device = "cpu"
        compute_type = "int8"
        
    return {
        "device": device,
        "compute_type": compute_type
    }

def check_ffmpeg_available() -> bool:
    """
    Verifica se o binário do FFmpeg está presente no PATH do sistema.
    """
    return shutil.which("ffmpeg") is not None

def ensure_ffmpeg() -> bool:
    """
    Garante que o FFmpeg esteja acessível, tentando carregar static_ffmpeg
    se o binário global não for encontrado.
    """
    if check_ffmpeg_available():
        return True
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
        return check_ffmpeg_available()
    except Exception:
        return False
