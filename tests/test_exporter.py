import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.exporter import export_all, DocxExporter, MarkdownExporter, TextExporter

@pytest.fixture
def sample_segments():
    return [
        {"start": 0.0, "end": 3.0, "timestamp": "[00:00:00] - [00:00:03]", "text": "Bem-vindos ao aplicativo de transcrição."},
        {"start": 3.5, "end": 7.0, "timestamp": "[00:00:03] - [00:00:07]", "text": "Ele gera arquivos em Word, Markdown e texto puro com facilidade."}
    ]

@pytest.fixture
def sample_metadata():
    return {
        "title": "Apresentação de Teste",
        "language": "pt",
        "language_probability": 0.99,
        "model": "large-v3-turbo",
        "duration": 7.0
    }

def test_export_all_creates_three_files(tmp_path, sample_segments, sample_metadata):
    results = export_all(
        segments=sample_segments,
        metadata=sample_metadata,
        output_dir=str(tmp_path),
        base_filename="teste_transcricao",
        include_timestamps=True
    )
    
    assert "docx" in results
    assert "md" in results
    assert "txt" in results
    
    assert os.path.exists(results["docx"])
    assert os.path.exists(results["md"])
    assert os.path.exists(results["txt"])
    
    # Valida conteudo do TXT
    with open(results["txt"], "r", encoding="utf-8") as f:
        txt_content = f.read()
    assert "Bem-vindos ao aplicativo de transcrição." in txt_content
    assert "[00:00:00]" in txt_content

    # Valida conteudo do MD
    with open(results["md"], "r", encoding="utf-8") as f:
        md_content = f.read()
    assert "# Transcrição: Apresentação de Teste" in md_content
    assert "large-v3-turbo" in md_content

def test_docx_exporter_integrity(tmp_path, sample_segments, sample_metadata):
    output_file = os.path.join(str(tmp_path), "documento.docx")
    DocxExporter.export(
        segments=sample_segments,
        metadata=sample_metadata,
        output_path=output_file,
        include_timestamps=True
    )
    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 1000  # Arquivo docx valido tem tamanho consideravel
