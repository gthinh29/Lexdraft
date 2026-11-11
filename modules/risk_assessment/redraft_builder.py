"""Bóc tách câu chữ Redline, vá lỗi dẫn chiếu hết hiệu lực và tái tạo văn bản hợp đồng hoàn chỉnh."""

import re
from typing import Any, Dict, List, Optional


def clean_redraft_text(text: str) -> str:
    """Làm sạch dấu ngoặc kép hoặc markdown code fence thừa quanh điều khoản soạn lại."""
    if not text:
        return ""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:markdown|text)?\s*|\s*```$", "", cleaned).strip()
    return cleaned.strip("\"'`")


def extract_redrafted_clause(risk_text: str) -> str:
    """Trích xuất nội dung Đề xuất soạn lại điều khoản (Redline) từ văn bản đánh giá rủi ro."""
    if not risk_text:
        return ""

    redline_match = re.search(
        r"(?:Đề xuất soạn lại điều khoản(?:\s*\(Redline\))?|Đề xuất điều chỉnh|Đề xuất sửa đổi)\s*\*?\*?\s*:\s*(.+)",
        risk_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not redline_match:
        return ""

    candidate = redline_match.group(1).strip().strip("\"'`")
    lower_cand = candidate.lower()
    if (
        any(
            skip in lower_cand
            for skip in (
                "không có",
                "không cần chỉnh sửa",
                "không cần sửa đổi",
                "giữ nguyên",
                "phù hợp quy định",
            )
        )
        and len(candidate) < 80
    ):
        return ""

    return candidate


def patch_expired_laws_in_text(
    text: str, expired_law_alerts: Optional[List[Dict[str, Any]]]
) -> str:
    """Thay thế trực tiếp các dòng viện dẫn văn bản hết hiệu lực trong Phần mở đầu bằng văn bản mới."""
    if not text or not expired_law_alerts:
        return text

    out_lines: List[str] = []
    replaced_inserted = set()
    for line in text.splitlines():
        lower_ln = line.lower()
        matched_alert = None
        for alert in expired_law_alerts:
            law_ref = (alert.get("law_ref") or "").lower()
            id_match = re.search(r"\d+/\d{4}/[a-zđ0-9-]+", law_ref, flags=re.IGNORECASE)
            if id_match and id_match.group(0).lower() in lower_ln:
                matched_alert = alert
                break
            if law_ref and any(
                part.strip() in lower_ln
                for part in re.split(r"[,;()]+", law_ref)
                if len(part.strip()) >= 8
            ):
                matched_alert = alert
                break

        if matched_alert:
            rep = (matched_alert.get("replaced_by") or "").strip()
            if rep and rep not in replaced_inserted:
                out_lines.append(f"- Căn cứ {rep};")
                replaced_inserted.add(rep)
        else:
            out_lines.append(line)

    missing_reps = [
        (a.get("replaced_by") or "").strip()
        for a in expired_law_alerts
        if (a.get("replaced_by") or "").strip()
        and (a.get("replaced_by") or "").strip() not in replaced_inserted
        and (a.get("replaced_by") or "").strip().lower() not in text.lower()
    ]
    if missing_reps:
        final_lines: List[str] = []
        inserted = False
        for ln in out_lines:
            if not inserted and re.match(
                r"^(?:Hôm nay|BÊN [AB]|ĐIỀU\s+1)", ln.strip(), flags=re.IGNORECASE
            ):
                for rep in missing_reps:
                    final_lines.append(f"- Căn cứ {rep};")
                inserted = True
            final_lines.append(ln)
        if not inserted:
            for rep in missing_reps:
                final_lines.append(f"- Căn cứ {rep};")
        return "\n".join(final_lines)

    return "\n".join(out_lines)


def build_redrafted_contract_text(
    risk_results: List[Dict[str, Any]],
    expired_law_alerts: Optional[List[Dict[str, Any]]] = None,
    contract_title: str = "HỢP ĐỒNG DỊCH VỤ (BẢN ĐÃ RÀ SOÁT & CHUẨN HÓA PHÁP LÝ 2026)",
) -> str:
    """Tái tạo toàn văn hợp đồng đã vá lỗi pháp lý từ danh sách điều khoản và bản Redline."""
    if not risk_results:
        return ""

    first_content = (risk_results[0].get("noi_dung") or "").upper()
    first_label = (risk_results[0].get("dieu_khoan") or "").lower()
    has_own_preamble = (
        "CỘNG HÒA" in first_content
        or "HỢP ĐỒNG" in first_content
        or "mở đầu" in first_label
    )

    lines: List[str] = []
    if not has_own_preamble:
        lines.extend(
            [
                "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM",
                "Độc lập - Tự do - Hạnh phúc",
                "---o0o---",
                "",
                contract_title.upper(),
                "",
            ]
        )
        if expired_law_alerts:
            lines.append("CĂN CỨ PHÁP LÝ ĐÃ CHUẨN HÓA (THAY THẾ VĂN BẢN HẾT HIỆU LỰC):")
            for alert in expired_law_alerts:
                replaced_by = alert.get("replaced_by", "")
                if replaced_by:
                    lines.append(f"- Căn cứ {replaced_by};")
            lines.append("")

    for idx, item in enumerate(risk_results, 1):
        label = item.get("dieu_khoan", f"Điều {idx}").strip()
        original_content = item.get("noi_dung", "").strip()
        is_preamble_item = idx == 1 and has_own_preamble

        redrafted = (
            item.get("redrafted_clause")
            or extract_redrafted_clause(item.get("rui_ro", ""))
        ).strip()

        if is_preamble_item:
            if redrafted and "CỘNG HÒA" in redrafted.upper():
                lines.append(redrafted)
            else:
                patched_preamble = patch_expired_laws_in_text(
                    original_content, expired_law_alerts
                )
                if redrafted and re.match(
                    r"^[-•*\s]*Căn\s+cứ\b", redrafted, re.IGNORECASE
                ):
                    clean_rep = re.sub(
                        r"^[-•*\s]*Căn\s+cứ\s+", "", redrafted, flags=re.IGNORECASE
                    ).strip()
                    if (
                        "36/2005/QH11" in clean_rep
                        and "Luật Thương mại 2020" in patched_preamble
                    ):
                        patched_preamble = re.sub(
                            r"^.*Luật Thương mại 2020.*$",
                            f"- Căn cứ {clean_rep}",
                            patched_preamble,
                            flags=re.MULTILINE | re.IGNORECASE,
                        )
                lines.append(patched_preamble)
        elif redrafted:
            if not re.match(r"^(?:ĐIỀU|Điều|PHẦN|Lời mở đầu|CỘNG HÒA)", redrafted):
                orig_first_line = (
                    original_content.splitlines()[0].strip() if original_content else ""
                )
                if re.match(r"^ĐIỀU\s+\d+", orig_first_line, flags=re.IGNORECASE):
                    lines.append(orig_first_line)
                else:
                    lines.append(label.upper())
                lines.append(redrafted)
            else:
                lines.append(redrafted)
        else:
            if original_content:
                lines.append(original_content)

        lines.append("")

    full_body = "\n".join(lines)
    if "ĐẠI DIỆN BÊN A" not in full_body.upper():
        lines.extend(
            [
                "| ĐẠI DIỆN BÊN A | ĐẠI DIỆN BÊN B |",
                "| :---: | :---: |",
                "| (Ký, ghi rõ họ tên và đóng dấu) | (Ký, ghi rõ họ tên và đóng dấu) |",
            ]
        )
    return "\n".join(lines)
