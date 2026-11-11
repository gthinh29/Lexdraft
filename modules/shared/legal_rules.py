"""Quy tắc trích dẫn pháp lý chuẩn và các hàm định dạng dữ liệu đầu vào cho Prompt."""

from typing import Any, Dict, List, Optional

STANDARD_LEGAL_CITATION_RULES = """QUY TẮC TRÍCH DẪN PHÁP LÝ BẮT BUỘC (CHUẨN KỸ THUẬT LẬP PHÁP VIỆT NAM):
1. CẤM TRÍCH DẪN TÊN FILE KỸ THUẬT: Tuyệt đối không xuất hiện đuôi file (.md, .docx, .pdf) hoặc tên file hệ thống trong văn bản trả lời.
2. NGUYÊN TẮC THỨ BẬC: Mọi viện dẫn điều khoản BẮT BUỘC tuân thủ đúng thứ tự từ nhỏ đến lớn: Điểm → Khoản → Điều → Tên văn bản (Ví dụ: 'điểm a khoản 1 Điều 301...', 'khoản 2 Điều 519...').
3. ĐỐI VỚI ĐẠO LUẬT THÔNG THƯỜNG (không phải văn bản hợp nhất):
   - Lần đầu viện dẫn: [Điểm/Khoản/Điều nếu có] [Tên Luật/Bộ luật] số [số hiệu] ngày [ngày ban hành] của Quốc hội (Ví dụ: 'Điều 513 Bộ luật Dân sự số 91/2015/QH13 ngày 24/11/2015 của Quốc hội').
   - Các lần tiếp theo: Rút gọn ngày ban hành: '[Điểm/Khoản nếu có] Điều [X] [Tên Luật/Bộ luật] số [số hiệu]' (Ví dụ: 'khoản 1 Điều 418 Bộ luật Dân sự số 91/2015/QH13'). Tuyệt đối KHÔNG gán nhãn VBHN cho văn bản này.
4. ĐỐI VỚI VĂN BẢN HỢP NHẤT (chỉ áp dụng khi văn bản nguồn có thông tin VBHN):
   - Lần đầu viện dẫn: BẮT BUỘC ghi đầy đủ thông tin luật gốc và thông tin VBHN: [Điểm/Khoản/Điều nếu có] [Tên Luật] số [số hiệu] ngày [ngày ban hành] của Quốc hội (hợp nhất tại Văn bản hợp nhất số [số VBHN] ngày [ngày ký VBHN] của Văn phòng Quốc hội).
     + Ví dụ Luật Thương mại: 'Điều 301 Luật Thương mại số 36/2005/QH11 ngày 14/06/2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH ngày 27/08/2025 của Văn phòng Quốc hội)'.
     + Ví dụ Luật Sở hữu trí tuệ: 'Điều 39 Luật Sở hữu trí tuệ số 50/2005/QH11 ngày 29/11/2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 55/VBHN-VPQH ngày 15/01/2026 của Văn phòng Quốc hội, sửa đổi bổ sung đến Luật số 131/2025/QH15)'.
   - Các lần tiếp theo: Rút gọn ngày tháng: '[Điểm/Khoản nếu có] Điều [X] [Tên Luật] số [số hiệu] (hợp nhất tại Văn bản hợp nhất số [số VBHN])'."""


def format_single_law_source_label(metadata: Dict[str, Any]) -> str:
    """Tạo chuỗi định danh nguồn luật chuẩn từ metadata của một chunk FAISS."""
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
    """Định dạng danh sách chunk luật từ FAISS thành khối văn bản đưa vào Prompt."""
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


def format_drafting_user_input(user_input: Dict[str, Any]) -> str:
    """Định dạng thông tin giao dịch và thông số đặc thù của người dùng khi soạn thảo."""
    labels = {
        "contract_type": "Loại hợp đồng dịch vụ",
        "category_id": "Mã phân loại nghiệp vụ",
        "stance_label": "Vị thế bảo vệ pháp lý ưu tiên",
        "so_hop_dong": "Số hợp đồng",
        "ben_a": "Bên A (Bên thuê dịch vụ)",
        "dia_chi_ben_a": "Địa chỉ / Mã số thuế Bên A",
        "ben_b": "Bên B (Bên cung cấp dịch vụ)",
        "dia_chi_ben_b": "Địa chỉ / Mã số thuế Bên B",
        "gia_tri_hop_dong": "Giá trị hợp đồng & Thuế GTGT",
        "thoi_han": "Thời hạn thực hiện hợp đồng",
        "pham_vi_cong_viec": "Phạm vi công việc",
        "pham_vi_cong_viec_va_ghi_chu": "Phạm vi công việc & Yêu cầu đặc thù",
        "dieu_khoan_bo_sung": "Các chốt chặn pháp lý bắt buộc tích hợp",
    }
    skip_keys = {"session_id", "stance_id", "specific_values"}
    lines = []
    for key, value in user_input.items():
        if key in skip_keys or value is None or value == "":
            continue
        label = labels.get(key, key)
        lines.append(f"- {label}: {value}")

    specific_values = user_input.get("specific_values")
    if isinstance(specific_values, dict) and specific_values:
        lines.append("\nTHÔNG SỐ NGHIỆP VỤ ĐẶC THÙ CỦA LOẠI HỢP ĐỒNG NÀY:")
        for sp_label, sp_val in specific_values.items():
            if sp_val:
                lines.append(f"  + {sp_label}: {sp_val}")

    return "\n".join(lines) if lines else "Không có thông tin bổ sung."


def format_expired_warning_block(
    expired_law_alerts: Optional[List[Dict[str, Any]]],
) -> str:
    """Định dạng khối cảnh báo văn bản pháp luật hết hiệu lực cho Prompt Rà soát & Vá lỗi."""
    if not expired_law_alerts:
        return ""
    warnings = []
    for alert in expired_law_alerts:
        law_name = alert.get("law_ref", "")
        status = alert.get("status", "")
        replaced = alert.get("replaced_by")
        msg = f"- {law_name} ({status})"
        if replaced:
            msg += f". Thay thế bởi: {replaced}"
        warnings.append(msg)

    return (
        "\n=== CẢNH BÁO TỪ HỆ THỐNG TIERED VALIDATION (VĂN BẢN HẾT HIỆU LỰC) ===\n"
        + "\n".join(warnings)
        + "\nLƯU Ý: Nếu điều khoản (đặc biệt Lời mở đầu/Căn cứ) dẫn chiếu các văn bản trên, PHẢI đánh dấu RỦI RO CAO và thay bằng văn bản mới.\n"
    )


def format_chat_context_chunks(chunks: List[Dict[str, Any]]) -> str:
    """Định dạng danh sách chunk hợp đồng và chunk luật cho Prompt Chatbot."""
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
    """Định dạng báo cáo rủi ro sơ bộ của hợp đồng cho Prompt Chatbot Chế độ A."""
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
