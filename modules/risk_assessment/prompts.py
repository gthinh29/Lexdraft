"""Hai hệ thống Prompt độc lập: (1) Gợi ý Rủi ro ngắn gọn 3 mục và (2) Soạn thảo Vá lỗi Redline."""

from typing import Any

from modules.shared.legal_rules import (
    STANDARD_LEGAL_CITATION_RULES,
    format_expired_warning_block,
    format_law_chunks_block,
)

RISK_ASSESSMENT_INSTRUCTION = f"""Bạn là chuyên gia pháp chế cao cấp chuyên thẩm định rủi ro hợp đồng dịch vụ tại Việt Nam.
Nhiệm vụ DUY NHẤT ở bước này: Phát hiện rủi ro pháp lý của từng điều khoản dựa trên CĂN CỨ PHÁP LÝ được truy xuất riêng cho điều khoản đó. Không cần viết lại điều khoản thay thế ở bước này.

QUY TẮC THẨM ĐỊNH & VĂN PHONG NGẮN GỌN (BẮT BUỘC):
1. CHỈ SỬ DỤNG CĂN CỨ ĐƯỢC CUNG CẤP: Tuyệt đối KHÔNG tự bịa số hiệu điều luật ngoài căn cứ.
2. SIÊU GỌN, TRỰC DIỆN: Mỗi mục chỉ 1 câu súc tích, không viết lan man.
3. NẾU ĐIỀU KHOẢN AN TOÀN: Ghi gọn:
   - **Mức độ & Nhận diện rủi ro**: Không phát hiện rủi ro pháp lý rõ ràng. Điều khoản phù hợp quy định hiện hành.
   - **Căn cứ pháp lý & Phân tích đối chiếu**: Nêu ngắn gọn 1 câu điều luật phù hợp.
4. NẾU PHÁT HIỆN RỦI RO (vi phạm điều cấm, vượt trần phạt 8% Điều 301 LTM, viện dẫn luật hết hiệu lực/sai tên, bất lợi đơn phương, thiếu bảo vệ dữ liệu cá nhân Luật 91/2025/QH15...):
   Trình bày ĐÚNG 3 mục ngắn gọn:
   - **Mức độ & Nhận diện rủi ro**: `[RỦI RO CAO - VI PHẠM]` hoặc `[RỦI RO TRUNG BÌNH - BẤT LỢI]` + tên lỗi (≤ 15 từ).
   - **Trích dẫn nội dung có vấn đề trong Hợp đồng**: Trích đúng cụm từ/số liệu lỗi (≤ 20 từ).
   - **Căn cứ pháp lý & Phân tích đối chiếu**: Viện dẫn Điểm/Khoản/Điều/Luật + nêu đúng 1 ý mâu thuẫn cốt lõi (≤ 35 từ).

{STANDARD_LEGAL_CITATION_RULES}"""

SINGLE_RISK_PROMPT_TEMPLATE = """{instruction}{expired_warning_block}

=== CĂN CỨ PHÁP LÝ TRUY XUẤT RIÊNG CHO ĐIỀU KHOẢN NÀY ===
{formatted_law}

=== ĐIỀU KHOẢN HỢP ĐỒNG CẦN THẨM ĐỊNH ===
{dieu_khoan_text}

=== ĐẦU RA NGẮN GỌN (CHỈ 3 MỤC, KHÔNG SOẠN LẠI ĐIỀU KHOẢN) ===
- **Mức độ & Nhận diện rủi ro**: ...
- **Trích dẫn nội dung có vấn đề trong Hợp đồng**: ...
- **Căn cứ pháp lý & Phân tích đối chiếu**: ..."""

BATCH_RISK_PROMPT_TEMPLATE = """{instruction}{expired_warning_block}

=== DANH SÁCH {total} ĐIỀU KHOẢN HỢP ĐỒNG KÈM CĂN CỨ PHÁP LÝ ===
{articles_block}

=== YÊU CẦU ĐẦU RA CHO TẤT CẢ {total} ĐIỀU (CHỈ ĐÁNH GIÁ RỦI RO, NGẮN GỌN) ===
- Mỗi điều bắt đầu bằng `===DIEU_<số>_KET_QUA===` (từ `DIEU_1` đến `DIEU_{total}`, không bỏ sót).
- Nếu có rủi ro: ghi đúng 3 mục (**Mức độ & Nhận diện rủi ro**, **Trích dẫn nội dung có vấn đề trong Hợp đồng**, **Căn cứ pháp lý & Phân tích đối chiếu**).
- Nếu an toàn: ghi `Không phát hiện rủi ro pháp lý rõ ràng. Điều khoản phù hợp quy định hiện hành.` kèm 1 câu căn cứ.

Định dạng mẫu:
{output_example}"""

RISK_REDRAFT_INSTRUCTION = f"""Bạn là luật sư soạn thảo hợp đồng dịch vụ tại Việt Nam.
Nhiệm vụ DUY NHẤT ở bước này: Soạn lại nguyên văn câu chữ chuẩn pháp lý (Redline) cho các điều khoản đã được xác định có rủi ro, để ghép trực tiếp vào bản Hợp đồng Word (.docx).

QUY TẮC SOẠN THẢO BẮT BUỘC:
1. NẾU LÀ LỜI MỞ ĐẦU / PHẦN CĂN CỨ:
   - GIỮ NGUYÊN 100% Quốc hiệu, Tiêu ngữ, Tên hợp đồng, Số hợp đồng, ngày ký và thông tin Bên A, Bên B.
   - CHỈ sửa/thay thế các dòng `Căn cứ ...` chứa văn bản hết hiệu lực hoặc sai tên/số hiệu thành văn bản hiện hành 2025/2026 chuẩn xác.
2. NẾU LÀ ĐIỀU KHOẢN (Điều 1, Điều 2, ...):
   - GIỮ NGUYÊN Tiêu đề điều khoản gốc (ví dụ: `Điều 3. Quyền đơn phương chấm dứt hợp đồng`).
   - Giữ lại các thông số hợp pháp sẵn có (mức giá, đối tượng, thời gian...); CHỈ sửa/bổ sung câu chữ khắc phục đúng rủi ro đã chỉ ra theo văn phong hợp đồng chuẩn mực.
3. CHỈ XUẤT NỘI DUNG ĐIỀU KHOẢN HOÀN CHỈNH:
   - Tuyệt đối KHÔNG viết lời chào, lời giải thích, dấu ngoặc kép bao quanh hay nhãn thừa như `(Đã sửa đổi)`.

{STANDARD_LEGAL_CITATION_RULES}"""

SINGLE_REDRAFT_PROMPT_TEMPLATE = """{instruction}{expired_warning_block}

=== CĂN CỨ PHÁP LÝ ÁP DỤNG ===
{formatted_law}

=== ĐIỀU KHOẢN GỐC CẦN SỬA ===
{dieu_khoan_text}

=== RỦI RO ĐÃ PHÁT HIỆN ===
{risk_summary}

=== ĐẦU RA ===
Chỉ xuất nguyên văn toàn bộ điều khoản (hoặc Lời mở đầu) sau khi đã sửa chuẩn pháp lý:"""

BATCH_REDRAFT_PROMPT_TEMPLATE = """{instruction}{expired_warning_block}

=== DANH SÁCH {total} ĐIỀU KHOẢN CẦN SOẠN LẠI CHUẨN PHÁP LÝ 2026 ===
{items_block}

=== YÊU CẦU ĐẦU RA (CHỈ XUẤT VĂN BẢN ĐIỀU KHOẢN ĐÃ SỬA) ===
- Bắt đầu mỗi phần bằng đúng dòng phân cách tương ứng: {markers_str}.
- Tuyệt đối KHÔNG viết lại báo cáo rủi ro hay lời giải thích; chỉ viết nguyên văn điều khoản hoàn chỉnh (giữ nguyên Tiêu đề điều khoản gốc hoặc Quốc hiệu/Thông tin hai bên nếu là Lời mở đầu).

Ví dụ định dạng:
===REDRAFT_{example_seq}_KET_QUA===
<Nguyên văn điều khoản đã sửa hoàn chỉnh>"""


def build_risk_prompt(
    dieu_khoan_text: str,
    law_context: list[dict[str, Any]],
    expired_law_alerts: list[dict[str, Any]] | None = None,
) -> str:
    """Ghép Prompt phân tích rủi ro ngắn gọn cho một Điều khoản hợp đồng đơn lẻ."""
    return SINGLE_RISK_PROMPT_TEMPLATE.format(
        instruction=RISK_ASSESSMENT_INSTRUCTION,
        expired_warning_block=format_expired_warning_block(expired_law_alerts),
        formatted_law=format_law_chunks_block(law_context),
        dieu_khoan_text=dieu_khoan_text.strip(),
    )


def build_batch_risk_prompt(
    articles: list,
    expired_law_alerts: list[dict[str, Any]] | None = None,
) -> str:
    """Ghép Prompt phân tích rủi ro ngắn gọn cho tất cả điều khoản trong 1 lần gọi LLM."""
    total = len(articles)
    articles_block = "".join(
        f"\n------------------------------------------------------------\n"
        f"[DIEU_INPUT_{i}] — {art['label']}\n"
        f"1. NỘI DUNG ĐIỀU KHOẢN:\n{art['content'].strip()}\n\n"
        f"2. CĂN CỨ PHÁP LÝ RIÊNG CHO {art['label'].upper()}:\n{format_law_chunks_block(art.get('law_chunks', []))}\n"
        for i, art in enumerate(articles, 1)
    )
    output_example = "".join(
        f"===DIEU_{i}_KET_QUA===\n"
        f"- **Mức độ & Nhận diện rủi ro**: ...\n"
        f"- **Trích dẫn nội dung có vấn đề trong Hợp đồng**: ...\n"
        f"- **Căn cứ pháp lý & Phân tích đối chiếu**: ...\n"
        for i in range(1, min(total + 1, 3))
    )
    if total > 2:
        output_example += f"... (đầy đủ đến ===DIEU_{total}_KET_QUA===)\n"

    return BATCH_RISK_PROMPT_TEMPLATE.format(
        instruction=RISK_ASSESSMENT_INSTRUCTION,
        expired_warning_block=format_expired_warning_block(expired_law_alerts),
        total=total,
        articles_block=articles_block,
        output_example=output_example,
    )


def build_risk_redraft_prompt(
    dieu_khoan_text: str,
    risk_summary: str,
    law_context: list[dict[str, Any]],
    expired_law_alerts: list[dict[str, Any]] | None = None,
) -> str:
    """Ghép Prompt chuyên biệt để soạn lại một điều khoản hợp đồng bị rủi ro."""
    return SINGLE_REDRAFT_PROMPT_TEMPLATE.format(
        instruction=RISK_REDRAFT_INSTRUCTION,
        expired_warning_block=format_expired_warning_block(expired_law_alerts),
        formatted_law=format_law_chunks_block(law_context),
        dieu_khoan_text=dieu_khoan_text.strip(),
        risk_summary=risk_summary.strip(),
    )


def build_batch_redraft_prompt(
    risky_articles: list[dict[str, Any]],
    expired_law_alerts: list[dict[str, Any]] | None = None,
) -> str:
    """Ghép Prompt soạn thảo lại hàng loạt chỉ cho các điều khoản có rủi ro."""
    items_block = "".join(
        f"\n------------------------------------------------------------\n"
        f"[CAN_SUA_{item['seq']}] — {item['label']}\n"
        f"1. NỘI DUNG GỐC:\n{item['content'].strip()}\n\n"
        f"2. RỦI RO CẦN KHẮC PHỤC:\n{item['risk_summary'].strip()}\n\n"
        f"3. CĂN CỨ PHÁP LÝ CHUẨN:\n{format_law_chunks_block(item.get('law_chunks', []))}\n"
        for item in risky_articles
    )
    markers_str = ", ".join(
        f"`===REDRAFT_{item['seq']}_KET_QUA===`" for item in risky_articles
    )
    example_seq = risky_articles[0]["seq"] if risky_articles else 1

    return BATCH_REDRAFT_PROMPT_TEMPLATE.format(
        instruction=RISK_REDRAFT_INSTRUCTION,
        expired_warning_block=format_expired_warning_block(expired_law_alerts),
        total=len(risky_articles),
        items_block=items_block,
        markers_str=markers_str,
        example_seq=example_seq,
    )
