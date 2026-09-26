"""
modules/risk_assessment/service.py

PUBLIC - interface DUY NHẤT mà module risk_assessment expose ra bên ngoài
(app.py hoặc module drafting chỉ được gọi qua đây, KHÔNG được import thẳng
retrieval.py hay prompts.py).

Tuân thủ:
- Implementation Plan Phần 8 (8A, 8B, 8C)
- SRS 4.2: Phân tích rủi ro hợp đồng dịch vụ theo pipeline One-shot
- Tự động liên kết context sang Chatbot (Chế độ A)
- Tiered Validation: Kiểm tra hiệu lực văn bản 3 tầng trước khi phân tích rủi ro
"""

import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from modules.risk_assessment import law_validity_checker, prompts, retrieval
from modules.shared import chunking, document_reader, llm_client

logger = logging.getLogger(__name__)


def analyze_contract(
    file_path_or_text: Union[str, Path],
    session_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Phân tích rủi ro pháp lý của một hợp đồng (dạng file upload hoặc text thô).

    Quy trình xử lý (SRS 4.2 & Implementation Plan 8C + Tiered Validation):
        0. [PRE-CHECK] Kiểm tra hiệu lực văn bản 3 tầng (Tiered Validation):
           - Cấp 1: Đối chiếu danh mục kiểm duyệt (expired_laws.json) — tin cậy 100%.
           - Cấp 2: Trích xuất từ Điều khoản thi hành của luật mới trong law_index — ~95%.
           - Cấp 3: LLM Fallback — ~80%, kết quả gắn nhãn "Cần xác minh".
        1. Đọc nội dung văn bản (hỗ trợ .pdf, .docx hoặc chuỗi text trực tiếp).
        2. Phân tách hợp đồng thành các Điều/Khoản bằng chunk_by_article().
        3. Duyệt tuần tự từng Điều:
           - Truy xuất các điều luật liên quan từ law_index qua retrieval.find_related_laws().
           - Ghép prompt phân tích rủi ro qua prompts.build_risk_prompt().
           - Gọi LLM sinh đánh giá có kiểm chứng (Grounded Generation) qua llm_client.
           - Nghỉ ngắn (1 giây) giữa các điều khoản để phòng ngừa Rate Limit (429).
        4. Tự động liên kết hợp đồng và báo cáo rủi ro vào Chatbot session (nếu có session_id).
        5. Trả về dict bao gồm:
           {
               "expired_law_alerts": [...],  # Cảnh báo hiệu lực từ Tiered Validation
               "risk_results": [             # Phân tích rủi ro từng Điều khoản
                   {
                       "dieu_khoan": "Điều 1...",
                       "rui_ro": "Nhận xét rủi ro...",
                       "can_cu": [{"article": "...", "source": "..."}, ...],
                   },
                   ...
               ]
           }

    Args:
        file_path_or_text: Đường dẫn file (str/Path) hoặc toàn bộ chuỗi text hợp đồng.
        session_id: (Tùy chọn) Mã phiên làm việc để đồng bộ sang module Chatbot.

    Returns:
        Dict gồm 'expired_law_alerts' (Tiered Validation) và 'risk_results' (phân tích từng Điều).
    """
    # 1. Trích xuất text
    path_obj = Path(str(file_path_or_text))
    if path_obj.exists() and path_obj.is_file():
        source_name = path_obj.name
        text = document_reader.read_document(path_obj)
    else:
        source_name = "contract_input"
        text = str(file_path_or_text)

    if not text.strip():
        logger.warning("Nội dung hợp đồng rỗng, không thể phân tích rủi ro.")
        return {"expired_law_alerts": [], "risk_results": []}

    # 0. [PRE-CHECK] Tiered Validation — Kiểm tra hiệu lực văn bản trước khi phân tích
    # Lấy sẵn các chunk "điều khoản thi hành" từ law_index để phục vụ Cấp 2
    hiệu_luc_chunks = retrieval.find_related_laws(
        "hiệu lực thi hành bãi bỏ thay thế hết hiệu lực", top_k=10
    )
    expired_law_alerts = law_validity_checker.check_expired_laws(
        contract_text=text,
        law_index_chunks=hiệu_luc_chunks,
        enable_llm_fallback=True,
    )
    if expired_law_alerts:
        logger.warning(
            "[Tiered Validation] Phát hiện %d cảnh báo hiệu lực văn bản trong hợp đồng '%s'.",
            len(expired_law_alerts),
            source_name,
        )
    else:
        logger.info(
            "[Tiered Validation] Không phát hiện văn bản hết hiệu lực trong hợp đồng '%s'.",
            source_name,
        )

    # 2. Chia chunk theo cấu trúc Điều/Khoản
    contract_chunks = chunking.chunk_by_article(
        text=text,
        source_metadata={"source": source_name},
    )

    if not contract_chunks:
        logger.warning("Không trích xuất được chunk nào từ hợp đồng.")
        return {"expired_law_alerts": expired_law_alerts, "risk_results": []}

    logger.info(
        "Bắt đầu phân tích rủi ro cho hợp đồng '%s' (%d điều khoản)...",
        source_name,
        len(contract_chunks),
    )

    risk_results: List[Dict[str, Any]] = []

    # 3. Phân tích từng Điều
    for idx, chunk in enumerate(contract_chunks, 1):
        content = chunk.get("content", "").strip()
        metadata = chunk.get("metadata", {})
        article_label = metadata.get("article") or f"Điều khoản {idx}"

        if not content:
            continue

        # 3.1: Tìm luật liên quan (top_k=3 để tiết kiệm token)
        law_chunks = retrieval.find_related_laws(content, top_k=3)

        # 3.2: Ghép prompt
        prompt = prompts.build_risk_prompt(
            dieu_khoan_text=content,
            law_context=law_chunks,
        )

        # 3.3: Gọi LLM sinh đánh giá có căn cứ
        try:
            llm_result = llm_client.generate_grounded_response(
                query=prompt,
                retrieved_chunks=law_chunks,
                threshold=0.35,  # Ngưỡng mềm cho phân tích rủi ro để không bỏ sót cảnh báo
            )
            risk_text = llm_result.get("answer", "")
            citations = llm_result.get("citations", [])
        except Exception as e:
            logger.exception("Lỗi khi phân tích rủi ro cho %s: %s", article_label, e)
            risk_text = f"Không thể phân tích điều khoản này do lỗi hệ thống: {str(e)}"
            citations = []

        risk_results.append(
            {
                "dieu_khoan": article_label,
                "noi_dung": content,
                "rui_ro": risk_text,
                "can_cu": citations,
            }
        )

        # Nghỉ 1s phòng thủ rate limit khi hợp đồng có nhiều điều khoản
        if idx < len(contract_chunks):
            time.sleep(1.0)

    # 4. Tự động đồng bộ context sang Chatbot (nếu có session_id)
    if session_id:
        try:
            from modules.chatbot_qa import service as chatbot_service

            chatbot_service.attach_contract_context(
                session_id=session_id,
                contract_chunks=contract_chunks,
                risk_report=risk_results,
            )
            logger.info(
                "Đã đồng bộ context hợp đồng sang Chatbot session: %s", session_id
            )
        except Exception:
            logger.exception(
                "Không thể tự động đồng bộ sang Chatbot session %s", session_id
            )

    logger.info(
        "Hoàn tất phân tích: %d cảnh báo hiệu lực, %d điều khoản được phân tích.",
        len(expired_law_alerts),
        len(risk_results),
    )
    return {
        "expired_law_alerts": expired_law_alerts,
        "risk_results": risk_results,
    }


def stream_analyze_contract(
    file_path_or_text: Union[str, Path],
    session_id: Optional[str] = None,
    original_name: Optional[str] = None,
):
    """
    Generator version của analyze_contract — yield kết quả ngay khi từng Điều hoàn tất.

    Mỗi lần yield là một tuple (event_type, payload):
        - ("meta",   {"total": N, "source": "...", "expired_law_alerts": [...]})
          → Phát ngay sau khi Tiered Validation và chunking xong.
        - ("result", {"index": i, "total": N, <risk dict>})
          → Phát sau mỗi điều khoản được phân tích xong.
        - ("done",   {"risk_results": [...], "expired_law_alerts": [...]})
          → Phát cuối cùng kèm đồng bộ Chatbot context.

    Cách dùng trong Streamlit:
        for event, data in stream_analyze_contract(path):
            if event == "meta":
                ...hiện banner expired_alerts...
            elif event == "result":
                ...append và re-render...
            elif event == "done":
                ...lưu session state...
    """
    # 1. Trích xuất text
    path_obj = Path(str(file_path_or_text))
    if path_obj.exists() and path_obj.is_file():
        # Dùng tên gốc nếu được truyền vào, không hiện tên tmp
        source_name = original_name or path_obj.name
        text = document_reader.read_document(path_obj)
    else:
        source_name = original_name or "contract_input"
        text = str(file_path_or_text)

    if not text.strip():
        logger.warning("[stream] Nội dung hợp đồng rỗng.")
        yield (
            "error",
            {
                "message": "Không trích xuất được nội dung từ file. "
                "File có thể bị lỗi, được bảo vệ bằng mật khẩu, "
                "hoặc không chứa điều khoản hợp đồng nào.",
            },
        )
        return

    # 0. Tiered Validation
    hieu_luc_chunks = retrieval.find_related_laws(
        "hiệu lực thi hành bãi bỏ thay thế hết hiệu lực", top_k=10
    )
    expired_law_alerts = law_validity_checker.check_expired_laws(
        contract_text=text,
        law_index_chunks=hieu_luc_chunks,
        enable_llm_fallback=False,  # Tắt LLM fallback để tiết kiệm quota (Cấp 1+2 đủ)
    )

    # 2. Chunking
    contract_chunks = chunking.chunk_by_article(
        text=text,
        source_metadata={"source": source_name},
    )

    total = len(contract_chunks)
    yield (
        "meta",
        {
            "total": total,
            "source": source_name,
            "expired_law_alerts": expired_law_alerts,
        },
    )

    if not contract_chunks:
        yield ("done", {"expired_law_alerts": expired_law_alerts, "risk_results": []})
        return

    risk_results: List[Dict[str, Any]] = []

    # 3. Thu thập law_chunks cho TẤT CẢ điều khoản
    yield (
        "progress",
        {"message": "🔍 Đang truy xuất căn cứ pháp lý...", "index": 0, "total": total},
    )
    articles_data = []
    for chunk in contract_chunks:
        content = chunk.get("content", "").strip()
        metadata = chunk.get("metadata", {})
        article_label = (
            metadata.get("article") or f"Điều khoản {len(articles_data) + 1}"
        )
        if not content:
            continue
        law_chunks = retrieval.find_related_laws(content, top_k=3)
        articles_data.append(
            {
                "label": article_label,
                "content": content,
                "law_chunks": law_chunks,
                "metadata": metadata,
            }
        )

    if not articles_data:
        yield ("done", {"expired_law_alerts": expired_law_alerts, "risk_results": []})
        return

    # 4. Gọi LLM cho toàn bộ hợp đồng (Batch mode)
    yield (
        "progress",
        {
            "message": f"🤖 Đang phân tích {len(articles_data)} điều khoản...",
            "index": 0,
            "total": total,
        },
    )

    batch_prompt = prompts.build_batch_risk_prompt(articles_data, expired_law_alerts)

    # Gộp tất cả law_chunks để trích xuất citations
    all_law_chunks: List[Dict] = []
    seen = set()
    for art in articles_data:
        for lc in art["law_chunks"]:
            key = lc.get("content", "")[:80]
            if key not in seen:
                seen.add(key)
                all_law_chunks.append(lc)

    RETRY_WAITS = [10, 15, 20, 30, 45, 60]
    raw_answer = ""
    for attempt in range(len(RETRY_WAITS) + 1):
        try:
            llm_result = llm_client.generate_grounded_response(
                query=batch_prompt,
                retrieved_chunks=all_law_chunks,
                threshold=0.0,  # Batch mode: không dùng threshold lọc, LLM đã có đủ context
            )
            # Kiểm tra rate limit
            ans = llm_result.get("answer", "")
            is_rate = llm_result.get("refusal") and any(
                k in ans.lower()
                for k in ("rate", "quota", "429", "quá tải", "hết hạn mức")
            )
            if not is_rate:
                raw_answer = ans
                break
            raise RuntimeError(f"Rate limit: {ans}")
        except Exception as e:
            if attempt < len(RETRY_WAITS):
                wait = RETRY_WAITS[attempt]
                logger.warning("[batch] Lỗi lần %d, chờ %ds: %s", attempt + 1, wait, e)
                yield (
                    "progress",
                    {
                        "message": f"⏳ Rate limit, thử lại sau {wait}s (lần {attempt + 1}/{len(RETRY_WAITS)})...",
                        "index": 0,
                        "total": total,
                    },
                )
                time.sleep(wait)
            else:
                logger.error("[batch] Hết retry: %s", e)
                raw_answer = ""

    # 5. Parse kết quả — tách theo ===DIEU_N_KET_QUA===
    import re

    # Primary parse: split produces ["preamble","1","text1","2","text2",...]
    parts = re.split(r"===DIEU_(\d+)_KET_QUA===", raw_answer, flags=re.IGNORECASE)
    parsed: Dict[int, str] = {}
    i = 1
    while i + 1 < len(parts):
        try:
            idx_num = int(parts[i])
            parsed[idx_num] = parts[i + 1].strip()
        except ValueError:
            pass
        i += 2

    # Fallback: dùng findall để bắt tất cả block kể cả khi LLM không xuống dòng
    # Tìm mọi cặp (số, nội dung) trong raw_answer
    if len(parsed) < len(articles_data):
        fallback_matches = re.findall(
            r"===DIEU_(\d+)_KET_QUA===(.*?)(?====DIEU_\d+_KET_QUA===|$)",
            raw_answer,
            flags=re.IGNORECASE | re.DOTALL,
        )
        for num_str, content in fallback_matches:
            try:
                num = int(num_str)
                if num not in parsed:
                    parsed[num] = content.strip()
            except ValueError:
                pass

    # 6. Yield kết quả từng Điều (parse xong là yield ngay)
    all_citations = llm_client.extract_citations_from_chunks(all_law_chunks)
    for seq, art in enumerate(articles_data, 1):
        risk_text = parsed.get(
            seq, "⚠️ Không trích xuất được đánh giá cho điều khoản này."
        )
        # Lọc citations thực sự được LLM đề cập trong đoạn đánh giá này
        used = [
            c
            for c in all_citations
            if c.get("article", "") and c["article"].lower() in risk_text.lower()
        ]
        item = {
            "dieu_khoan": art["label"],
            "noi_dung": art["content"],
            "rui_ro": risk_text,
            "can_cu": used,
        }
        risk_results.append(item)
        yield ("result", {"index": seq, "total": len(articles_data), **item})

    # 7. Đồng bộ Chatbot context
    if session_id:
        try:
            from modules.chatbot_qa import service as chatbot_service

            chatbot_service.attach_contract_context(
                session_id=session_id,
                contract_chunks=contract_chunks,
                risk_report=risk_results,
            )
        except Exception:
            logger.exception(
                "[stream] Không thể đồng bộ Chatbot session %s", session_id
            )

    yield (
        "done",
        {
            "expired_law_alerts": expired_law_alerts,
            "risk_results": risk_results,
            "contract_chunks": contract_chunks,
        },
    )
