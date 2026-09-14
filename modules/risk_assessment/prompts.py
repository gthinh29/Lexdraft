"""
modules/risk_assessment/prompts.py

PRIVATE - chỉ được import từ modules/risk_assessment/service.py.
Không được import trực tiếp từ module khác hoặc từ app.py (đúng SRS 3.2).

Prompt template phục vụ đánh giá rủi ro pháp lý cho từng Điều khoản trong hợp đồng.
Ràng buộc chặt chẽ LLM với căn cứ pháp lý được truy xuất, chống hallucination (SRS 5.3).
"""

from typing import Any, Dict, List

RISK_ASSESSMENT_INSTRUCTION = (
    "Bạn là chuyên gia pháp lý cao cấp chuyên rà soát và phát hiện rủi ro hợp đồng dịch vụ tại Việt Nam. "
    "Nhiệm vụ của bạn là phân tích một điều khoản cụ thể trong hợp đồng dựa trên các CĂN CỨ PHÁP LÝ được cung cấp. "
    "QUY TẮC BẮT BUỘC:\n"
    "1. Chỉ sử dụng thông tin và quy định trong phần CĂN CỨ PHÁP LÝ bên dưới để đối chiếu và đánh giá.\n"
    "2. KHÔNG tự bịa đặt điều luật, số hiệu văn bản hoặc các chế tài không có trong CĂN CỨ.\n"
    "3. Nếu điều khoản phù hợp quy định hoặc không có căn cứ pháp lý nào thể hiện điều khoản này vi phạm, "
    "hãy trả lời rõ ràng: 'Không phát hiện rủi ro pháp lý rõ ràng.' và giải thích ngắn gọn.\n"
    "4. Nếu phát hiện rủi ro (vi phạm điều cấm, vượt quá mức trần phạt vi phạm, thiếu thỏa thuận bồi thường, "
    "điều khoản bất lợi đơn phương, viện dẫn luật hết hiệu lực...): Hãy chỉ rõ (a) Rủi ro cụ thể, "
    "(b) Căn cứ pháp lý vi phạm (số Điều, tên Luật), (c) Khuyến nghị chỉnh sửa cụ thể.\n"
    "5. QUY TẮC TRÍCH DẪN PHÁP LÝ BẮT BUỘC:\n"
    "   - NGUYÊN TẮC THỨ BẬC: Mọi viện dẫn căn cứ vi phạm BẮT BUỘC tuân thủ đúng thứ bậc: Điểm → Khoản → Điều → Tên văn bản (Ví dụ: 'điểm a khoản 1 Điều 301...', 'khoản 2 Điều 292...').\n"
    "   - ĐỐI VỚI VĂN BẢN LUẬT THÔNG THƯỜNG (không phải văn bản hợp nhất):\n"
    "     + Lần đầu: [Điểm/Khoản/Điều nếu có] [Tên Luật] số [số hiệu] ngày [ngày ban hành] của Quốc hội.\n"
    "     + Các lần sau: Trích dẫn bình thường, rút gọn: '[Điểm/Khoản nếu có] Điều [X] [Tên Luật] số [số hiệu]' (Ví dụ: 'theo quy định tại Điều 401 Bộ luật Dân sự số 91/2015/QH13'). Tuyệt đối KHÔNG ghi VBHN cho các văn bản này.\n"
    "   - NẾU LÀ VĂN BẢN HỢP NHẤT (chỉ áp dụng khi văn bản nguồn được chú thích là VBHN):\n"
    "     + Lần đầu: BẮT BUỘC ghi đầy đủ thông tin luật gốc và VBHN: [Điểm/Khoản/Điều nếu có] [Tên Luật] số [số hiệu] ngày [ngày ban hành] của Quốc hội (hợp nhất tại Văn bản hợp nhất số [số VBHN] ngày [ngày ký VBHN] của Văn phòng Quốc hội).\n"
    "       (Ví dụ: 'theo quy định tại Điều 292 Luật Thương mại số 36/2005/QH11 ngày 14 tháng 6 năm 2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH ngày 27 tháng 8 năm 2025 của Văn phòng Quốc hội)').\n"
    "     + Các lần sau: Trích dẫn như bình thường (số Điều lấy chuẩn theo VBHN), rút gọn ngày tháng: '[Điểm/Khoản nếu có] Điều [X] [Tên Luật] số [số hiệu] (hợp nhất tại Văn bản hợp nhất số [số VBHN])' (Ví dụ: 'theo quy định tại điểm a khoản 1 Điều 301 Luật Thương mại số 36/2005/QH11 (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH)')."
)


def _format_law_context(law_chunks: List[Dict[str, Any]]) -> str:
    """Định dạng danh sách các chunk luật liên quan thành khối văn bản có đánh số điều."""
    if not law_chunks:
        return "Không tìm thấy điều luật liên quan trực tiếp trong cơ sở dữ liệu."

    parts = []
    for chunk in law_chunks:
        metadata = chunk.get("metadata", {})
        article = metadata.get("article") or metadata.get("article_number") or "N/A"
        law_name = metadata.get("law_name", "")
        law_number = metadata.get("law_number", "")
        issued_date = metadata.get("issued_date", "")
        vbhn_number = metadata.get("vbhn_number", "")
        vbhn_date = metadata.get("vbhn_date", "")

        if law_name and law_number:
            source_label = f"{law_name} số {law_number}"
            if issued_date:
                source_label += f" ngày {issued_date} của Quốc hội"
            if vbhn_number:
                if vbhn_date:
                    source_label += f" (hợp nhất tại Văn bản hợp nhất số {vbhn_number} ngày {vbhn_date} của Văn phòng Quốc hội)"
                else:
                    source_label += f" (hợp nhất tại Văn bản hợp nhất số {vbhn_number})"
        else:
            source_label = metadata.get("source") or metadata.get("doc_name") or "N/A"

        header = f"[{article} - {source_label}]"
        parts.append(f"{header}\n{chunk.get('content', '')}")

    return "\n\n".join(parts)


def build_risk_prompt(dieu_khoan_text: str, law_context: List[Dict[str, Any]]) -> str:
    """
    Ghép prompt phân tích rủi ro cho một Điều khoản hợp đồng.

    Args:
        dieu_khoan_text: Nội dung đầy đủ của Điều khoản cần phân tích.
        law_context: Danh sách các chunk điều luật liên quan (từ retrieval.py).

    Returns:
        Prompt hoàn chỉnh gửi cho LLM.
    """
    formatted_law = _format_law_context(law_context)

    prompt = f"""{RISK_ASSESSMENT_INSTRUCTION}

CĂN CỨ PHÁP LÝ LIÊN QUAN:
{formatted_law}

ĐIỀU KHOẢN HỢP ĐỒNG CẦN ĐÁNH GIÁ:
{dieu_khoan_text.strip()}

YÊU CẦU ĐẦU RA:
- Nhận xét rủi ro: [Ghi rõ rủi ro hoặc ghi 'Không phát hiện rủi ro pháp lý rõ ràng']
- Căn cứ pháp lý đối chiếu: [Điều luật cụ thể từ CĂN CỨ ở trên]
- Đề xuất điều chỉnh (nếu có rủi ro): [Nêu phương án sửa đổi câu chữ cụ thể để bên sử dụng hợp đồng tự bảo vệ mình]"""

    return prompt
