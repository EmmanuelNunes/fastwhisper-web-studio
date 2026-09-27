import pytest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.downloader import WebAudioDownloader, DownloadError

def test_invalid_url_raises_value_error():
    downloader = WebAudioDownloader()
    with pytest.raises(ValueError):
        downloader.download_audio("")
    with pytest.raises(ValueError):
        downloader.download_audio("invalid-url-without-protocol")

@patch('core.downloader.yt_dlp.YoutubeDL')
def test_successful_audio_download(mock_ydl_class, tmp_path):
    mock_ydl_instance = MagicMock()
    mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance
    
    mock_info = {
        'id': 'abc1234',
        'title': 'Video de Teste',
        'duration': 120.0,
        'uploader': 'Canal Teste',
        'ext': 'mp3'
    }
    mock_ydl_instance.extract_info.return_value = mock_info
    
    # Mock para prepare_filename
    expected_path = os.path.join(str(tmp_path), "abc1234_Video de Teste.mp3")
    mock_ydl_instance.prepare_filename.return_value = os.path.join(str(tmp_path), "abc1234_Video de Teste.webm")
    
    # Simula arquivo criado apos pós-processamento
    with open(expected_path, "w") as f:
        f.write("audio_data")

    downloader = WebAudioDownloader(output_dir=str(tmp_path))
    result = downloader.download_audio("https://www.youtube.com/watch?v=abc1234")
    
    assert result["title"] == "Video de Teste"
    assert result["duration"] == 120.0
    assert result["uploader"] == "Canal Teste"
    assert result["file_path"] == expected_path

@patch('core.downloader.yt_dlp.YoutubeDL')
def test_download_failure_raises_download_error(mock_ydl_class):
    mock_ydl_instance = MagicMock()
    mock_ydl_class.return_value.__enter__.return_value = mock_ydl_instance
    mock_ydl_instance.extract_info.side_effect = Exception("Video indisponivel ou privado")
    
    downloader = WebAudioDownloader()
    with pytest.raises(DownloadError) as exc_info:
        downloader.download_audio("https://www.youtube.com/watch?v=error")
    assert "Falha ao extrair áudio" in str(exc_info.value)
