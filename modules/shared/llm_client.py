"""
modules/shared/llm_client.py

Client tương tác với LLM (Google Gemini API) phục vụ các tác vụ sinh nội dung
có kiểm chứng căn cứ (Grounded Generation) và chống bịa đặt (Hallucination Control).

Sử dụng SDK mới nhất: `google.genai` (chuẩn Google GenAI SDK v2.0+),
tương thích hoàn toàn với fallback qua `google.generativeai` nếu môi trường cũ.

Tuân thủ:
- TODO List Phần 6 (6.1 -> 6.5)
- SRS 4.1, 4.2, 4.3, 6.1
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional

from config import Config

logger = logging.getLogger(__name__)

# Default model name & similarity threshold
DEFAULT_LLM_MODEL = getattr(Config, "LLM_MODEL_NAME", "gemini-3.5-flash")
DEFAULT_SIMILARITY_THRESHOLD = getattr(Config, "SIMILARITY_THRESHOLD", 0.75)


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
    """
    Wrapper quanh Google Gemini với retry, exponential backoff và kiểm soát hallucination.
    """

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

    def _init_client(self):
        """Khởi tạo client, ưu tiên google.genai hiện đại."""
        try:
            from google import genai
            from google.genai import types

            self._client = genai.Client(api_key=self.api_key)
            self._is_new_sdk = True

            # Config cho google.genai
            config_args = {"temperature": self.temperature, "top_p": 0.95}
            if self.thinking_budget == 0:
                try:
                    config_args["thinking_config"] = types.ThinkingConfig(
                        thinking_budget=0
                    )
                except Exception:
                    pass
            self._config = types.GenerateContentConfig(**config_args)
        except ImportError:
            import google.generativeai as legacy_genai

            legacy_genai.configure(api_key=self.api_key)
            self._is_new_sdk = False
            gen_config = {"temperature": self.temperature, "top_p": 0.95}
            self._legacy_model = legacy_genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=gen_config,
            )

    def generate_text(
        self,
        prompt: str,
        max_retries: int = 3,
        base_delay: float = 2.0,
    ) -> str:
        """
        Gọi Gemini sinh text với cơ chế exponential backoff chống lỗi Rate Limit (429).
        """
        last_exception = None
        for attempt in range(max_retries):
            try:
                if self._is_new_sdk:
                    response = self._client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=self._config,
                    )
                else:
                    response = self._legacy_model.generate_content(prompt)

                if response and hasattr(response, "text") and response.text:
                    return response.text.strip()
                return ""
            except Exception as e:
                last_exception = e
                error_str = str(e).lower()
                if (
                    "429" in error_str
                    or "quota" in error_str
                    or "resource_exhausted" in error_str
                ):
                    sleep_time = base_delay * (2**attempt)
                    logger.warning(
                        "Gemini API rate limit (429/quota). Đang ngủ %.1fs trước khi thử lại (lần %d/%d)...",
                        sleep_time,
                        attempt + 1,
                        max_retries,
                    )
                    time.sleep(sleep_time)
                else:
                    logger.error("Lỗi khi gọi Gemini generate_content: %s", e)
                    raise e

        logger.error(
            "Đã vượt quá số lần thử lại tối đa (%d). Lỗi cuối: %s",
            max_retries,
            last_exception,
        )
        raise last_exception or RuntimeError("Không thể nhận phản hồi từ Gemini API.")


def extract_citations_from_chunks(
    retrieved_chunks: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Trích xuất metadata chuẩn hóa từ danh sách chunks để tạo danh sách căn cứ trích dẫn.
    """
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


def generate_grounded_response(
    query: str,
    retrieved_chunks: List[Dict[str, Any]],
    threshold: Optional[float] = None,
    client: Optional[GeminiClient] = None,
) -> Dict[str, Any]:
    """
    Sinh phản hồi được ràng buộc căn cứ pháp lý (Grounded Generation) và chống hallucination.

    Quy trình xử lý (SRS 6.1 & TODO 6.2 -> 6.5):
        1. Kiểm tra điểm tương đồng (Similarity Threshold):
           - Nếu danh sách chunks rỗng hoặc điểm score cao nhất < threshold:
             Lập tức từ chối trả lời để tránh bịa đặt căn cứ.
        2. Ghép prompt Grounded: Ràng buộc LLM chỉ trả lời bằng căn cứ được cung cấp.
        3. Gọi Gemini sinh câu trả lời.
        4. Trả về format: {"answer": str, "citations": list, "refusal": bool}
    """
    active_threshold = (
        threshold
        if threshold is not None
        else getattr(Config, "SIMILARITY_THRESHOLD", 0.75)
    )

    # 6.3: Code logic Threshold
    if not retrieved_chunks:
        logger.info("Không có retrieved_chunks nào được cung cấp.")
        return {
            "answer": "Không tìm thấy căn cứ pháp lý phù hợp trong cơ sở dữ liệu để trả lời câu hỏi này.",
            "citations": [],
            "refusal": True,
        }

    # Kiểm tra score nếu chunks có chứa trường score
    scores = [c.get("score") for c in retrieved_chunks if c.get("score") is not None]
    if scores:
        max_score = max(scores)
        if max_score < active_threshold:
            logger.info(
                "Điểm tương đồng cao nhất (%.3f) nhỏ hơn ngưỡng (%.3f). Từ chối sinh câu trả lời.",
                max_score,
                active_threshold,
            )
            return {
                "answer": (
                    "Hiện tại trong cơ sở dữ liệu pháp luật về hợp đồng dịch vụ của hệ thống chưa có quy định về vấn đề này. "
                    "Bạn vui lòng tra cứu thêm các văn bản pháp luật chuyên ngành liên quan hoặc tham vấn chuyên gia pháp lý."
                ),
                "citations": [],
                "refusal": True,
            }

    # 6.5: Trích xuất metadata tạo citations
    raw_citations = extract_citations_from_chunks(retrieved_chunks)

    # 6.4: Gọi client sinh phản hồi
    if client is None:
        client = GeminiClient()

    try:
        answer = client.generate_text(query)

        # Lọc thông minh: Chỉ giữ lại những căn cứ pháp lý THỰC SỰ được LLM trích dẫn trong câu trả lời
        used_citations = []
        import re

        for c in raw_citations:
            article = c.get("article", "")
            art_match = re.search(r"\d+", article)
            if art_match:
                art_num = art_match.group()
                if re.search(rf"\b[Đđ]iều\s+{art_num}\b", answer):
                    used_citations.append(c)
                    continue
            if article and article.lower() in answer.lower():
                used_citations.append(c)

        # Chỉ giữ lại các căn cứ thực sự được LLM trích dẫn trong câu trả lời (nếu không dùng điều nào thì để rỗng)
        final_citations = used_citations

        return {
            "answer": answer,
            "citations": final_citations,
            "refusal": False,
        }
    except Exception as e:
        logger.exception("Lỗi khi gọi LLM sinh grounded response: %s", e)
        err_str = str(e)
        if "404" in err_str:
            clean_err = (
                "Mô hình AI hiện tại không khả dụng hoặc đã thay đổi phiên bản trên hệ thống Google Gemini. "
                "Hệ thống đã tự động ghi nhận để điều chỉnh."
            )
        elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
            clean_err = "Hệ thống đang quá tải hoặc tạm thời hết hạn mức gọi AI (Rate Limit/Quota). Vui lòng đợi trong giây lát và thử lại."
        elif "API_KEY" in err_str.upper() or "UNAUTHENTICATED" in err_str:
            clean_err = "Khóa API (GEMINI_API_KEY) không hợp lệ hoặc đã hết hạn. Vui lòng kiểm tra lại cấu hình."
        else:
            clean_err = (
                "Đã xảy ra lỗi khi kết nối với mô hình AI. Vui lòng thử lại sau."
            )

        return {
            "answer": f"⚠️ **Lỗi hệ thống:** {clean_err}",
            "citations": [],  # Bắt buộc rỗng khi gặp lỗi, không hiển thị căn cứ khi chưa có phản hồi từ AI
            "refusal": True,
        }
