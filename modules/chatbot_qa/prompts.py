"""
modules/chatbot_qa/prompts.py

PRIVATE - chỉ được import từ modules/chatbot_qa/service.py.

Prompt linh hoạt cho 2 chế độ:
  - Chế độ A: có ngữ cảnh hợp đồng & báo cáo rủi ro (tiếp nối Module 1/2).
  - Chế độ B: chỉ tra cứu luật chung, độc lập.
"""

from typing import Any, Dict, List, Optional

CHATBOT_BASE_INSTRUCTION = (
    "Bạn là trợ lý pháp lý tư vấn về hợp đồng dịch vụ. "
    "Chỉ sử dụng thông tin trong phần CĂN CỨ dưới đây để trả lời. "
    "Nếu không đủ căn cứ để trả lời, hãy nói rõ là không có thông tin, "
    "KHÔNG tự suy diễn hoặc bịa thêm nội dung không có trong CĂN CỨ."
)

# Chỉ lấy vài lượt gần nhất khi ghép vào prompt, tránh phình token (SRS 6.1).
MAX_HISTORY_TURNS_IN_PROMPT = 6


def _format_context_chunks(chunks: List[Dict[str, Any]]) -> str:
    if not chunks:
        return "Không có căn cứ nào được tìm thấy."

    parts = []
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        label = metadata.get("article") or "N/A"
        source = metadata.get("source") or metadata.get("index", "N/A")
        parts.append(f"[{label} - {source}]\n{chunk.get('content', '')}")
    return "\n\n".join(parts)


def _format_risk_report(risk_report: Optional[List[Dict[str, Any]]]) -> str:
    if not risk_report:
        return ""

    parts = [
        f"- Điều khoản: {item.get('dieu_khoan', 'N/A')}\n"
        f"  Rủi ro: {item.get('rui_ro', 'N/A')}"
        for item in risk_report
    ]
    return "\n".join(parts)


def _format_history(history: List[Dict[str, str]]) -> str:
    if not history:
        return "Chưa có lịch sử hội thoại."

    recent = history[-MAX_HISTORY_TURNS_IN_PROMPT:]
    lines = [
        f"{'Người dùng' if turn['role'] == 'user' else 'Trợ lý'}: {turn['text']}"
        for turn in recent
    ]
    return "\n".join(lines)


def build_chat_prompt(
    query: str,
    context_chunks: List[Dict[str, Any]],
    history: List[Dict[str, str]],
    has_contract_context: bool,
    risk_report: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Ghép prompt cho 1 lượt hỏi trong chatbot.

    Args:
        query: câu hỏi hiện tại.
        context_chunks: chunk truy xuất được (từ retrieval.search_context).
        history: lịch sử hội thoại dạng text (từ chat_session.get_text_history()),
            KHÔNG bao gồm lượt hỏi hiện tại.
        has_contract_context: True = Chế độ A, False = Chế độ B.
        risk_report: báo cáo rủi ro từ Module 2 (chỉ dùng ở Chế độ A).

    Returns:
        Prompt hoàn chỉnh, sẵn sàng gửi cho llm_client.
    """
    context_text = _format_context_chunks(context_chunks)
    history_text = _format_history(history)

    if has_contract_context:
        mode_instruction = (
            "Bạn đang ở CHẾ ĐỘ TƯ VẤN CÓ NGỮ CẢNH HỢP ĐỒNG. Người dùng đã upload/soạn "
            "một hợp đồng cụ thể và đã có báo cáo rủi ro sơ bộ bên dưới. Hãy trả lời "
            "bám sát cả nội dung hợp đồng và các điều luật liên quan."
        )
        risk_report_text = _format_risk_report(risk_report)
        risk_section = (
            f"\n\nBÁO CÁO RỦI RO SƠ BỘ CỦA HỢP ĐỒNG:\n{risk_report_text}"
            if risk_report_text
            else ""
        )
    else:
        mode_instruction = (
            "Bạn đang ở CHẾ ĐỘ TRA CỨU PHÁP LUẬT CHUNG (không có hợp đồng cụ thể nào "
            "được đính kèm). KHÔNG phân tích hay suy đoán về một hợp đồng cụ thể nào."
        )
        risk_section = ""

    prompt = f"""{CHATBOT_BASE_INSTRUCTION}

{mode_instruction}

LỊCH SỬ HỘI THOẠI GẦN ĐÂY:
{history_text}

CĂN CỨ:
{context_text}{risk_section}

CÂU HỎI HIỆN TẠI: {query}"""

    return prompt
