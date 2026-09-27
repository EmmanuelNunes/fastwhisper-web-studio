import pytest
import os
import sys
from unittest.mock import patch, AsyncMock, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.pdf_reader import (
    PDFReader,
    AVAILABLE_VOICES_PTBR,
    DEFAULT_VOICE,
    extract_text_from_pdf,
    synthesize_speech_ptbr
)

def test_available_voices_ptbr():
    assert "pt-BR-FranciscaNeural" in AVAILABLE_VOICES_PTBR
    assert "pt-BR-AntonioNeural" in AVAILABLE_VOICES_PTBR
    assert DEFAULT_VOICE == "pt-BR-FranciscaNeural"

def test_extract_text_from_pdf_nonexistent():
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("arquivo_inexistente.pdf")

@patch('core.pdf_reader.pypdf.PdfReader')
def test_extract_text_from_pdf_mocked(mock_reader_class, tmp_path):
    dummy_pdf = tmp_path / "teste.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4 dummy")
    
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_value = "Esta é a primeira página do documento de teste."
    
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Esta é a segunda página com mais conteúdo em português."
    
    mock_instance = mock_reader_class.return_value
    mock_instance.pages = [mock_page1, mock_page2]
    
    result = extract_text_from_pdf(str(dummy_pdf))
    assert result["total_pages"] == 2
    assert "primeira página" in result["full_text"]
    assert "segunda página" in result["full_text"]
    assert len(result["pages"]) == 2

@patch('core.pdf_reader.edge_tts.Communicate')
def test_synthesize_speech_ptbr(mock_communicate_class, tmp_path):
    mock_instance = AsyncMock()
    mock_communicate_class.return_value = mock_instance
    mock_instance.save = AsyncMock()

    output_audio = tmp_path / "audio_narrado.mp3"
    result_path = synthesize_speech_ptbr(
        text="Olá, esta é uma leitura em português brasileiro.",
        output_path=str(output_audio),
        voice="pt-BR-FranciscaNeural"
    )

    assert result_path == str(output_audio)
    mock_communicate_class.assert_called_once()
