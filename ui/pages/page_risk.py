"""ui/pages/page_risk.py

Màn hình "📤 Gợi ý Rủi ro Pháp lý":
- Tải lên file hợp đồng (.pdf, .docx)
- Rà soát tự động 100% bằng One-shot stream pipeline
- Báo cáo rủi ro chi tiết, cảnh báo luật hết hiệu lực và panel đánh giá tổng quan.
"""

import logging
import tempfile
from pathlib import Path

import streamlit as st

try:
    from modules.risk_assessment import service as risk_assessment_service
except ImportError:
    risk_assessment_service = None

try:
    from modules.chatbot_qa import service as chatbot_service
except ImportError:
    chatbot_service = None

logger = logging.getLogger(__name__)


def _is_risky(rui_ro_text: str) -> bool:
    """True nếu đây là đánh giá CÓ rủi ro."""
    if not rui_ro_text:
        return False
    no_risk_phrases = [
        "không phát hiện rủi ro",
        "không có rủi ro",
        "phù hợp quy định",
        "không vi phạm",
        "không phát hiện vi phạm",
    ]
    lower = rui_ro_text.lower()
    return not any(phrase in lower for phrase in no_risk_phrases)


def render_risk_panel(target=None):
    """Render panel rủi ro cố định trong cột phải với UX Dashboard chuyên nghiệp."""
    ctx = target if target is not None else st.container()
    with ctx:
        st.markdown(
            "<div class='risk-panel-header'>"
            "<span>📊 Báo cáo Rủi ro Pháp lý</span>"
            "</div>",
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

        # TÍNH TOÁN MỨC ĐỘ RỦI RO TỔNG QUAN (RISK HEALTH METER)
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
            f"<div>"
            f"<div class='risk-meter-title'>Đánh giá tổng quan</div>"
            f"{health_badge}"
            f"</div>"
            f"</div>"
            f"{source_info}"
            f"<div class='risk-summary-metrics'>"
            f"<div class='metric-pill metric-pill-red'>🔴 {len(risky_items)} Rủi ro</div>"
            f"<div class='metric-pill metric-pill-yellow'>🚨 {len(expired)} Luật cũ</div>"
            f"<div class='metric-pill metric-pill-green'>✅ {len(safe_items)} An toàn</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # TABS TƯƠNG TÁC HIỆN ĐẠI CHO PANEL RỦI RO
        tab_risk, tab_expired, tab_safe = st.tabs(
            [
                f"🔴 Rủi ro ({len(risky_items)})",
                f"🚨 Hiệu lực ({len(expired)})",
                f"✅ An toàn ({len(safe_items)})",
            ]
        )

        with tab_risk:
            if risk_report is None and not risky_items:
                st.info("Chưa thực hiện phân tích rủi ro chi tiết.")
            elif not risky_items:
                st.markdown(
                    "<div class='safe-card'>"
                    "<div class='safe-card-title'>🎉 Không phát hiện rủi ro pháp lý</div>"
                    "<div class='safe-card-body'>Tất cả các điều khoản được phân tích đều phù hợp với quy định pháp luật hiện hành.</div>"
                    "</div>",
                    unsafe_allow_html=True,
                )
            else:
                for idx, item in enumerate(risky_items, 1):
                    label = item.get("dieu_khoan", f"Điều khoản {idx}")
                    rui_ro = item.get("rui_ro", "")
                    can_cu = item.get("can_cu", [])

                    citations_html = ""
                    if can_cu:
                        cit_lines = []
                        for cc in can_cu:
                            if isinstance(cc, dict):
                                art = cc.get("article", "")
                                src = cc.get("source", "")
                                cit_lines.append(
                                    f"📌 <b>{art}</b> — {src}" if art else f"📌 {src}"
                                )
                            else:
                                cit_lines.append(f"📌 {cc}")
                        citations_html = (
                            "<div class='risk-card-citations'>"
                            + "<br>".join(cit_lines)
                            + "</div>"
                        )

                    st.markdown(
                        f"<div class='risk-card'>"
                        f"<div class='risk-card-header'>"
                        f"<div class='risk-card-title'>🔴 {label}</div>"
                        f"<span class='risk-tag'>CẦN ĐIỀU CHỈNH</span>"
                        f"</div>"
                        f"<div class='risk-card-body'>{rui_ro}</div>"
                        f"{citations_html}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

        with tab_expired:
            if not expired:
                st.markdown(
                    "<div class='safe-card'>"
                    "<div class='safe-card-title'>✅ Dẫn chiếu pháp lý an toàn</div>"
                    "<div class='safe-card-body'>Không phát hiện văn bản pháp luật bãi bỏ/hết hiệu lực nào được dẫn chiếu trong hợp đồng.</div>"
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


def render():
    """Render giao diện chính của trang Gợi ý Rủi ro Pháp lý."""
    col_main, col_risk = st.columns([3, 2], gap="large")

    with col_main:
        st.subheader("📤 Rà soát & Gợi ý Rủi ro Pháp lý Hợp đồng")

        if st.session_state.upload_file_name:
            st.markdown(
                f"<div class='feature-card' style='border-left: 4px solid #38bdf8; margin-bottom: 16px;'>"
                f"<div class='feature-card-title'>📄 Hồ sơ Hợp đồng đang làm việc: <b>{st.session_state.upload_file_name}</b></div>"
                f"<div class='feature-card-desc'>Hệ thống đã nạp và trích xuất cấu trúc văn bản. Bạn có thể xem báo cáo rủi ro ở Panel bên phải hoặc chuyển sang Chatbot để trao đổi chuyên sâu.</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            # Hiển thị thông báo trạng thái kết quả rà soát
            if st.session_state.last_risk_report:
                risk_report = st.session_state.last_risk_report
                risky = [r for r in risk_report if _is_risky(r.get("rui_ro", ""))]
                safe_count = len(risk_report) - len(risky)
                st.markdown(
                    f"<div style='display:flex;align-items:center;justify-content:space-between;"
                    f"background:#0f172a;border:1px solid #1e293b;border-radius:10px;padding:10px 16px;margin-bottom:14px;'>"
                    f"<div style='display:flex;align-items:center;gap:12px;font-size:0.86rem;'>"
                    f"<span>✅ <b>Đã hoàn tất rà soát:</b></span>"
                    f"<span style='background:#450a0a;color:#fca5a5;padding:3px 10px;border-radius:20px;border:1px solid #991b1b;font-weight:600;'>🔴 {len(risky)} rủi ro</span>"
                    f"<span style='background:#064e3b;color:#6ee7b7;padding:3px 10px;border-radius:20px;border:1px solid #047857;font-weight:600;'>✅ {safe_count} an toàn</span>"
                    f"</div>"
                    f"<span style='font-size:0.8rem;color:#94a3b8;'>👉 Xem chi tiết ở Panel bên phải</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

            # Hàng nút thao tác: Cân đối, bằng chiều cao, chuẩn UI
            if not st.session_state.last_risk_report:
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
                        st.session_state.upload_file_name = None
                        st.session_state.upload_tmp_path = None
                        st.session_state.last_risk_report = None
                        st.session_state.last_expired_alerts = []
                        st.session_state.risk_source_name = None
                        st.session_state.pending_risk_upload = False
                        if chatbot_service:
                            chatbot_service.attach_contract_context(
                                session_id=st.session_state.session_id,
                                contract_chunks=[],
                                risk_report=[],
                            )
                        st.rerun()

                # Chạy phân tích trực tiếp từ tmp_path đã lưu (không phụ thuộc widget uploader)
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
                                        "📄 **{}** — Trích xuất **{}** điều khoản".format(
                                            data["source"], total_chunks
                                        )
                                    )
                                elif event == "result":
                                    idx = data["index"]
                                    pct = int(idx / max(data["total"], 1) * 100)
                                    progress_bar.progress(
                                        pct,
                                        text="Đang rà soát {}... ({}/{})".format(
                                            data["dieu_khoan"], idx, data["total"]
                                        ),
                                    )
                                    accumulated.append(
                                        {
                                            "dieu_khoan": data["dieu_khoan"],
                                            "noi_dung": data.get("noi_dung", ""),
                                            "rui_ro": data.get("rui_ro", ""),
                                            "can_cu": data.get("can_cu", []),
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
                c_chat, c_btn = st.columns([1, 1], gap="medium")
                with c_chat:
                    if st.button(
                        "💬 Chuyển sang Chatbot Q&A",
                        use_container_width=True,
                        type="primary",
                        key="goto_chatbot_from_risk",
                    ):
                        st.session_state["nav_page"] = "💬 Chatbot Hỏi – Đáp (Q&A)"
                        st.rerun()
                with c_btn:
                    if st.button(
                        "🗑️ Gỡ file hợp đồng",
                        use_container_width=True,
                        key="remove_active_contract",
                    ):
                        st.session_state.upload_file_name = None
                        st.session_state.upload_tmp_path = None
                        st.session_state.last_risk_report = None
                        st.session_state.last_expired_alerts = []
                        st.session_state.risk_source_name = None
                        st.session_state.pending_risk_upload = False
                        if chatbot_service:
                            chatbot_service.attach_contract_context(
                                session_id=st.session_state.session_id,
                                contract_chunks=[],
                                risk_report=[],
                            )
                        st.rerun()
        else:
            # FEATURE OVERVIEW CARDS
            st.markdown(
                "<div class='feature-grid'>"
                "<div class='feature-card'>"
                "<div class='feature-card-icon'>🔍</div>"
                "<div class='feature-card-title'>Rà soát Tự động 100%</div>"
                "<div class='feature-card-desc'>Phân tách hợp đồng thành từng Điều/Khoản và rà soát rủi ro pháp lý theo pipeline One-shot.</div>"
                "</div>"
                "<div class='feature-card'>"
                "<div class='feature-card-icon'>🚨</div>"
                "<div class='feature-card-title'>Tiered Law Checker</div>"
                "<div class='feature-card-desc'>Phát hiện sớm các văn bản pháp luật đã hết hiệu lực thi hành dựa trên 3 tầng kiểm duyệt.</div>"
                "</div>"
                "<div class='feature-card'>"
                "<div class='feature-card-icon'>📚</div>"
                "<div class='feature-card-title'>Grounded Citations</div>"
                "<div class='feature-card-desc'>Truy xuất điều khoản luật chính xác từ Bộ luật Dân sự 2015 & Luật Thương mại 2005.</div>"
                "</div>"
                "</div>",
                unsafe_allow_html=True,
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
                    st.session_state.pending_risk_upload = True
                    st.session_state.last_risk_report = None
                    st.session_state.last_expired_alerts = []
                    st.session_state.risk_source_name = None

                    # Tự động parse và nạp ngay context Điều/Khoản vào Chatbot
                    # để người dùng có thể chuyển sang tab Chatbot hỏi đáp tức thì mà không cần đợi bấm phân tích
                    try:
                        from modules.shared.document_reader import read_document
                        from modules.shared.chunking import chunk_by_article

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

                st.markdown(
                    f"<div class='feature-card' style='border-left:4px solid #10b981;margin-bottom:12px;'>"
                    f"<div class='feature-card-title'>📄 File hợp đồng đã tải lên: <b>{uploaded_file.name}</b></div>"
                    f"<div class='stepper-container'>"
                    f"<span class='stepper-step'>1. Parse Document</span> ➔ "
                    f"<span class='stepper-step'>2. Law Validity Check</span> ➔ "
                    f"<span class='stepper-step'>3. Vector RAG</span> ➔ "
                    f"<span class='stepper-step'>4. Risk Audit</span>"
                    f"</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                if st.session_state.pending_risk_upload:
                    action_container = st.empty()
                    with action_container.container():
                        st.info(
                            "🤖 Vui lòng chọn tác vụ rà soát cho file hợp đồng này:"
                        )
                        c1, c2 = st.columns([1, 1], gap="medium")
                        with c1:
                            do_analyze = st.button(
                                "🔍 Phân tích rủi ro ngay",
                                use_container_width=True,
                                type="primary",
                                key="confirm_upload_risk",
                            )
                        with c2:
                            cancel = st.button(
                                "⛔ Hủy file",
                                use_container_width=True,
                                key="cancel_upload_risk",
                            )

                    if cancel:
                        st.session_state.upload_file_name = None
                        st.session_state.upload_tmp_path = None
                        st.session_state.last_risk_report = None
                        st.session_state.last_expired_alerts = []
                        st.session_state.risk_source_name = None
                        st.session_state.pending_risk_upload = False
                        # Tăng key để reset widget file_uploader
                        st.session_state["_uploader_key"] = (
                            st.session_state.get("_uploader_key", 0) + 1
                        )
                        if chatbot_service:
                            chatbot_service.attach_contract_context(
                                session_id=st.session_state.session_id,
                                contract_chunks=[],
                                risk_report=[],
                            )
                        st.rerun()

                    if do_analyze:
                        st.session_state.pending_risk_upload = False
                        action_container.markdown(
                            "⏳ **Đang thực hiện Pipeline Rà soát Rủi ro...**"
                        )
                        if risk_assessment_service is None:
                            st.error("Module phân tích rủi ro chưa sẵn sàng.")
                        else:
                            tmp_path = st.session_state.upload_tmp_path
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
                                    original_name=uploaded_file.name,
                                ):
                                    if event == "meta":
                                        total_chunks = data["total"]
                                        ea = data["expired_law_alerts"]
                                        st.session_state.last_expired_alerts = ea
                                        st.session_state.risk_source_name = data[
                                            "source"
                                        ]
                                        progress_placeholder.markdown(
                                            "📄 **{}** — Trích xuất thành công **{}** điều khoản".format(
                                                data["source"], total_chunks
                                            )
                                        )

                                    elif event == "result":
                                        idx = data["index"]
                                        pct = int(idx / max(data["total"], 1) * 100)
                                        progress_bar.progress(
                                            pct,
                                            text="Đang rà soát {}... ({}/{})".format(
                                                data["dieu_khoan"], idx, data["total"]
                                            ),
                                        )
                                        accumulated.append(
                                            {
                                                "dieu_khoan": data["dieu_khoan"],
                                                "noi_dung": data.get("noi_dung", ""),
                                                "rui_ro": data.get("rui_ro", ""),
                                                "can_cu": data.get("can_cu", []),
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
                                            pct,
                                            text=data.get("message", "Đang xử lý..."),
                                        )

                                    elif event == "error":
                                        progress_bar.empty()
                                        progress_placeholder.empty()
                                        st.session_state.pending_risk_upload = False
                                        st.session_state.upload_file_name = None
                                        st.session_state.upload_tmp_path = None
                                        st.session_state["_uploader_key"] = (
                                            st.session_state.get("_uploader_key", 0) + 1
                                        )
                                        # Lưu lỗi để hiển thị sau khi rerun
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
                                                    risk_report=data["risk_results"]
                                                    or [],
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
            # NOTE: Không xóa state khi uploader trả về None (xảy ra khi tab qua lại).
            # State chỉ được xóa khi người dùng bấm nút "Gỡ file" hoặc "Hủy file" một cách tường minh.

    render_risk_panel(col_risk)
