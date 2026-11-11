"""Định dạng thông tin giao dịch, thông số đặc thù và chiến lược vị thế cho Prompt soạn thảo."""

from typing import Any, Dict

_USER_INPUT_LABELS = {
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

_SKIP_KEYS = {"session_id", "stance_id", "specific_values"}


def format_drafting_user_input(user_input: Dict[str, Any]) -> str:
    """Chuyển đổi dict thông tin giao dịch người dùng thành văn bản có cấu trúc."""
    lines = []
    for key, value in user_input.items():
        if key in _SKIP_KEYS or value is None or value == "":
            continue
        lines.append(f"- {_USER_INPUT_LABELS.get(key, key)}: {value}")

    specific_values = user_input.get("specific_values")
    if isinstance(specific_values, dict) and specific_values:
        lines.append("\nTHÔNG SỐ NGHIỆP VỤ ĐẶC THÙ CỦA LOẠI HỢP ĐỒNG NÀY:")
        for sp_label, sp_val in specific_values.items():
            if sp_val:
                lines.append(f"  + {sp_label}: {sp_val}")

    return "\n".join(lines) if lines else "Không có thông tin bổ sung."


def format_stance_block(stance_cfg: Dict[str, Any]) -> str:
    """Định dạng khối chỉ dẫn Vị thế Bảo vệ Pháp lý (Stance) từ cấu hình taxonomy."""
    directives = "\n".join(
        f"  * {d}" for d in stance_cfg.get("drafting_directives", [])
    )
    if not directives:
        return ""
    label = stance_cfg.get("label", "Cân bằng hai bên")
    return f"CHIẾN LƯỢC VỊ THẾ BẢO VỆ PHÁP LÝ ({label}):\n{directives}"
