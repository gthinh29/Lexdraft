"""Kiểm tra hiệu lực văn bản pháp luật được dẫn chiếu trong hợp đồng theo cơ chế 3 tầng (Tiered Validation)."""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_EXPIRED_LAWS_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "expired_laws.json"
)
_expired_laws_cache: Optional[List[Dict[str, Any]]] = None

_REPEAL_PATTERNS = [
    re.compile(
        r"(?:bãi bỏ|thay thế|hết hiệu lực|không còn hiệu lực).{0,100}?"
        r"(Luật|Nghị định|Thông tư|Quyết định|Pháp lệnh)\s+[^\.,;]{5,80}",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(
        r"(Luật|Nghị định|Thông tư|Quyết định|Pháp lệnh)\s+[^\.,;]{5,80}"
        r".{0,50}?(?:hết hiệu lực|bị bãi bỏ|được thay thế)",
        re.IGNORECASE | re.DOTALL,
    ),
]

_LAW_REFERENCE_PATTERN = re.compile(
    r"(?:Căn cứ|Theo|Dựa trên|Phù hợp với|Tuân thủ)\s+"
    r"((?:Luật|Bộ luật|Nghị định|Thông tư|Quyết định|Pháp lệnh|Công văn)"
    r"[^;,\n\.]{5,120})",
    re.IGNORECASE,
)

_INLINE_LAW_PATTERN = re.compile(
    r"\b(?:Luật|Bộ luật|Nghị định|Thông tư|Quyết định|Pháp lệnh)"
    r"\s+[A-ZÀ-Ỹa-zà-ỹ\s]+(?:\d{4}|\d{2,3}/\d{4}/\w+)"
    r"(?:\s+số\s+[\w/]+)?",
    re.UNICODE,
)

_LLM_FALLBACK_PROMPT = """Bạn là chuyên gia pháp lý Việt Nam.
Nhiệm vụ: Xác định xem văn bản pháp luật sau đây có còn hiệu lực tại thời điểm hiện tại không.

Văn bản cần kiểm tra: "{law_name}"

Hãy trả lời theo đúng định dạng JSON sau (không thêm bất kỳ nội dung nào khác):
{{
  "is_expired": true/false,
  "status": "Hết hiệu lực" hoặc "Còn hiệu lực" hoặc "Không xác định",
  "replaced_by": "Tên văn bản thay thế (nếu có)" hoặc null,
  "reason": "Lý do ngắn gọn (1-2 câu)"
}}

Nếu không chắc chắn, hãy đặt is_expired=false và status="Không xác định".
TUYỆT ĐỐI không bịa đặt số hiệu hay tên văn bản không có thực."""


def _load_expired_laws() -> List[Dict[str, Any]]:
    """Đọc và lưu bộ nhớ đệm danh mục văn bản hết hiệu lực từ expired_laws.json."""
    global _expired_laws_cache
    if _expired_laws_cache is not None:
        return _expired_laws_cache

    if not _EXPIRED_LAWS_PATH.exists():
        logger.warning(
            "Không tìm thấy file cấu hình expired_laws.json tại: %s.",
            _EXPIRED_LAWS_PATH,
        )
        _expired_laws_cache = []
        return _expired_laws_cache

    try:
        with open(_EXPIRED_LAWS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        _expired_laws_cache = data.get("expired_laws", [])
    except Exception as e:
        logger.exception("Lỗi khi đọc file expired_laws.json: %s", e)
        _expired_laws_cache = []

    return _expired_laws_cache


def _check_tier1(law_name: str) -> Optional[Dict[str, Any]]:
    """Cấp 1: Đối chiếu văn bản với danh mục kiểm duyệt (độ tin cậy 100%)."""
    expired_laws = _load_expired_laws()
    law_name_lower = law_name.lower()

    for entry in expired_laws:
        for keyword in entry.get("keywords", []):
            if keyword.lower() in law_name_lower:
                return {
                    "source": "tier1_curated",
                    "confidence": "100%",
                    "confidence_label": "🟢 Xác định (nguồn kiểm duyệt)",
                    "law_ref": law_name,
                    "status": entry.get("status", "Hết hiệu lực"),
                    "expire_date": entry.get("expire_date"),
                    "replaced_by": entry.get("replaced_by"),
                    "note": entry.get("note", ""),
                }
    return None


def _extract_repealed_laws_from_text(hieu_luc_text: str) -> List[str]:
    """Trích xuất tên các văn bản bị bãi bỏ từ điều khoản thi hành."""
    found = []
    for pattern in _REPEAL_PATTERNS:
        matches = pattern.findall(hieu_luc_text)
        for m in matches:
            fragment = m if isinstance(m, str) else " ".join(m)
            fragment = fragment.strip()
            if fragment and len(fragment) > 10:
                found.append(fragment)
    return list(set(found))


def _check_tier2(
    law_name: str, law_index_chunks: Optional[List[Dict[str, Any]]] = None
) -> Optional[Dict[str, Any]]:
    """Cấp 2: Tìm trong các chunk điều khoản thi hành của law_index xem văn bản có bị bãi bỏ không."""
    if not law_index_chunks:
        return None

    law_name_lower = law_name.lower()
    for chunk in law_index_chunks:
        content = chunk.get("content", "")
        article = str(chunk.get("metadata", {}).get("article", "")).lower()
        if not any(
            kw in article for kw in ["hiệu lực", "thi hành", "hết hiệu lực", "bãi bỏ"]
        ):
            if "hiệu lực" not in content.lower()[:200]:
                continue

        if law_name_lower[:20] in content.lower():
            repealed = _extract_repealed_laws_from_text(content)
            if repealed:
                meta = chunk.get("metadata", {})
                return {
                    "source": "tier2_statutory",
                    "confidence": "~95%",
                    "confidence_label": "🔵 Rất cao (trích từ văn bản luật)",
                    "law_ref": law_name,
                    "status": "Có dấu hiệu hết hiệu lực",
                    "expire_date": None,
                    "replaced_by": f"Xem: {meta.get('source', 'Văn bản luật mới trong hệ thống')}",
                    "note": f"Phát hiện từ điều khoản thi hành của: {meta.get('source', 'N/A')}",
                }

    return None


def _check_tier3(law_name: str) -> Optional[Dict[str, Any]]:
    """Cấp 3: Hỏi LLM phán đoán hiệu lực văn bản đơn lẻ."""
    from modules.shared.llm_client import GeminiClient

    try:
        client = GeminiClient()
        prompt = _LLM_FALLBACK_PROMPT.format(law_name=law_name)
        raw_response = client.generate_text(prompt)
        json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if not json_match:
            return None

        result = json.loads(json_match.group())
        if (
            result.get("is_expired") is True
            and result.get("status") != "Không xác định"
        ):
            return {
                "source": "tier3_llm_fallback",
                "confidence": "~80%",
                "confidence_label": "🟡 Cần xác minh (suy luận của AI)",
                "law_ref": law_name,
                "status": result.get("status", "Có thể hết hiệu lực"),
                "expire_date": None,
                "replaced_by": result.get("replaced_by"),
                "note": f"AI nhận định: {result.get('reason', '')}. ⚠️ Đây là suy luận của AI, vui lòng xác minh lại với nguồn chính thức.",
            }
    except Exception as e:
        logger.warning(
            "Cấp 3: Lỗi khi hỏi LLM về hiệu lực văn bản '%s': %s", law_name, e
        )

    return None


def _check_tier3_batch(law_names: List[str]) -> List[Dict[str, Any]]:
    """Cấp 3 Batch: Kiểm tra hiệu lực đồng thời nhiều văn bản trong 1 lần gọi LLM."""
    if not law_names:
        return []

    from modules.shared.llm_client import GeminiClient

    law_list_str = "\n".join(f'{i+1}. "{name}"' for i, name in enumerate(law_names))
    prompt = f"""Bạn là chuyên gia pháp lý Việt Nam.
Xác định xem các văn bản pháp luật sau có còn hiệu lực không.

{law_list_str}

Trả lời mảng JSON (không thêm nội dung khác):
[
  {{"index": 1, "is_expired": true/false, "status": "Hết hiệu lực"|"Còn hiệu lực"|"Không xác định", "replaced_by": null, "reason": "..."}}
]
Nếu không chắc đặt is_expired=false. Không bịa số hiệu văn bản."""

    try:
        client = GeminiClient()
        raw = client.generate_text(prompt)
        json_match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not json_match:
            return []
        results = json.loads(json_match.group())
        alerts = []
        for item in results:
            if (
                item.get("is_expired") is True
                and item.get("status") != "Không xác định"
            ):
                idx = item.get("index", 1) - 1
                law_ref = law_names[idx] if 0 <= idx < len(law_names) else "N/A"
                alerts.append(
                    {
                        "source": "tier3_llm_fallback",
                        "confidence": "~80%",
                        "confidence_label": "🟡 Cần xác minh (suy luận của AI)",
                        "law_ref": law_ref,
                        "status": item.get("status", "Có thể hết hiệu lực"),
                        "expire_date": None,
                        "replaced_by": item.get("replaced_by"),
                        "note": f"AI nhận định: {item.get('reason', '')}. ⚠️ Vui lòng xác minh lại.",
                    }
                )
        return alerts
    except Exception as e:
        logger.warning("Cấp 3 batch: Lỗi khi hỏi LLM: %s", e)
        return []


def extract_law_references(contract_text: str) -> List[str]:
    """Trích xuất danh sách tên văn bản pháp luật được dẫn chiếu trong hợp đồng."""
    found = []
    seen = set()

    for m in _LAW_REFERENCE_PATTERN.finditer(contract_text):
        ref = m.group(1).strip().rstrip(".,;:")
        if ref and ref not in seen:
            found.append(ref)
            seen.add(ref)

    for m in _INLINE_LAW_PATTERN.finditer(contract_text):
        ref = m.group(0).strip()
        if ref and ref not in seen and len(ref) > 10:
            found.append(ref)
            seen.add(ref)

    return found


def check_expired_laws(
    contract_text: str,
    law_index_chunks: Optional[List[Dict[str, Any]]] = None,
    enable_llm_fallback: bool = True,
) -> List[Dict[str, Any]]:
    """Kiểm tra toàn bộ văn bản pháp luật dẫn chiếu trong hợp đồng theo cơ chế 3 tầng."""
    law_refs = extract_law_references(contract_text)
    if not law_refs:
        return []

    alerts: List[Dict[str, Any]] = []
    unresolved: List[str] = []

    for law_name in law_refs:
        result = _check_tier1(law_name)
        if result:
            alerts.append(result)
            continue

        result = _check_tier2(law_name, law_index_chunks)
        if result:
            alerts.append(result)
            continue

        unresolved.append(law_name)

    if enable_llm_fallback and unresolved:
        alerts.extend(_check_tier3_batch(unresolved))

    return alerts
