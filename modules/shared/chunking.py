"""Phân đoạn văn bản pháp lý và hợp đồng thành từng Điều khoản độc lập."""

import logging
import re
from typing import Any, Dict, List, Optional

from modules.shared.law_metadata import extract_law_header, extract_template_header

logger = logging.getLogger(__name__)

FALLBACK_ARTICLE_LABEL = "Quy định chung"

ARTICLE_HEADER_PATTERN = re.compile(
    r"(?m)^(?:#{1,4}\s*)?(?:\*{1,2})?Điều\s+(\d+)[.:\s]?(.*?)$",
    re.IGNORECASE,
)


def chunk_by_article(
    text: str,
    source_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Chia văn bản thành các chunk theo từng Điều; giữ Lời mở đầu nếu đứng trước Điều 1."""
    source_metadata = dict(source_metadata) if source_metadata else {}

    if not text or not text.strip():
        logger.warning(
            "chunk_by_article nhận text rỗng (source=%s).",
            source_metadata.get("source", "unknown"),
        )
        return []

    matches = list(ARTICLE_HEADER_PATTERN.finditer(text))
    if not matches:
        return [
            {
                "content": text.strip(),
                "metadata": {**source_metadata, "article": FALLBACK_ARTICLE_LABEL},
            }
        ]

    chunks: List[Dict[str, Any]] = []
    preamble_text = text[: matches[0].start()].strip()
    if preamble_text:
        chunks.append(
            {
                "content": preamble_text,
                "metadata": {**source_metadata, "article": "Lời mở đầu"},
            }
        )

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        art_content = text[start:end].strip()
        if not art_content:
            continue
        chunks.append(
            {
                "content": art_content,
                "metadata": {**source_metadata, "article": f"Điều {match.group(1)}"},
            }
        )

    return chunks


chunk_contract_by_articles = chunk_by_article

__all__ = [
    "FALLBACK_ARTICLE_LABEL",
    "ARTICLE_HEADER_PATTERN",
    "chunk_by_article",
    "chunk_contract_by_articles",
    "extract_law_header",
    "extract_template_header",
]
