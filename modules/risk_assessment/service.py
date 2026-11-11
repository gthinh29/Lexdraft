"""Điều phối pipeline phân tích rủi ro pháp lý và soạn thảo vá lỗi điều khoản (2-Stage RAG Pipeline)."""

import logging
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from modules.risk_assessment import law_validity_checker, prompts, retrieval
from modules.risk_assessment.redraft_builder import (
    build_redrafted_contract_text,
    clean_redraft_text,
    extract_redrafted_clause,
)
from modules.shared import chunking, document_reader, llm_client

logger = logging.getLogger(__name__)

__all__ = [
    "analyze_contract",
    "stream_analyze_contract",
    "extract_redrafted_clause",
    "build_redrafted_contract_text",
]

_SAFE_PHRASES = (
    "không phát hiện rủi ro",
    "không có rủi ro",
    "phù hợp quy định",
    "phù hợp với quy định",
    "không vi phạm",
    "không phát hiện vi phạm",
)


def _is_risky_text(risk_text: str) -> bool:
    """Kiểm tra đánh giá của LLM có xác định điều khoản bị rủi ro hay không."""
    if not risk_text:
        return False
    lower = risk_text.lower()
    if "không trích xuất được" in lower:
        return False
    return not any(p in lower for p in _SAFE_PHRASES)


def _load_contract_text(
    file_path_or_text: Union[str, Path], original_name: Optional[str] = None
) -> Tuple[str, str]:
    """Đọc nội dung hợp đồng từ đường dẫn file hoặc chuỗi văn bản thô."""
    path_obj = Path(str(file_path_or_text))
    if path_obj.exists() and path_obj.is_file():
        return original_name or path_obj.name, document_reader.read_document(path_obj)
    return original_name or "contract_input", str(file_path_or_text)


def _run_validity_precheck(
    text: str, enable_llm_fallback: bool
) -> List[Dict[str, Any]]:
    """Chạy kiểm tra hiệu lực văn bản 3 tầng trước khi rà soát từng điều khoản."""
    eff_chunks = retrieval.find_related_laws(
        "hiệu lực thi hành bãi bỏ thay thế hết hiệu lực", top_k=10
    )
    return law_validity_checker.check_expired_laws(
        contract_text=text,
        law_index_chunks=eff_chunks,
        enable_llm_fallback=enable_llm_fallback,
    )


def _filter_clause_citations(
    risk_text: str, law_chunks: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Chỉ giữ lại các căn cứ pháp lý thực sự được nhắc tới trong nhận xét rủi ro."""
    local_citations = llm_client.extract_citations_from_chunks(law_chunks)
    used = []
    for c in local_citations:
        article_lbl = c.get("article", "")
        art_match = re.search(r"\d+", article_lbl)
        if art_match and re.search(rf"\b[Đđ]iều\s+{art_match.group()}\b", risk_text):
            used.append(c)
        elif article_lbl and article_lbl.lower() in risk_text.lower():
            used.append(c)
    return used


def _parse_batch_markers(raw_answer: str, marker_prefix: str) -> Dict[int, str]:
    """Tách các khối `===<marker_prefix>_<N>_KET_QUA===` từ phản hồi batch của LLM."""
    if not raw_answer:
        return {}
    pattern = rf"==={re.escape(marker_prefix)}_(\d+)_KET_QUA==="
    parts = re.split(pattern, raw_answer, flags=re.IGNORECASE)
    parsed: Dict[int, str] = {}
    for i in range(1, len(parts) - 1, 2):
        try:
            parsed[int(parts[i])] = parts[i + 1].strip()
        except ValueError:
            pass

    fallback_matches = re.findall(
        rf"==={re.escape(marker_prefix)}_(\d+)_KET_QUA===(.*?)(?===={re.escape(marker_prefix)}_\d+_KET_QUA===|$)",
        raw_answer,
        flags=re.IGNORECASE | re.DOTALL,
    )
    for num_str, content in fallback_matches:
        try:
            parsed.setdefault(int(num_str), content.strip())
        except ValueError:
            pass
    return parsed


def _invoke_batch_llm_with_retry(
    prompt_text: str,
    retrieved_chunks: List[Dict[str, Any]],
    total: int,
    stage_label: str,
):
    """Gọi LLM theo lô kèm cơ chế tự động thử lại khi gặp giới hạn hạn mức (429)."""
    retry_waits = [10, 15, 20, 30, 45, 60]
    raw_answer = ""
    debug_trace = None
    for attempt in range(len(retry_waits) + 1):
        try:
            llm_result = llm_client.generate_grounded_response(
                query=prompt_text,
                retrieved_chunks=retrieved_chunks,
                threshold=0.0,
            )
            ans = llm_result.get("answer", "")
            debug_trace = llm_result.get("debug_trace")
            is_rate = llm_result.get("refusal") and any(
                k in ans.lower()
                for k in ("rate", "quota", "429", "quá tải", "hết hạn mức")
            )
            if not is_rate:
                raw_answer = ans
                break
            raise RuntimeError(f"Rate limit: {ans}")
        except Exception as e:
            if attempt < len(retry_waits):
                wait = retry_waits[attempt]
                logger.warning(
                    "[%s] Lỗi lần %d, chờ %ds: %s", stage_label, attempt + 1, wait, e
                )
                yield (
                    "progress",
                    {
                        "message": f"⏳ Rate limit ({stage_label}), thử lại sau {wait}s...",
                        "index": 0,
                        "total": total,
                    },
                )
                time.sleep(wait)
            else:
                logger.error("[%s] Hết retry: %s", stage_label, e)
                raw_answer = ""
    yield ("_llm_done", (raw_answer, debug_trace))


def _sync_chatbot_context(
    session_id: Optional[str],
    contract_chunks: List[Dict[str, Any]],
    risk_results: List[Dict[str, Any]],
) -> None:
    """Đồng bộ ngữ cảnh hợp đồng và báo cáo rủi ro sang phiên Chatbot Q&A."""
    if not session_id:
        return
    try:
        from modules.chatbot_qa import service as chatbot_service

        chatbot_service.attach_contract_context(
            session_id=session_id,
            contract_chunks=contract_chunks,
            risk_report=risk_results,
        )
    except Exception:
        logger.exception("Không thể đồng bộ sang Chatbot session %s", session_id)


def analyze_contract(
    file_path_or_text: Union[str, Path],
    session_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Phân tích rủi ro pháp lý tuần tự cho một hợp đồng (file hoặc chuỗi văn bản)."""
    source_name, text = _load_contract_text(file_path_or_text)
    if not text.strip():
        logger.warning("Nội dung hợp đồng rỗng, không thể phân tích rủi ro.")
        return {"expired_law_alerts": [], "risk_results": []}

    expired_law_alerts = _run_validity_precheck(text, enable_llm_fallback=True)
    contract_chunks = chunking.chunk_by_article(
        text=text, source_metadata={"source": source_name}
    )
    if not contract_chunks:
        return {"expired_law_alerts": expired_law_alerts, "risk_results": []}

    risk_results: List[Dict[str, Any]] = []
    for idx, chunk in enumerate(contract_chunks, 1):
        content = chunk.get("content", "").strip()
        if not content:
            continue
        article_label = chunk.get("metadata", {}).get("article") or f"Điều khoản {idx}"
        law_chunks = retrieval.find_related_laws(content, top_k=3)
        prompt = prompts.build_risk_prompt(
            dieu_khoan_text=content,
            law_context=law_chunks,
            expired_law_alerts=expired_law_alerts,
        )

        debug_trace = None
        try:
            llm_result = llm_client.generate_grounded_response(
                query=prompt, retrieved_chunks=law_chunks, threshold=0.35
            )
            risk_text = llm_result.get("answer", "")
            citations = llm_result.get("citations", [])
            debug_trace = llm_result.get("debug_trace")
        except Exception as e:
            logger.exception("Lỗi khi phân tích rủi ro cho %s: %s", article_label, e)
            risk_text = f"Không thể phân tích điều khoản này do lỗi hệ thống: {e}"
            citations = []

        risk_results.append(
            {
                "dieu_khoan": article_label,
                "noi_dung": content,
                "rui_ro": risk_text,
                "can_cu": citations,
                "redrafted_clause": extract_redrafted_clause(risk_text),
                "local_law_chunks": law_chunks,
                "debug_trace": debug_trace,
            }
        )
        if idx < len(contract_chunks):
            time.sleep(1.0)

    _sync_chatbot_context(session_id, contract_chunks, risk_results)
    return {"expired_law_alerts": expired_law_alerts, "risk_results": risk_results}


def stream_analyze_contract(
    file_path_or_text: Union[str, Path],
    session_id: Optional[str] = None,
    original_name: Optional[str] = None,
):
    """Phân tích rủi ro hợp đồng 2 pha theo luồng sự kiện (Stage 1: Rà soát -> Stage 2: Vá lỗi Redline)."""
    source_name, text = _load_contract_text(file_path_or_text, original_name)
    if not text.strip():
        yield (
            "error",
            {
                "message": "Không trích xuất được nội dung từ file. "
                "File có thể bị lỗi, được bảo vệ bằng mật khẩu, "
                "hoặc không chứa điều khoản hợp đồng nào.",
            },
        )
        return

    expired_law_alerts = _run_validity_precheck(text, enable_llm_fallback=False)
    contract_chunks = chunking.chunk_by_article(
        text=text, source_metadata={"source": source_name}
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

    yield (
        "progress",
        {"message": "🔍 Đang truy xuất căn cứ pháp lý...", "index": 0, "total": total},
    )
    articles_data = []
    for chunk in contract_chunks:
        content = chunk.get("content", "").strip()
        if not content:
            continue
        metadata = chunk.get("metadata", {})
        article_label = (
            metadata.get("article") or f"Điều khoản {len(articles_data) + 1}"
        )
        articles_data.append(
            {
                "label": article_label,
                "content": content,
                "law_chunks": retrieval.find_related_laws(content, top_k=3),
                "metadata": metadata,
            }
        )

    if not articles_data:
        yield ("done", {"expired_law_alerts": expired_law_alerts, "risk_results": []})
        return

    yield (
        "progress",
        {
            "message": f"🤖 Bước 1/2: Đang rà soát rủi ro {len(articles_data)} điều khoản...",
            "index": 0,
            "total": total,
        },
    )

    all_law_chunks: List[Dict] = []
    seen_chunks = set()
    for art in articles_data:
        for lc in art["law_chunks"]:
            key = lc.get("content", "")[:80]
            if key not in seen_chunks:
                seen_chunks.add(key)
                all_law_chunks.append(lc)

    raw_answer = ""
    batch_debug_trace = None
    batch_risk_prompt = prompts.build_batch_risk_prompt(
        articles_data, expired_law_alerts
    )
    for ev_type, payload in _invoke_batch_llm_with_retry(
        batch_risk_prompt, all_law_chunks, total, "batch_risk"
    ):
        if ev_type == "_llm_done":
            raw_answer, batch_debug_trace = payload
        else:
            yield (ev_type, payload)

    parsed = _parse_batch_markers(raw_answer, "DIEU")
    risky_for_redraft: List[Dict[str, Any]] = []
    per_article_eval: List[Dict[str, Any]] = []

    for seq, art in enumerate(articles_data, 1):
        risk_text = parsed.get(
            seq, "Không phát hiện rủi ro. Điều khoản phù hợp với quy định pháp luật."
        )
        used = _filter_clause_citations(risk_text, art.get("law_chunks", []))
        per_article_eval.append(
            {"seq": seq, "art": art, "risk_text": risk_text, "used": used}
        )
        if _is_risky_text(risk_text):
            risky_for_redraft.append(
                {
                    "seq": seq,
                    "label": art["label"],
                    "content": art["content"],
                    "risk_summary": risk_text,
                    "law_chunks": art.get("law_chunks", []),
                }
            )

    redrafted_map: Dict[int, str] = {}
    redraft_debug_trace = None
    if risky_for_redraft:
        yield (
            "progress",
            {
                "message": f"✍️ Bước 2/2: Đang soạn thảo vá lỗi cho {len(risky_for_redraft)} điều khoản rủi ro...",
                "index": 0,
                "total": total,
            },
        )
        batch_redraft_prompt = prompts.build_batch_redraft_prompt(
            risky_for_redraft, expired_law_alerts
        )
        redraft_raw = ""
        for ev_type, payload in _invoke_batch_llm_with_retry(
            batch_redraft_prompt, all_law_chunks, total, "batch_redraft"
        ):
            if ev_type == "_llm_done":
                redraft_raw, redraft_debug_trace = payload
            else:
                yield (ev_type, payload)
        redrafted_map = {
            k: clean_redraft_text(v)
            for k, v in _parse_batch_markers(redraft_raw, "REDRAFT").items()
        }

    risk_results: List[Dict[str, Any]] = []
    for entry in per_article_eval:
        seq = entry["seq"]
        art = entry["art"]
        risk_text = entry["risk_text"]
        item = {
            "dieu_khoan": art["label"],
            "noi_dung": art["content"],
            "rui_ro": risk_text,
            "can_cu": entry["used"],
            "redrafted_clause": redrafted_map.get(seq)
            or extract_redrafted_clause(risk_text),
            "local_law_chunks": art.get("law_chunks", []),
        }
        risk_results.append(item)
        yield ("result", {"index": seq, "total": len(articles_data), **item})

    _sync_chatbot_context(session_id, contract_chunks, risk_results)
    yield (
        "done",
        {
            "expired_law_alerts": expired_law_alerts,
            "risk_results": risk_results,
            "contract_chunks": contract_chunks,
            "debug_trace": batch_debug_trace,
            "redraft_debug_trace": redraft_debug_trace,
        },
    )
