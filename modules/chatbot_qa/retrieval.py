"""Truy xuất ngữ cảnh kép từ chỉ mục hợp đồng (contract_index) và chỉ mục luật (law_index)."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import config
from modules.chatbot_qa.chat_session import ChatSession

try:
    from modules.shared.embedding import VectorDB
except ImportError:
    VectorDB = None

logger = logging.getLogger(__name__)

_law_db = None

_PARTY_KEYWORDS = (
    "bên a",
    "bên b",
    "ben a",
    "ben b",
    "công ty",
    "cong ty",
    "đại diện",
    "dai dien",
    "chủ thể",
    "chu the",
    "trụ sở",
    "tru so",
    "mã số thuế",
    "ma so thue",
    "khách hàng",
    "khach hang",
)


def _get_law_db():
    global _law_db
    if _law_db is None:
        if VectorDB is None:
            raise RuntimeError("modules.shared.embedding.VectorDB chưa sẵn sàng.")
        index_dir = Path(getattr(config, "FAISS_INDEX_DIR", "data/faiss_index"))
        _law_db = VectorDB()
        _law_db.load_index(str(index_dir / "law_index"))
    return _law_db


def _get_or_build_contract_db(session: ChatSession):
    """Khởi tạo hoặc lấy từ bộ nhớ đệm chỉ mục FAISS cho hợp đồng trong phiên."""
    if VectorDB is None:
        raise RuntimeError("modules.shared.embedding.VectorDB chưa sẵn sàng.")

    if session.contract_vector_db is not None:
        return session.contract_vector_db

    if not session.contract_chunks:
        logger.warning(
            "Session '%s' đang ở Chế độ A nhưng không có contract_chunks.",
            session.session_id,
        )
        return None

    contract_db = VectorDB()
    contract_db.create_index(session.contract_chunks)
    session.contract_vector_db = contract_db
    return contract_db


def _search_contract_chunks(
    query: str, session: ChatSession, limit: int
) -> List[Dict[str, Any]]:
    """Truy xuất các điều khoản liên quan trong hợp đồng đang mở của phiên."""
    contract_db = _get_or_build_contract_db(session)
    if contract_db is None:
        return []

    contract_hits = contract_db.hybrid_search(query, top_k=limit)
    good_hits = [h for h in contract_hits if h.get("score", 0) >= 0.35]
    chosen = good_hits if good_hits else contract_hits[:5]

    if any(kw in query.lower() for kw in _PARTY_KEYWORDS) and session.contract_chunks:
        has_preamble = any(
            h.get("metadata", {}).get("article") == "Lời mở đầu" for h in chosen
        )
        if not has_preamble:
            preamble_hit = next(
                (
                    h
                    for h in contract_hits
                    if h.get("metadata", {}).get("article") == "Lời mở đầu"
                ),
                None,
            )
            if preamble_hit:
                chosen.append(preamble_hit)

    for hit in chosen:
        hit.setdefault("metadata", {})["index"] = "contract_index"
    return chosen


def _search_law_chunks(
    query: str, limit: int, min_score: float
) -> List[Dict[str, Any]]:
    """Truy xuất các điều luật liên quan từ law_index theo ngưỡng tương đồng."""
    law_hits = _get_law_db().hybrid_search(query, top_k=limit)
    good_hits = [h for h in law_hits if h.get("score", 0) >= min_score]
    chosen = good_hits if good_hits else law_hits[:2]
    for hit in chosen:
        hit.setdefault("metadata", {})["index"] = "law_index"
    return chosen


def search_context(
    query: str,
    has_session: bool = False,
    session: Optional[ChatSession] = None,
    top_k: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Truy xuất tổng hợp điều khoản hợp đồng (nếu ở Chế độ A) và căn cứ pháp luật."""
    cfg = getattr(config, "Config", config)
    limit = top_k or getattr(cfg, "RETRIEVAL_TOP_K", 10)
    min_score = getattr(cfg, "RELEVANCE_SCORE_THRESHOLD", 0.65)

    results: List[Dict[str, Any]] = []
    if has_session:
        if session is None:
            raise ValueError("has_session=True nhưng không truyền session.")
        results.extend(_search_contract_chunks(query, session, limit))

    results.extend(_search_law_chunks(query, limit, min_score))
    return results
