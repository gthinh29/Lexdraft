"""
modules/drafting/prompts.py

PRIVATE - chỉ được import từ modules/drafting/service.py.

Prompt template sinh bản nháp hợp đồng dịch vụ, ghép từ 3 biến:
  - {template}    : cấu trúc mẫu hợp đồng tham khảo (từ template_index)
  - {law_context} : các điều luật liên quan (từ law_index)
  - {user_input}  : thông tin người dùng nhập trên form
"""

from typing import Any, Dict, List

DRAFTING_SYSTEM_INSTRUCTION = (
    "Bạn là một trợ lý pháp lý soạn thảo hợp đồng dịch vụ. "
    "Chỉ được soạn thảo dựa trên MẪU CẤU TRÚC và CĂN CỨ PHÁP LÝ được cung cấp bên dưới. "
    "Không tự ý bịa thêm điều khoản không có căn cứ hoặc không phù hợp với thông tin người dùng. "
    "Nếu thiếu thông tin cần thiết để hoàn thiện một điều khoản, hãy để "
    "[CẦN BỔ SUNG: <mô tả thông tin còn thiếu>] thay vì tự suy diễn."
)


def _format_law_context(law_context: List[Dict[str, Any]]) -> str:
    if not law_context:
        return "Không có căn cứ pháp lý bổ sung."

    parts = []
    for chunk in law_context:
        metadata = chunk.get("metadata", {})
        article = metadata.get("article") or "N/A"
        source = metadata.get("source", "N/A")
        parts.append(f"[{article} - {source}]\n{chunk.get('content', '')}")
    return "\n\n".join(parts)


def _format_user_input(user_input: Dict[str, Any]) -> str:
    return "\n".join(f"- {key}: {value}" for key, value in user_input.items())


def build_drafting_prompt(
    template: str,
    law_context: List[Dict[str, Any]],
    user_input: Dict[str, Any],
) -> str:
    """
    Ghép prompt sinh hợp đồng theo 3 biến: template, law_context, user_input.

    Args:
        template: text mẫu hợp đồng (lấy từ retrieval.retrieve_template).
        law_context: danh sách chunk luật liên quan (lấy từ retrieval.retrieve_relevant_law).
        user_input: dict thông tin người dùng nhập trên form.

    Returns:
        Prompt hoàn chỉnh, sẵn sàng gửi cho llm_client.
    """
    law_context_text = _format_law_context(law_context)
    user_input_text = _format_user_input(user_input)
    template_text = template.strip() if template else "Không có mẫu cấu trúc tham khảo."

    prompt = f"""{DRAFTING_SYSTEM_INSTRUCTION}

MẪU CẤU TRÚC THAM KHẢO:
{template_text}

CĂN CỨ PHÁP LÝ LIÊN QUAN:
{law_context_text}

THÔNG TIN NGƯỜI DÙNG CUNG CẤP:
{user_input_text}

YÊU CẦU: Soạn thảo bản nháp hợp đồng dịch vụ hoàn chỉnh, đúng cấu trúc Điều/Khoản,
dựa trên mẫu và căn cứ pháp lý ở trên, điền đầy đủ thông tin người dùng đã cung cấp."""

    return prompt
