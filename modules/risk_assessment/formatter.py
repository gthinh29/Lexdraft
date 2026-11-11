"""Định dạng cảnh báo hiệu lực, danh sách điều khoản lô và dữ liệu Redline cho Prompt Rà soát Rủi ro."""

from typing import Any, Dict, List, Optional

from modules.shared.legal_rules import format_law_chunks_block


def format_expired_warning_block(
    expired_law_alerts: Optional[List[Dict[str, Any]]],
) -> str:
    """Định dạng khối cảnh báo văn bản pháp luật hết hiệu lực."""
    if not expired_law_alerts:
        return ""
    warnings = []
    for alert in expired_law_alerts:
        msg = f"- {alert.get('law_ref', '')} ({alert.get('status', '')})"
        replaced = alert.get("replaced_by")
        if replaced:
            msg += f". Thay thế bởi: {replaced}"
        warnings.append(msg)

    return (
        "\n=== CẢNH BÁO TỪ HỆ THỐNG TIERED VALIDATION (VĂN BẢN HẾT HIỆU LỰC) ===\n"
        + "\n".join(warnings)
        + "\nLƯU Ý: Nếu điều khoản (đặc biệt Lời mở đầu/Căn cứ) dẫn chiếu các văn bản trên, PHẢI đánh dấu RỦI RO CAO và thay bằng văn bản mới.\n"
    )


def format_batch_articles_block(articles: List[Dict[str, Any]]) -> str:
    """Định dạng danh sách điều khoản kèm căn cứ pháp lý riêng thành khối cho batch prompt."""
    return "".join(
        f"\n------------------------------------------------------------\n"
        f"[DIEU_INPUT_{i}] — {art['label']}\n"
        f"1. NỘI DUNG ĐIỀU KHOẢN:\n{art['content'].strip()}\n\n"
        f"2. CĂN CỨ PHÁP LÝ RIÊNG CHO {art['label'].upper()}:\n{format_law_chunks_block(art.get('law_chunks', []))}\n"
        for i, art in enumerate(articles, 1)
    )


def format_batch_output_example(total: int) -> str:
    """Tạo phần ví dụ định dạng đầu ra cho prompt rà soát hàng loạt."""
    example = "".join(
        f"===DIEU_{i}_KET_QUA===\n"
        f"- **Mức độ & Nhận diện rủi ro**: ...\n"
        f"- **Trích dẫn nội dung có vấn đề trong Hợp đồng**: ...\n"
        f"- **Căn cứ pháp lý & Phân tích đối chiếu**: ...\n"
        for i in range(1, min(total + 1, 3))
    )
    if total > 2:
        example += f"... (đầy đủ đến ===DIEU_{total}_KET_QUA===)\n"
    return example


def format_batch_redraft_items(risky_articles: List[Dict[str, Any]]) -> str:
    """Định dạng danh sách điều khoản lỗi kèm rủi ro và căn cứ cho prompt soạn lại."""
    return "".join(
        f"\n------------------------------------------------------------\n"
        f"[CAN_SUA_{item['seq']}] — {item['label']}\n"
        f"1. NỘI DUNG GỐC:\n{item['content'].strip()}\n\n"
        f"2. RỦI RO CẦN KHẮC PHỤC:\n{item['risk_summary'].strip()}\n\n"
        f"3. CĂN CỨ PHÁP LÝ CHUẨN:\n{format_law_chunks_block(item.get('law_chunks', []))}\n"
        for item in risky_articles
    )
