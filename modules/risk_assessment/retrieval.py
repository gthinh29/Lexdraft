"""Truy vấn các điều luật liên quan từ law_index phục vụ đánh giá rủi ro hợp đồng."""

import logging
from pathlib import Path
from typing import Any, Dict, List

import config

try:
    from modules.shared.embedding import VectorDB
except ImportError:
    VectorDB = None

logger = logging.getLogger(__name__)

_law_db: Any = None


def _get_law_db() -> Any:
    global _law_db
    if _law_db is None:
        if VectorDB is None:
            raise RuntimeError("modules.shared.embedding.VectorDB chưa sẵn sàng.")
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
    """Truy xuất các điều luật liên quan đến nội dung của một điều khoản hợp đồng."""
    db = _get_law_db()
    if db.index is None or db.index.ntotal == 0:
        return []

    try:
        return db.hybrid_search(query=dieu_khoan_text, top_k=top_k)
    except Exception:
        logger.exception("Lỗi khi truy xuất điều luật cho điều khoản.")
        return []
