"""Truy xuất ngữ cảnh kép từ chỉ mục hợp đồng (contract_index) và chỉ mục luật (law_index)."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from modules.shared.embedding import VectorDB
except ImportError:
    VectorDB = None

import config
from modules.chatbot_qa.chat_session import ChatSession

logger = logging.getLogger(__name__)

_law_db = None


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


def search_context(
    query: str,
    has_session: bool = False,
    session: Optional[ChatSession] = None,
    top_k: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Truy xuất các đoạn điều khoản hợp đồng và điều luật liên quan đến câu hỏi."""
    config_top_k = getattr(getattr(config, "Config", config), "RETRIEVAL_TOP_K", 10)
    limit = top_k or config_top_k
    min_score = getattr(
        getattr(config, "Config", config), "RELEVANCE_SCORE_THRESHOLD", 0.65
    )

    results: List[Dict[str, Any]] = []

    if has_session:
        if session is None:
            raise ValueError("has_session=True nhưng không truyền session.")

        contract_db = _get_or_build_contract_db(session)
        if contract_db is not None:
            contract_hits = contract_db.hybrid_search(query, top_k=limit)
            good_contract_hits = [h for h in contract_hits if h.get("score", 0) >= 0.35]
            chosen_contract = (
                good_contract_hits if good_contract_hits else contract_hits[:5]
            )

            party_keywords = (
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
            q_lower = query.lower()
            if any(kw in q_lower for kw in party_keywords) and session.contract_chunks:
                has_preamble = any(
                    h.get("metadata", {}).get("article") == "Lời mở đầu"
                    for h in chosen_contract
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
                        chosen_contract.append(preamble_hit)

            for hit in chosen_contract:
                hit.setdefault("metadata", {})["index"] = "contract_index"
            results.extend(chosen_contract)

    law_db = _get_law_db()
    law_hits = law_db.hybrid_search(query, top_k=limit)
    good_law_hits = [h for h in law_hits if h.get("score", 0) >= min_score]
    chosen_law = good_law_hits if good_law_hits else law_hits[:2]
    for hit in chosen_law:
        hit.setdefault("metadata", {})["index"] = "law_index"
    results.extend(chosen_law)

    return results
