"""Điều phối luồng hỏi đáp Chatbot pháp lý (Session -> Retrieval -> Prompt -> LLM)."""

import logging
from typing import Any, Dict, List, Optional

from modules.chatbot_qa import prompts, retrieval
from modules.chatbot_qa.chat_session import ChatSession

try:
    from modules.shared import llm_client
except ImportError:
    llm_client = None

logger = logging.getLogger(__name__)

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
    """Nạp hoặc xóa ngữ cảnh hợp đồng cho phiên chat (chuyển đổi giữa Chế độ A và Chế độ B)."""
    session = _get_or_create_session(session_id)
    session.set_contract_context(contract_chunks, risk_report)


def handle_chat(
    message: str,
    session_id: str,
    risk_report_context: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Xử lý một lượt hỏi đáp của người dùng kèm kiểm soát ngưỡng Cosine (Gatekeeper)."""
    if llm_client is None:
        raise RuntimeError("modules.shared.llm_client chưa sẵn sàng.")

    session = _get_or_create_session(session_id)
    if risk_report_context is not None:
        session.risk_report = risk_report_context

    history_before = session.get_text_history()
    session.add_message("user", message)

    context_chunks = retrieval.search_context(
        query=message,
        has_session=session.has_contract_context,
        session=session,
    )

    prompt = prompts.build_chat_prompt(
        query=message,
        context_chunks=context_chunks,
        history=history_before,
        has_contract_context=session.has_contract_context,
        risk_report=session.risk_report,
    )

    chat_threshold = 0.60 if session.has_contract_context else 0.75
    refusal_msg = (
        "Nội dung câu hỏi không nằm trong hợp đồng dịch vụ đã đính kèm hoặc cơ sở dữ liệu pháp luật của hệ thống. "
        "Bạn vui lòng đặt câu hỏi liên quan đến các điều khoản của hợp đồng này hoặc các quy định pháp luật về hợp đồng dịch vụ."
        if session.has_contract_context
        else None
    )
    result = llm_client.generate_grounded_response(
        query=prompt,
        retrieved_chunks=context_chunks,
        threshold=chat_threshold,
        refusal_message=refusal_msg,
    )

    answer = result.get("answer", "")
    session.add_message("model", answer)

    return {
        "answer": answer,
        "citations": result.get("citations", []),
        "refusal": result.get("refusal", False),
        "debug_trace": result.get("debug_trace"),
    }
