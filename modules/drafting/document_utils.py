"""modules/drafting/document_utils.py

Xử lý xuất tài liệu Word (.docx) và kết xuất HTML A4 preview cho Hợp đồng.
"""

import io
import re

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None


def format_draft_as_a4_html(draft_text: str) -> str:
    """Format markdown text into a formal A4 legal paper HTML layout using markdown-it.

    Special header lines (contract title, number, quoc hieu) are extracted BEFORE
    markdown rendering to avoid markdown-it wrapping them in <p> tags (which would
    override centering via the justify rule).
    """
    if not draft_text:
        return ""

    try:
        from markdown_it import MarkdownIt

        md = MarkdownIt("commonmark", {"html": True}).enable("table")
    except Exception:  # noqa: BLE001
        md = None

    lines = draft_text.split("\n")
    # We'll build segments: each segment is either a raw HTML string (special header)
    # or a list of normal lines to be rendered with markdown-it.
    segments = []  # list of {"type": "html"|"md", "content": str}
    md_buffer = []

    def flush_md_buffer():
        if md_buffer:
            text = "\n".join(md_buffer)
            segments.append({"type": "md", "content": text})
            md_buffer.clear()

    for line in lines:
        line_str = line.strip()
        if not line_str:
            md_buffer.append("")
            continue

        clean = re.sub(r"^[#\*\_\-\s]+|[#\*\_\-\s]+$", "", line_str).strip()
        clean_upper = clean.upper()

        special_html = None
        if "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in clean_upper:
            special_html = "<div class='contract-title' style='font-size:1.15rem;'>CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</div>"
        elif "ĐỘC LẬP" in clean_upper and "HẠNH PHÚC" in clean_upper:
            special_html = (
                "<div class='contract-title' style='font-size:1.1rem;margin-top:2px;'>Độc lập – Tự do – Hạnh phúc</div>"
                "<div class='contract-number' style='font-size:0.85rem;margin:4px auto 18px auto;letter-spacing:2px;font-style:normal;'>---o0o---</div>"
            )
        elif (
            ("HỢP ĐỒNG" in clean_upper or "BẢN NHÁP" in clean_upper)
            and len(clean) < 120
            and not clean_upper.startswith("ĐIỀU")
        ):
            special_html = f"<div class='contract-title'>{clean}</div>"
        elif bool(re.match(r"^SỐ\s*:", clean_upper)):
            special_html = f"<div class='contract-number'>{clean}</div>"

        if special_html is not None:
            flush_md_buffer()
            segments.append({"type": "html", "content": special_html})
        else:
            md_buffer.append(line_str)

    flush_md_buffer()

    # Now render each segment
    html_parts = []
    for seg in segments:
        if seg["type"] == "html":
            html_parts.append(seg["content"])
        else:
            if md is not None:
                rendered = md.render(seg["content"])
            else:
                rendered = seg["content"].replace("\n", "<br>")
            html_parts.append(rendered)

    html = "".join(html_parts)

    # Phân loại bảng thông thường (căn trái) vs Bảng chữ ký 2 bên (căn giữa)
    def _mark_signature_tables(match):
        table_html = match.group(0)
        if any(kw in table_html for kw in ["ĐẠI DIỆN", "(Ký", "Ký,", "Ký tên"]):
            return table_html.replace("<table>", "<table class='signature-table'>", 1)
        return table_html

    html = re.sub(r"<table>.*?</table>", _mark_signature_tables, html, flags=re.DOTALL)

    return f"<div class='a4-paper-container'>{html}</div>"


def build_docx_bytes(draft_text: str) -> bytes:
    """Tạo file Word (.docx) chuẩn mẫu văn bản pháp quy Việt Nam (Nghị định 30/2020/NĐ-CP)."""
    if DocxDocument is None:
        raise RuntimeError("python-docx chưa được cài đặt.")

    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Cm, Inches, Pt, RGBColor

    doc = DocxDocument()

    # Căn lề trang chuẩn A4 Việt Nam (Trên 2cm, Dưới 2cm, Trái 3cm, Phải 2cm)
    for section in doc.sections:
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(2.0)

    # Cấu hình Style mặc định Times New Roman 13pt
    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(13)
    normal_style.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
    normal_style.paragraph_format.line_spacing = 1.25
    normal_style.paragraph_format.space_after = Pt(4)

    lines = draft_text.split("\n")
    in_table = False
    table_rows = []

    def _add_styled_runs(paragraph, text):
        parts = re.split(r"(\*\*.*?\*\*|\*.*?\*)", text)
        for part in parts:
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

    def _flush_table(rows):
        if not rows:
            return
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

        is_sig = any(
            "ĐẠI DIỆN" in str(r) or "(Ký" in str(r) or "Ký," in str(r)
            for r in parsed_rows
        )

        for row_idx, row_data in enumerate(parsed_rows):
            for col_idx, cell_text in enumerate(row_data):
                if col_idx < num_cols:
                    cell = table.cell(row_idx, col_idx)
                    p = cell.paragraphs[0]
                    p.paragraph_format.space_after = Pt(2)
                    p.paragraph_format.first_line_indent = Pt(0)
                    if is_sig:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    else:
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    _add_styled_runs(p, cell_text)

        p_after = doc.add_paragraph()
        p_after.paragraph_format.space_after = Pt(4)

    for line in lines:
        line_str = line.strip()
        if not line_str:
            if in_table:
                in_table = False
                _flush_table(table_rows)
                table_rows = []
            continue

        clean_text_str = (
            line_str.replace("**", "")
            .replace("__", "")
            .replace("###", "")
            .replace("##", "")
            .replace("#", "")
            .strip()
        )

        if "|" in line_str:
            in_table = True
            table_rows.append(line_str)
            continue

        # Bỏ qua dấu ngăn cách Markdown (--- hoặc ***)
        if re.match(r"^[-\*_]{3,}$", line_str):
            continue

        if in_table:
            in_table = False
            _flush_table(table_rows)
            table_rows = []

        # 1. Quốc hiệu
        if "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in clean_text_str:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM")
            run.bold = True
            run.font.size = Pt(13)
        # 2. Tiêu ngữ
        elif (
            "Độc lập – Tự do – Hạnh phúc" in clean_text_str
            or "Độc lập - Tự do - Hạnh phúc" in clean_text_str
        ):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(12)
            run = p.add_run("Độc lập – Tự do – Hạnh phúc")
            run.bold = True
            run.font.size = Pt(13)
        # 3. Tên Hợp đồng
        elif clean_text_str.startswith(("HỢP ĐỒNG", "BẢN NHÁP HỢP ĐỒNG")):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(clean_text_str)
            run.bold = True
            run.font.size = Pt(16)
        # 4. Số Hợp đồng
        elif clean_text_str.startswith(("Số:", "Số :")):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(14)
            run = p.add_run(clean_text_str)
            run.italic = True
        # 5. ĐIỀU khoản hoặc Tiêu đề mục chính
        elif (
            clean_text_str.upper().startswith("ĐIỀU ")
            or clean_text_str.upper().startswith("THÔNG TIN CÁC BÊN")
            or clean_text_str.upper().startswith("BÊN A")
            or clean_text_str.upper().startswith("BÊN B")
            or line_str.startswith("#")
        ):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(clean_text_str.upper())
            run.bold = True
            run.font.size = Pt(13)
        # 6. Căn cứ pháp lý
        elif "Căn cứ" in clean_text_str or "căn cứ" in clean_text_str:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.first_line_indent = Inches(0.3)
            p.paragraph_format.space_after = Pt(3)
            formatted_cancu = re.sub(r"^[\*\-\#\s]+", "", line_str)
            formatted_cancu = (
                formatted_cancu.replace("**", "")
                .replace("*", "")
                .replace("#", "")
                .strip()
            )
            run = p.add_run(f"- {formatted_cancu}")
            run.italic = True
        # 7. Đoạn văn bản bình thường / danh sách
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

    if in_table and table_rows:
        _flush_table(table_rows)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


def docx_bytes_to_preview_html(docx_bytes: bytes) -> str:
    """Render .docx bytes → HTML bằng cách đọc trực tiếp alignment/style từ python-docx.

    Căn giữa tự động dựa vào paragraph.alignment trong Word — không cần regex hay heuristic.
    """
    if DocxDocument is None:
        return ""

    from docx.enum.text import WD_ALIGN_PARAGRAPH

    ALIGN_MAP = {
        WD_ALIGN_PARAGRAPH.CENTER: "center",
        WD_ALIGN_PARAGRAPH.RIGHT: "right",
        WD_ALIGN_PARAGRAPH.JUSTIFY: "justify",
        WD_ALIGN_PARAGRAPH.LEFT: "left",
        None: "justify",  # default Normal style → justify
    }

    doc = DocxDocument(io.BytesIO(docx_bytes))
    parts = []

    def _runs_to_html(paragraph):
        """Chuyển runs của paragraph thành inline HTML (giữ bold/italic)."""
        html_runs = []
        for run in paragraph.runs:
            text = (
                run.text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
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

    def _table_to_html(table):
        rows_html = []
        is_sig = any(
            any(kw in cell.text for kw in ["ĐẠI DIỆN", "(Ký", "Ký,", "Ký tên"])
            for row in table.rows
            for cell in row.cells
        )
        cls = " class='signature-table'" if is_sig else ""
        for row in table.rows:
            cells_html = []
            for cell in row.cells:
                cell_content = "<br>".join(
                    _runs_to_html(p) or "&nbsp;" for p in cell.paragraphs
                )
                cells_html.append(f"<td>{cell_content}</td>")
            rows_html.append("<tr>" + "".join(cells_html) + "</tr>")
        return f"<table{cls}><tbody>" + "".join(rows_html) + "</tbody></table>"

    for block in doc.element.body:
        tag = block.tag.split("}")[-1]  # 'p' hoặc 'tbl'

        if tag == "p":
            from docx.text.paragraph import Paragraph

            para = Paragraph(block, doc)
            inline = _runs_to_html(para)
            # Bỏ qua dòng trống hoặc dấu ngăn cách (--- ***)
            if not inline.strip() or re.match(r"^[-\*_]{3,}$", para.text.strip()):
                parts.append("<p style='margin:4px 0;'>&nbsp;</p>")
                continue

            align = ALIGN_MAP.get(para.alignment, "justify")

            # Font size → heading vs normal
            max_pt = 0
            for run in para.runs:
                if run.font.size:
                    max_pt = max(max_pt, run.font.size.pt)

            is_bold = any(run.bold for run in para.runs if run.text.strip())

            if align == "center":
                # Căn giữa tự động từ Word alignment — dùng CSS class để override Streamlit
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
            from docx.table import Table

            tbl = Table(block, doc)
            parts.append(_table_to_html(tbl))

    html_body = "".join(parts)
    return f"<div class='a4-paper-container'>{html_body}</div>"
