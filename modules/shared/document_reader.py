"""Đọc và trích xuất nội dung văn bản thô từ file PDF, DOCX, Markdown và TXT."""

import logging
from pathlib import Path
from typing import Union

import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)

PathLike = Union[str, Path]


def read_pdf(file_path: PathLike) -> str:
    """Đọc text từng trang PDF bằng pdfplumber, bỏ qua trang scan không có text."""
    file_path = Path(file_path)
    text_parts = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
            else:
                logger.warning(
                    "Trang %s trong file '%s' không trích xuất được text (có thể là ảnh scan).",
                    page_number,
                    file_path.name,
                )

    return "\n".join(text_parts)


def read_docx(file_path: PathLike) -> str:
    """Đọc toàn bộ đoạn văn bản từ file DOCX bằng python-docx."""
    document = Document(Path(file_path))
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


def read_md(file_path: PathLike) -> str:
    """Đọc nội dung file Markdown hoặc text thuần theo bảng mã UTF-8."""
    return Path(file_path).read_text(encoding="utf-8")


def read_document(file_path: PathLike) -> str:
    """Điều hướng đọc văn bản theo phần mở rộng (.pdf, .docx, .md, .txt)."""
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return read_pdf(file_path)
    if suffix == ".docx":
        return read_docx(file_path)
    if suffix in (".md", ".txt"):
        return read_md(file_path)

    raise ValueError(
        f"Định dạng file không được hỗ trợ: '{suffix}' (file: {file_path.name}). "
        "Hệ thống hỗ trợ .pdf, .docx và .md."
    )
