import pytest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.transcriber import TranscriberManager, AVAILABLE_MODELS

@pytest.fixture(autouse=True)
def reset_manager():
    TranscriberManager().clear_cache()
    yield
    TranscriberManager().clear_cache()

def test_available_models_list():
    assert "tiny" in AVAILABLE_MODELS
    assert "base" in AVAILABLE_MODELS
    assert "small" in AVAILABLE_MODELS
    assert "medium" in AVAILABLE_MODELS
    assert "large-v3-turbo" in AVAILABLE_MODELS

@patch('core.transcriber.WhisperModel')
def test_transcriber_manager_initialization(mock_whisper_class):
    manager = TranscriberManager()
    model = manager.get_model("tiny")
    assert mock_whisper_class.called
    assert manager.current_model_name == "tiny"

@patch('core.transcriber.WhisperModel')
def test_transcribe_generator_yields_segments(mock_whisper_class, tmp_path):
    mock_instance = MagicMock()
    mock_whisper_class.return_value = mock_instance
    
    # Mock dos segmentos retornados pelo faster-whisper
    mock_seg1 = MagicMock()
    mock_seg1.start = 0.0
    mock_seg1.end = 2.5
    mock_seg1.text = " Olá mundo,"
    
    mock_seg2 = MagicMock()
    mock_seg2.start = 2.5
    mock_seg2.end = 5.0
    mock_seg2.text = " bem-vindos ao teste."
    
    mock_info = MagicMock()
    mock_info.language = "pt"
    mock_info.language_probability = 0.98
    mock_info.duration = 5.0
    
    mock_instance.transcribe.return_value = ([mock_seg1, mock_seg2], mock_info)
    
    dummy_audio = tmp_path / "fake_audio.mp3"
    dummy_audio.write_bytes(b"dummy audio data")
    
    manager = TranscriberManager()
    events = list(manager.transcribe_stream(str(dummy_audio), model_name="tiny", language="pt"))
    
    # O gerador deve produzir atualizacoes parciais e o resultado final
    assert len(events) >= 2
    final_result = events[-1]
    assert "segments" in final_result
    assert len(final_result["segments"]) == 2
    assert final_result["segments"][0]["text"] == "Olá mundo,"
    assert final_result["segments"][1]["text"] == "bem-vindos ao teste."
    assert final_result["language"] == "pt"
