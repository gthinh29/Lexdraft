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
    "từ phần CĂN CỨ PHÁP LÝ bên dưới — không dẫn chiếu văn bản không có trong danh sách được cung cấp.\n"
    "7. QUY TẮC TRÍCH DẪN PHÁP LÝ BẮT BUỘC:\n"
    "   a) NGUYÊN TẮC THỨ BẬC: Mọi viện dẫn điều khoản BẮT BUỘC tuân thủ đúng thứ tự từ nhỏ đến lớn: "
    "Điểm → Khoản → Điều → Tên văn bản (Ví dụ: 'điểm a khoản 1 Điều 301...', 'khoản 2 Điều 292...').\n"
    "   b) ĐỐI VỚI VĂN BẢN LUẬT THÔNG THƯỜNG (không phải văn bản hợp nhất):\n"
    "      - Khi viện dẫn lần đầu (tại phần Căn cứ hoặc khi xuất hiện lần đầu): [Điểm/Khoản/Điều nếu có] [Tên Luật] số [số hiệu] ngày [ngày ban hành] của Quốc hội.\n"
    "        (Ví dụ: 'Căn cứ Bộ luật Dân sự số 91/2015/QH13 ngày 24 tháng 11 năm 2015 của Quốc hội;')\n"
    "      - Các lần sau: Trích dẫn bình thường, rút gọn: '[Điểm/Khoản nếu có] Điều [X] [Tên Luật] số [số hiệu]' (Ví dụ: 'theo quy định tại Điều 401 Bộ luật Dân sự số 91/2015/QH13'). Tuyệt đối KHÔNG ghi VBHN cho các văn bản này.\n"
    "   c) NẾU LÀ VĂN BẢN HỢP NHẤT (chỉ áp dụng khi văn bản nguồn được chú thích là VBHN):\n"
    "      - Khi viện dẫn lần đầu (tại phần Căn cứ hoặc khi xuất hiện lần đầu): BẮT BUỘC ghi đầy đủ thông tin luật gốc và thông tin VBHN: [Điểm/Khoản/Điều nếu có] [Tên Luật] số [số hiệu] ngày [ngày ban hành] của Quốc hội (hợp nhất tại Văn bản hợp nhất số [số VBHN] ngày [ngày ký VBHN] của Văn phòng Quốc hội).\n"
    "        (Ví dụ: 'Căn cứ Luật Thương mại số 36/2005/QH11 ngày 14 tháng 6 năm 2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH ngày 27 tháng 8 năm 2025 của Văn phòng Quốc hội);')\n"
    "      - Các lần sau: Trích dẫn như bình thường (số Điều lấy chuẩn theo VBHN), rút gọn ngày tháng: '[Điểm/Khoản nếu có] Điều [X] [Tên Luật] số [số hiệu] (hợp nhất tại Văn bản hợp nhất số [số VBHN])'.\n"
    "        (Ví dụ: 'theo quy định tại Điều 292 Luật Thương mại số 36/2005/QH11 (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH)' hoặc 'theo quy định tại điểm a khoản 1 Điều 301 Luật Thương mại số 36/2005/QH11 (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH)')."
)


def _format_law_context(law_context: List[Dict[str, Any]]) -> str:
    if not law_context:
        return "Không có căn cứ pháp lý bổ sung từ cơ sở tri thức."

    parts = []
    for chunk in law_context:
        metadata = chunk.get("metadata", {})
        article = metadata.get("article") or "N/A"

        # Ưu tiên hiển thị tên luật đầy đủ + số hiệu + ngày ban hành/VBHN
        law_name = metadata.get("law_name", "")
        law_number = metadata.get("law_number", "")
        issued_date = metadata.get("issued_date", "")
        is_consolidated = metadata.get("is_consolidated", False)
        consolidated_year = metadata.get("consolidated_year", "")
        vbhn_number = metadata.get("vbhn_number", "")
        vbhn_date = metadata.get("vbhn_date", "")
        latest_amendment = metadata.get("latest_amendment", "")

        if law_name and law_number:
            source_label = f"{law_name} số {law_number}"
            if issued_date:
                source_label += f" ngày {issued_date} của Quốc hội"

            if is_consolidated:
                if vbhn_number and vbhn_date:
                    source_label += f" (hợp nhất tại Văn bản hợp nhất số {vbhn_number} ngày {vbhn_date} của Văn phòng Quốc hội)"
                elif vbhn_number:
                    source_label += f" (hợp nhất tại Văn bản hợp nhất số {vbhn_number})"
                elif consolidated_year:
                    source_label += f" (văn bản hợp nhất năm {consolidated_year})"
                if latest_amendment:
                    source_label += f", sửa đổi lần cuối bởi Luật số {latest_amendment}"
        else:
            # Fallback về tên file nếu chưa parse được
            source_label = metadata.get("source", "N/A")

        header = f"[{article} - {source_label}]"
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
