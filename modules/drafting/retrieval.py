"""
modules/drafting/retrieval.py

PRIVATE - chỉ được import từ modules/drafting/service.py.
Không được import trực tiếp từ module khác hoặc từ app.py (đúng nguyên tắc
ranh giới module trong SRS 3.2).

Truy xuất:
  - Mẫu hợp đồng phù hợp từ `template_index`.
  - Điều luật liên quan từ `law_index`.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from modules.shared.embedding import VectorDB  # Phần 4 - Dev B
except ImportError:
    VectorDB = None

import config

logger = logging.getLogger(__name__)

# Cache module-level: cả 2 index đều tĩnh (offline), chỉ cần load 1 lần.
_template_db = None
_law_db = None


def _get_template_db():
    global _template_db
    if _template_db is None:
        if VectorDB is None:
            raise RuntimeError(
                "modules.shared.embedding.VectorDB chưa sẵn sàng (Phần 4 chưa build)."
            )
        index_dir = Path(getattr(config, "FAISS_INDEX_DIR", "data/faiss_index"))
        _template_db = VectorDB()
        _template_db.load_index(str(index_dir / "template_index"))
    return _template_db


def _get_law_db():
    global _law_db
    if _law_db is None:
        if VectorDB is None:
            raise RuntimeError(
                "modules.shared.embedding.VectorDB chưa sẵn sàng (Phần 4 chưa build)."
            )
        index_dir = Path(getattr(config, "FAISS_INDEX_DIR", "data/faiss_index"))
        _law_db = VectorDB()
        _law_db.load_index(str(index_dir / "law_index"))
    return _law_db


def retrieve_template(contract_type_query: str, top_k: int = 1) -> Optional[Dict[str, Any]]:
    """
    Lấy mẫu hợp đồng phù hợp nhất từ template_index.

    Args:
        contract_type_query: mô tả loại hợp đồng, vd "hợp đồng thiết kế website".
        top_k: số ứng viên lấy về trước khi chọn cái tốt nhất (mặc định chỉ lấy 1).

    Returns:
        Chunk mẫu tốt nhất (content + metadata), hoặc None nếu không tìm thấy.
    """
    db = _get_template_db()
    hits = db.hybrid_search(contract_type_query, top_k=top_k)

    if not hits:
        logger.warning(
            "Không tìm thấy mẫu hợp đồng phù hợp cho query: '%s'", contract_type_query
        )
        return None

    return hits[0]


def retrieve_relevant_law(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Lấy các điều luật liên quan từ law_index để làm căn cứ soạn thảo.

    Args:
        query: mô tả loại hợp đồng / nội dung cần đối chiếu luật.
        top_k: số chunk luật lấy về (SRS 6.1 khuyến nghị giữ ở mức 3-5).

    Returns:
        Danh sách chunk luật (content + metadata).
    """
    db = _get_law_db()
    return db.hybrid_search(query, top_k=top_k)
