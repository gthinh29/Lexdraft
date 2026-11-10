"""
modules/drafting/service.py
Service hỗ trợ soạn thảo hợp đồng theo Phân loại (Taxonomy), Vị thế Bảo vệ Pháp lý (Stance)
và cung cấp dữ liệu White-Box RAG Inspector.
"""

import logging
from typing import Any, Dict, Optional

from modules.drafting import prompts, retrieval

try:
    from modules.shared import llm_client  # Phần 6 - Dev B
except ImportError:
    llm_client = None

try:
    from modules.risk_assessment import (
        service as risk_assessment_service,
    )  # Phần 8 - Dev B
except ImportError:
    risk_assessment_service = None

logger = logging.getLogger(__name__)


def generate_contract_draft(user_input_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sinh bản nháp hợp đồng dịch vụ theo Phân loại (Taxonomy) & Vị thế Bảo vệ Pháp lý (Stance).

    Luồng xử lý:
        1. Lấy khung phân loại chuẩn (Clause Playbook) từ contract_taxonomy.json (hoặc fallback template_index).
        2. Lấy các điều luật liên quan từ law_index (Multi-query RAG theo phân loại + yêu cầu người dùng).
        3. Ghép prompt kèm Chiến lược Vị thế Bảo vệ (Bên A / Bên B / Cân bằng) và gọi LLM sinh bản nháp.
        4. Trả về bản nháp, danh sách căn cứ pháp lý đã sử dụng, và debug_trace cho White-Box Inspector.
    """
    if "contract_type" not in user_input_dict:
        raise ValueError(
            "user_input_dict thiếu key 'contract_type' để truy xuất mẫu và luật liên quan."
        )

    contract_type_query = user_input_dict["contract_type"]
    category_id = user_input_dict.get("category_id")

    # 7.1: Retrieval - lấy khung phân loại (Clause Playbook) + các điều luật liên quan
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

    # 7.2: Ghép prompt
    prompt = prompts.build_drafting_prompt(template_text, law_context, user_input_dict)

    # 7.3: Gọi LLM sinh bản nháp (threshold=0.0 vì soạn thảo cần sinh văn bản chứ không từ chối như chatbot)
    if llm_client is None:
        raise RuntimeError(
            "modules.shared.llm_client chưa sẵn sàng (Phần 6 chưa build)."
        )

    draft_result = llm_client.generate_grounded_response(
        query=prompt,
        retrieved_chunks=law_context,
        threshold=0.0,
    )
    draft_text = draft_result.get("answer", "")
    citations = draft_result.get("citations", [])
    debug_trace = draft_result.get("debug_trace")

    return {
        "draft": draft_text,
        "citations": citations,
        "debug_trace": debug_trace,
        "risk_report": [],
        "expired_law_alerts": [],
    }


def _run_risk_assessment_safely(
    draft_text: str, session_id: Optional[str]
) -> Optional[Any]:
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
