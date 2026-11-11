"""Trích xuất metadata pháp lý từ phần mở đầu (preamble) của văn bản luật và mẫu hợp đồng."""

import logging
import re
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_MONTHS_VI = {
    "1": "01",
    "2": "02",
    "3": "03",
    "4": "04",
    "5": "05",
    "6": "06",
    "7": "07",
    "8": "08",
    "9": "09",
    "10": "10",
    "11": "11",
    "12": "12",
}

_LAW_NAME_MAP = {
    "DÂN SỰ": "Dân sự",
    "THƯƠNG MẠI": "Thương mại",
    "SỞ HỮU TRÍ TUỆ": "Sở hữu trí tuệ",
    "GIAO DỊCH ĐIỆN TỬ": "Giao dịch điện tử",
    "BẢO VỆ DỮ LIỆU CÁ NHÂN": "Bảo vệ dữ liệu cá nhân",
    "CHUYỂN ĐỔI SỐ": "Chuyển đổi số",
    "TRÍ TUỆ NHÂN TẠO": "Trí tuệ nhân tạo",
}


def _normalize_date(day: str, month: str, year: str) -> str:
    """Chuẩn hóa ngày tháng năm thành chuỗi dd/mm/yyyy."""
    return f"{int(day):02d}/{_MONTHS_VI.get(month, month)}/{year}"


def _extract_title_from_preamble(preamble: str) -> str:
    """Tìm tên Luật hoặc Bộ luật từ tiêu đề trong phần mở đầu."""
    title_match = re.search(
        r"[*#_\s]*((?:BỘ\s+)?LUẬT)[*#_\s]*\n+[*#_\s]*([^\n*#_]+)",
        preamble,
        re.IGNORECASE,
    )
    if not title_match:
        return ""
    prefix = "Bộ luật" if "BỘ" in title_match.group(1).strip().upper() else "Luật"
    clean_name = re.sub(r"[*#_]", "", title_match.group(2).strip()).strip()
    normalized = _LAW_NAME_MAP.get(clean_name.upper(), clean_name.title())
    return f"{prefix} {normalized}"


def _populate_vbhn_fields(result: Dict[str, Any], preamble: str, filename: str) -> None:
    """Bổ sung thông tin số hiệu VBHN, năm hợp nhất và ngày ký xác thực cho Văn bản hợp nhất."""
    year_match = re.search(r"(\d{4})\.md$", filename, re.IGNORECASE)
    if year_match:
        result["consolidated_year"] = year_match.group(1)
    elif result["issued_date"]:
        result["consolidated_year"] = result["issued_date"].split("/")[-1]

    vbhn_num = re.search(r"Số:\s*(\d+/VBHN-[A-Z]+)", preamble, re.IGNORECASE)
    if vbhn_num:
        result["vbhn_number"] = vbhn_num.group(1).strip()

    vbhn_date = re.search(
        r"Hà\s+Nội,\s+ngày\s+(\d+)\s+tháng\s+(\d+)\s+năm\s+(\d+)",
        preamble,
        re.IGNORECASE,
    )
    if vbhn_date:
        result["vbhn_date"] = _normalize_date(
            vbhn_date.group(1), vbhn_date.group(2), vbhn_date.group(3)
        )


def extract_law_header(text: str, filename: str = "") -> Dict[str, Any]:
    """Trích xuất metadata pháp lý từ 80 dòng mở đầu của văn bản luật hoặc VBHN."""
    preamble = "\n".join(text.splitlines()[:80])
    result: Dict[str, Any] = {
        "law_name": "",
        "law_number": "",
        "issued_date": "",
        "effective_date": "",
        "is_consolidated": filename.upper().startswith("VBHN"),
        "consolidated_year": "",
        "latest_amendment": "",
        "amended_by": [],
        "status": "Còn hiệu lực",
    }

    vbhn_main = re.search(
        r"(Luật[^\n]{3,60}?)\s+số\s+(\d+/\d+/QH\d+)\s+ngày\s+(\d+)\s+tháng\s+(\d+)\s+năm\s+(\d+)"
        r".*?có hiệu lực kể từ ngày\s+(\d+)\s+tháng\s+(\d+)\s+năm\s+(\d+)",
        preamble,
        re.DOTALL,
    )
    if vbhn_main:
        result["law_name"] = vbhn_main.group(1).strip()
        result["law_number"] = vbhn_main.group(2)
        result["issued_date"] = _normalize_date(
            vbhn_main.group(3), vbhn_main.group(4), vbhn_main.group(5)
        )
        result["effective_date"] = _normalize_date(
            vbhn_main.group(6), vbhn_main.group(7), vbhn_main.group(8)
        )

    if not result["law_number"]:
        law_num = re.search(r"Luật số[:\s]+([\d/A-Z]+)", preamble, re.IGNORECASE)
        if law_num:
            result["law_number"] = law_num.group(1).strip()

    if not result["issued_date"]:
        date_match = re.search(r"ngày\s+(\d+)\s+tháng\s+(\d+)\s+năm\s+(\d+)", preamble)
        if date_match:
            result["issued_date"] = _normalize_date(
                date_match.group(1), date_match.group(2), date_match.group(3)
            )
        else:
            dash_date = re.search(r"[Nn]gày\s+(\d{1,2})-(\d{1,2})-(\d{4})", preamble)
            if dash_date:
                result["issued_date"] = _normalize_date(
                    dash_date.group(1), dash_date.group(2), dash_date.group(3)
                )

    if not result["law_name"]:
        result["law_name"] = _extract_title_from_preamble(preamble)

    if not result["effective_date"]:
        eff_match = re.search(
            r"Luật này có hiệu lực thi hành từ ngày\s+(\d+)\s+tháng\s+(\d+)\s+năm\s+(\d+)",
            text,
            re.IGNORECASE,
        )
        if eff_match:
            result["effective_date"] = _normalize_date(
                eff_match.group(1), eff_match.group(2), eff_match.group(3)
            )

    amended_match = re.search(
        r"(?:sửa đổi(?:,\s*bổ sung)?\s+bởi\s*:?)(.*?)(?=Căn cứ|Quốc hội ban hành|$)",
        preamble,
        re.DOTALL | re.IGNORECASE,
    )
    if amended_match:
        amended_numbers = re.findall(r"\b(\d+/\d+/QH\d+)\b", amended_match.group(1))
        result["amended_by"] = [n for n in amended_numbers if n != result["law_number"]]
    if result["amended_by"]:
        result["latest_amendment"] = result["amended_by"][-1]

    if result["is_consolidated"]:
        _populate_vbhn_fields(result, preamble, filename)

    return result


def extract_template_header(text: str, filename: str = "") -> Dict[str, Any]:
    """Trích xuất tên mẫu hợp đồng, căn cứ pháp lý và tình trạng hiệu lực từ phần mở đầu."""
    parts = re.split(r"(?i)\n(?:#+\s*)?(?:\*{1,2})?Điều\s+1\b", text, maxsplit=1)
    preamble = parts[0] if len(parts) > 1 else text[:3000]

    name_match = re.search(r"(?:#+\s*)?(HỢP ĐỒNG\s+[^\n]+)", preamble, re.IGNORECASE)
    if name_match:
        raw_name = name_match.group(1).strip("#* _").strip()
        tpl_name = " ".join(w.capitalize() for w in raw_name.split())
    else:
        tpl_name = filename.replace(".md", "").replace("_", " ").title()

    legal_bases: List[str] = []
    for line in preamble.splitlines():
        clean_l = re.sub(r"^[\s\-_*\\#]+", "", line).strip()
        clean_l = re.sub(r"[\s;_\.]+$", "", clean_l)
        if re.match(
            r"^Căn cứ\s+(vào\s+)?(Bộ luật|Luật|Nghị định|Thông tư)",
            clean_l,
            re.IGNORECASE,
        ):
            legal_bases.append(clean_l)

    expired_alerts: List[Dict[str, Any]] = []
    try:
        from modules.risk_assessment.law_validity_checker import check_expired_laws

        expired_alerts = check_expired_laws(preamble, enable_llm_fallback=False)
    except Exception as e:
        logger.warning("Không thể kiểm tra hiệu lực căn cứ mẫu hợp đồng: %s", e)

    has_expired = len(expired_alerts) > 0
    if has_expired:
        bad_laws = [a.get("law_ref", "") for a in expired_alerts]
        validity_status = f"Cảnh báo: Căn cứ hết hiệu lực ({', '.join(bad_laws)})"
    else:
        validity_status = "Chuẩn căn cứ (Tất cả văn bản còn hiệu lực)"

    return {
        "doc_type": "template",
        "template_name": tpl_name,
        "legal_bases": legal_bases,
        "basis_validity": validity_status,
        "has_expired_basis": has_expired,
        "expired_alerts": expired_alerts,
    }
