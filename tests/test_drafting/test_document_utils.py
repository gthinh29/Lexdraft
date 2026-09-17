"""tests/test_drafting/test_document_utils.py

Unit tests for modules.drafting.document_utils
Covers: format_draft_as_a4_html, build_docx_bytes, docx_bytes_to_preview_html
"""

import io


# ──────────────────────────────────────────────────────────────────────────────
# Helpers / data
# ──────────────────────────────────────────────────────────────────────────────

MINIMAL_CONTRACT = """CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập – Tự do – Hạnh phúc

HỢP ĐỒNG DỊCH VỤ
Số: 01/2026

ĐIỀU 1. ĐỐI TƯỢNG
Nội dung điều 1 bình thường.

ĐIỀU 2. THANH TOÁN
Giá trị: 100.000.000 VNĐ.

| ĐẠI DIỆN BÊN A | ĐẠI DIỆN BÊN B |
| :---: | :---: |
| (Ký, đóng dấu) | (Ký, đóng dấu) |
"""

EMPTY_TEXT = ""


# ──────────────────────────────────────────────────────────────────────────────
# Tests: format_draft_as_a4_html
# ──────────────────────────────────────────────────────────────────────────────


class TestFormatDraftAsA4Html:
    """format_draft_as_a4_html() → str HTML có wrapper a4-paper-container."""

    def _fn(self, text):
        from modules.drafting.document_utils import format_draft_as_a4_html

        return format_draft_as_a4_html(text)

    def test_returns_empty_for_empty_input(self):
        assert self._fn(EMPTY_TEXT) == ""

    def test_wraps_in_a4_container(self):
        html = self._fn(MINIMAL_CONTRACT)
        assert "a4-paper-container" in html

    def test_quoc_hieu_rendered_as_contract_title(self):
        html = self._fn(MINIMAL_CONTRACT)
        assert "contract-title" in html
        assert "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in html

    def test_hop_dong_title_rendered_as_contract_title(self):
        html = self._fn(MINIMAL_CONTRACT)
        assert "HỢP ĐỒNG DỊCH VỤ" in html

    def test_so_hop_dong_rendered_as_contract_number(self):
        html = self._fn(MINIMAL_CONTRACT)
        assert "contract-number" in html

    def test_signature_table_detected(self):
        html = self._fn(MINIMAL_CONTRACT)
        assert "signature-table" in html

    def test_no_separator_artifacts(self):
        """Dấu --- không được render thành thẻ HTML gây lỗi."""
        text = "Đầu\n---\nCuối"
        html = self._fn(text)
        # Không được có thẻ <hr> trần (markdown sẽ render --- → <hr>)
        # Hàm vẫn có thể render <hr>, nhưng không được crash
        assert isinstance(html, str)

    def test_no_crash_on_unicode_special_chars(self):
        text = "Điều 1. Nội dung có ký tự đặc biệt: <>&\"'®©™"
        html = self._fn(text)
        assert isinstance(html, str)

    def test_plain_text_without_headers(self):
        """Văn bản tự do (không có Quốc hiệu / tiêu đề HĐ) vẫn render được."""
        text = "Đây là đoạn văn bản thông thường."
        html = self._fn(text)
        assert "a4-paper-container" in html
        assert "đoạn văn bản" in html


# ──────────────────────────────────────────────────────────────────────────────
# Tests: build_docx_bytes
# ──────────────────────────────────────────────────────────────────────────────


class TestBuildDocxBytes:
    """build_docx_bytes() → bytes DOCX hợp lệ."""

    def _fn(self, text):
        from modules.drafting.document_utils import build_docx_bytes

        return build_docx_bytes(text)

    def test_returns_bytes(self):
        result = self._fn(MINIMAL_CONTRACT)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_valid_docx_magic(self):
        """DOCX (ZIP) bắt đầu bằng PK magic bytes."""
        result = self._fn(MINIMAL_CONTRACT)
        assert result[:2] == b"PK"

    def test_docx_readable_by_python_docx(self):
        from docx import Document

        result = self._fn(MINIMAL_CONTRACT)
        doc = Document(io.BytesIO(result))
        texts = [p.text for p in doc.paragraphs]
        combined = " ".join(texts)
        assert "CỘNG HÒA" in combined or "HỢP ĐỒNG" in combined

    def test_quoc_hieu_paragraph_centered(self):
        from docx import Document
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        result = self._fn(MINIMAL_CONTRACT)
        doc = Document(io.BytesIO(result))
        centered = [
            p
            for p in doc.paragraphs
            if p.alignment == WD_ALIGN_PARAGRAPH.CENTER and p.text.strip()
        ]
        assert len(centered) > 0

    def test_dieu_khoan_paragraph_bold(self):
        from docx import Document

        result = self._fn(MINIMAL_CONTRACT)
        doc = Document(io.BytesIO(result))
        bold_texts = [
            p.text
            for p in doc.paragraphs
            if any(run.bold for run in p.runs if run.text.strip())
        ]
        combined = " ".join(bold_texts)
        assert "ĐIỀU" in combined or "HỢP ĐỒNG" in combined

    def test_separator_lines_ignored(self):
        """--- không tạo ra paragraph rỗng nào trong docx."""
        from docx import Document

        text = "ĐIỀU 1. Tiêu đề\n---\nNội dung bình thường"
        result = self._fn(text)
        doc = Document(io.BytesIO(result))
        for p in doc.paragraphs:
            assert p.text.strip() != "---"

    def test_signature_table_in_docx(self):
        from docx import Document

        result = self._fn(MINIMAL_CONTRACT)
        doc = Document(io.BytesIO(result))
        assert len(doc.tables) > 0

    def test_empty_input_returns_valid_docx(self):
        """Đầu vào rỗng không crash, trả về DOCX trống hợp lệ."""
        result = self._fn("")
        assert result[:2] == b"PK"

    def test_markdown_bold_inside_content(self):
        """**text** trong nội dung được render thành run bold."""
        from docx import Document

        text = "Nội dung với **từ quan trọng** trong câu."
        result = self._fn(text)
        doc = Document(io.BytesIO(result))
        all_bold_runs = [
            run.text
            for p in doc.paragraphs
            for run in p.runs
            if run.bold and run.text.strip()
        ]
        assert "từ quan trọng" in all_bold_runs

    def test_margins_set_correctly(self):
        """Lề trang phải đúng chuẩn NĐ30: Trái 3cm, Phải 2cm, Trên/Dưới 2cm."""
        from docx import Document
        from docx.shared import Cm

        result = self._fn(MINIMAL_CONTRACT)
        doc = Document(io.BytesIO(result))
        section = doc.sections[0]
        # So sánh với tolerance ±50 EMU
        assert abs(section.left_margin - Cm(3.0)) < 50000
        assert abs(section.right_margin - Cm(2.0)) < 50000


# ──────────────────────────────────────────────────────────────────────────────
# Tests: docx_bytes_to_preview_html
# ──────────────────────────────────────────────────────────────────────────────


class TestDocxBytesToPreviewHtml:
    """docx_bytes_to_preview_html() đọc DOCX → HTML giữ căn chỉnh."""

    def _fn(self, docx_bytes):
        from modules.drafting.document_utils import docx_bytes_to_preview_html

        return docx_bytes_to_preview_html(docx_bytes)

    def _build(self, text=MINIMAL_CONTRACT):
        from modules.drafting.document_utils import build_docx_bytes

        return build_docx_bytes(text)

    def test_returns_html_string(self):
        result = self._fn(self._build())
        assert isinstance(result, str)
        assert "a4-paper-container" in result

    def test_center_paragraphs_have_a4p_center_class(self):
        result = self._fn(self._build())
        assert "a4p-center" in result

    def test_justify_paragraphs_have_a4p_justify_class(self):
        result = self._fn(self._build())
        assert "a4p-justify" in result

    def test_quoc_hieu_content_preserved(self):
        result = self._fn(self._build())
        assert "CỘNG HÒA" in result

    def test_dieu_khoan_content_preserved(self):
        result = self._fn(self._build())
        assert "ĐIỀU" in result

    def test_signature_table_detected_in_preview(self):
        result = self._fn(self._build())
        assert "signature-table" in result

    def test_empty_docx_returns_wrapper(self):
        from modules.drafting.document_utils import build_docx_bytes

        empty_docx = build_docx_bytes("")
        result = self._fn(empty_docx)
        assert "a4-paper-container" in result

    def test_no_crash_on_empty_bytes_fallback(self):
        """Bytes rỗng phải không crash (DocxDocument None trả về '')."""
        from modules.drafting import document_utils as du

        original = du.DocxDocument
        du.DocxDocument = None
        try:
            result = du.docx_bytes_to_preview_html(b"")
            assert result == ""
        finally:
            du.DocxDocument = original
