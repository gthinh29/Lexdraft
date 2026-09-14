"""
modules/drafting/prompts.py

PRIVATE - chỉ được import từ modules/drafting/service.py.

Prompt template sinh bản nháp hợp đồng dịch vụ, ghép từ 3 biến:
  - {user_input}  : thông tin người dùng nhập trên form       — xác định nhiệm vụ
  - {law_context} : các điều luật liên quan (từ law_index)    — nguồn nội dung ưu tiên
  - {template}    : cấu trúc mẫu hợp đồng (từ template_index) — tham chiếu bố cục
"""

from typing import Any, Dict, List

DRAFTING_SYSTEM_INSTRUCTION = (
    "Bạn là chuyên gia pháp lý soạn thảo hợp đồng dịch vụ tại Việt Nam. "
    "Nhiệm vụ của bạn là soạn bản nháp hợp đồng dịch vụ hoàn chỉnh, có giá trị pháp lý, "
    "dựa trên thông tin người dùng cung cấp và các căn cứ pháp luật được trích xuất bên dưới.\n"
    "QUY TẮC BẮT BUỘC:\n"
    "1. CĂN CỨ PHÁP LÝ là nguồn ưu tiên cao nhất. Mọi điều khoản trong hợp đồng phải "
    "tuân thủ và không được mâu thuẫn với các quy định trong phần CĂN CỨ PHÁP LÝ.\n"
    "2. MẪU CẤU TRÚC (nếu có) chỉ dùng để tham chiếu bố cục và thứ tự các điều khoản — "
    "không được sao chép nguyên vẹn nội dung từ mẫu nếu mẫu không phù hợp với thông tin người dùng hoặc luật hiện hành.\n"
    "3. Điều khoản phạt vi phạm KHÔNG được vượt quá 8% giá trị phần hợp đồng bị vi phạm "
    "(theo Điều 301 Luật Thương mại). Nếu người dùng nhập mức phạt cao hơn, hãy tự động điều chỉnh về 8% và ghi chú.\n"
    "4. Nếu thiếu thông tin để hoàn thiện một điều khoản, ghi rõ [CẦN BỔ SUNG: <mô tả>] "
    "thay vì tự suy diễn hoặc bịa thêm.\n"
    "5. KHÔNG tự thêm điều khoản không có căn cứ pháp lý hoặc không được người dùng yêu cầu.\n"
    "6. Phần 'Căn cứ' ở đầu hợp đồng phải liệt kê đúng tên và số hiệu văn bản pháp luật "
    "từ phần CĂN CỨ PHÁP LÝ bên dưới — không dẫn chiếu văn bản không có trong danh sách được cung cấp."
)


def _format_law_context(law_context: List[Dict[str, Any]]) -> str:
    if not law_context:
        return "Không có căn cứ pháp lý bổ sung từ cơ sở tri thức."

    parts = []
    for chunk in law_context:
        metadata = chunk.get("metadata", {})
        article = metadata.get("article") or "N/A"
        source = metadata.get("source", "N/A")
        title = metadata.get("title", "")
        header = f"[{article} - {source}]" + (f" ({title})" if title else "")
        parts.append(f"{header}\n{chunk.get('content', '')}")
    return "\n\n".join(parts)


def _format_user_input(user_input: Dict[str, Any]) -> str:
    labels = {
        "contract_type": "Loại hợp đồng",
        "ben_a": "Bên A (Bên thuê dịch vụ)",
        "dia_chi_ben_a": "Địa chỉ Bên A",
        "ben_b": "Bên B (Bên cung cấp dịch vụ)",
        "dia_chi_ben_b": "Địa chỉ Bên B",
        "pham_vi_cong_viec": "Phạm vi công việc",
        "gia_tri_hop_dong": "Giá trị hợp đồng",
        "thoi_han": "Thời hạn hợp đồng",
    }
    lines = []
    for key, value in user_input.items():
        if key == "session_id":
            continue
        label = labels.get(key, key)
        lines.append(f"- {label}: {value}")
    return "\n".join(lines) if lines else "Không có thông tin bổ sung."


def build_drafting_prompt(
    template: str,
    law_context: List[Dict[str, Any]],
    user_input: Dict[str, Any],
) -> str:
    """
    Ghép prompt sinh hợp đồng theo thứ tự Query-first:
      1. Thông tin người dùng (nhiệm vụ) — LLM đọc trước để hiểu rõ cần làm gì
      2. Căn cứ pháp lý (context chính) — nội dung luật để soạn đúng quy định
      3. Mẫu cấu trúc (context phụ)    — tham chiếu bố cục, thứ tự điều khoản

    Args:
        template: text mẫu hợp đồng (lấy từ retrieval.retrieve_template).
                  Nếu không có, prompt vẫn hoạt động bình thường nhờ law_context.
        law_context: danh sách chunk luật liên quan (lấy từ retrieval.retrieve_relevant_law).
        user_input: dict thông tin người dùng nhập trên form.

    Returns:
        Prompt hoàn chỉnh, sẵn sàng gửi cho llm_client.
    """
    law_context_text = _format_law_context(law_context)
    user_input_text = _format_user_input(user_input)
    template_text = (
        template.strip()
        if template
        else "Không có mẫu cấu trúc tham khảo (sinh hoàn toàn từ căn cứ pháp lý)."
    )
    contract_type = user_input.get("contract_type", "hợp đồng dịch vụ")

    prompt = f"""{DRAFTING_SYSTEM_INSTRUCTION}

THÔNG TIN NGƯỜI DÙNG CUNG CẤP (nhiệm vụ cần thực hiện):
{user_input_text}

CĂN CỨ PHÁP LÝ LIÊN QUAN (ưu tiên cao nhất khi soạn nội dung):
{law_context_text}

MẪU CẤU TRÚC THAM KHẢO (chỉ dùng để tham chiếu bố cục, thứ tự điều khoản):
{template_text}

YÊU CẦU ĐẦU RA:
Soạn thảo bản nháp {contract_type} hoàn chỉnh theo cấu trúc Điều/Khoản chuẩn pháp lý Việt Nam, gồm đầy đủ:
- Quốc hiệu, tiêu đề hợp đồng
- Phần Căn cứ pháp lý (chỉ dẫn chiếu các văn bản trong CĂN CỨ PHÁP LÝ bên trên)
- Thông tin hai bên
- Các điều khoản nội dung (phạm vi, giá trị, thanh toán, nghiệm thu, bảo mật, phạt vi phạm, chấm dứt)
- Điều khoản chung và ký kết
Tuân thủ tuyệt đối các QUY TẮC BẮT BUỘC đã nêu ở trên."""

    return prompt
