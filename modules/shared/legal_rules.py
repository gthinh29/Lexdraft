"""
modules/shared/legal_rules.py
Định nghĩa tập trung Quy tắc Trích dẫn Pháp lý và hàm định dạng Context RAG dùng chung
cho toàn bộ 3 phân hệ (Soạn thảo, Rà soát Rủi ro, Chatbot Q&A).

Mục đích thiết kế:
1. Tuân thủ nguyên tắc DRY (Don't Repeat Yourself) — sửa quy tắc trích dẫn ở 1 nơi duy nhất.
2. Giúp mã nguồn các file prompts.py ngắn gọn, tường minh, dễ dàng trình bày trước Hội đồng.
"""

from typing import Any, Dict, List

STANDARD_LEGAL_CITATION_RULES = (
    "QUY TẮC TRÍCH DẪN PHÁP LÝ BẮT BUỘC (CHUẨN KỸ THUẬT LẬP PHÁP VIỆT NAM):\n"
    "1. CẤM TRÍCH DẪN TÊN FILE KỸ THUẬT: Tuyệt đối không xuất hiện đuôi file (.md, .docx, .pdf) hoặc tên file hệ thống trong văn bản trả lời.\n"
    "2. NGUYÊN TẮC THỨ BẬC: Mọi viện dẫn điều khoản BẮT BUỘC tuân thủ đúng thứ tự từ nhỏ đến lớn: "
    "Điểm → Khoản → Điều → Tên văn bản (Ví dụ: 'điểm a khoản 1 Điều 301...', 'khoản 2 Điều 519...').\n"
    "3. ĐỐI VỚI ĐẠO LUẬT THÔNG THƯỜNG (không phải văn bản hợp nhất):\n"
    "   - Lần đầu viện dẫn: [Điểm/Khoản/Điều nếu có] [Tên Luật/Bộ luật] số [số hiệu] ngày [ngày ban hành] của Quốc hội "
    "(Ví dụ: 'Điều 513 Bộ luật Dân sự số 91/2015/QH13 ngày 24/11/2015 của Quốc hội').\n"
    "   - Các lần tiếp theo: Rút gọn ngày ban hành: '[Điểm/Khoản nếu có] Điều [X] [Tên Luật/Bộ luật] số [số hiệu]' "
    "(Ví dụ: 'khoản 1 Điều 418 Bộ luật Dân sự số 91/2015/QH13'). Tuyệt đối KHÔNG gán nhãn VBHN cho văn bản này.\n"
    "4. ĐỐI VỚI VĂN BẢN HỢP NHẤT (chỉ áp dụng khi văn bản nguồn có thông tin VBHN):\n"
    "   - Lần đầu viện dẫn: BẮT BUỘC ghi đầy đủ thông tin luật gốc và thông tin VBHN: "
    "[Điểm/Khoản/Điều nếu có] [Tên Luật] số [số hiệu] ngày [ngày ban hành] của Quốc hội (hợp nhất tại Văn bản hợp nhất số [số VBHN] ngày [ngày ký VBHN] của Văn phòng Quốc hội).\n"
    "     + Ví dụ Luật Thương mại: 'Điều 301 Luật Thương mại số 36/2005/QH11 ngày 14/06/2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH ngày 27/08/2025 của Văn phòng Quốc hội)'.\n"
    "     + Ví dụ Luật Sở hữu trí tuệ: 'Điều 39 Luật Sở hữu trí tuệ số 50/2005/QH11 ngày 29/11/2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 55/VBHN-VPQH ngày 15/01/2026 của Văn phòng Quốc hội, sửa đổi bổ sung đến Luật số 131/2025/QH15)'.\n"
    "   - Các lần tiếp theo: Rút gọn ngày tháng: '[Điểm/Khoản nếu có] Điều [X] [Tên Luật] số [số hiệu] (hợp nhất tại Văn bản hợp nhất số [số VBHN])'."
)


def format_single_law_source_label(metadata: Dict[str, Any]) -> str:
    """
    Tạo chuỗi định danh nguồn luật chuẩn xác từ metadata của một chunk FAISS.
    """
    law_name = metadata.get("law_name", "")
    law_number = metadata.get("law_number", "")
    issued_date = metadata.get("issued_date", "")
    is_consolidated = metadata.get("is_consolidated", False)
    vbhn_number = metadata.get("vbhn_number", "")
    vbhn_date = metadata.get("vbhn_date", "")
    latest_amendment = metadata.get("latest_amendment", "")

    if law_name and law_number:
        label = f"{law_name} số {law_number}"
        if issued_date:
            label += f" ngày {issued_date} của Quốc hội"
        if is_consolidated or vbhn_number:
            if vbhn_number and vbhn_date:
                label += f" (hợp nhất tại Văn bản hợp nhất số {vbhn_number} ngày {vbhn_date} của Văn phòng Quốc hội)"
            elif vbhn_number:
                label += f" (hợp nhất tại Văn bản hợp nhất số {vbhn_number})"
            if latest_amendment:
                label += f", sửa đổi lần cuối bởi Luật số {latest_amendment}"
        return label

    return metadata.get("source") or metadata.get("doc_name") or "Căn cứ pháp lý"


def format_law_chunks_block(law_chunks: List[Dict[str, Any]]) -> str:
    """
    Biến danh sách các chunk luật truy xuất từ FAISS thành khối văn bản có cấu trúc
    tường minh để đưa vào Prompt cho LLM.
    """
    if not law_chunks:
        return "Không tìm thấy điều luật liên quan trực tiếp trong cơ sở dữ liệu."

    parts = []
    for chunk in law_chunks:
        metadata = chunk.get("metadata", {})
        article = metadata.get("article") or metadata.get("article_number") or "N/A"
        score = chunk.get("score")
        source_label = format_single_law_source_label(metadata)
        score_str = (
            f" | Độ tương đồng Cosine: {score:.3f}"
            if isinstance(score, (int, float))
            else ""
        )
        header = f"[{article} — {source_label}{score_str}]"
        parts.append(f"{header}\n{chunk.get('content', '').strip()}")

    return "\n\n".join(parts)
