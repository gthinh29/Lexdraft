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
    top_k: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Truy xuất ngữ cảnh liên quan cho 1 câu hỏi của người dùng.
    Linh hoạt lấy tối đa RETRIEVAL_TOP_K điều luật có độ tương đồng cao (>= RELEVANCE_SCORE_THRESHOLD).

    Args:
        query: câu hỏi hiện tại.
        has_session: True nếu phiên đang ở Chế độ A (có ngữ cảnh hợp đồng).
        session: đối tượng ChatSession hiện tại - BẮT BUỘC nếu has_session=True.
        top_k: số chunk lấy về tối đa (mặc định lấy từ config.RETRIEVAL_TOP_K, thường là 10).

    Returns:
        Danh sách chunk (content + metadata), gộp từ contract_index và law_index.
    """
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
            # Lấy các điều khoản có độ tương đồng tốt (>= 0.35) hoặc top 5 điều khoản liên quan nhất
            good_contract_hits = [h for h in contract_hits if h.get("score", 0) >= 0.35]
            chosen_contract = (
                good_contract_hits if good_contract_hits else contract_hits[:5]
            )

            # Đảm bảo nếu câu hỏi về các bên mà chunk Lời mở đầu chưa có trong top thì đính kèm theo điểm tìm kiếm tự nhiên
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
    # Lọc các điều luật có điểm tương đồng cao >= min_score
    good_law_hits = [h for h in law_hits if h.get("score", 0) >= min_score]
    # Nếu không có điều nào đạt min_score, giữ lại 2 điều cao nhất để downstream llm_client kiểm tra ngưỡng từ chối
    chosen_law = good_law_hits if good_law_hits else law_hits[:2]
    for hit in chosen_law:
        hit.setdefault("metadata", {})["index"] = "law_index"
    results.extend(chosen_law)

    return results
