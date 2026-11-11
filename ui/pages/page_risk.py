"""Giao diện phân hệ Rà soát Rủi ro Pháp lý và Tự động Vá lỗi (Redline)."""

import html
import logging
import re
import tempfile
from pathlib import Path

import streamlit as st

from modules.drafting.document_utils import build_docx_bytes
from ui.components.rag_inspector import render_rag_inspector
from ui.state import clear_active_risk_contract, persist_drafting_keys

try:
    from modules.risk_assessment import redraft_builder
    from modules.risk_assessment import service as risk_assessment_service
except ImportError:
    risk_assessment_service = None
    redraft_builder = None

try:
    from modules.chatbot_qa import service as chatbot_service
except ImportError:
    chatbot_service = None

logger = logging.getLogger(__name__)


def _format_risk_body_html(rui_ro: str) -> str:
    """Chuyển đổi markdown đánh giá của LLM sang HTML hiển thị trong thẻ rủi ro."""
    if not rui_ro:
        return ""
    escaped = html.escape(rui_ro.strip())
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b style='color:#f8fafc;'>\1</b>", escaped)
    escaped = re.sub(
        r"`([^`]+)`",
        r"<span style='background:#1e293b;color:#38bdf8;padding:1px 6px;border-radius:4px;font-size:0.78rem;'>\1</span>",
        escaped,
    )
    lines = []
    for line in escaped.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith("- ") or s.startswith("* "):
            lines.append(
                f"<div style='margin-bottom:6px;line-height:1.55;'>• {s[2:]}</div>"
            )
        else:
            lines.append(f"<div style='margin-bottom:6px;line-height:1.55;'>{s}</div>")
    return "".join(lines)


def _is_risky(rui_ro_text: str) -> bool:
    """Kiểm tra điều khoản có bị đánh dấu rủi ro hay không."""
    if not rui_ro_text:
        return False
    lower = rui_ro_text.lower()
    if "không trích xuất được" in lower:
        return False
    no_risk_phrases = (
        "không phát hiện rủi ro",
        "không có rủi ro",
        "phù hợp quy định",
        "không vi phạm",
        "không phát hiện vi phạm",
    )
    return not any(phrase in lower for phrase in no_risk_phrases)


def render_risk_panel(target=None):
    """Render bảng tổng hợp báo cáo rủi ro pháp lý bên cột phải."""
    ctx = target if target is not None else st.container()
    with ctx:
        st.markdown(
            "<div class='risk-panel-header'><span>📊 Báo cáo Rủi ro Pháp lý</span></div>",
            unsafe_allow_html=True,
        )

        expired = st.session_state.last_expired_alerts or []
        risk_report = st.session_state.last_risk_report
        source = st.session_state.risk_source_name or st.session_state.upload_file_name

        if risk_report is None and not expired:
            st.markdown(
                "<div class='panel-empty'>"
                "<div class='icon'>⚖️</div>"
                "<div style='font-weight:600;color:#cbd5e1;margin-bottom:4px;'>Sẵn sàng rà soát rủi ro</div>"
                "<div>Tải lên file hợp đồng hoặc soạn thảo hợp đồng ở cột bên trái. Hệ thống sẽ tự động rà soát điều khoản và kiểm tra hiệu lực văn bản pháp luật liên quan.</div>"
                "</div>",
                unsafe_allow_html=True,
            )
            return

        risky_items = [
            item for item in (risk_report or []) if _is_risky(item.get("rui_ro", ""))
        ]
        safe_items = [
            item
            for item in (risk_report or [])
            if not _is_risky(item.get("rui_ro", ""))
        ]

        if len(expired) > 0 or len(risky_items) >= 2:
            health_badge = (
                "<span class='risk-level-badge risk-badge-high'>🔴 Rủi ro Cao</span>"
            )
        elif len(risky_items) == 1:
            health_badge = "<span class='risk-level-badge risk-badge-medium'>🟡 Rủi ro Trung bình</span>"
        else:
            health_badge = "<span class='risk-level-badge risk-badge-safe'>🟢 An toàn Pháp lý</span>"

        source_info = (
            f"<div style='font-size:0.75rem;color:#38bdf8;margin-top:4px;'>📄 Document: <b>{source}</b></div>"
            if source
            else ""
        )

        st.markdown(
            f"<div class='risk-meter-card'>"
            f"<div style='display:flex;justify-content:space-between;align-items:center;'>"
            f"<div><div class='risk-meter-title'>Đánh giá tổng quan</div>{health_badge}</div>"
            f"</div>"
            f"{source_info}"
            f"<div class='risk-summary-metrics'>"
            f"<div class='metric-pill metric-pill-red'>🔴 {len(risky_items)} Rủi ro</div>"
            f"<div class='metric-pill metric-pill-yellow'>🚨 {len(expired)} Luật cũ</div>"
            f"<div class='metric-pill metric-pill-green'>✅ {len(safe_items)} An toàn</div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

        tab_risk, tab_expired, tab_safe = st.tabs(
            [
                f"🔴 Rủi ro ({len(risky_items)})",
                f"🚨 Hiệu lực ({len(expired)})",
                f"✅ An toàn ({len(safe_items)})",
            ]
        )

        with tab_risk:
            with st.container(height=430, border=False):
                if risk_report is None and not risky_items:
                    st.info("Chưa thực hiện phân tích rủi ro chi tiết.")
                elif not risky_items:
                    st.markdown(
                        "<div class='safe-card'>"
                        "<div class='safe-card-title'>🎉 Không phát hiện rủi ro pháp lý</div>"
                        "<div class='safe-card-body'>Tất cả các điều khoản đều phù hợp quy định hiện hành.</div>"
                        "</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    for idx, item in enumerate(risky_items, 1):
                        label = item.get("dieu_khoan", f"Điều khoản {idx}")
                        rui_ro = item.get("rui_ro", "")
                        can_cu = item.get("can_cu", [])

                        first_line = next(
                            (
                                ln.strip("-* ")
                                for ln in rui_ro.splitlines()
                                if ln.strip()
                            ),
                            "Cần điều chỉnh",
                        )
                        short_hint = re.sub(r"\*\*(.+?)\*\*", r"\1", first_line)
                        if len(short_hint) > 55:
                            short_hint = short_hint[:52] + "..."

                        with st.expander(
                            f"🔴 {label} — {short_hint}", expanded=(idx == 1)
                        ):
                            formatted_rui_ro = _format_risk_body_html(rui_ro)
                            st.markdown(
                                f"<div class='risk-card-body'>{formatted_rui_ro}</div>",
                                unsafe_allow_html=True,
                            )
                            if can_cu:
                                st.caption(
                                    "📚 **Căn cứ:** "
                                    + " • ".join(
                                        f"{cc.get('article', '')} ({cc.get('source', '')})"
                                        if isinstance(cc, dict)
                                        else str(cc)
                                        for cc in can_cu
                                    )
                                )

        with tab_expired:
            with st.container(height=430, border=False):
                if not expired:
                    st.markdown(
                        "<div class='safe-card'>"
                        "<div class='safe-card-title'>✅ Dẫn chiếu pháp lý an toàn</div>"
                        "<div class='safe-card-body'>Không phát hiện văn bản hết hiệu lực.</div>"
                        "</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    for a in expired:
                        law_ref = a.get("law_ref", "Văn bản")
                        replaced_by = a.get("replaced_by", "")
                        note = a.get("note", "")

                        st.markdown(
                            f"<div class='expired-banner'>"
                            f"<div class='expired-banner-title'>🚨 VĂN BẢN HẾT HIỆU LỰC</div>"
                            f"<div class='expired-banner-item'><b>Văn bản viện dẫn:</b> {law_ref}</div>"
                            f"<div class='expired-banner-item'><b>Trạng thái:</b> Đã hết hiệu lực thi hành</div>"
                            f"{f'<div class="expired-banner-item"><b>Văn bản thay thế:</b> {replaced_by}</div>' if replaced_by else ''}"
                            f"{f'<div class="expired-banner-item" style="font-size:0.75rem;color:#fca5a5;margin-top:6px;">ℹ️ {note}</div>' if note else ''}"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

        with tab_safe:
            with st.container(height=430, border=False):
                if not risk_report:
                    st.caption("Chưa có dữ liệu.")
                elif not safe_items:
                    st.caption("Tất cả các điều khoản được quét đều có điểm cần lưu ý.")
                else:
                    for item in safe_items:
                        label = item.get("dieu_khoan", "Điều khoản")
                        rui_ro = item.get("rui_ro", "Phù hợp quy định pháp luật.")
                        st.markdown(
                            f"<div class='safe-card'>"
                            f"<div class='safe-card-title'>✅ {label}</div>"
                            f"<div class='safe-card-body'>{rui_ro}</div>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )


def _render_redraft_section(risk_report: list | None, expired_alerts: list | None):
    """Hiển thị khu vực đối chiếu Redline Before/After, toàn văn hợp đồng đã vá lỗi và RAG Inspector."""
    if not risk_report:
        return

    risky_items = [item for item in risk_report if _is_risky(item.get("rui_ro", ""))]
    patched_text = ""
    if (risky_items or expired_alerts) and redraft_builder:
        patched_text = redraft_builder.build_redrafted_contract_text(
            risk_results=risk_report,
            expired_law_alerts=expired_alerts,
        )

    tab_redline, tab_full, tab_rag = st.tabs(
        [
            f"🔀 Vá lỗi Redline ({len(risky_items)})",
            "📄 Toàn văn đã Vá lỗi",
            "🔍 RAG Inspector",
        ]
    )

    with tab_redline:
        if not risky_items and not expired_alerts:
            st.success("🎉 Hợp đồng an toàn, không có điều khoản cần vá lỗi.")
        else:
            if patched_text:
                c_dl, c_open = st.columns([1, 1], gap="small")
                with c_dl:
                    try:
                        docx_bytes = build_docx_bytes(patched_text)
                        st.download_button(
                            label="📥 Tải HĐ đã Vá lỗi (.docx)",
                            data=docx_bytes,
                            file_name="hop_dong_da_va_loi_chuan_2026.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True,
                            type="primary",
                            key="dl_redrafted_contract_docx",
                        )
                    except Exception as e:
                        logger.warning("Không thể tạo file docx vá lỗi: %s", e)

                with c_open:
                    if st.button(
                        "📝 Mở trên Trang giấy A4",
                        use_container_width=True,
                        key="open_redrafted_in_drafting",
                    ):
                        all_cits = []
                        seen_c = set()
                        for item in risk_report:
                            for cc in item.get("can_cu", []):
                                ck = (
                                    (cc.get("article", ""), cc.get("source", ""))
                                    if isinstance(cc, dict)
                                    else str(cc)
                                )
                                if ck not in seen_c:
                                    seen_c.add(ck)
                                    all_cits.append(cc)
                        st.session_state.last_draft = patched_text
                        st.session_state.last_draft_citations = all_cits
                        st.session_state.last_draft_debug_trace = st.session_state.get(
                            "last_risk_debug_trace"
                        )
                        st.session_state.last_draft_meta = {
                            "category_name": st.session_state.get("risk_source_name")
                            or "Hợp đồng đã Rà soát & Vá lỗi Pháp lý",
                            "stance_label": "Bản Redline chuẩn Pháp lý 2026",
                        }
                        st.session_state["preview_zoom"] = 100
                        persist_drafting_keys({"preview_zoom": 100})
                        st.session_state["nav_page"] = "📝 Hỗ trợ Soạn thảo Hợp đồng"
                        st.rerun()

            if risky_items:
                clause_labels = [
                    f"{i}. {it.get('dieu_khoan', f'Điều {i}')}"
                    for i, it in enumerate(risky_items, 1)
                ]
                prev_idx = st.session_state.get("redline_clause_selector", 0)
                if not isinstance(prev_idx, int) or prev_idx >= len(risky_items):
                    st.session_state["redline_clause_selector"] = 0
                chosen_idx = st.selectbox(
                    "Chọn điều khoản đối chiếu Before / After:",
                    options=range(len(risky_items)),
                    format_func=lambda i: clause_labels[i],
                    key="redline_clause_selector",
                )
                chosen_idx = min(max(int(chosen_idx or 0), 0), len(risky_items) - 1)
                item = risky_items[chosen_idx]
                orig_clause = item.get("noi_dung", "").strip()
                redrafted = item.get("redrafted_clause", "").strip()
                if not redrafted and redraft_builder:
                    redrafted = redraft_builder.extract_redrafted_clause(
                        item.get("rui_ro", "")
                    )

                with st.container(height=280, border=False):
                    col_before, col_after = st.columns(2, gap="small")
                    with col_before:
                        st.markdown(
                            "<div style='background:#450a0a;border:1px solid #991b1b;border-radius:8px;padding:10px;'>"
                            "<div style='font-weight:700;color:#fca5a5;font-size:0.78rem;margin-bottom:4px;'>❌ BẢN GỐC</div>"
                            f"<div style='font-size:0.82rem;color:#fecaca;line-height:1.5;white-space:pre-wrap;'>"
                            f"{html.escape(orig_clause or 'Không có nội dung gốc.')}</div></div>",
                            unsafe_allow_html=True,
                        )
                    with col_after:
                        display_after = (
                            redrafted
                            if redrafted
                            else "Xem chi tiết hướng dẫn điều chỉnh ở Panel bên phải."
                        )
                        st.markdown(
                            "<div style='background:#064e3b;border:1px solid #059669;border-radius:8px;padding:10px;'>"
                            "<div style='font-weight:700;color:#6ee7b7;font-size:0.78rem;margin-bottom:4px;'>✅ ĐỀ XUẤT SỬA ĐỔI (REDLINE)</div>"
                            f"<div style='font-size:0.82rem;color:#d1fae5;line-height:1.5;white-space:pre-wrap;'>"
                            f"{html.escape(display_after)}</div></div>",
                            unsafe_allow_html=True,
                        )

    with tab_full:
        if patched_text:
            st.text_area(
                "patched_contract_text",
                value=patched_text,
                height=360,
                label_visibility="collapsed",
            )
        else:
            st.caption("Không có nội dung cần sửa đổi.")

    with tab_rag:
        sub_p1, sub_p2 = st.tabs(
            [
                "🔍 Prompt 1: Gợi ý Rủi ro",
                "✍️ Prompt 2: Soạn thảo Vá lỗi",
            ]
        )
        with sub_p1:
            render_rag_inspector(
                st.session_state.get("last_risk_debug_trace"),
                key_prefix="risk_inspector",
                use_expander=False,
            )
        with sub_p2:
            redraft_trace = st.session_state.get("last_redraft_debug_trace")
            if redraft_trace:
                render_rag_inspector(
                    redraft_trace,
                    key_prefix="redraft_inspector",
                    use_expander=False,
                )
            else:
                st.caption("Không có điều khoản cần chạy Prompt Soạn thảo vá lỗi.")


def render():
    """Render giao diện chính của trang Gợi ý Rủi ro Pháp lý."""
    col_main, col_risk = st.columns([3, 2], gap="large")

    with col_main:
        st.subheader("📤 Rà soát & Gợi ý Rủi ro Pháp lý Hợp đồng")

        if st.session_state.upload_file_name:
            if not st.session_state.last_risk_report:
                if st.session_state.get("_risk_api_error"):
                    st.error(st.session_state.pop("_risk_api_error"))
                st.markdown(
                    f"<div style='background:#0f172a;border:1px solid #1e293b;border-left:4px solid #38bdf8;"
                    f"border-radius:8px;padding:8px 12px;margin-bottom:8px;font-size:0.84rem;'>"
                    f"📄 File đang chọn: <b>{html.escape(st.session_state.upload_file_name)}</b>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                c_run, c_chat, c_btn = st.columns([1, 1, 1], gap="small")
                with c_run:
                    run_clicked = st.button(
                        "🔍 Phân tích rủi ro",
                        use_container_width=True,
                        type="primary",
                        key="active_run_analysis",
                    )
                with c_chat:
                    if st.button(
                        "💬 Chatbot Q&A",
                        use_container_width=True,
                        key="goto_chatbot_from_risk",
                    ):
                        st.session_state["nav_page"] = "💬 Chatbot Hỏi – Đáp (Q&A)"
                        st.rerun()
                with c_btn:
                    if st.button(
                        "🗑️ Gỡ file",
                        use_container_width=True,
                        key="remove_active_contract",
                    ):
                        clear_active_risk_contract(chatbot_service)
                        st.rerun()

                if run_clicked:
                    tmp_path = st.session_state.upload_tmp_path
                    orig_name = st.session_state.upload_file_name
                    if not tmp_path or not Path(tmp_path).exists():
                        st.error(
                            "File hợp đồng không còn khả dụng. Vui lòng tải lên lại."
                        )
                    elif risk_assessment_service is None:
                        st.error("Module phân tích rủi ro chưa sẵn sàng.")
                    else:
                        progress_bar = st.progress(0, text="Đang khởi tạo...")
                        progress_placeholder = st.empty()
                        accumulated = []
                        try:
                            for (
                                event,
                                data,
                            ) in risk_assessment_service.stream_analyze_contract(
                                file_path_or_text=tmp_path,
                                session_id=st.session_state.session_id,
                                original_name=orig_name,
                            ):
                                if event == "meta":
                                    total_chunks = data["total"]
                                    st.session_state.last_expired_alerts = data[
                                        "expired_law_alerts"
                                    ]
                                    st.session_state.risk_source_name = data["source"]
                                    progress_placeholder.markdown(
                                        f"📄 **{data['source']}** — Trích xuất **{total_chunks}** điều khoản"
                                    )
                                elif event == "result":
                                    idx = data["index"]
                                    pct = int(idx / max(data["total"], 1) * 100)
                                    progress_bar.progress(
                                        pct,
                                        text=f"Đang rà soát {data['dieu_khoan']}... ({idx}/{data['total']})",
                                    )
                                    accumulated.append(
                                        {
                                            "dieu_khoan": data["dieu_khoan"],
                                            "noi_dung": data.get("noi_dung", ""),
                                            "rui_ro": data.get("rui_ro", ""),
                                            "can_cu": data.get("can_cu", []),
                                            "redrafted_clause": data.get(
                                                "redrafted_clause", ""
                                            ),
                                            "local_law_chunks": data.get(
                                                "local_law_chunks", []
                                            ),
                                        }
                                    )
                                    st.session_state.last_risk_report = list(
                                        accumulated
                                    )
                                elif event == "progress":
                                    pct = int(
                                        data["index"] / max(data["total"], 1) * 100
                                    )
                                    progress_bar.progress(
                                        pct, text=data.get("message", "Đang xử lý...")
                                    )
                                elif event == "error":
                                    progress_bar.empty()
                                    progress_placeholder.empty()
                                    st.session_state.last_risk_report = None
                                    if data.get("debug_trace"):
                                        st.session_state.last_risk_debug_trace = (
                                            data.get("debug_trace")
                                        )
                                    if data.get("keep_file"):
                                        st.session_state["_risk_api_error"] = data.get(
                                            "message",
                                            "Hệ thống AI tạm thời quá tải. Vui lòng thử lại.",
                                        )
                                    else:
                                        st.session_state.upload_file_name = None
                                        st.session_state.upload_tmp_path = None
                                        st.session_state["_uploader_key"] = (
                                            st.session_state.get("_uploader_key", 0) + 1
                                        )
                                        st.session_state["_upload_error"] = data.get(
                                            "message",
                                            "File không chứa nội dung hợp đồng hợp lệ.",
                                        )
                                    st.rerun()
                                elif event == "done":
                                    progress_bar.progress(
                                        100, text="✅ Hoàn tất rà soát rủi ro!"
                                    )
                                    progress_placeholder.empty()
                                    st.session_state.last_risk_report = data[
                                        "risk_results"
                                    ]
                                    st.session_state.last_expired_alerts = data[
                                        "expired_law_alerts"
                                    ]
                                    st.session_state.last_risk_debug_trace = data.get(
                                        "debug_trace"
                                    )
                                    st.session_state.last_redraft_debug_trace = (
                                        data.get("redraft_debug_trace")
                                    )
                                    chunks = (
                                        data.get("contract_chunks")
                                        or st.session_state.get("contract_chunks")
                                        or []
                                    )
                                    if chunks:
                                        st.session_state.contract_chunks = chunks
                                    if chatbot_service:
                                        try:
                                            chatbot_service.attach_contract_context(
                                                session_id=st.session_state.session_id,
                                                contract_chunks=chunks,
                                                risk_report=data["risk_results"] or [],
                                            )
                                        except Exception:
                                            logger.exception(
                                                "Không thể đồng bộ context sang chatbot_qa."
                                            )
                                    st.rerun()
                        except Exception:
                            logger.exception("Lỗi khi phân tích.")
                            st.error(
                                "Đã có lỗi trong quá trình rà soát. Vui lòng thử lại."
                            )
            else:
                risk_report = st.session_state.last_risk_report
                risky = [r for r in risk_report if _is_risky(r.get("rui_ro", ""))]
                safe_count = len(risk_report) - len(risky)
                c_stat, c_chat, c_btn = st.columns([2.1, 1, 0.8], gap="small")
                with c_stat:
                    st.markdown(
                        f"<div style='background:#0f172a;border:1px solid #1e293b;border-left:3px solid #38bdf8;"
                        f"border-radius:8px;padding:7px 12px;font-size:0.82rem;display:flex;align-items:center;gap:10px;'>"
                        f"<span style='white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>📄 <b>{html.escape(st.session_state.upload_file_name)}</b></span>"
                        f"<span style='color:#fca5a5;font-weight:600;white-space:nowrap;'>🔴 {len(risky)}</span>"
                        f"<span style='color:#6ee7b7;font-weight:600;white-space:nowrap;'>✅ {safe_count}</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
                with c_chat:
                    if st.button(
                        "💬 Hỏi AI",
                        use_container_width=True,
                        type="primary",
                        key="goto_chatbot_from_risk",
                    ):
                        st.session_state["nav_page"] = "💬 Chatbot Hỏi – Đáp (Q&A)"
                        st.rerun()
                with c_btn:
                    if st.button(
                        "🗑️ Gỡ",
                        use_container_width=True,
                        key="remove_active_contract",
                    ):
                        clear_active_risk_contract(chatbot_service)
                        st.rerun()

                _render_redraft_section(
                    st.session_state.last_risk_report,
                    st.session_state.last_expired_alerts,
                )
        else:
            st.caption(
                "Tải lên hợp đồng `.pdf` / `.docx` để kiểm tra hiệu lực văn bản 3 tầng, rà soát rủi ro và tự động đề xuất Redline sửa đổi."
            )

            if "_uploader_key" not in st.session_state:
                st.session_state["_uploader_key"] = 0

            if st.session_state.get("_upload_error"):
                st.error(
                    f"⚠️ **Không thể phân tích file vừa tải lên.**\n\n"
                    f"{st.session_state['_upload_error']}\n\n"
                    "ℹ️ Hãy thử lại với file hợp đồng hợp lệ (.pdf hoặc .docx) "
                    "có nội dung điều khoản rõ ràng."
                )
                st.session_state["_upload_error"] = None

            uploaded_file = st.file_uploader(
                "Tải lên file hợp đồng dịch vụ (.pdf, .docx)",
                type=["pdf", "docx"],
                label_visibility="collapsed",
                key=f"file_uploader_{st.session_state['_uploader_key']}",
            )

            if uploaded_file is not None:
                if st.session_state.upload_file_name != uploaded_file.name:
                    suffix = Path(uploaded_file.name).suffix
                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=suffix
                    ) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        st.session_state.upload_tmp_path = tmp.name
                    st.session_state.upload_file_name = uploaded_file.name
                    st.session_state.pending_risk_upload = False
                    st.session_state.last_risk_report = None
                    st.session_state.last_expired_alerts = []
                    st.session_state.last_risk_debug_trace = None
                    st.session_state.last_redraft_debug_trace = None
                    st.session_state.risk_source_name = None

                    try:
                        from modules.shared.chunking import chunk_by_article
                        from modules.shared.document_reader import read_document

                        parsed_text = read_document(st.session_state.upload_tmp_path)
                        if parsed_text and parsed_text.strip():
                            chunks = chunk_by_article(
                                parsed_text,
                                {"source": uploaded_file.name, "doc_type": "contract"},
                            )
                            if chunks:
                                st.session_state.contract_chunks = chunks
                                if chatbot_service:
                                    chatbot_service.attach_contract_context(
                                        session_id=st.session_state.session_id,
                                        contract_chunks=chunks,
                                        risk_report=[],
                                    )
                    except Exception as e:
                        logger.warning(
                            "Không thể parse và nạp sớm ngữ cảnh hợp đồng: %s", e
                        )

                    st.rerun()

    render_risk_panel(col_risk)
