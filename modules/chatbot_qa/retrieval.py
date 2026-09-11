"""
modules/chatbot_qa/retrieval.py

PRIVATE - chỉ được import từ modules/chatbot_qa/service.py.

search_context(query, has_session):
  - has_session=False (Chế độ B): chỉ search law_index.
  - has_session=True  (Chế độ A): search cả contract_index (ephemeral, theo
    session hiện tại) + law_index.

LƯU Ý ranh giới module (SRS 3.2): contract_index của phiên KHÔNG được đọc
trực tiếp từ state nội bộ của risk_assessment. Dữ liệu contract_chunks phải
được truyền vào từ bên ngoài qua interface công khai
(chatbot_qa/service.py::attach_contract_context), sau đó module này tự build
và cache 1 VectorDB ephemeral ngay trên object ChatSession.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from modules.shared.embedding import VectorDB  # Phần 4 - Dev B
except ImportError:
    VectorDB = None

import config
from modules.chatbot_qa.chat_session import ChatSession

logger = logging.getLogger(__name__)

# law_index tĩnh (offline), chỉ cần load 1 lần cho toàn bộ module.
_law_db = None


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


def _get_or_build_contract_db(session: ChatSession):
    """
    Build (hoặc lấy từ cache) contract_index ephemeral cho 1 phiên cụ thể.
    """
    if VectorDB is None:
        raise RuntimeError(
            "modules.shared.embedding.VectorDB chưa sẵn sàng (Phần 4 chưa build)."
        )

    if session.contract_vector_db is not None:
        return session.contract_vector_db

    if not session.contract_chunks:
        logger.warning(
            "Session '%s' đang ở Chế độ A nhưng không có contract_chunks nào "
            "để build contract_index - bỏ qua bước search hợp đồng.",
            session.session_id,
        )
        return None

    contract_db = VectorDB()
    contract_db.create_index(session.contract_chunks)
    session.contract_vector_db = contract_db  # cache lại cho các lượt hỏi sau
    return contract_db


def search_context(
    query: str,
    has_session: bool = False,
    session: Optional[ChatSession] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Truy xuất ngữ cảnh liên quan cho 1 câu hỏi của người dùng.

    Args:
        query: câu hỏi hiện tại.
        has_session: True nếu phiên đang ở Chế độ A (có ngữ cảnh hợp đồng).
        session: đối tượng ChatSession hiện tại - BẮT BUỘC nếu has_session=True.
        top_k: số chunk lấy về mỗi index (SRS 6.1 khuyến nghị 3-5).

    Returns:
        Danh sách chunk (content + metadata), gộp từ contract_index (nếu có,
        đánh dấu metadata["index"] = "contract_index") và law_index
        (metadata["index"] = "law_index").
    """
    results: List[Dict[str, Any]] = []

    if has_session:
        if session is None:
            raise ValueError("has_session=True nhưng không truyền session.")

        contract_db = _get_or_build_contract_db(session)
        if contract_db is not None:
            contract_hits = contract_db.hybrid_search(query, top_k=top_k)
            for hit in contract_hits:
                hit.setdefault("metadata", {})["index"] = "contract_index"
            results.extend(contract_hits)

    law_db = _get_law_db()
    law_hits = law_db.hybrid_search(query, top_k=top_k)
    for hit in law_hits:
        hit.setdefault("metadata", {})["index"] = "law_index"
    results.extend(law_hits)

    return results
