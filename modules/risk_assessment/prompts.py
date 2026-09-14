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
    "(b) Căn cứ pháp lý vi phạm (số Điều, tên Luật), (c) Khuyến nghị chỉnh sửa cụ thể."
)


def _format_law_context(law_chunks: List[Dict[str, Any]]) -> str:
    """Định dạng danh sách các chunk luật liên quan thành khối văn bản có đánh số điều."""
    if not law_chunks:
        return "Không tìm thấy điều luật liên quan trực tiếp trong cơ sở dữ liệu."

    parts = []
    for chunk in law_chunks:
        metadata = chunk.get("metadata", {})
        article = metadata.get("article") or metadata.get("article_number") or "N/A"
        source = metadata.get("source") or metadata.get("doc_name") or "N/A"
        title = metadata.get("title", "")
        header = f"[{article} - {source}]" + (f" ({title})" if title else "")
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
