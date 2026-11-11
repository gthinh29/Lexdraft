"""Client kết nối Google Gemini API kèm kiểm soát căn cứ pháp lý (Code Gatekeeper)."""

import logging
import os
import re
import time
from typing import Any, Dict, List, Optional

from config import Config

logger = logging.getLogger(__name__)

DEFAULT_LLM_MODEL = getattr(Config, "LLM_MODEL_NAME", "gemini-3.5-flash")
DEFAULT_SIMILARITY_THRESHOLD = getattr(Config, "SIMILARITY_THRESHOLD", 0.75)

_DEFAULT_REFUSAL = (
    "Hiện tại trong cơ sở dữ liệu pháp luật về hợp đồng dịch vụ của hệ thống chưa có quy định về vấn đề này. "
    "Bạn vui lòng tra cứu thêm các văn bản pháp luật chuyên ngành liên quan hoặc tham vấn chuyên gia pháp lý."
)


def _get_api_key() -> str:
    api_key = getattr(Config, "GEMINI_API_KEY", None) or os.environ.get(
        "GEMINI_API_KEY"
    )
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY chưa được cấu hình. Vui lòng thêm vào file .env hoặc biến môi trường."
        )
    return api_key


class GeminiClient:
    """Wrapper gọi Google Gemini API với cơ chế tự động thử lại khi gặp lỗi 429."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.2,
        thinking_budget: int = 0,
    ):
        self.api_key = _get_api_key()
        self.model_name = model_name or DEFAULT_LLM_MODEL
        self.temperature = temperature
        self.thinking_budget = thinking_budget
        self._init_client()

    def _init_client(self) -> None:
        try:
            from google import genai
            from google.genai import types

            self._client = genai.Client(api_key=self.api_key)
            self._is_new_sdk = True
            config_args: Dict[str, Any] = {
                "temperature": self.temperature,
                "top_p": 0.95,
            }
            if self.thinking_budget and self.thinking_budget > 0:
                try:
                    config_args["thinking_config"] = types.ThinkingConfig(
                        thinking_budget=self.thinking_budget
                    )
                except Exception:
                    pass
            self._config = types.GenerateContentConfig(**config_args)
        except ImportError:
            import google.generativeai as legacy_genai  # type: ignore

            legacy_genai.configure(api_key=self.api_key)
            self._is_new_sdk = False
            self._legacy_model = legacy_genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={"temperature": self.temperature, "top_p": 0.95},
            )

    def generate_text(
        self,
        prompt: str,
        max_retries: int = 4,
        base_delay: float = 2.0,
    ) -> str:
        """Gọi Gemini sinh văn bản với exponential backoff khi quá tải (429/503)."""
        last_exception = None
        transient_tokens = (
            "429",
            "503",
            "500",
            "502",
            "504",
            "quota",
            "resource_exhausted",
            "unavailable",
            "high demand",
            "overloaded",
            "timeout",
        )
        for attempt in range(max_retries):
            try:
                response = (
                    self._client.models.generate_content(
                        model=self.model_name, contents=prompt, config=self._config
                    )
                    if self._is_new_sdk
                    else self._legacy_model.generate_content(prompt)
                )
                return (
                    response.text.strip()
                    if response and getattr(response, "text", None)
                    else ""
                )
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()
                if not any(k in error_str for k in transient_tokens):
                    logger.error("Lỗi khi gọi Gemini generate_content: %s", e)
                    raise

                retry_match = re.search(
                    r"retry in (\d+(?:\.\d+)?)s", str(e), re.IGNORECASE
                )
                sleep_time = (
                    min(float(retry_match.group(1)) + 1.0, 45.0)
                    if retry_match
                    else base_delay * (2**attempt)
                )
                logger.warning(
                    "Gemini API tạm thời quá tải/rate limit. Chờ %.1fs (lần %d/%d)...",
                    sleep_time,
                    attempt + 1,
                    max_retries,
                )
                time.sleep(sleep_time)

        logger.error("Vượt quá số lần thử lại (%d): %s", max_retries, last_exception)
        if last_exception is not None and any(
            k in str(last_exception).lower()
            for k in ("503", "unavailable", "high demand", "overloaded")
        ):
            raise RuntimeError(
                "Máy chủ Gemini AI đang quá tải tạm thời (503 UNAVAILABLE). "
                "Vui lòng đợi vài giây rồi bấm thử lại."
            ) from last_exception
        raise RuntimeError(
            "Google Gemini API Free Tier Quota Exceeded (Lỗi 429: Vượt quá giới hạn gọi API). "
            "Vui lòng đợi khoảng 30-40 giây sau đó bấm thử lại."
        ) from last_exception


def extract_citations_from_chunks(
    retrieved_chunks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Trích xuất metadata chuẩn hóa từ danh sách chunks để tạo danh sách căn cứ trích dẫn."""
    citations = []
    seen = set()

    for chunk in retrieved_chunks:
        metadata = chunk.get("metadata", {})
        article = metadata.get("article") or metadata.get("article_number") or "N/A"
        law_name = metadata.get("law_name", "")
        law_number = metadata.get("law_number", "")
        vbhn_number = metadata.get("vbhn_number", "")

        if law_name and law_number:
            source_display = f"{law_name} số {law_number}"
            if vbhn_number:
                source_display += f" (VBHN {vbhn_number})"
        else:
            source_display = metadata.get("source") or metadata.get("doc_name") or "N/A"

        key = (str(article), str(source_display))
        if key not in seen:
            seen.add(key)
            citations.append(
                {
                    "article": str(article),
                    "source": str(source_display),
                    "raw_file": metadata.get("source", ""),
                    "title": metadata.get("title", ""),
                    "score": chunk.get("score"),
                }
            )

    return citations


def _filter_used_citations(
    raw_citations: List[Dict[str, Any]], answer: str
) -> List[Dict[str, Any]]:
    """Giữ lại các căn cứ thực sự được nhắc tới trong câu trả lời của LLM."""
    used = []
    for c in raw_citations:
        article = c.get("article", "")
        art_match = re.search(r"\d+", article)
        if art_match and re.search(rf"\b[Đđ]iều\s+{art_match.group()}\b", answer):
            used.append(c)
        elif article and article.lower() in answer.lower():
            used.append(c)
    return used


def _build_chunk_previews(
    chunks: Optional[List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Tạo danh sách xem trước chunk gọn nhẹ phục vụ RAG Inspector."""
    return [
        {
            "article": c.get("metadata", {}).get("article", "N/A"),
            "law_name": c.get("metadata", {}).get("law_name")
            or c.get("metadata", {}).get("source", "N/A"),
            "law_number": c.get("metadata", {}).get("law_number", ""),
            "vbhn_number": c.get("metadata", {}).get("vbhn_number", ""),
            "score": round(float(c["score"]), 4)
            if c.get("score") is not None
            else None,
            "content": c.get("content", ""),
        }
        for c in (chunks or [])
    ]


def _build_debug_trace(
    model: str,
    threshold: float,
    max_score: Optional[float],
    passed: bool,
    reason: str,
    previews: List[Dict[str, Any]],
    prompt: str,
    raw_response: str,
    filtered_citations: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Đóng gói dữ liệu truy vết cho White-Box RAG Inspector."""
    return {
        "model": model,
        "threshold": threshold,
        "max_similarity_score": round(float(max_score), 4)
        if max_score is not None
        else None,
        "gatekeeper_passed": passed,
        "gatekeeper_reason": reason,
        "retrieved_chunks_count": len(previews),
        "retrieved_chunks": previews,
        "final_prompt_sent_to_llm": prompt,
        "raw_llm_response": raw_response,
        "filtered_citations": filtered_citations,
    }


def _format_api_error(err: Exception) -> str:
    """Chuyển đổi ngoại lệ kỹ thuật thành thông báo thân thiện cho người dùng."""
    err_str = str(err)
    lower = err_str.lower()
    if "404" in err_str:
        return (
            "Mô hình AI hiện tại không khả dụng hoặc đã thay đổi phiên bản trên hệ thống Google Gemini. "
            "Hệ thống đã tự động ghi nhận để điều chỉnh."
        )
    if any(k in lower for k in ("503", "unavailable", "high demand", "overloaded")):
        return (
            "Máy chủ Gemini AI đang quá tải tạm thời (Lỗi 503 UNAVAILABLE). "
            "Vui lòng đợi vài giây rồi bấm thử lại."
        )
    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
        return "Hệ thống đang quá tải hoặc tạm thời hết hạn mức gọi AI (Rate Limit/Quota). Vui lòng đợi trong giây lát và thử lại."
    if "API_KEY" in err_str.upper() or "UNAUTHENTICATED" in err_str:
        return "Khóa API (GEMINI_API_KEY) không hợp lệ hoặc đã hết hạn. Vui lòng kiểm tra lại cấu hình."
    return "Đã xảy ra lỗi khi kết nối với mô hình AI. Vui lòng thử lại sau."


def generate_grounded_response(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
    threshold: Optional[float] = None,
    client: Optional[GeminiClient] = None,
    refusal_message: Optional[str] = None,
) -> Dict[str, Any]:
    """Sinh phản hồi được ràng buộc căn cứ pháp lý kèm kiểm tra ngưỡng Cosine (Gatekeeper)."""
    active_threshold = (
        threshold
        if threshold is not None
        else getattr(Config, "SIMILARITY_THRESHOLD", 0.75)
    )
    active_refusal = refusal_message or _DEFAULT_REFUSAL
    scores = [c.get("score") for c in retrieved_chunks if c.get("score") is not None]
    max_score = max(scores) if scores else None
    previews = _build_chunk_previews(retrieved_chunks)

    if not retrieved_chunks:
        return {
            "answer": active_refusal,
            "citations": [],
            "refusal": True,
            "debug_trace": _build_debug_trace(
                DEFAULT_LLM_MODEL,
                active_threshold,
                None,
                False,
                "Danh sách retrieved_chunks rỗng -> Chặn tại tầng Code Python (0 API call).",
                [],
                query,
                "[BỊ CHẶN BỞI CODE GATEKEEPER - KHÔNG GỌI GEMINI API]",
                [],
            ),
        }

    if max_score is not None and max_score < active_threshold:
        return {
            "answer": active_refusal,
            "citations": [],
            "refusal": True,
            "debug_trace": _build_debug_trace(
                DEFAULT_LLM_MODEL,
                active_threshold,
                max_score,
                False,
                f"Điểm tương đồng cao nhất ({max_score:.3f}) < Ngưỡng Gatekeeper ({active_threshold:.2f}) -> Chặn tại tầng Code Python (0 API call).",
                previews,
                query,
                "[BỊ CHẶN BỞI CODE GATEKEEPER - KHÔNG GỌI GEMINI API]",
                [],
            ),
        }

    raw_citations = extract_citations_from_chunks(retrieved_chunks)
    active_client = client or GeminiClient()

    try:
        answer = active_client.generate_text(query)
        used_citations = _filter_used_citations(raw_citations, answer)
        reason = (
            f"Pass Gatekeeper (max_score={max_score:.3f} >= threshold={active_threshold:.2f})"
            if max_score is not None
            else f"Pass Gatekeeper (threshold={active_threshold:.2f})"
        )
        return {
            "answer": answer,
            "citations": used_citations,
            "refusal": False,
            "debug_trace": _build_debug_trace(
                active_client.model_name,
                active_threshold,
                max_score,
                True,
                reason,
                previews,
                query,
                answer,
                used_citations,
            ),
        }
    except Exception as e:
        logger.exception("Lỗi khi gọi LLM sinh grounded response: %s", e)
        clean_err = _format_api_error(e)
        return {
            "answer": f"⚠️ **Lỗi hệ thống:** {clean_err}",
            "citations": [],
            "refusal": True,
            "debug_trace": _build_debug_trace(
                active_client.model_name,
                active_threshold,
                max_score,
                False,
                f"Lỗi khi gọi API LLM: {clean_err}",
                previews,
                query,
                f"ERROR: {e}",
                [],
            ),
        }
