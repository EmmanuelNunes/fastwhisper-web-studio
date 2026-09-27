import os
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
except ImportError:
    Document = None

class DocxExporter:
    @staticmethod
    def export(
        segments: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        output_path: str,
        include_timestamps: bool = True
    ) -> str:
        if Document is None:
            raise RuntimeError("O pacote python-docx não está instalado.")

        doc = Document()

        # Configura margens padrão (1 polegada)
        for section in doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

        # Título Principal
        title_p = doc.add_paragraph()
        title_run = title_p.add_run("FastWhisper Web Studio — Transcrição de Áudio")
        title_run.font.name = "Calibri"
        title_run.font.size = Pt(20)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(30, 58, 138) # Azul escuro profissional
        title_p.paragraph_format.space_after = Pt(12)

        # Informações de Metadados
        meta_table = doc.add_table(rows=5, cols=2)
        meta_table.style = 'Table Grid'
        
        info_items = [
            ("Título da Fonte:", str(metadata.get("title", "Áudio"))),
            ("Data da Transcrição:", datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
            ("Duração:", f"{float(metadata.get('duration', 0.0)):.1f} segundos"),
            ("Idioma Detectado:", f"{metadata.get('language', 'pt').upper()} ({int(float(metadata.get('language_probability', 1.0)) * 100)}%)"),
            ("Modelo Utilizado:", str(metadata.get("model", "faster-whisper")))
        ]

        for i, (label, val) in enumerate(info_items):
            row = meta_table.rows[i]
            cell_label = row.cells[0]
            cell_val = row.cells[1]
            
            p_label = cell_label.paragraphs[0]
            r_l = p_label.add_run(label)
            r_l.font.bold = True
            r_l.font.size = Pt(9.5)
            
            p_val = cell_val.paragraphs[0]
            r_v = p_val.add_run(val)
            r_v.font.size = Pt(9.5)

        doc.add_paragraph().paragraph_format.space_after = Pt(12)

        # Divisor / Cabeçalho da transcrição
        h2 = doc.add_heading("Conteúdo Transcrito", level=1)
        h2.paragraph_format.space_after = Pt(8)

        # Conteúdo com parágrafos
        for seg in segments:
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            
            if include_timestamps:
                # Marcação de tempo em cinza discreto e negrito
                ts = seg.get("timestamp", f"[{seg.get('start', 0.0):.1f}s]")
                ts_run = p.add_run(f"{ts}  ")
                ts_run.font.bold = True
                ts_run.font.size = Pt(9)
                ts_run.font.color.rgb = RGBColor(107, 114, 128) # Cinza suave

            text_run = p.add_run(seg.get("text", ""))
            text_run.font.size = Pt(11)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        doc.save(output_path)
        return output_path


class MarkdownExporter:
    @staticmethod
    def export(
        segments: List[Dict[str, Any]],
        metadata: Dict[str, Any],
        output_path: str,
        include_timestamps: bool = True
    ) -> str:
        title = metadata.get("title", "Áudio")
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        model = metadata.get("model", "faster-whisper")
        lang = metadata.get("language", "pt")
        duration = float(metadata.get("duration", 0.0))

        lines = [
            "---",
            f"title: \"{title}\"",
            f"date: \"{date_str}\"",
            f"model: \"{model}\"",
            f"language: \"{lang}\"",
            f"duration_seconds: {duration:.1f}",
            "---",
            "",
            f"# Transcrição: {title}",
            "",
            f"> Transcrito automaticamente pelo **FastWhisper Web Studio** ({model}) em {date_str}.",
            "",
            "## Conteúdo",
            ""
        ]

        for seg in segments:
            text = seg.get("text", "")
            if include_timestamps:
                ts = seg.get("timestamp", f"[{seg.get('start', 0.0):.1f}s]")
                lines.append(f"**`{ts}`** {text}  ")
            else:
                lines.append(f"{text}\n")

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return output_path


class TextExporter:
    @staticmethod
    def export(
        segments: List[Dict[str, Any]],
        output_path: str,
        include_timestamps: bool = True
    ) -> str:
        lines = []
        for seg in segments:
            text = seg.get("text", "")
            if include_timestamps:
                ts = seg.get("timestamp", f"[{seg.get('start', 0.0):.1f}s]")
                lines.append(f"{ts}  {text}")
            else:
                lines.append(text)

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        return output_path


def export_all(
    segments: List[Dict[str, Any]],
    metadata: Dict[str, Any],
    output_dir: str = "outputs",
    base_filename: str = "transcricao",
    include_timestamps: bool = True
) -> Dict[str, str]:
    """
    Exporta simultaneamente a transcrição nos formatos .docx, .md e .txt.
    Retorna os caminhos dos arquivos gerados.
    """
    os.makedirs(output_dir, exist_ok=True)

    # Remove caracteres inválidos para nome de arquivo
    safe_name = "".join([c for c in base_filename if c.isalnum() or c in (' ', '_', '-')]).strip()
    if not safe_name:
        safe_name = "transcricao"
    safe_name = safe_name[:60]

    docx_path = os.path.join(output_dir, f"{safe_name}.docx")
    md_path = os.path.join(output_dir, f"{safe_name}.md")
    txt_path = os.path.join(output_dir, f"{safe_name}.txt")

    DocxExporter.export(segments, metadata, docx_path, include_timestamps)
    MarkdownExporter.export(segments, metadata, md_path, include_timestamps)
    TextExporter.export(segments, txt_path, include_timestamps)

    return {
        "docx": docx_path,
        "md": md_path,
        "txt": txt_path
    }
