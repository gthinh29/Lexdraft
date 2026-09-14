"""
modules/risk_assessment/retrieval.py

PRIVATE - chỉ được import từ modules/risk_assessment/service.py.
Không được import trực tiếp từ module khác hoặc từ app.py (đúng SRS 3.2).

Truy xuất các điều luật liên quan từ `law_index` phục vụ phân tích rủi ro.
Áp dụng cơ chế module-level cache để load FAISS index 1 lần duy nhất.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

import config
from modules.shared.embedding import VectorDB

logger = logging.getLogger(__name__)

# Cache law_index ở module-level (chỉ load 1 lần cho toàn bộ tiến trình)
_law_db: VectorDB | None = None


def _get_law_db() -> VectorDB:
    global _law_db
    if _law_db is None:
        index_dir = Path(getattr(config, "FAISS_INDEX_DIR", "data/faiss_index"))
        law_index_path = index_dir / "law_index"

        _law_db = VectorDB()
        try:
            _law_db.load_index(str(law_index_path))
        except FileNotFoundError:
            logger.warning(
                "law_index chưa được xây dựng tại '%s'. Chức năng đối soát luật sẽ hoạt động ở chế độ fallback.",
                law_index_path,
            )
    return _law_db


def find_related_laws(dieu_khoan_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Truy xuất các điều luật liên quan đến nội dung của 1 Điều khoản hợp đồng.

    Args:
        dieu_khoan_text: Text của Điều khoản.
        top_k: Số chunk luật lấy về (SRS 6.1 khuyến nghị top_k=3 để tránh phình token
               khi phân tích hợp đồng có nhiều điều khoản).

    Returns:
        Danh sách chunk luật liên quan kèm metadata và score.
    """
    db = _get_law_db()
    if db.index is None or db.index.ntotal == 0:
        return []

    try:
        return db.hybrid_search(query=dieu_khoan_text, top_k=top_k)
    except Exception:
        logger.exception("Lỗi khi truy xuất điều luật cho điều khoản.")
        return []
