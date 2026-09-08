"""
modules/shared/document_reader.py

Module dùng chung: đọc nội dung text thô từ file PDF / DOCX.
Không xử lý logic chunking / cấu trúc pháp lý tại đây (xem chunking.py).

Phạm vi hỗ trợ (theo SRS 1.3): chỉ đọc PDF dạng text (không OCR ảnh scan).
"""

import logging
from pathlib import Path
from typing import Union

import pdfplumber
from docx import Document

# TODO: Nếu module logger chuẩn đã có sẵn trong modules/shared/,
# hãy thay dòng dưới bằng: from modules.shared.logger import get_logger
# logger = get_logger(__name__)
logger = logging.getLogger(__name__)

PathLike = Union[str, Path]


def read_pdf(file_path: PathLike) -> str:
    """
    Đọc toàn bộ text từ file PDF bằng pdfplumber.

    Các trang không trích xuất được text (nhiều khả năng là ảnh scan)
    sẽ bị bỏ qua và log warning, KHÔNG raise lỗi để không chặn cả pipeline.

    Args:
        file_path: đường dẫn tới file .pdf

    Returns:
        Toàn bộ text các trang, nối bằng ký tự xuống dòng.
    """
    file_path = Path(file_path)
    text_parts = []

    with pdfplumber.open(file_path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
            else:
                logger.warning(
                    "Trang %s trong file '%s' không trích xuất được text "
                    "(có thể là ảnh scan) - đã bỏ qua.",
                    page_number,
                    file_path.name,
                )

    return "\n".join(text_parts)


def read_docx(file_path: PathLike) -> str:
    """
    Đọc toàn bộ text từ file DOCX bằng python-docx.
    Chỉ lấy text ở cấp paragraph (không đọc text trong bảng/table).

    Args:
        file_path: đường dẫn tới file .docx

    Returns:
        Toàn bộ text các đoạn văn, nối bằng ký tự xuống dòng.
    """
    file_path = Path(file_path)
    document = Document(file_path)

    paragraphs = [p.text for p in document.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def read_document(file_path: PathLike) -> str:
    """
    Controller: tự động chọn hàm đọc phù hợp dựa theo đuôi file.

    Args:
        file_path: đường dẫn tới file .pdf hoặc .docx

    Returns:
        Text thô trích xuất từ file.

    Raises:
        FileNotFoundError: nếu file không tồn tại.
        ValueError: nếu định dạng file không được hỗ trợ.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return read_pdf(file_path)
    elif suffix == ".docx":
        return read_docx(file_path)
    else:
        raise ValueError(
            f"Định dạng file không được hỗ trợ: '{suffix}' (file: {file_path.name}). "
            "Hệ thống chỉ hỗ trợ .pdf và .docx."
        )
