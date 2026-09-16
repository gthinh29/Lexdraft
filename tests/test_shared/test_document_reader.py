"""tests/test_shared/test_document_reader.py

Unit tests for modules.shared.document_reader.
"""

import sys
import tempfile
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from docx import Document as DocxDocument

# Mock pdfplumber before importing document_reader to avoid ModuleNotFoundError
if "pdfplumber" not in sys.modules:
    _mock_pdf = types.ModuleType("pdfplumber")
    _mock_pdf.open = MagicMock()
    sys.modules["pdfplumber"] = _mock_pdf

from modules.shared.document_reader import (  # noqa: E402
    read_document,
    read_docx,
    read_md,
)


class TestDocumentReader:
    """Test suite for document_reader module."""

    def test_read_docx_success(self, sample_docx_file):
        """Kiểm tra đọc file docx hợp lệ."""
        content = read_docx(sample_docx_file)
        assert isinstance(content, str)
        assert "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" in content
        assert "ĐIỀU 1. ĐỐI TƯỢNG HỢP ĐỒNG" in content

    def test_read_md_success(self):
        """Kiểm tra đọc file markdown và text."""
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".md", mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write("# Hợp đồng dịch vụ\nĐiều 1. Nội dung dịch vụ")
            tmp_path = Path(tmp.name)

        try:
            content = read_md(tmp_path)
            assert "# Hợp đồng dịch vụ" in content
            assert "Điều 1" in content
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_read_document_routing_docx(self, sample_docx_file):
        """Kiểm tra routing tự động với file .docx."""
        content = read_document(sample_docx_file)
        assert "ĐIỀU 2" in content

    def test_read_document_routing_md(self):
        """Kiểm tra routing tự động với file .md."""
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".md", mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write("Nội dung markdown thử nghiệm")
            tmp_path = Path(tmp.name)

        try:
            content = read_document(tmp_path)
            assert "Nội dung markdown thử nghiệm" in content
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_read_document_not_found(self):
        """Kiểm tra ném lỗi FileNotFoundError khi đường dẫn không tồn tại."""
        non_existent = Path("non_existent_file_12345.docx")
        with pytest.raises(FileNotFoundError, match="Không tìm thấy file"):
            read_document(non_existent)

    def test_read_document_unsupported_format(self):
        """Kiểm tra ném lỗi ValueError khi định dạng không được hỗ trợ."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as tmp:
            tmp.write(b"binary content")
            tmp_path = Path(tmp.name)

        try:
            with pytest.raises(ValueError, match="Định dạng file không được hỗ trợ"):
                read_document(tmp_path)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_read_empty_docx(self):
        """Kiểm tra đọc file docx hoàn toàn rỗng."""
        doc = DocxDocument()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            doc.save(tmp.name)
            tmp_path = Path(tmp.name)

        try:
            content = read_docx(tmp_path)
            assert content == ""
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
