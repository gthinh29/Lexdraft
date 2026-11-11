"""Xuất bản hợp đồng sang file Word (.docx) chuẩn Nghị định 30/2020/NĐ-CP và dựng giao diện giấy A4 HTML."""

import io
import re

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

_SIG_KEYWORDS = ("ĐẠI DIỆN", "(Ký", "Ký,", "Ký tên")


def _mark_signature_tables(html_text: str) -> str:
    def _replace(match):
        table_html = match.group(0)
        if any(kw in table_html for kw in _SIG_KEYWORDS):
            return table_html.replace("<table>", "<table class='signature-table'>", 1)
        return table_html

    return re.sub(r"<table>.*?</table>", _replace, html_text, flags=re.DOTALL)


def format_draft_as_a4_html(draft_text: str) -> str:
    """Chuyển đổi văn bản hợp đồng Markdown sang bố cục trang giấy A4 HTML."""
    if not draft_text:
        return ""

    try:
        from markdown_it import MarkdownIt

        md = MarkdownIt("commonmark", {"html": True}).enable("table")
    except Exception:  # noqa: BLE001
        md = None

    segments = []
    md_buffer = []

    def _flush_md():
        if md_buffer:
            segments.append({"type": "md", "content": "\n".join(md_buffer)})
            md_buffer.clear()

    for line in draft_text.split("\n"):
        line_str = line.strip()
        if not line_str:
            md_buffer.append("")
            continue

        clean = re.sub(r"^[#\*\_\-\s]+|[#\*\_\-\s]+$", "", line_str).strip()
        clean_upper = clean.upper()

        special_html = None
        if re.match(r"^[-_\*]*o0o[-_\*]*$", clean, re.IGNORECASE):
            special_html = "<div class='contract-number' style='font-style:normal;letter-spacing:2px;margin:2px auto 10px auto;'>---o0o---</div>"
        elif "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in clean_upper:
            special_html = "<div class='contract-title' style='font-size:1.15rem;'>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>"
        elif "ĐỘC LẬP" in clean_upper and "HẠNH PHÚC" in clean_upper:
            special_html = "<div class='contract-title' style='font-size:1.1rem;margin-top:2px;'>Độc lập – Tự do – Hạnh phúc</div>"
        elif (
            ("HỢP ĐỒNG" in clean_upper or "BẢN NHÁP" in clean_upper)
            and len(clean) < 120
            and not clean_upper.startswith("ĐIỀU")
        ):
            special_html = f"<div class='contract-title'>{clean}</div>"
        elif re.match(r"^SỐ\s*:", clean_upper):
            special_html = f"<div class='contract-number'>{clean}</div>"

        if special_html is not None:
            _flush_md()
            segments.append({"type": "html", "content": special_html})
        else:
            md_buffer.append(line_str)

    _flush_md()

    html_parts = []
    for seg in segments:
        if seg["type"] == "html":
            html_parts.append(seg["content"])
        else:
            rendered = (
                md.render(seg["content"])
                if md is not None
                else seg["content"].replace("\n", "<br>")
            )
            html_parts.append(rendered)

    return f"<div class='a4-paper-container'>{_mark_signature_tables(''.join(html_parts))}</div>"


def _add_styled_runs(paragraph, text: str) -> None:
    """Chèn văn bản có giữ nguyên định dạng in đậm (**...**) và in nghiêng (*...*)."""
    for part in re.split(r"(\*\*.*?\*\*|\*.*?\*)", text):
        if not part:
            continue
        run = paragraph.add_run()
        if part.startswith("**") and part.endswith("**"):
            run.text = part[2:-2]
            run.bold = True
        elif part.startswith("*") and part.endswith("*"):
            run.text = part[1:-1]
            run.italic = True
        else:
            run.text = part


def _flush_docx_table(doc, rows: list) -> None:
    """Dựng bảng Word từ các dòng bảng Markdown và căn giữa nếu là bảng chữ ký."""
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt

    parsed_rows = []
    for r in rows:
        cells = [c.strip() for c in r.split("|")[1:-1]]
        if cells and not all(c.startswith("-") or c == "" for c in cells):
            parsed_rows.append(cells)
    if not parsed_rows:
        return

    num_cols = max(len(r) for r in parsed_rows)
    table = doc.add_table(rows=len(parsed_rows), cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    is_sig = any(any(kw in str(r) for kw in _SIG_KEYWORDS) for r in parsed_rows)

    for row_idx, row_data in enumerate(parsed_rows):
        for col_idx, cell_text in enumerate(row_data):
            if col_idx < num_cols:
                p = table.cell(row_idx, col_idx).paragraphs[0]
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.first_line_indent = Pt(0)
                p.alignment = (
                    WD_ALIGN_PARAGRAPH.CENTER if is_sig else WD_ALIGN_PARAGRAPH.LEFT
                )
                _add_styled_runs(p, cell_text)

    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def _is_section_heading(line_str: str, clean_text: str, clean_upper: str) -> bool:
    """Xác định dòng có phải tiêu đề Điều khoản hoặc tiêu đề mục chính hay không."""
    if (
        re.match(r"^ĐIỀU\s+\d+(?:[\.\:\s]|$)", clean_upper) and len(clean_text) <= 140
    ) or clean_upper.startswith("THÔNG TIN CÁC BÊN"):
        return True
    if line_str.startswith("#"):
        return True
    return len(clean_text) <= 65 and bool(
        re.match(r"^BÊN\s+[AB]\s*(?:\([^)]+\))?\s*:?\s*$", clean_upper)
    )


def build_docx_bytes(draft_text: str) -> bytes:
    """Tạo file Word (.docx) chuẩn hành chính Việt Nam (Nghị định 30/2020/NĐ-CP)."""
    if DocxDocument is None:
        raise RuntimeError("python-docx chưa được cài đặt.")

    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Cm, Inches, Pt, RGBColor

    doc = DocxDocument()
    for section in doc.sections:
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(2.0)

    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(13)
    normal_style.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    normal_style.paragraph_format.line_spacing = 1.25
    normal_style.paragraph_format.space_after = Pt(4)

    table_rows = []
    for line in draft_text.split("\n"):
        line_str = line.strip()
        if not line_str:
            if table_rows:
                _flush_docx_table(doc, table_rows)
                table_rows = []
            continue

        if "|" in line_str:
            table_rows.append(line_str)
            continue

        if re.match(r"^[-\*_]{3,}$", line_str):
            continue

        if table_rows:
            _flush_docx_table(doc, table_rows)
            table_rows = []

        clean_text = (
            line_str.replace("**", "")
            .replace("__", "")
            .replace("###", "")
            .replace("##", "")
            .replace("#", "")
            .strip()
        )
        clean_upper = clean_text.upper()

        if re.match(r"^[-_\*]*o0o[-_\*]*$", clean_text, re.IGNORECASE):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(8)
            p.add_run("---o0o---").font.size = Pt(12)
        elif "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in clean_upper:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM")
            run.bold = True
            run.font.size = Pt(13)
        elif "ĐỘC LẬP" in clean_upper and "HẠNH PHÚC" in clean_upper:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run("Độc lập – Tự do – Hạnh phúc")
            run.bold = True
            run.font.size = Pt(13)
        elif (
            clean_upper.startswith(("HỢP ĐỒNG", "BẢN NHÁP HỢP ĐỒNG"))
            and len(clean_text) < 120
        ):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(clean_text)
            run.bold = True
            run.font.size = Pt(16)
        elif clean_upper.startswith(("SỐ:", "SỐ :")):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(10)
            run = p.add_run(clean_text)
            run.italic = True
        elif _is_section_heading(line_str, clean_text, clean_upper):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(clean_text.upper())
            run.bold = True
            run.font.size = Pt(13)
        elif re.match(r"^[-•*\s]*Căn\s+cứ\b", clean_text, re.IGNORECASE):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.first_line_indent = Inches(0.3)
            p.paragraph_format.space_after = Pt(3)
            formatted_cancu = re.sub(r"^[\*\-\•\#\s]+", "", line_str)
            formatted_cancu = (
                formatted_cancu.replace("**", "")
                .replace("*", "")
                .replace("#", "")
                .strip()
            )
            p.add_run(f"- {formatted_cancu}").italic = True
        else:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(4)
            p_text = re.sub(r"^#+\s*", "", line_str).strip()
            if p_text.startswith(("* ", "- ")):
                p_text = "• " + p_text[2:].strip()
            else:
                p.paragraph_format.first_line_indent = Inches(0.4)
            _add_styled_runs(p, p_text)

    if table_rows:
        _flush_docx_table(doc, table_rows)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


def _runs_to_html(paragraph) -> str:
    """Chuyển danh sách runs của một đoạn Word sang inline HTML."""
    html_runs = []
    for run in paragraph.runs:
        text = run.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if not text:
            continue
        if run.bold and run.italic:
            text = f"<strong><em>{text}</em></strong>"
        elif run.bold:
            text = f"<strong>{text}</strong>"
        elif run.italic:
            text = f"<em>{text}</em>"
        html_runs.append(text)
    return "".join(html_runs)


def _docx_table_to_html(table) -> str:
    """Chuyển bảng python-docx sang thẻ <table> HTML, tự gắn class bảng chữ ký."""
    is_sig = any(
        any(kw in cell.text for kw in _SIG_KEYWORDS)
        for row in table.rows
        for cell in row.cells
    )
    cls = " class='signature-table'" if is_sig else ""
    rows_html = [
        "<tr>"
        + "".join(
            f"<td>{'<br>'.join(_runs_to_html(p) or '&nbsp;' for p in cell.paragraphs)}</td>"
            for cell in row.cells
        )
        + "</tr>"
        for row in table.rows
    ]
    return f"<table{cls}><tbody>{''.join(rows_html)}</tbody></table>"


def docx_bytes_to_preview_html(docx_bytes: bytes) -> str:
    """Chuyển file .docx bytes sang HTML giữ nguyên căn chỉnh đoạn và bảng chữ ký."""
    if DocxDocument is None:
        return ""

    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    align_map = {
        WD_ALIGN_PARAGRAPH.CENTER: "center",
        WD_ALIGN_PARAGRAPH.RIGHT: "right",
        WD_ALIGN_PARAGRAPH.JUSTIFY: "justify",
        WD_ALIGN_PARAGRAPH.LEFT: "left",
        None: "justify",
    }

    doc = DocxDocument(io.BytesIO(docx_bytes))
    parts = []
    for block in doc.element.body:
        tag = block.tag.split("}")[-1]
        if tag == "p":
            para = Paragraph(block, doc)
            inline = _runs_to_html(para)
            if not inline.strip() or re.match(r"^[-\*_]{3,}$", para.text.strip()):
                parts.append("<p style='margin:4px 0;'>&nbsp;</p>")
                continue

            align = align_map.get(para.alignment, "justify")
            if align == "center":
                max_pt = max(
                    (run.font.size.pt for run in para.runs if run.font.size),
                    default=0,
                )
                is_bold = any(run.bold for run in para.runs if run.text.strip())
                fs = max(max_pt, 13)
                bold_style = (
                    "font-weight:bold;text-transform:uppercase;" if is_bold else ""
                )
                parts.append(
                    f"<p class='a4p-center' style='font-size:{fs:.0f}pt;{bold_style}'>{inline}</p>"
                )
            elif align == "justify":
                parts.append(f"<p class='a4p-justify'>{inline}</p>")
            else:
                parts.append(f"<p class='a4p-left'>{inline}</p>")
        elif tag == "tbl":
            parts.append(_docx_table_to_html(Table(block, doc)))

    return f"<div class='a4-paper-container'>{''.join(parts)}</div>"
