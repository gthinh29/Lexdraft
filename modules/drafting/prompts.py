"""Mẫu Prompt soạn thảo hợp đồng dịch vụ theo Phân loại (Taxonomy) và Vị thế Pháp lý (Stance)."""

from typing import Any, Dict, List

from modules.drafting import retrieval
from modules.shared.legal_rules import (
    STANDARD_LEGAL_CITATION_RULES,
    format_drafting_user_input,
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
6. VĂN PHONG PHÁP LÝ CÔ ĐỌNG: Mỗi khoản viết súc tích 1–2 câu chuẩn mực, rõ ràng quyền/nghĩa vụ và chế tài, tránh viết dài dòng trùng lặp ý giữa các điều.

{STANDARD_LEGAL_CITATION_RULES}"""

DRAFTING_PROMPT_TEMPLATE = """{system_instruction}

=== 1. THÔNG TIN GIAO DỊCH & THÔNG SỐ ĐẶC THÙ NGƯỜNG DÙNG CUNG CẤP ===
{user_input_text}

=== 2. {stance_block} ===

=== 3. CĂN CỨ PHÁP LÝ TRUY XUẤT TỪ VECTOR DB (ƯU TIÊN CAO NHẤT) ===
{law_context_text}

=== 4. KHUNG PHÂN LOẠI & BỐ CỤC ĐIỀU KHOẢN CHUẨN (CLAUSE PLAYBOOK) ===
{template_text}

=== 5. YÊU CẦU ĐẦU RA ===
Hãy soạn thảo bản nháp {contract_type} hoàn chỉnh theo chuẩn văn bản pháp lý Việt Nam (bao gồm Quốc hiệu, Tiêu đề, Số hợp đồng, Phần Căn cứ pháp lý dẫn chiếu đúng văn bản năm 2025/2026, Thông tin các bên, đầy đủ các Điều khoản theo Khung phân loại và Bảng chữ ký Đại diện Bên A - Đại diện Bên B).
Lưu ý: Chỉ xuất nội dung văn bản hợp đồng hoàn chỉnh, không thêm lời bình luận ngoài hợp đồng."""


def build_drafting_prompt(
    template: str,
    law_context: List[Dict[str, Any]],
    user_input: Dict[str, Any],
) -> str:
    """Ghép dữ liệu giao dịch, chiến lược vị thế và căn cứ RAG vào mẫu Prompt soạn thảo."""
    contract_type = user_input.get("contract_type", "hợp đồng dịch vụ")
    stance_cfg = retrieval.get_stance_config(user_input.get("stance_id", "balanced"))
    stance_directives = "\n".join(
        f"  * {d}" for d in stance_cfg.get("drafting_directives", [])
    )
    stance_block = (
        f"CHIẾN LƯỢC VỊ THẾ BẢO VỆ PHÁP LÝ ({stance_cfg.get('label', 'Cân bằng hai bên')}):\n{stance_directives}"
        if stance_directives
        else ""
    )
    template_text = (
        template.strip()
        if template
        else "Không có mẫu cấu trúc tham khảo (sinh hoàn toàn từ căn cứ pháp lý)."
    )

    return DRAFTING_PROMPT_TEMPLATE.format(
        system_instruction=DRAFTING_SYSTEM_INSTRUCTION,
        user_input_text=format_drafting_user_input(user_input),
        stance_block=stance_block,
        law_context_text=format_law_chunks_block(law_context),
        template_text=template_text,
        contract_type=contract_type,
    )
