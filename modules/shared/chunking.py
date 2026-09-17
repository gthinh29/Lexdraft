"""
modules/shared/chunking.py

Module dùng chung: chia văn bản pháp lý / hợp đồng thành các chunk theo
đơn vị "Điều" (structure-aware chunking), đúng theo SRS Chương 5.2.

Không dùng Fixed-size / Recursive / Semantic chunking vì văn bản luật
và hợp đồng đã có ranh giới cấu trúc rõ ràng theo Điều/Khoản.
"""

import logging
import re
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Hàm parse metadata pháp lý từ phần mở đầu (preamble) của văn bản luật.
# Hỗ trợ 2 định dạng:
#   1. Luật thường:  "Luật số: 91/2015/QH13  Hà Nội, ngày 24 tháng 11 năm 2015"
#   2. VBHN:         "Luật X số YYY ngày ... có hiệu lực kể từ ngày ... được sửa đổi bởi:"
# ---------------------------------------------------------------------------

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


def _normalize_date(day: str, month: str, year: str) -> str:
    """Chuẩn hóa ngày tháng năm thành chuỗi dd/mm/yyyy."""
    return f"{int(day):02d}/{_MONTHS_VI.get(month, month)}/{year}"


def extract_law_header(text: str, filename: str = "") -> Dict[str, Any]:
    """
    Parse phần mở đầu (preamble) của văn bản pháp luật để trích xuất metadata.

    Args:
        text: toàn bộ nội dung plain-text của file luật.
        filename: tên file (dùng để phát hiện VBHN qua tiền tố 'VBHN_').

    Returns:
        Dict chứa các trường metadata pháp lý:
        {
            "law_name": str,               # "Luật Sở hữu trí tuệ"
            "law_number": str,             # "50/2005/QH11"
            "issued_date": str,            # "29/11/2005"
            "effective_date": str,         # "01/07/2006"
            "is_consolidated": bool,       # True nếu là VBHN
            "consolidated_year": str,      # "2026" (năm ban hành VBHN)
            "latest_amendment": str,       # "131/2025/QH15" (luật sửa đổi mới nhất)
            "amended_by": List[str],       # ["36/2009/QH12", "07/2022/QH15", ...]
            "status": str,                 # "Còn hiệu lực"
        }
    """
    # Chỉ parse trong 80 dòng đầu (preamble)
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

    # --- Định dạng VBHN ---
    # VD: "Luật Sở hữu trí tuệ số 50/2005/QH11 ngày 29 tháng 11 năm 2005
    #      của Quốc hội, có hiệu lực kể từ ngày 01 tháng 7 năm 2006"
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

    # --- Định dạng luật thường ---
    # VD: "Luật số: 91/2015/QH13  Hà Nội, ngày 24 tháng 11 năm 2015"
    if not result["law_number"]:
        law_num = re.search(
            r"Luật số[:\s]+([\d/A-Z]+)",
            preamble,
            re.IGNORECASE,
        )
        if law_num:
            result["law_number"] = law_num.group(1).strip()

    if not result["issued_date"]:
        date_match = re.search(
            r"ngày\s+(\d+)\s+tháng\s+(\d+)\s+năm\s+(\d+)",
            preamble,
        )
        if date_match:
            result["issued_date"] = _normalize_date(
                date_match.group(1), date_match.group(2), date_match.group(3)
            )
        else:
            # Fallback: dạng "Ngày DD-MM-YYYY" (hay gặp ở file từ Công báo)
            dash_date = re.search(r"[Nn]gày\s+(\d{1,2})-(\d{1,2})-(\d{4})", preamble)
            if dash_date:
                result["issued_date"] = _normalize_date(
                    dash_date.group(1), dash_date.group(2), dash_date.group(3)
                )

    # Lấy tên luật từ tiêu đề (dòng LUẬT / BỘ LUẬT + dòng tiếp theo)
    if not result["law_name"]:
        title_match = re.search(
            r"[*#_\s]*(?:BỘ\s+)?LUẬT[*#_\s]*\n+[*#_\s]*([^\n*#_]+)",
            preamble,
            re.IGNORECASE,
        )
        if title_match:
            clean_name = title_match.group(1).strip()
            clean_name = re.sub(r"[*#_]", "", clean_name).strip()
            result["law_name"] = "Luật " + clean_name.title()

    # Hiệu lực nếu chưa có: tìm Điều hiệu lực thi hành trong toàn bộ văn bản
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

    # --- Danh sách văn bản sửa đổi (cho VBHN) ---
    # Chỉ lấy từ phần "được sửa đổi, bổ sung bởi:" trong preamble
    # Tìm đoạn sau cụm "sửa đổi, bổ sung bởi" hoặc "sửa đổi bởi"
    amended_section_match = re.search(
        r"(?:sửa đổi(?:,\s*bổ sung)?\s+bởi\s*:?)(.*?)(?=Căn cứ|Quốc hội ban hành|$)",
        preamble,
        re.DOTALL | re.IGNORECASE,
    )
    if amended_section_match:
        amended_section = amended_section_match.group(1)
        amended_numbers = re.findall(r"\b(\d+/\d+/QH\d+)\b", amended_section)
        result["amended_by"] = [n for n in amended_numbers if n != result["law_number"]]
    else:
        result["amended_by"] = []

    if result["amended_by"]:
        result["latest_amendment"] = result["amended_by"][-1]

    # --- Năm ban hành VBHN (từ tên file hoặc header VBHN) ---
    if result["is_consolidated"]:
        year_match = re.search(r"(\d{4})\.md$", filename, re.IGNORECASE)
        if year_match:
            result["consolidated_year"] = year_match.group(1)
        elif result["issued_date"]:
            result["consolidated_year"] = result["issued_date"].split("/")[-1]

        # Trích xuất số hiệu VBHN (VD: "Số: 113/VBHN-VPQH")
        vbhn_num = re.search(r"Số:\s*(\d+/VBHN-[A-Z]+)", preamble, re.IGNORECASE)
        if vbhn_num:
            result["vbhn_number"] = vbhn_num.group(1).strip()

        # Trích xuất ngày ký xác thực VBHN (VD: "Hà Nội, ngày 27 tháng 8 năm 2025")
        vbhn_date = re.search(
            r"Hà\s+Nội,\s+ngày\s+(\d+)\s+tháng\s+(\d+)\s+năm\s+(\d+)",
            preamble,
            re.IGNORECASE,
        )
        if vbhn_date:
            result["vbhn_date"] = _normalize_date(
                vbhn_date.group(1), vbhn_date.group(2), vbhn_date.group(3)
            )

    return result


def extract_template_header(text: str, filename: str = "") -> Dict[str, Any]:
    """
    Parse phần mở đầu của mẫu hợp đồng để trích xuất metadata:
    - doc_type: "template"
    - template_name: tên loại hợp đồng (vd: "Hợp đồng dịch vụ thiết kế website")
    - legal_bases: danh sách các văn bản luật căn cứ
    - basis_validity: trạng thái hiệu lực ("Chuẩn căn cứ" hoặc cảnh báo)
    - has_expired_basis: bool
    - expired_alerts: danh sách cảnh báo nếu có căn cứ hết hiệu lực
    """
    # Lấy phần mở đầu trước Điều 1
    parts = re.split(r"(?i)\n(?:#+\s*)?(?:\*{1,2})?Điều\s+1\b", text, maxsplit=1)
    preamble = parts[0] if len(parts) > 1 else text[:3000]

    # 1. Tìm tên hợp đồng
    name_match = re.search(r"(?:#+\s*)?(HỢP ĐỒNG\s+[^\n]+)", preamble, re.IGNORECASE)
    if name_match:
        raw_name = name_match.group(1).strip("#* _").strip()
        tpl_name = " ".join([w.capitalize() for w in raw_name.split()])
    else:
        tpl_name = filename.replace(".md", "").replace("_", " ").title()

    # 2. Trích xuất các dòng căn cứ pháp luật
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

    # 3. Kiểm tra tính chuẩn xác/hiệu lực của các căn cứ bằng Tiered Validation
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


logger = logging.getLogger(__name__)

# Nhãn dùng cho các đoạn không xác định được số Điều cụ thể (Phần 3.6).
FALLBACK_ARTICLE_LABEL = "Quy định chung"

# Regex nhận diện tiêu đề Điều ở đầu dòng (hỗ trợ Markdown header #, bold **, hoặc plain text)
# Neo bằng ^ (?m) để TRÁNH bắt nhầm các câu trích dẫn nội tuyến ở giữa câu (vd: 'theo Điều 37...')
ARTICLE_HEADER_PATTERN = re.compile(
    r"(?m)^(?:#{1,4}\s*)?(?:\*{1,2})?Điều\s+(\d+)[.:\s]?(.*?)$",
    re.IGNORECASE,
)


def chunk_by_article(
    text: str,
    source_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Chia văn bản thành các chunk theo từng "Điều".

    Args:
        text: text thô (đã đọc từ document_reader.read_document).
        source_metadata: metadata gốc của văn bản, vd:
            {"source": "BoLuatDanSu2015.pdf"}
            Sẽ được merge vào metadata của từng chunk.

    Returns:
        Danh sách dict theo format:
        [
            {
                "content": "Điều 1. Nội dung...",
                "metadata": {"source": "...", "article": "Điều 1"}
            },
            ...
        ]

        Fallback: nếu văn bản không chứa cấu trúc 'Điều' ở đầu dòng,
        toàn bộ text được trả về như MỘT chunk duy nhất với "article": "Quy định chung".
    """
    source_metadata = dict(source_metadata) if source_metadata else {}

    if not text or not text.strip():
        logger.warning(
            "chunk_by_article nhận text rỗng (source=%s) - trả về mảng rỗng.",
            source_metadata.get("source", "unknown"),
        )
        return []

    matches = list(ARTICLE_HEADER_PATTERN.finditer(text))

    if not matches:
        logger.warning(
            "Không tìm thấy cấu trúc 'Điều' ở đầu dòng trong văn bản (source=%s). "
            "Áp dụng fallback: trả về toàn văn bản dưới dạng 1 chunk với "
            "article='%s'.",
            source_metadata.get("source", "unknown"),
            FALLBACK_ARTICLE_LABEL,
        )
        return [
            {
                "content": text.strip(),
                "metadata": {**source_metadata, "article": FALLBACK_ARTICLE_LABEL},
            }
        ]

    chunks: List[Dict[str, Any]] = []

    # Lưu lại phần Lời mở đầu / Căn cứ / Thông tin các bên (trước Điều đầu tiên) nếu có
    first_match_start = matches[0].start()
    preamble_text = text[:first_match_start].strip()
    if preamble_text:
        chunks.append(
            {
                "content": preamble_text,
                "metadata": {**source_metadata, "article": "Lời mở đầu"},
            }
        )

    # Cắt từng Điều từ vị trí bắt đầu của Điều này đến vị trí bắt đầu của Điều kế tiếp
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        art_content = text[start:end].strip()

        if not art_content:
            continue

        article_label = f"Điều {match.group(1)}"
        chunks.append(
            {
                "content": art_content,
                "metadata": {**source_metadata, "article": article_label},
            }
        )

    if not chunks:
        # Trường hợp hiếm: có match nhưng nội dung rỗng sau khi strip.
        logger.warning(
            "Regex khớp nhưng không tạo được chunk hợp lệ nào (source=%s).",
            source_metadata.get("source", "unknown"),
        )

    return chunks


# Alias for backward compatibility
chunk_contract_by_articles = chunk_by_article


# ---------------------------------------------------------------------------
# Phần 3.7 - BLIND TEST: chạy trực tiếp file này để in kết quả chunking ra
# terminal, kiểm tra bằng mắt việc cắt Điều và gán metadata có đúng không,
# TRƯỚC KHI kích hoạt gọi API Embedding (Phần 4) trên dữ liệu thật.
#
# Cách chạy: python -m modules.shared.chunking
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    _SAMPLE_TEXT = """
Điều 1. Phạm vi điều chỉnh
Luật này quy định về hợp đồng dịch vụ giữa các bên.

ĐIỀU 2: Đối tượng áp dụng
Áp dụng cho cá nhân, tổ chức có hoạt động cung cấp dịch vụ.

điều 3 Giải thích từ ngữ
Trong Luật này, các từ ngữ dưới đây được hiểu như sau...

Điều 10. Quyền và nghĩa vụ của các bên
1. Bên cung cấp dịch vụ có quyền...
2. Bên sử dụng dịch vụ có nghĩa vụ...
"""

    _SAMPLE_TEXT_NO_STRUCTURE = """
Đây là một đoạn văn bản tự do, không được đánh số theo cấu trúc Điều/Khoản,
ví dụ như phần lời mở đầu hoặc mô tả tổng quan của một mẫu hợp đồng.
"""

    print("=" * 80)
    print("BLIND TEST 1: Văn bản có cấu trúc Điều (hoa/thường/dấu câu khác nhau)")
    print("=" * 80)
    result_1 = chunk_by_article(_SAMPLE_TEXT, {"source": "test_luat_mau.txt"})
    for idx, chunk in enumerate(result_1, start=1):
        print(f"\n--- Chunk {idx} ---")
        print("Metadata:", chunk["metadata"])
        print("Content :", chunk["content"][:120].replace("\n", " "), "...")

    print("\n" + "=" * 80)
    print("BLIND TEST 2: Văn bản KHÔNG có cấu trúc Điều (kiểm tra fallback)")
    print("=" * 80)
    result_2 = chunk_by_article(_SAMPLE_TEXT_NO_STRUCTURE, {"source": "test_tu_do.txt"})
    for idx, chunk in enumerate(result_2, start=1):
        print(f"\n--- Chunk {idx} ---")
        print("Metadata:", chunk["metadata"])
        print("Content :", chunk["content"][:120].replace("\n", " "), "...")

    print("\n" + "=" * 80)
    print(
        f"Tổng kết: Test 1 -> {len(result_1)} chunks | Test 2 -> {len(result_2)} chunks"
    )
    print("=" * 80)
