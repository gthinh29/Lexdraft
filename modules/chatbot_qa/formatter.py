"""Định dạng ngữ cảnh hợp đồng, điều luật, báo cáo rủi ro và lịch sử hội thoại cho Prompt Chatbot."""

from typing import Any, Dict, List, Optional

from modules.shared.legal_rules import format_single_law_source_label


def format_chat_context_chunks(chunks: List[Dict[str, Any]]) -> str:
    """Phân tách và định dạng các chunk hợp đồng và điều luật cho Prompt Chatbot."""
    if not chunks:
        return "Không có căn cứ nào được tìm thấy."

    contract_parts = []
    law_parts = []

    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        is_contract = metadata.get("index") == "contract_index" or any(
            str(metadata.get("source", "")).endswith(ext)
            for ext in (".pdf", ".docx", ".txt", ".md")
        )
        article = metadata.get("article") or metadata.get("article_number") or "N/A"

        if is_contract:
            source_label = metadata.get("source") or "Văn bản Hợp đồng"
            contract_parts.append(
                f"[{article} - {source_label}]\n{chunk.get('content', '')}"
            )
        else:
            source_label = format_single_law_source_label(metadata)
            law_parts.append(
                f"[{article} - {source_label}]\n{chunk.get('content', '')}"
            )

    output_sections = []
    if contract_parts:
        output_sections.append(
            "=== NỘI DUNG ĐIỀU KHOẢN HỢP ĐỒNG ĐƯỢC CUNG CẤP ===\n"
            + "\n\n".join(contract_parts)
        )
    if law_parts:
        output_sections.append(
            "=== CĂN CỨ PHÁP LUẬT THAM CHIẾU ===\n" + "\n\n".join(law_parts)
        )

    return (
        "\n\n".join(output_sections)
        if output_sections
        else "Không có căn cứ nào được tìm thấy."
    )


def format_chat_risk_report(risk_report: Optional[List[Dict[str, Any]]]) -> str:
    """Định dạng báo cáo rủi ro sơ bộ của hợp đồng cho Prompt Chế độ A."""
    if not risk_report:
        return ""
    return "\n".join(
        f"- Điều khoản: {item.get('dieu_khoan', 'N/A')}\n"
        f"  Rủi ro: {item.get('rui_ro', 'N/A')}"
        for item in risk_report
    )


def format_chat_history(history: List[Dict[str, str]], max_turns: int = 6) -> str:
    """Định dạng các lượt hội thoại gần nhất cho Prompt Chatbot."""
    if not history:
        return "Chưa có lịch sử hội thoại."
    recent = history[-max_turns:]
    return "\n".join(
        f"{'Người dùng' if turn['role'] == 'user' else 'Trợ lý'}: {turn['text']}"
        for turn in recent
    )
