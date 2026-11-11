"""Điều phối luồng soạn thảo hợp đồng dịch vụ (Retrieval -> Prompt -> LLM)."""

import logging
from typing import Any, Dict, Optional

from modules.drafting import prompts, retrieval

try:
    from modules.shared import llm_client
except ImportError:
    llm_client = None

try:
    from modules.risk_assessment import service as risk_assessment_service
except ImportError:
    risk_assessment_service = None

logger = logging.getLogger(__name__)


def generate_contract_draft(user_input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Sinh bản nháp hợp đồng dịch vụ theo Phân loại (Taxonomy) và Vị thế Pháp lý (Stance)."""
    if "contract_type" not in user_input_dict:
        raise ValueError(
            "user_input_dict thiếu key 'contract_type' để truy xuất mẫu và luật liên quan."
        )

    contract_type_query = user_input_dict["contract_type"]
    category_id = user_input_dict.get("category_id")

    template_hit = retrieval.retrieve_template(category_id or contract_type_query)
    if template_hit is None:
        logger.warning(
            "Không tìm thấy mẫu hợp đồng cho '%s' - sẽ soạn không dựa trên mẫu cấu trúc.",
            contract_type_query,
        )
    template_text = template_hit["content"] if template_hit else ""

    if category_id:
        law_context = retrieval.retrieve_relevant_law(
            contract_type_query, category_id=category_id
        )
    else:
        law_context = retrieval.retrieve_relevant_law(contract_type_query)

    prompt = prompts.build_drafting_prompt(template_text, law_context, user_input_dict)

    if llm_client is None:
        raise RuntimeError("modules.shared.llm_client chưa sẵn sàng.")

    draft_result = llm_client.generate_grounded_response(
        query=prompt,
        retrieved_chunks=law_context,
        threshold=0.0,
    )

    return {
        "draft": draft_result.get("answer", ""),
        "citations": draft_result.get("citations", []),
        "refusal": draft_result.get("refusal", False),
        "debug_trace": draft_result.get("debug_trace"),
        "risk_report": [],
        "expired_law_alerts": [],
    }


def _run_risk_assessment_safely(
    draft_text: str, session_id: Optional[str]
) -> Optional[Any]:
    """Chạy phân tích rủi ro tùy chọn cho bản nháp vừa sinh."""
    if risk_assessment_service is None:
        logger.warning("modules.risk_assessment.service chưa sẵn sàng.")
        return None

    try:
        return risk_assessment_service.analyze_contract(
            file_path_or_text=draft_text,
            session_id=session_id,
        )
    except Exception:
        logger.exception("Lỗi khi chạy risk_assessment cho bản nháp vừa sinh.")
        return None
