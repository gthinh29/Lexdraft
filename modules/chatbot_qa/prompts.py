"""
modules/chatbot_qa/prompts.py

PRIVATE - chỉ được import từ modules/chatbot_qa/service.py.

Prompt linh hoạt cho 2 chế độ:
  - Chế độ A: có ngữ cảnh hợp đồng & báo cáo rủi ro (tiếp nối Module 1/2).
  - Chế độ B: chỉ tra cứu luật chung, độc lập.
"""

from typing import Any, Dict, List, Optional

CHATBOT_BASE_INSTRUCTION = (
    "Bạn là chuyên gia tư vấn pháp lý về hợp đồng dịch vụ tại Việt Nam.\n\n"
    "QUY TẮC BẮT BUỘC VỀ CĂN CỨ PHÁP LÝ (CHỐNG HALLUCINATION):\n"
    "1. CHỈ sử dụng thông tin và quy định có trong phần CĂN CỨ PHÁP LÝ dưới đây để trả lời câu hỏi. TUYỆT ĐỐI KHÔNG tự bịa đặt điều luật không có trong CĂN CỨ.\n"
    "2. VỚI CÂU HỎI KHÁI NIỆM HOẶC TỔNG QUAN VỀ MỘT ĐẠO LUẬT (Ví dụ: 'Luật Thương mại là gì?', 'Bộ luật Dân sự là gì?'):\n"
    "   - Trong kỹ thuật lập pháp, các đạo luật không có điều khoản định nghĩa danh từ riêng, mà bản chất của luật được xác định qua thông tin định danh (Tên luật, số hiệu, ngày ban hành trong tiêu đề/metadata của CĂN CỨ) kết hợp với Điều 1 (Phạm vi điều chỉnh), Điều 2 (Đối tượng áp dụng), Điều 3 (Giải thích từ ngữ) nếu có trong CĂN CỨ.\n"
    "   - Khi CĂN CỨ đã có thông tin về đạo luật đó, BẮT BUỘC phải sử dụng thông tin định danh cùng Điều 1, Điều 2 và các điều khoản có trong CĂN CỨ để giải thích rõ ràng bản chất đạo luật cho người dùng. Tuyệt đối KHÔNG từ chối máy móc.\n"
    "3. KHI THỰC SỰ KHÔNG CÓ HOẶC KHÔNG ĐỦ CĂN CỨ PHÁP LÝ ĐỂ TRẢ LỜI CÂU HỎI:\n"
    "   - BẮT BUỘC phải từ chối trả lời một cách lịch sự, nhã nhặn, chuyên nghiệp:\n"
    "     'Hiện tại trong cơ sở dữ liệu pháp luật về hợp đồng dịch vụ của hệ thống chưa có quy định về vấn đề này. Bạn vui lòng tra cứu thêm các văn bản pháp luật chuyên ngành liên quan hoặc tham vấn chuyên gia pháp lý.'\n"
    "   - TUYỆT ĐỐI KHÔNG dùng các câu máy móc cộc lốc như 'Thông tin trong CĂN CỨ không có...'.\n\n"
    "QUY TẮC TRÍCH DẪN PHÁP LÝ BẮT BUỘC:\n"
    "1. TUYỆT ĐỐI KHÔNG trích dẫn tên file kỹ thuật (ví dụ: cấm dùng các từ như .md, .docx, VBHN_Luatthuongmai2025.md) trong câu trả lời.\n"
    "2. NGUYÊN TẮC THỨ BẬC: Mọi viện dẫn điều khoản BẮT BUỘC tuân thủ đúng thứ bậc: Điểm → Khoản → Điều → Tên văn bản (Ví dụ: 'theo quy định tại khoản 1 Điều 301...').\n"
    "3. ĐỐI VỚI VĂN BẢN LUẬT THÔNG THƯỜNG (không phải văn bản hợp nhất):\n"
    "   - Lần đầu: [Điểm/Khoản/Điều nếu có] [Tên Luật] số [số hiệu] ngày [ngày ban hành] của Quốc hội (Ví dụ: 'Điều 418 Bộ luật Dân sự số 91/2015/QH13 ngày 24 tháng 11 năm 2015 của Quốc hội').\n"
    "   - Các lần sau: Trích dẫn bình thường, rút gọn: '[Điểm/Khoản nếu có] Điều [X] [Tên Luật] số [số hiệu]' (Ví dụ: 'Điều 418 Bộ luật Dân sự số 91/2015/QH13'). Tuyệt đối KHÔNG ghi VBHN cho các văn bản này.\n"
    "4. NẾU LÀ VĂN BẢN HỢP NHẤT (chỉ áp dụng khi văn bản nguồn được chú thích là VBHN):\n"
    "   - Lần đầu: BẮT BUỘC ghi đầy đủ thông tin luật gốc và thông tin VBHN: [Điểm/Khoản/Điều nếu có] [Tên Luật] số [số hiệu] ngày [ngày ban hành] của Quốc hội (hợp nhất tại Văn bản hợp nhất số [số VBHN] ngày [ngày ký VBHN] của Văn phòng Quốc hội).\n"
    "     (Ví dụ: 'Điều 301 Luật Thương mại số 36/2005/QH11 ngày 14 tháng 6 năm 2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH ngày 27 tháng 8 năm 2025 của Văn phòng Quốc hội)').\n"
    "   - Các lần sau: Trích dẫn như bình thường (số Điều lấy chuẩn theo VBHN), rút gọn ngày tháng: '[Điểm/Khoản nếu có] Điều [X] [Tên Luật] số [số hiệu] (hợp nhất tại Văn bản hợp nhất số [số VBHN])' (Ví dụ: 'Điều 301 Luật Thương mại số 36/2005/QH11 (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH)')."
)

# Chỉ lấy vài lượt gần nhất khi ghép vào prompt, tránh phình token (SRS 6.1).
MAX_HISTORY_TURNS_IN_PROMPT = 6


def _format_context_chunks(chunks: List[Dict[str, Any]]) -> str:
    if not chunks:
        return "Không có căn cứ nào được tìm thấy."

    parts = []
    for chunk in chunks:
        metadata = chunk.get("metadata", {})
        article = metadata.get("article") or metadata.get("article_number") or "N/A"
        law_name = metadata.get("law_name", "")
        law_number = metadata.get("law_number", "")
        issued_date = metadata.get("issued_date", "")
        is_consolidated = metadata.get("is_consolidated", False)
        vbhn_number = metadata.get("vbhn_number", "")
        vbhn_date = metadata.get("vbhn_date", "")

        if law_name and law_number:
            source_label = f"{law_name} số {law_number}"
            if issued_date:
                source_label += f" ngày {issued_date} của Quốc hội"
            if is_consolidated and vbhn_number:
                if vbhn_date:
                    source_label += f" (hợp nhất tại Văn bản hợp nhất số {vbhn_number} ngày {vbhn_date} của Văn phòng Quốc hội)"
                else:
                    source_label += f" (hợp nhất tại Văn bản hợp nhất số {vbhn_number})"
        else:
            source_label = metadata.get("source") or metadata.get("index", "N/A")

        parts.append(f"[{article} - {source_label}]\n{chunk.get('content', '')}")
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

CĂN CỨ PHÁP LÝ ĐƯỢC CUNG CẤP:
{context_text}{risk_section}

CÂU HỎI HIỆN TẠI: {query}"""

    return prompt
