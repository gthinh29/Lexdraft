"""
modules/risk_assessment/law_validity_checker.py

PRIVATE — Chỉ được import từ modules/risk_assessment/service.py.

Cơ chế kiểm tra hiệu lực văn bản pháp luật 3 tầng (Tiered Validation):

  Cấp 1 (100% tin cậy): Đối chiếu với danh mục kiểm duyệt thủ công `data/expired_laws.json`.
  Cấp 2 (~95% tin cậy): Trích xuất quan hệ thay thế từ "Điều khoản thi hành" của các
                         văn bản luật đã được nạp vào law_index (sẽ bổ sung sau khi có data).
  Cấp 3 (~80% tin cậy): Fallback — Hỏi LLM phán đoán dựa trên tri thức nội tại.

Phân cấp ưu tiên khi xung đột:
  Cấp 1 > Cấp 2 > Cấp 3

Mọi cảnh báo từ Cấp 3 sẽ được gắn nhãn "Cần xác minh" để người dùng không
nhầm lẫn với kết quả từ nguồn chính thức.
"""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Đường dẫn file cấu hình Cấp 1
# ---------------------------------------------------------------------------
_EXPIRED_LAWS_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "expired_laws.json"
)

# Cache bộ nhớ để không đọc file mỗi lần gọi
_expired_laws_cache: Optional[List[Dict[str, Any]]] = None


# ---------------------------------------------------------------------------
# Cấp 1 — Curated Rules (Danh mục kiểm duyệt sẵn)
# ---------------------------------------------------------------------------


def _load_expired_laws() -> List[Dict[str, Any]]:
    """Đọc và cache danh mục văn bản hết hiệu lực từ file JSON (Cấp 1)."""
    global _expired_laws_cache
    if _expired_laws_cache is not None:
        return _expired_laws_cache

    if not _EXPIRED_LAWS_PATH.exists():
        logger.warning(
            "Không tìm thấy file cấu hình expired_laws.json tại: %s. "
            "Cấp 1 sẽ không hoạt động.",
            _EXPIRED_LAWS_PATH,
        )
        _expired_laws_cache = []
        return _expired_laws_cache

    try:
        with open(_EXPIRED_LAWS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        _expired_laws_cache = data.get("expired_laws", [])
        logger.info(
            "Đã tải %d quy tắc văn bản hết hiệu lực (Cấp 1) từ %s.",
            len(_expired_laws_cache),
            _EXPIRED_LAWS_PATH,
        )
    except Exception as e:
        logger.exception("Lỗi khi đọc file expired_laws.json: %s", e)
        _expired_laws_cache = []

    return _expired_laws_cache


def _check_tier1(law_name: str) -> Optional[Dict[str, Any]]:
    """
    Cấp 1: Đối chiếu văn bản với danh mục kiểm duyệt (độ tin cậy 100%).

    Returns:
        Dict chứa thông tin vi phạm nếu phát hiện, None nếu không có trong danh mục.
    """
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


# ---------------------------------------------------------------------------
# Cấp 2 — Statutory Ground Truth (Trích xuất từ Điều khoản thi hành)
# ---------------------------------------------------------------------------

# Pattern nhận diện câu "bãi bỏ/thay thế/hết hiệu lực" trong văn bản luật
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


def _extract_repealed_laws_from_text(hiệu_luc_text: str) -> List[str]:
    """Trích xuất tên các văn bản bị bãi bỏ từ điều khoản thi hành (Cấp 2 - nội bộ)."""
    found = []
    for pattern in _REPEAL_PATTERNS:
        matches = pattern.findall(hiệu_luc_text)
        for m in matches:
            fragment = m if isinstance(m, str) else " ".join(m)
            fragment = fragment.strip()
            if fragment and len(fragment) > 10:
                found.append(fragment)
    return list(set(found))


def _check_tier2(
    law_name: str, law_index_chunks: Optional[List[Dict[str, Any]]] = None
) -> Optional[Dict[str, Any]]:
    """
    Cấp 2: Tìm trong các chunk "Điều khoản thi hành" của law_index xem văn bản
    có bị bãi bỏ không (độ tin cậy ~95%).

    Chú ý: Cần truyền vào `law_index_chunks` — danh sách các chunk đã được
    lọc sẵn với metadata `article` chứa từ khóa "hiệu lực" hoặc "thi hành".
    Nếu chưa có law_index hoặc chưa có dữ liệu, trả về None.

    Returns:
        Dict chứa thông tin vi phạm nếu phát hiện, None nếu không phát hiện.
    """
    if not law_index_chunks:
        logger.debug("Cấp 2: Không có law_index_chunks để kiểm tra.")
        return None

    law_name_lower = law_name.lower()

    for chunk in law_index_chunks:
        content = chunk.get("content", "")
        # Chỉ xét các chunk thuộc điều khoản "hiệu lực thi hành"
        article = str(chunk.get("metadata", {}).get("article", "")).lower()
        if not any(
            kw in article for kw in ["hiệu lực", "thi hành", "hết hiệu lực", "bãi bỏ"]
        ):
            if "hiệu lực" not in content.lower()[:200]:
                continue

        # Kiểm tra xem law_name có bị nhắc đến trong ngữ cảnh bãi bỏ/hết hiệu lực không
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


# ---------------------------------------------------------------------------
# Cấp 3 — LLM Fallback (Tri thức nội tại của AI)
# ---------------------------------------------------------------------------

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


def _check_tier3(law_name: str) -> Optional[Dict[str, Any]]:
    """
    Cấp 3: Hỏi LLM phán đoán hiệu lực văn bản dựa trên tri thức nội tại (độ tin cậy ~80%).

    Kết quả luôn được gắn nhãn "Cần xác minh" để người dùng không nhầm lẫn
    với kết quả từ nguồn chính thức.

    Returns:
        Dict chứa thông tin cảnh báo (gắn nhãn "Cần xác minh"), None nếu LLM không chắc.
    """
    from modules.shared.llm_client import GeminiClient

    try:
        client = GeminiClient()
        prompt = _LLM_FALLBACK_PROMPT.format(law_name=law_name)
        raw_response = client.generate_text(prompt)

        # Trích xuất JSON từ phản hồi LLM (đề phòng LLM thêm markdown ```json)
        json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if not json_match:
            logger.debug("Cấp 3: LLM không trả về JSON hợp lệ cho '%s'.", law_name)
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
    """
    Cấp 3 Batch: Hỏi LLM 1 lần với TẤT CẢ văn bản còn lại.
    N văn bản = 1 API call thay vì N calls.
    """
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


def extract_law_references(contract_text: str) -> List[str]:
    """
    Trích xuất danh sách tên văn bản pháp luật được dẫn chiếu trong hợp đồng.
    Tìm kiếm cả phần "Căn cứ..." ở đầu hợp đồng lẫn các dẫn chiếu nội tuyến.

    Args:
        contract_text: Toàn bộ nội dung hợp đồng dạng text.

    Returns:
        Danh sách tên văn bản (đã loại trùng, giữ thứ tự xuất hiện).
    """
    found = []
    seen = set()

    # Ưu tiên tìm cụm "Căn cứ ..." trước (độ chính xác cao nhất)
    for m in _LAW_REFERENCE_PATTERN.finditer(contract_text):
        ref = m.group(1).strip().rstrip(".,;:")
        if ref and ref not in seen:
            found.append(ref)
            seen.add(ref)

    # Bổ sung dẫn chiếu nội tuyến nếu cần (VD: "theo Điều 301 Luật Thương mại 2005...")
    for m in _INLINE_LAW_PATTERN.finditer(contract_text):
        ref = m.group(0).strip()
        if ref and ref not in seen and len(ref) > 10:
            found.append(ref)
            seen.add(ref)

    logger.debug("extract_law_references: Tìm thấy %d văn bản dẫn chiếu.", len(found))
    return found


# ---------------------------------------------------------------------------
# Hàm tổng hợp chính — Tiered Validation
# ---------------------------------------------------------------------------


def check_expired_laws(
    contract_text: str,
    law_index_chunks: Optional[List[Dict[str, Any]]] = None,
    enable_llm_fallback: bool = True,
) -> List[Dict[str, Any]]:
    """
    Kiểm tra toàn bộ văn bản pháp luật được dẫn chiếu trong hợp đồng theo cơ chế 3 tầng.

    Quy trình:
        1. Trích xuất danh sách văn bản dẫn chiếu từ hợp đồng.
        2. Với mỗi văn bản, lần lượt kiểm tra qua Cấp 1 → 2 → 3 (dừng ngay khi có kết quả).
        3. Tổng hợp danh sách cảnh báo có phân cấp độ tin cậy.

    Args:
        contract_text:      Toàn bộ nội dung hợp đồng dạng text.
        law_index_chunks:   (Tùy chọn) Các chunk từ law_index để kiểm tra Cấp 2.
                            Nên lọc sẵn các chunk có metadata liên quan "hiệu lực thi hành".
        enable_llm_fallback: Bật/tắt Cấp 3 (LLM). Tắt khi muốn tiết kiệm API quota.

    Returns:
        Danh sách cảnh báo, mỗi phần tử là một Dict với cấu trúc:
        {
            "source":            "tier1_curated" | "tier2_statutory" | "tier3_llm_fallback",
            "confidence":        "100%" | "~95%" | "~80%",
            "confidence_label":  Nhãn hiển thị cho người dùng,
            "law_ref":           Tên văn bản bị phát hiện trong hợp đồng,
            "status":            Trạng thái (Hết hiệu lực / Không tồn tại / ...),
            "expire_date":       Ngày hết hiệu lực (nếu có),
            "replaced_by":       Văn bản thay thế (nếu có),
            "note":              Ghi chú bổ sung,
        }
        Trả về danh sách rỗng nếu không phát hiện vấn đề gì.
    """
    law_refs = extract_law_references(contract_text)
    if not law_refs:
        logger.info("Không trích xuất được văn bản dẫn chiếu nào trong hợp đồng.")
        return []

    logger.info(
        "Bắt đầu kiểm tra hiệu lực %d văn bản dẫn chiếu (Tiered Validation)...",
        len(law_refs),
    )

    alerts: List[Dict[str, Any]] = []
    unresolved: List[str] = []  # Văn bản Cấp 1+2 không xử lý được → gửi batch cho Cấp 3

    for law_name in law_refs:
        # --- Cấp 1: Danh mục kiểm duyệt (Ground Truth tuyệt đối) ---
        result = _check_tier1(law_name)
        if result:
            logger.info(
                "Cấp 1 phát hiện vi phạm: '%s' → %s", law_name, result["status"]
            )
            alerts.append(result)
            continue

        # --- Cấp 2: Trích xuất từ Điều khoản thi hành của luật mới ---
        result = _check_tier2(law_name, law_index_chunks)
        if result:
            logger.info(
                "Cấp 2 phát hiện vi phạm: '%s' → %s", law_name, result["status"]
            )
            alerts.append(result)
            continue

        # Chưa có kết quả từ Cấp 1+2 → đưa vào danh sách chờ batch
        unresolved.append(law_name)

    # --- Cấp 3: Hỏi LLM 1 lần cho TẤT CẢ văn bản chưa giải quyết được ---
    if enable_llm_fallback and unresolved:
        logger.info("Cấp 3 batch: Hỏi LLM 1 lần cho %d văn bản...", len(unresolved))
        tier3_alerts = _check_tier3_batch(unresolved)
        alerts.extend(tier3_alerts)
        if tier3_alerts:
            for a in tier3_alerts:
                logger.info(
                    "Cấp 3 (AI) phát hiện: '%s' → %s", a["law_ref"], a["status"]
                )

    logger.info(
        "Hoàn tất kiểm tra hiệu lực: %d/%d văn bản có vấn đề.",
        len(alerts),
        len(law_refs),
    )
    return alerts
