"""
modules/shared/chunking.py

Module dùng chung: chia văn bản pháp lý / hợp đồng thành các chunk theo
đơn vị "Điều" (structure-aware chunking), đúng theo SRS Chương 5.2.

Không dùng Fixed-size / Recursive / Semantic chunking vì văn bản luật
và hợp đồng đã có ranh giới cấu trúc rõ ràng theo Điều/Khoản.
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Regex chuẩn theo SRS 5.2 - dùng DOTALL để khớp nội dung nhiều dòng trong 1 Điều.
ARTICLE_PATTERN = re.compile(
    r"(Điều\s+\d+[\.:]?.*?)(?=Điều\s+\d+|\Z)",
    re.DOTALL,
)

# Regex phụ để lấy nhãn "Điều X" ra khỏi nội dung, dùng làm metadata.
ARTICLE_LABEL_PATTERN = re.compile(r"Điều\s+\d+")


def chunk_by_article(
    text: str,
    source_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Chia văn bản thành các chunk theo từng "Điều".

    Args:
        text: text thô (đã đọc từ document_reader.read_document).
        source_metadata: metadata gốc của văn bản, vd:
            {"source": "BoLuatDanSu2015.pdf"}
            Sẽ được merge vào metadata của từng chunk.

    Returns:
        Danh sách dict theo format:
        [
            {
                "content": "Điều 1. Nội dung...",
                "metadata": {"source": "...", "article": "Điều 1"}
            },
            ...
        ]

        Fallback: nếu văn bản không chứa từ khóa "Điều" nào (vd: một số
        mẫu hợp đồng tự do không đánh số Điều), toàn bộ text được trả về
        như MỘT chunk duy nhất với "article": None, để không mất dữ liệu.
    """
    source_metadata = dict(source_metadata) if source_metadata else {}

    if not text or not text.strip():
        logger.warning(
            "chunk_by_article nhận text rỗng (source=%s) - trả về mảng rỗng.",
            source_metadata.get("source", "unknown"),
        )
        return []

    matches = list(ARTICLE_PATTERN.finditer(text))

    if not matches:
        logger.warning(
            "Không tìm thấy cấu trúc 'Điều' trong văn bản (source=%s). "
            "Áp dụng fallback: trả về toàn văn bản dưới dạng 1 chunk.",
            source_metadata.get("source", "unknown"),
        )
        return [
            {
                "content": text.strip(),
                "metadata": {**source_metadata, "article": None},
            }
        ]

    chunks: List[Dict[str, Any]] = []

    for match in matches:
        raw_content = match.group(1).strip()

        if not raw_content:
            continue

        label_match = ARTICLE_LABEL_PATTERN.search(raw_content)
        article_label = label_match.group(0) if label_match else None

        chunks.append(
            {
                "content": raw_content,
                "metadata": {**source_metadata, "article": article_label},
            }
        )

    if not chunks:
        # Trường hợp hiếm: có match nhưng nội dung rỗng sau khi strip.
        logger.warning(
            "Regex khớp nhưng không tạo được chunk hợp lệ nào (source=%s).",
            source_metadata.get("source", "unknown"),
        )

    return chunks
