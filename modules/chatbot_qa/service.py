"""
modules/chatbot_qa/service.py

PUBLIC - đây là interface DUY NHẤT mà module chatbot_qa expose ra bên ngoài
(app.py hoặc module khác chỉ được gọi qua đây, KHÔNG được import thẳng
retrieval.py, prompts.py hay chat_session.py).
"""

import logging
from typing import Any, Dict, List, Optional

from modules.chatbot_qa import prompts, retrieval
from modules.chatbot_qa.chat_session import ChatSession

try:
    from modules.shared import llm_client  # Phần 6 - Dev B
except ImportError:
    llm_client = None

logger = logging.getLogger(__name__)

# Lưu session trong RAM theo session_id (đủ dùng cho 1 tiến trình Streamlit).
# Nếu cần persist qua nhiều lần restart app, thay bằng DB/redis tại đây.
_SESSIONS: Dict[str, ChatSession] = {}


def _get_or_create_session(session_id: str) -> ChatSession:
    if session_id not in _SESSIONS:
        _SESSIONS[session_id] = ChatSession(session_id)
    return _SESSIONS[session_id]


def attach_contract_context(
    session_id: str,
    contract_chunks: List[Dict[str, Any]],
    risk_report: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """
    Gọi từ app.py (Phần 10) NGAY SAU KHI Module 1 (Soạn thảo) hoặc Module 2
    (Gợi ý rủi ro) hoàn tất, để chuyển phiên chat sang Chế độ A.

    Không bắt buộc gọi hàm này nếu người dùng chỉ vào thẳng tab Chatbot để
    tra cứu luật chung (Chế độ B) - khi đó session giữ nguyên has_contract_context=False.

    Args:
        session_id: định danh phiên (nên trùng với session_id đã dùng ở
            drafting.service.generate_contract_draft / risk_assessment.service.analyze_contract).
        contract_chunks: các chunk Điều/Khoản của hợp đồng (từ chunking.chunk_by_article).
        risk_report: kết quả gợi ý rủi ro từ Module 2 (Phần 8), có thể để None.
    """
    session = _get_or_create_session(session_id)
    session.set_contract_context(contract_chunks, risk_report)


def handle_chat(
    message: str,
    session_id: str,
    risk_report_context: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Xử lý 1 lượt hỏi-đáp của chatbot (đúng SRS 4.3).

    Args:
        message: câu hỏi hiện tại của người dùng.
        session_id: định danh phiên hội thoại.
        risk_report_context: báo cáo rủi ro (nếu có) để nạp/refresh vào session.
            Truyền None nếu session đã có sẵn context từ trước (qua
            attach_contract_context) hoặc đang ở Chế độ B (tra cứu luật chung).
            Lưu ý: hàm này KHÔNG tự bật Chế độ A chỉ vì có risk_report_context -
            muốn bật Chế độ A với contract_chunks đầy đủ, hãy gọi
            attach_contract_context() trước.

    Returns:
        {"answer": str, "citations": list}

    Raises:
        RuntimeError: nếu modules.shared.llm_client (Phần 6) chưa sẵn sàng.
    """
    if llm_client is None:
        raise RuntimeError(
            "modules.shared.llm_client chưa sẵn sàng (Phần 6 chưa build)."
        )

    session = _get_or_create_session(session_id)

    if risk_report_context is not None:
        session.risk_report = risk_report_context

    # Lấy lịch sử TRƯỚC khi thêm lượt hỏi hiện tại, để không lặp câu hỏi trong prompt.
    history_before = session.get_text_history()
    session.add_message("user", message)

    # 9.2: retrieval - contract_index (nếu Chế độ A) + law_index
    context_chunks = retrieval.search_context(
        query=message,
        has_session=session.has_contract_context,
        session=session,
    )

    # 9.3: ghép prompt theo đúng chế độ hiện tại của session
    prompt = prompts.build_chat_prompt(
        query=message,
        context_chunks=context_chunks,
        history=history_before,
        has_contract_context=session.has_contract_context,
        risk_report=session.risk_report,
    )

    # Gọi LLM qua cơ chế chống hallucination chung (Phần 6)
    result = llm_client.generate_grounded_response(
        query=prompt,
        retrieved_chunks=context_chunks,
    )

    answer = result.get("answer", "")
    citations = result.get("citations", [])

    session.add_message("model", answer)

    return {"answer": answer, "citations": citations}
