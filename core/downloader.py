import os
import re
from typing import Dict, Any, Optional

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

class DownloadError(Exception):
    """Exceção levantada quando ocorre um erro na extração ou download do áudio."""
    pass

class WebAudioDownloader:
    """
    Responsável por extrair áudio de alta qualidade de links web
    (YouTube, Twitter/X, Instagram, SoundCloud, podcasts, etc.) via yt-dlp.
    """
    def __init__(self, output_dir: str = "temp_audio"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _sanitize_url(self, url: str) -> str:
        if not url or not isinstance(url, str):
            raise ValueError("URL não pode ser vazia.")
        url = url.strip()
        if not (url.startswith("http://") or url.startswith("https://")):
            raise ValueError("URL inválida: deve iniciar com http:// ou https://")
        return url

    def download_audio(self, url: str) -> Dict[str, Any]:
        """
        Extrai a melhor faixa de áudio e a converte para MP3 em 192kbps.
        Retorna dicionário com metadados e o caminho do arquivo gerado.
        """
        valid_url = self._sanitize_url(url)
        
        if yt_dlp is None:
            raise DownloadError("O pacote yt-dlp não está instalado. Instale-o com: pip install yt-dlp")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.output_dir, '%(id)s_%(title).50s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(valid_url, download=True)
                
                # Se for playlist, pega o primeiro item
                if 'entries' in info and info['entries']:
                    info = info['entries'][0]

                title = info.get('title', 'audio_desconhecido')
                duration = info.get('duration', 0.0)
                uploader = info.get('uploader', 'desconhecido')

                # yt-dlp converte a extensão para .mp3 no pós-processamento FFmpeg
                original_filename = ydl.prepare_filename(info)
                base_name, _ = os.path.splitext(original_filename)
                mp3_path = f"{base_name}.mp3"

                # Se por ventura o arquivo com extensão original for o mantido
                if not os.path.exists(mp3_path) and os.path.exists(original_filename):
                    mp3_path = original_filename

                return {
                    "file_path": mp3_path,
                    "title": title,
                    "duration": float(duration) if duration else 0.0,
                    "uploader": uploader
                }

        except Exception as e:
            raise DownloadError(f"Falha ao extrair áudio da URL: {str(e)}") from e
