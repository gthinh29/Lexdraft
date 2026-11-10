"""
modules/drafting/prompts.py
Định nghĩa các mẫu prompt phục vụ sinh nội dung và hoàn thiện hợp đồng theo Phân loại (Taxonomy)
và Vị thế Bảo vệ Pháp lý (Stance-Based Drafting).
"""

from typing import Any, Dict, List

from modules.drafting import retrieval
from modules.shared.legal_rules import (
    STANDARD_LEGAL_CITATION_RULES,
    format_law_chunks_block,
)

DRAFTING_SYSTEM_INSTRUCTION = f"""Bạn là chuyên gia pháp lý cao cấp chuyên soạn thảo hợp đồng dịch vụ tại Việt Nam.
Nhiệm vụ của bạn là soạn bản nháp hợp đồng dịch vụ hoàn chỉnh, chặt chẽ về mặt pháp lý, dựa trên:
(1) Phân loại hợp đồng & Vị thế bảo vệ pháp lý được chỉ định,
(2) Thông tin giao dịch và các thông số nghiệp vụ đặc thù do người dùng cung cấp,
(3) Các CĂN CỨ PHÁP LÝ được truy xuất từ cơ sở dữ liệu (RAG).

QUY TẮC SOẠN THẢO BẮT BUỘC:
1. CĂN CỨ PHÁP LÝ là nguồn ưu tiên cao nhất. Mọi điều khoản trong hợp đồng phải tuân thủ và không được mâu thuẫn với các quy định trong phần CĂN CỨ PHÁP LÝ.
2. BÁM SÁT PHÂN LOẠI & KHUNG ĐIỀU KHOẢN BẮT BUỘC (CLAUSE PLAYBOOK): Phải triển khai đầy đủ các Điều khoản theo đúng cấu trúc đặc thù của loại hợp đồng được chọn.
3. TUÂN THỦ VỊ THẾ BẢO VỆ PHÁP LÝ (LEGAL STANCE): Soạn thảo câu chữ về Nghiệm thu, Thanh toán, Sở hữu trí tuệ, Chế tài và Chấm dứt hợp đồng theo đúng chiến lược bảo vệ quyền lợi của bên được chọn, nhưng TUYỆT ĐỐI KHÔNG vượt quá giới hạn pháp định (ví dụ: mức phạt vi phạm thương mại không được vượt quá 8% theo Điều 301 Luật Thương mại).
4. Nếu thiếu thông tin chi tiết của một bên, giữ nguyên ký hiệu điền khuyết `[●]` hoặc `[CẦN BỔ SUNG: <mô tả>]` thay vì tự bịa đặt số liệu.
5. QUY TẮC TRÌNH BÀY VĂN BẢN HÀNH CHÍNH CHUẨN A4:
   - Mở đầu bằng Quốc hiệu, Tiêu ngữ, Tên hợp đồng (IN HOA), Số hợp đồng, Phần Căn cứ pháp lý, Thông tin Bên A và Bên B.
   - Mỗi Điều và mỗi khoản con (ví dụ: `1.1.`, `1.2.`, `2.1.`, `2.2.`) BẮT BUỘC phải tách ra từng dòng riêng biệt (dùng 2 dấu xuống dòng `\\n\\n` giữa các khoản). Tuyệt đối KHÔNG gộp nhiều khoản trên cùng một đoạn văn.

{STANDARD_LEGAL_CITATION_RULES}"""


def _format_law_context(law_context: List[Dict[str, Any]]) -> str:
    """Wrapper tương thích ngược, gọi thẳng hàm chuẩn hóa dùng chung."""
    return format_law_chunks_block(law_context)


def _format_user_input(user_input: Dict[str, Any]) -> str:
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

    # Bổ sung các trường thông số đặc thù theo phân loại hợp đồng (nếu có)
    specific_values = user_input.get("specific_values")
    if isinstance(specific_values, dict) and specific_values:
        lines.append("\nTHÔNG SỐ NGHIỆP VỤ ĐẶC THÙ CỦA LOẠI HỢP ĐỒNG NÀY:")
        for sp_label, sp_val in specific_values.items():
            if sp_val:
                lines.append(f"  + {sp_label}: {sp_val}")

    return "\n".join(lines) if lines else "Không có thông tin bổ sung."


def build_drafting_prompt(
    template: str,
    law_context: List[Dict[str, Any]],
    user_input: Dict[str, Any],
) -> str:
    """
    Ghép prompt sinh hợp đồng theo cấu trúc Tường minh (White-Box):
      1. System Instruction + Quy tắc trích dẫn chuẩn
      2. Chiến lược Vị thế Đàm phán Pháp lý (Bảo vệ Bên A / Bảo vệ Bên B / Cân bằng)
      3. Thông tin giao dịch & Thông số đặc thù theo Phân loại hợp đồng
      4. Căn cứ pháp lý truy xuất từ FAISS (RAG Context)
      5. Khung cấu trúc điều khoản bắt buộc (Clause Playbook)
    """
    law_context_text = format_law_chunks_block(law_context)
    user_input_text = _format_user_input(user_input)
    template_text = (
        template.strip()
        if template
        else "Không có mẫu cấu trúc tham khảo (sinh hoàn toàn từ căn cứ pháp lý)."
    )
    contract_type = user_input.get("contract_type", "hợp đồng dịch vụ")
    stance_id = user_input.get("stance_id", "balanced")
    stance_cfg = retrieval.get_stance_config(stance_id)
    stance_directives = "\n".join(
        f"  * {d}" for d in stance_cfg.get("drafting_directives", [])
    )

    stance_block = (
        f"CHIẾN LƯỢC VỊ THẾ BẢO VỆ PHÁP LÝ ({stance_cfg.get('label', 'Cân bằng hai bên')}):\n"
        f"{stance_directives}"
        if stance_directives
        else ""
    )

    prompt = f"""{DRAFTING_SYSTEM_INSTRUCTION}

=== 1. THÔNG TIN GIAO DỊCH & THÔNG SỐ ĐẶC THÙ NGƯỜI DÙNG CUNG CẤP ===
{user_input_text}

=== 2. {stance_block} ===

=== 3. CĂN CỨ PHÁP LÝ TRUY XUẤT TỪ VECTOR DB (ƯU TIÊN CAO NHẤT) ===
{law_context_text}

=== 4. KHUNG PHÂN LOẠI & BỐ CỤC ĐIỀU KHOẢN CHUẨN (CLAUSE PLAYBOOK) ===
{template_text}

=== 5. YÊU CẦU ĐẦU RA ===
Hãy soạn thảo bản nháp {contract_type} hoàn chỉnh theo chuẩn văn bản pháp lý Việt Nam (bao gồm Quốc hiệu, Tiêu đề, Số hợp đồng, Phần Căn cứ pháp lý dẫn chiếu đúng văn bản năm 2025/2026, Thông tin các bên, đầy đủ các Điều khoản theo Khung phân loại và Bảng chữ ký Đại diện Bên A - Đại diện Bên B).
Lưu ý: Chỉ xuất nội dung văn bản hợp đồng hoàn chỉnh, không thêm lời bình luận ngoài hợp đồng."""

    return prompt
