"""
modules/drafting/service.py

PUBLIC - đây là interface DUY NHẤT mà module drafting expose ra bên ngoài
(app.py hoặc module khác chỉ được gọi qua đây, KHÔNG được import thẳng
retrieval.py hay prompts.py).
"""

import logging
from typing import Any, Dict, Optional

from modules.drafting import prompts, retrieval

try:
    from modules.shared import llm_client  # Phần 6 - Dev B
except ImportError:
    llm_client = None

try:
    from modules.risk_assessment import service as risk_assessment_service  # Phần 8 - Dev B
except ImportError:
    risk_assessment_service = None

logger = logging.getLogger(__name__)


def generate_contract_draft(user_input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sinh bản nháp hợp đồng dịch vụ và tự động chạy gợi ý rủi ro cho bản nháp đó.

    Luồng xử lý (đúng SRS 4.1):
        1. Lấy mẫu từ template_index dựa trên loại hợp đồng.
        2. Lấy luật liên quan từ law_index.
        3. Ghép prompt và gọi LLM sinh bản nháp.
        4. Tự động gọi risk_assessment.service.analyze_contract() cho bản nháp
           vừa sinh, trả về cả bản nháp và báo cáo rủi ro.

    Args:
        user_input_dict: dict thông tin từ form. BẮT BUỘC có key "contract_type"
            (mô tả loại hợp đồng, vd "hợp đồng thiết kế website") để làm query
            truy xuất mẫu + luật. Các key khác (bên A, bên B, giá trị hợp đồng,
            thời hạn, phạm vi công việc...) tùy theo thiết kế form ở Phần 10.
            Có thể kèm "session_id" nếu muốn liên kết luôn với 1 phiên chatbot.

    Returns:
        {
            "draft": str,                       # bản nháp hợp đồng
            "risk_report": list | None,         # kết quả Phần 8, None nếu Phần 8
                                                 # chưa sẵn sàng hoặc lỗi khi phân tích
        }

    Raises:
        ValueError: nếu thiếu "contract_type" trong user_input_dict.
        RuntimeError: nếu modules.shared.llm_client (Phần 6) chưa sẵn sàng.
    """
    if "contract_type" not in user_input_dict:
        raise ValueError(
            "user_input_dict thiếu key 'contract_type' để truy xuất mẫu và luật liên quan."
        )

    contract_type_query = user_input_dict["contract_type"]

    # 7.1: Retrieval - lấy mẫu + luật
    template_hit = retrieval.retrieve_template(contract_type_query)
    if template_hit is None:
        logger.warning(
            "Không tìm thấy mẫu hợp đồng cho '%s' - sẽ soạn không dựa trên mẫu cấu trúc.",
            contract_type_query,
        )
    template_text = template_hit["content"] if template_hit else ""

    law_context = retrieval.retrieve_relevant_law(contract_type_query)

    # 7.2: Ghép prompt
    prompt = prompts.build_drafting_prompt(template_text, law_context, user_input_dict)

    # 7.3: Gọi LLM sinh bản nháp
    if llm_client is None:
        raise RuntimeError(
            "modules.shared.llm_client chưa sẵn sàng (Phần 6 chưa build)."
        )

    draft_result = llm_client.generate_grounded_response(
        query=prompt,
        retrieved_chunks=law_context,
    )
    draft_text = draft_result.get("answer", "")

    # 7.4: Tự động chạy risk_assessment cho bản nháp vừa sinh
    risk_report = _run_risk_assessment_safely(draft_text, user_input_dict.get("session_id"))

    return {
        "draft": draft_text,
        "risk_report": risk_report,
    }


def _run_risk_assessment_safely(draft_text: str, session_id: Optional[str]) -> Optional[Any]:
    if risk_assessment_service is None:
        logger.warning(
            "modules.risk_assessment.service chưa sẵn sàng (Phần 8 chưa build). "
            "Trả về bản nháp mà không kèm báo cáo rủi ro."
        )
        return None

    try:
        return risk_assessment_service.analyze_contract(
            file_path_or_text=draft_text,
            session_id=session_id,
        )
    except Exception:
        logger.exception("Lỗi khi chạy risk_assessment cho bản nháp vừa sinh.")
        return None
