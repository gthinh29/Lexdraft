"""Giao diện phân hệ Soạn thảo Hợp đồng 2 cột (Cấu hình ↔ Xem trước A4)."""

import logging

import streamlit as st

try:
    from modules.drafting import retrieval as drafting_retrieval
    from modules.drafting import service as drafting_service
except ImportError:
    drafting_service = None
    drafting_retrieval = None

from modules.drafting.document_utils import (
    build_docx_bytes,
    docx_bytes_to_preview_html,
    format_draft_as_a4_html,
)
from ui.components.rag_inspector import render_rag_inspector
from ui.presets import QUICK_FILL_PRESETS
from ui.state import (
    apply_drafting_preset,
    clear_draft_form,
    init_drafting_form_state,
    on_drafting_category_change,
    persist_drafting_keys,
)

logger = logging.getLogger(__name__)


def render():
    """Render giao diện Soạn thảo Hợp đồng 2 cột (Trái: Cấu hình | Phải: A4 Preview)."""
    st.subheader("📝 Soạn thảo Hợp đồng theo Phân loại & Vị thế Pháp lý")

    taxonomy = (
        drafting_retrieval.load_contract_taxonomy()
        if drafting_retrieval
        else {"categories": {}, "stances": {}}
    )
    categories = taxonomy.get("categories", {})
    stances = taxonomy.get("stances", {})
    init_drafting_form_state(categories, stances)

    cat_keys = list(categories.keys()) if categories else ["software_dev"]
    cat_labels = {k: f"{categories[k].get('short_title', k)}" for k in cat_keys}
    stance_keys = list(stances.keys()) if stances else ["balanced"]
    stance_labels = {k: stances[k].get("short_name", k) for k in stance_keys}

    col_cfg, col_preview = st.columns([1.05, 1.35], gap="large")

    with col_cfg:
        c_cat, c_stance = st.columns(2, gap="small")
        with c_cat:
            selected_cat_id = st.selectbox(
                "📌 Phân loại Hợp đồng",
                options=cat_keys,
                format_func=lambda k: cat_labels.get(k, k),
                key="selected_taxonomy_cat",
                on_change=on_drafting_category_change,
                args=(categories,),
            )
        with c_stance:
            selected_stance_id = st.selectbox(
                "⚖️ Vị thế Pháp lý",
                options=stance_keys,
                format_func=lambda k: stance_labels.get(k, k),
                key="selected_taxonomy_stance",
            )

        active_cat = categories.get(selected_cat_id, {})
        active_stance = stances.get(selected_stance_id, {})

        c_tool1, c_tool2, c_tool3 = st.columns([1.15, 1.05, 0.8], gap="small")
        with c_tool1:
            with st.popover("⚡ Mẫu nhanh", use_container_width=True):
                st.caption("Chọn nhanh bộ dữ liệu mẫu chuẩn 2026:")
                for preset in QUICK_FILL_PRESETS:
                    st.button(
                        preset["btn_label"],
                        use_container_width=True,
                        key=f"preset_{preset['id']}",
                        on_click=apply_drafting_preset,
                        args=(categories, preset),
                    )
        with c_tool2:
            with st.popover("📋 Playbook", use_container_width=True):
                st.markdown(f"**{active_stance.get('label', '')}**")
                st.caption(active_stance.get("description", ""))
                st.markdown(
                    "**Luật:** " + "; ".join(active_cat.get("governing_laws", [])[:3])
                )
                for cl in active_cat.get("mandatory_clauses", []):
                    st.markdown(f"- `{cl}`")
        with c_tool3:
            st.button(
                "🧹 Xóa",
                use_container_width=True,
                key="demo_clear",
                on_click=clear_draft_form,
                args=(categories,),
            )

        with st.form("drafting_form"):
            col_c1, col_c2 = st.columns([2.3, 1])
            with col_c1:
                contract_type = st.text_input(
                    "Tiêu đề hợp đồng *",
                    key="draft_contract_type",
                )
            with col_c2:
                contract_num = st.text_input("Số HĐ", key="draft_contract_num")

            col_a, col_b = st.columns(2)
            with col_a:
                party_a = st.text_input(
                    "Bên A (Bên thuê)",
                    key="draft_party_a",
                    placeholder="Công ty ABC...",
                )
            with col_b:
                party_b = st.text_input(
                    "Bên B (Cung ứng)",
                    key="draft_party_b",
                    placeholder="Công ty XYZ...",
                )

            col_v, col_t = st.columns(2)
            with col_v:
                contract_value = st.text_input(
                    "Giá trị HĐ",
                    key="draft_value",
                    placeholder="150.000.000 VNĐ",
                )
            with col_t:
                duration = st.text_input(
                    "Thời hạn",
                    key="draft_duration",
                    placeholder="06 tháng",
                )

            custom_notes = st.text_area(
                "Phạm vi công việc & Thỏa thuận riêng",
                key="draft_notes",
                height=72,
                placeholder="VD: Chia 3 đợt thanh toán, bàn giao mã nguồn...",
            )

            specific_fields = active_cat.get("specific_fields", [])
            specific_inputs = {}
            with st.expander(
                "⚙️ Thông số đặc thù & Chốt chặn luật 2025/2026 (Mở rộng)",
                expanded=False,
            ):
                for sf in specific_fields:
                    sf_key = sf["key"]
                    sf_label = sf["label"]
                    specific_inputs[sf_label] = st.text_input(
                        sf_label,
                        placeholder=sf.get("placeholder", ""),
                        key=f"dyn_{selected_cat_id}_{sf_key}",
                    )
                opt_pdp = st.checkbox(
                    "🔒 Luật BVDLCN 91/2025/QH15 & NDA 02 năm",
                    key="draft_opt_pdp",
                )
                opt_ip = st.checkbox(
                    "🧠 Luật SHTT (VBHN 55/2026) & Luật AI 134/2025/QH15",
                    key="draft_opt_ip",
                )
                opt_penalty = st.checkbox(
                    "⚡ Trần phạt 8% (Điều 301 LTM - VBHN 113/2025)",
                    key="draft_opt_penalty",
                )
                opt_dispute = st.checkbox(
                    "⚖️ Giải quyết tranh chấp tại Tòa án / Trọng tài VIAC",
                    key="draft_opt_dispute",
                )

            submitted = st.form_submit_button(
                "🚀 Soạn thảo Hợp đồng",
                use_container_width=True,
                type="primary",
            )

        if submitted:
            if not contract_type.strip():
                st.error("Vui lòng nhập Tiêu đề hợp đồng.")
            elif drafting_service is None:
                st.error("Module Soạn thảo chưa sẵn sàng.")
            else:
                safeguards = []
                if opt_pdp:
                    safeguards.append(
                        "Bảo vệ dữ liệu cá nhân theo Luật số 91/2025/QH15 và bảo mật thông tin 02 năm"
                    )
                if opt_ip:
                    safeguards.append(
                        "Quy định quyền sở hữu trí tuệ theo Luật SHTT số 50/2005/QH11 (VBHN 55/VBHN-VPQH năm 2026) và Luật Trí tuệ nhân tạo số 134/2025/QH15"
                    )
                if opt_penalty:
                    safeguards.append(
                        "Chế tài phạt vi phạm tuân thủ trần 8% tại Điều 301 Luật Thương mại số 36/2005/QH11 (VBHN 113/VBHN-VPQH năm 2025)"
                    )
                if opt_dispute:
                    safeguards.append(
                        "Giải quyết tranh chấp thông qua thương lượng hoặc tại Tòa án nhân dân có thẩm quyền / Trọng tài thương mại"
                    )

                user_input = {
                    "contract_type": contract_type,
                    "category_id": selected_cat_id,
                    "stance_id": selected_stance_id,
                    "stance_label": active_stance.get("label", ""),
                    "so_hop_dong": contract_num,
                    "session_id": st.session_state.session_id,
                    "ben_a": party_a.strip() or "[BÊN THUÊ DỊCH VỤ - BÊN A]",
                    "ben_b": party_b.strip() or "[BÊN CUNG CẤP DỊCH VỤ - BÊN B]",
                    "gia_tri_hop_dong": contract_value.strip()
                    or "[●] VNĐ (Đã bao gồm VAT)",
                    "thoi_han": duration.strip() or "[●] tháng kể từ ngày ký",
                    "pham_vi_cong_viec_va_ghi_chu": custom_notes.strip()
                    or "Soạn theo các điều khoản dịch vụ chuẩn của phân loại đã chọn.",
                    "specific_values": specific_inputs,
                    "dieu_khoan_bo_sung": "; ".join(safeguards) if safeguards else None,
                }

                with st.spinner("Đang truy xuất RAG và soạn thảo hợp đồng..."):
                    try:
                        result = drafting_service.generate_contract_draft(user_input)
                        draft_text = (result.get("draft") or "").strip()
                        if result.get("refusal") or not draft_text:
                            st.error(
                                draft_text
                                or "Không thể sinh bản nháp hợp đồng. Vui lòng thử lại."
                            )
                        else:
                            st.session_state.last_draft = draft_text
                            st.session_state.last_draft_citations = result.get(
                                "citations", []
                            )
                            st.session_state.last_draft_debug_trace = result.get(
                                "debug_trace"
                            )
                            st.session_state.last_draft_meta = {
                                "category_name": active_cat.get("name", contract_type),
                                "stance_label": active_stance.get("short_name", ""),
                            }
                            st.session_state.last_risk_report = None
                            st.session_state.last_expired_alerts = []
                            st.session_state.pending_risk_draft = False
                            persist_drafting_keys(
                                {
                                    "selected_taxonomy_cat": selected_cat_id,
                                    "selected_taxonomy_stance": selected_stance_id,
                                    "draft_contract_type": contract_type,
                                    "draft_contract_num": contract_num,
                                    "draft_party_a": party_a,
                                    "draft_party_b": party_b,
                                    "draft_value": contract_value,
                                    "draft_duration": duration,
                                    "draft_notes": custom_notes,
                                    "draft_opt_pdp": opt_pdp,
                                    "draft_opt_ip": opt_ip,
                                    "draft_opt_penalty": opt_penalty,
                                    "draft_opt_dispute": opt_dispute,
                                }
                            )
                            st.rerun()
                    except Exception:
                        logger.exception("Lỗi khi sinh bản nháp.")
                        st.error("Đã có lỗi trong quá trình sinh bản nháp.")

        sync_snapshot = {
            "selected_taxonomy_cat": selected_cat_id,
            "selected_taxonomy_stance": selected_stance_id,
            "draft_contract_type": contract_type,
            "draft_contract_num": contract_num,
            "draft_party_a": party_a,
            "draft_party_b": party_b,
            "draft_value": contract_value,
            "draft_duration": duration,
            "draft_notes": custom_notes,
            "draft_opt_pdp": opt_pdp,
            "draft_opt_ip": opt_ip,
            "draft_opt_penalty": opt_penalty,
            "draft_opt_dispute": opt_dispute,
        }
        for sf in specific_fields:
            sf_wkey = f"dyn_{selected_cat_id}_{sf['key']}"
            if sf_wkey in st.session_state:
                sync_snapshot[sf_wkey] = st.session_state[sf_wkey]
        persist_drafting_keys(sync_snapshot)

    with col_preview:
        if not st.session_state.get("last_draft"):
            st.markdown(
                "<div class='panel-empty' style='margin-top:24px;'>"
                "<div class='icon'>📄</div>"
                "<div style='font-weight:600;color:#cbd5e1;margin-bottom:6px;'>Chưa có bản dự thảo</div>"
                "<div>Chọn mẫu điền nhanh bên trái hoặc nhập thông tin giao dịch rồi bấm <b>🚀 Soạn thảo</b> để xem ngay bản A4 và tải về file <code>.docx</code>.</div>"
                "</div>",
                unsafe_allow_html=True,
            )
            return

        draft_meta = st.session_state.get("last_draft_meta") or {}
        cat_display = draft_meta.get("category_name", "Hợp đồng Dịch vụ")
        stance_display = draft_meta.get("stance_label", "Cân bằng")
        draft_citations = st.session_state.get("last_draft_citations") or []

        try:
            docx_bytes = build_docx_bytes(st.session_state.last_draft)
            _docx_build_err = None
        except RuntimeError as e:
            docx_bytes = None
            _docx_build_err = str(e)

        c_meta, c_dl, c_zoom = st.columns([1.6, 1.1, 0.8], gap="small")
        with c_meta:
            st.markdown(
                f"<div style='background:#0f172a;border:1px solid #1e293b;border-left:3px solid #10b981;"
                f"border-radius:8px;padding:7px 10px;font-size:0.8rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>"
                f"✅ <b>{cat_display}</b> • <span style='color:#6ee7b7;'>{stance_display}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with c_dl:
            if docx_bytes is not None:
                st.download_button(
                    "⬇️ Tải .docx",
                    data=docx_bytes,
                    file_name="hop_dong_du_thao_lexdraft.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                    type="primary",
                )
        with c_zoom:
            if "preview_zoom" not in st.session_state:
                st.session_state["preview_zoom"] = st.session_state.get(
                    "drafting_persisted", {}
                ).get("preview_zoom", 100)
            _zoom_pct = st.slider(
                "Zoom",
                min_value=60,
                max_value=140,
                step=5,
                format="%d%%",
                key="preview_zoom",
                label_visibility="collapsed",
            )
            persist_drafting_keys({"preview_zoom": _zoom_pct})

        if _docx_build_err:
            st.warning(_docx_build_err)

        tab_a4, tab_raw, tab_cit, tab_rag = st.tabs(
            [
                "📄 Trang giấy A4",
                "✏️ Mã nguồn",
                f"📚 Căn cứ ({len(draft_citations)})",
                "🔍 RAG Inspector",
            ]
        )
        with tab_a4:
            if docx_bytes is not None:
                try:
                    _preview_html = docx_bytes_to_preview_html(docx_bytes)
                    _zoomed = (
                        f"<div style='zoom:{_zoom_pct}%;transform-origin:top left;'>"
                        f"{_preview_html}</div>"
                    )
                    st.markdown(_zoomed, unsafe_allow_html=True)
                except Exception:  # noqa: BLE001
                    st.markdown(
                        format_draft_as_a4_html(st.session_state.last_draft),
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown(
                    format_draft_as_a4_html(st.session_state.last_draft),
                    unsafe_allow_html=True,
                )

        with tab_raw:
            with st.container(height=480, border=False):
                st.code(
                    st.session_state.last_draft,
                    language="markdown",
                    wrap_lines=True,
                )

        with tab_cit:
            if not draft_citations:
                st.caption("Không có điều luật trích xuất riêng.")
            else:
                with st.container(height=480, border=False):
                    for c in draft_citations:
                        st.markdown(
                            f"- 📌 **{c.get('article', 'N/A')}** — {c.get('source', '')}"
                        )

        with tab_rag:
            render_rag_inspector(
                st.session_state.get("last_draft_debug_trace"),
                key_prefix="drafting_inspector",
                use_expander=False,
            )
