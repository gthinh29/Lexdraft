"""
ui/pages/page_drafting.py
Giao diện phân hệ hỗ trợ soạn thảo hợp đồng theo Phân loại (Taxonomy),
Vị thế Bảo vệ Pháp lý (Stance-Based Drafting) và tích hợp White-Box RAG Inspector.
"""

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

logger = logging.getLogger(__name__)


def render():
    """Render giao diện chính của trang Hỗ trợ Soạn thảo Hợp đồng."""
    st.subheader("📝 Hỗ trợ Soạn thảo Hợp đồng Dịch vụ theo Phân loại & Vị thế Pháp lý")

    taxonomy = (
        drafting_retrieval.load_contract_taxonomy()
        if drafting_retrieval
        else {"categories": {}, "stances": {}}
    )
    categories = taxonomy.get("categories", {})
    stances = taxonomy.get("stances", {})

    # -----------------------------------------------------------------------
    # BƯỚC 1: CHỌN PHÂN LOẠI HỢP ĐỒNG DỊCH VỤ & VỊ THẾ BẢO VỆ (NGOÀI FORM ĐỂ CẬP NHẬT ĐỘNG)
    # -----------------------------------------------------------------------
    st.markdown(
        "<div class='feature-card' style='border-left:4px solid #38bdf8;margin-bottom:14px;'>"
        "<div class='feature-card-title'>🗂️ Bước 1: Chọn Phân loại Hợp đồng Dịch vụ & Vị thế Bảo vệ Pháp lý</div>"
        "<div class='feature-card-desc'>Mỗi loại hợp đồng có hệ thống văn bản luật điều chỉnh, thông số kỹ thuật/nghiệp vụ và khung điều khoản chuẩn (Clause Playbook) riêng biệt.</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    cat_keys = list(categories.keys()) if categories else ["software_dev"]
    cat_labels = {
        k: f"{categories[k].get('short_title', k)} — {categories[k].get('name', '')}"
        for k in cat_keys
    }

    stance_keys = list(stances.keys()) if stances else ["balanced"]
    stance_labels = {k: stances[k].get("label", k) for k in stance_keys}

    col_cat, col_stance = st.columns([1.3, 1], gap="medium")
    with col_cat:
        selected_cat_id = st.selectbox(
            "📌 Phân loại Hợp đồng Dịch vụ *",
            options=cat_keys,
            format_func=lambda k: cat_labels.get(k, k),
            key="selected_taxonomy_cat",
        )
    with col_stance:
        selected_stance_id = st.selectbox(
            "⚖️ Vị thế Bảo vệ Pháp lý (Ai là người thuê soạn thảo?) *",
            options=stance_keys,
            format_func=lambda k: stance_labels.get(k, k),
            key="selected_taxonomy_stance",
        )

    active_cat = categories.get(selected_cat_id, {})
    active_stance = stances.get(selected_stance_id, {})

    # Hiển thị tóm tắt Pháp lý & Khung Điều khoản của Phân loại đang chọn
    with st.expander(
        f"📋 Xem Khung Điều khoản Chuẩn ({len(active_cat.get('mandatory_clauses', []))} Điều) & Chiến lược '{active_stance.get('short_name', '')}' sẽ áp dụng",
        expanded=False,
    ):
        c_info1, c_info2 = st.columns(2)
        with c_info1:
            st.markdown("**🏛️ Văn bản Luật điều chỉnh bắt buộc (2025/2026):**")
            for law in active_cat.get("governing_laws", []):
                st.markdown(f"- 📘 *{law}*")
            st.markdown("**📑 Khung Điều khoản Bắt buộc (Clause Playbook):**")
            for cl in active_cat.get("mandatory_clauses", []):
                st.markdown(f"- `{cl}`")
        with c_info2:
            st.markdown(
                f"**🎯 Chiến lược soạn thảo: {active_stance.get('label', '')}**"
            )
            st.caption(active_stance.get("description", ""))
            for directive in active_stance.get("drafting_directives", []):
                st.markdown(f"- ✅ {directive}")

    # QUICK ACTION CHIPS
    st.markdown("**💡 Kịch bản điền nhanh thực nghiệm:**")
    q1, q2, q3, q_clear = st.columns([1.2, 1.2, 1.2, 0.8])
    with q1:
        if st.button(
            "💻 Mẫu HĐ Phần mềm / AI", use_container_width=True, key="preset_sw"
        ):
            st.session_state["selected_taxonomy_cat"] = "software_dev"
            st.session_state["selected_taxonomy_stance"] = "protect_party_a"
            st.session_state["fill_party_a"] = "Tập đoàn Đầu tư & Thương mại Alpha"
            st.session_state["fill_party_b"] = "Công ty TNHH Phần mềm & AI Beta Tech"
            st.session_state["fill_value"] = "350.000.000 VNĐ (Đã bao gồm 10% VAT)"
            st.session_state["fill_duration"] = (
                "06 tháng chia làm 03 giai đoạn nghiệm thu"
            )
            st.session_state["fill_notes"] = (
                "Xây dựng hệ thống ERP tích hợp trợ lý AI nội bộ; yêu cầu tuân thủ Luật Trí tuệ nhân tạo 134/2025/QH15 và Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15."
            )
            st.rerun()
    with q2:
        if st.button(
            "🌐 Mẫu HĐ Thiết kế Web", use_container_width=True, key="preset_web"
        ):
            st.session_state["selected_taxonomy_cat"] = "web_design"
            st.session_state["selected_taxonomy_stance"] = "protect_party_b"
            st.session_state["fill_party_a"] = "Công ty TNHH Thương mại Quốc tế Đông Á"
            st.session_state["fill_party_b"] = "Công ty Cổ phần Giải pháp Số LexWeb"
            st.session_state["fill_value"] = "120.000.000 VNĐ (Đã bao gồm VAT)"
            st.session_state["fill_duration"] = "45 ngày làm việc kể từ ngày ký"
            st.session_state["fill_notes"] = (
                "Thiết kế website thương mại điện tử đa ngôn ngữ kèm cổng thanh toán trực tuyến và đăng ký tên miền .vn chính chủ."
            )
            st.rerun()
    with q3:
        if st.button("📣 Mẫu HĐ Marketing", use_container_width=True, key="preset_mkt"):
            st.session_state["selected_taxonomy_cat"] = "digital_marketing"
            st.session_state["selected_taxonomy_stance"] = "balanced"
            st.session_state["fill_party_a"] = (
                "Công ty Cổ phần Mỹ phẩm Thiên Nhiên Xanh"
            )
            st.session_state["fill_party_b"] = (
                "Công ty TNHH Truyền thông Sáng tạo Nova Agency"
            )
            st.session_state["fill_value"] = "200.000.000 VNĐ"
            st.session_state["fill_duration"] = "03 tháng chiến dịch liên tục"
            st.session_state["fill_notes"] = (
                "Triển khai chiến dịch quảng cáo đa kênh tuân thủ Luật sửa đổi Luật Quảng cáo số 75/2025/QH15."
            )
            st.rerun()
    with q_clear:
        if st.button("🧹 Xóa form", use_container_width=True, key="demo_clear"):
            for k in [
                "fill_party_a",
                "fill_party_b",
                "fill_value",
                "fill_duration",
                "fill_notes",
            ]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    default_code = f"01/2026/{active_cat.get('default_code_suffix', 'HĐDV')}"

    # -----------------------------------------------------------------------
    # BƯỚC 2: FORM NHẬP THÔNG TIN CỐT LÕI & THÔNG SỐ ĐẶC THÙ THEO PHÂN LOẠI
    # -----------------------------------------------------------------------
    with st.form("drafting_form"):
        st.markdown("#### 📌 2. Thông tin Chủ thể & Giá trị Giao dịch")
        col_c1, col_c2 = st.columns([3, 1])
        with col_c1:
            contract_type = st.text_input(
                "Tên tiêu đề hợp đồng dịch vụ *",
                value=active_cat.get("name", "Hợp đồng Dịch vụ"),
            )
        with col_c2:
            contract_num = st.text_input("Số Hợp đồng", value=default_code)

        col_a, col_b = st.columns(2)
        with col_a:
            party_a = st.text_input(
                "Bên A (Bên thuê dịch vụ)",
                value=st.session_state.get("fill_party_a", ""),
                placeholder="Công ty TNHH ABC... (Bỏ trống = [BÊN THUÊ DỊCH VỤ])",
            )
        with col_b:
            party_b = st.text_input(
                "Bên B (Bên cung cấp dịch vụ)",
                value=st.session_state.get("fill_party_b", ""),
                placeholder="Công ty Cổ phần XYZ... (Bỏ trống = [BÊN CUNG CẤP DỊCH VỤ])",
            )

        col_v, col_t = st.columns(2)
        with col_v:
            contract_value = st.text_input(
                "Giá trị hợp đồng (VNĐ)",
                value=st.session_state.get("fill_value", ""),
                placeholder="VD: 150.000.000 VNĐ (Bỏ trống = [●])",
            )
        with col_t:
            duration = st.text_input(
                "Thời hạn thực hiện",
                value=st.session_state.get("fill_duration", ""),
                placeholder="VD: 06 tháng kể từ ngày ký (Bỏ trống = [●])",
            )

        # CÁC TRƯỜNG ĐỘNG ĐẶC THÙ CỦA LOẠI HỢP ĐỒNG ĐANG CHỌN
        specific_fields = active_cat.get("specific_fields", [])
        specific_inputs = {}
        if specific_fields:
            st.markdown(
                f"#### ⚙️ 3. Thông số Nghiệp vụ Đặc thù: *{active_cat.get('short_title', '')}*"
            )
            for sf in specific_fields:
                sf_key = sf["key"]
                sf_label = sf["label"]
                sf_val = st.text_input(
                    sf_label,
                    value=sf.get("default", ""),
                    placeholder=sf.get("placeholder", ""),
                    key=f"dyn_{selected_cat_id}_{sf_key}",
                )
                specific_inputs[sf_label] = sf_val

        st.markdown("#### 📝 4. Phạm vi Công việc & Yêu cầu Đàm phán Riêng")
        custom_notes = st.text_area(
            "Nhập yêu cầu nghiệp vụ chi tiết hoặc thỏa thuận riêng bạn muốn đưa vào hợp đồng:",
            value=st.session_state.get("fill_notes", ""),
            height=90,
            placeholder="VD: Chia làm 3 đợt thanh toán 30% - 40% - 30%; yêu cầu bàn giao toàn bộ tài liệu kỹ thuật...",
        )

        st.markdown("#### 🛡️ 5. Chốt chặn Tuân thủ Pháp luật Hiện hành (2025/2026)")
        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            opt_pdp = st.checkbox(
                "🔒 Tuân thủ Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 & NDA 02 năm",
                value=True,
            )
            opt_ip = st.checkbox(
                "🧠 Ràng buộc Quyền Sở hữu trí tuệ theo VBHN số 55/VBHN-VPQH (2026) & Luật AI 134/2025/QH15",
                value=True,
            )
        with c_opt2:
            opt_penalty = st.checkbox(
                "⚡ Trần phạt vi phạm 8% (Điều 301 Luật Thương mại - VBHN 113/VBHN-VPQH)",
                value=True,
            )
            opt_dispute = st.checkbox(
                "⚖️ Giải quyết tranh chấp tại Tòa án có thẩm quyền / Trọng tài VIAC",
                value=True,
            )

        submitted = st.form_submit_button(
            f"🚀 Soạn thảo Hợp đồng ({active_cat.get('short_title', '')} | {active_stance.get('short_name', '')})",
            use_container_width=True,
        )

    if submitted:
        if not contract_type.strip():
            st.error("Vui lòng chọn hoặc nhập Loại hợp đồng.")
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

            name_a = (
                party_a.strip() if party_a.strip() else "[BÊN THUÊ DỊCH VỤ - BÊN A]"
            )
            name_b = (
                party_b.strip() if party_b.strip() else "[BÊN CUNG CẤP DỊCH VỤ - BÊN B]"
            )
            val_str = (
                contract_value.strip()
                if contract_value.strip()
                else "[●] VNĐ (Đã bao gồm thuế GTGT)"
            )
            dur_str = (
                duration.strip() if duration.strip() else "[●] tháng kể từ ngày ký"
            )
            notes_str = (
                custom_notes.strip()
                if custom_notes.strip()
                else "Soạn theo các điều khoản dịch vụ chuẩn của phân loại đã chọn."
            )

            user_input = {
                "contract_type": contract_type,
                "category_id": selected_cat_id,
                "stance_id": selected_stance_id,
                "stance_label": active_stance.get("label", ""),
                "so_hop_dong": contract_num,
                "session_id": st.session_state.session_id,
                "ben_a": name_a,
                "ben_b": name_b,
                "gia_tri_hop_dong": val_str,
                "thoi_han": dur_str,
                "pham_vi_cong_viec_va_ghi_chu": notes_str,
                "specific_values": specific_inputs,
                "dieu_khoan_bo_sung": "; ".join(safeguards) if safeguards else None,
            }

            with st.spinner(
                f"Đang truy xuất Multi-query RAG cho '{active_cat.get('short_title', '')}' và thiết kế điều khoản theo vị thế '{active_stance.get('short_name', '')}'..."
            ):
                try:
                    result = drafting_service.generate_contract_draft(user_input)
                    st.session_state.last_draft = result.get("draft")
                    st.session_state.last_draft_citations = result.get("citations", [])
                    st.session_state.last_draft_debug_trace = result.get("debug_trace")
                    st.session_state.last_draft_meta = {
                        "category_name": active_cat.get("name", contract_type),
                        "stance_label": active_stance.get("label", ""),
                    }
                    st.session_state.last_risk_report = None
                    st.session_state.last_expired_alerts = []
                    st.session_state.pending_risk_draft = False
                except Exception:
                    logger.exception("Lỗi khi sinh bản nháp.")
                    st.error("Đã có lỗi trong quá trình sinh bản nháp.")

    if st.session_state.get("last_draft"):
        st.divider()
        draft_meta = st.session_state.get("last_draft_meta") or {}
        cat_display = draft_meta.get("category_name", "Hợp đồng Dịch vụ")
        stance_display = draft_meta.get("stance_label", "Cân bằng hai bên")

        st.markdown(
            f"<div class='feature-card' style='border-left:4px solid #10b981;margin-bottom:12px;'>"
            f"<div class='feature-card-title'>📄 VĂN BẢN DỰ THẢO: {cat_display.upper()}</div>"
            f"<div class='feature-card-desc'><b>Vị thế pháp lý áp dụng:</b> {stance_display} — Đã đối chiếu và tích hợp căn cứ từ FAISS VectorDB.</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Hiển thị các Điều luật thực tế đã được AI trích dẫn trong hợp đồng vừa soạn
        draft_citations = st.session_state.get("last_draft_citations") or []
        if draft_citations:
            with st.expander(
                f"📚 Căn cứ Pháp lý đã viện dẫn trong Dự thảo ({len(draft_citations)} Điều luật xác thực từ RAG)",
                expanded=True,
            ):
                for c in draft_citations:
                    st.markdown(
                        f"- 📌 **{c.get('article', 'N/A')}** — {c.get('source', '')}"
                    )

        # Hiển thị White-Box RAG & Prompt Inspector (Giải quyết triệt để Feedback 5 của giảng viên)
        render_rag_inspector(
            st.session_state.get("last_draft_debug_trace"),
            title="🔍 [White-Box RAG Inspector] Xem Chunks Luật truy xuất từ FAISS & Toàn văn Prompt Soạn thảo gửi LLM",
            expanded=False,
            key_prefix="drafting_inspector",
        )

        # Build docx once — dùng cho cả preview lẫn download
        try:
            docx_bytes = build_docx_bytes(st.session_state.last_draft)
            _docx_build_err = None
        except RuntimeError as e:
            docx_bytes = None
            _docx_build_err = str(e)

        # Zoom control
        _zoom_col, _spacer = st.columns([1, 3])
        with _zoom_col:
            _zoom_pct = st.slider(
                "🔍 Zoom preview",
                min_value=50,
                max_value=150,
                value=st.session_state.get("preview_zoom", 100),
                step=5,
                format="%d%%",
                key="preview_zoom",
                label_visibility="visible",
            )

        tab_a4, tab_raw = st.tabs(
            ["📄 Trang giấy A4 (Paper View)", "✏️ Mã nguồn / Text chỉnh sửa"]
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
            st.text_area(
                "noi_dung_raw",
                st.session_state.last_draft,
                height=380,
                label_visibility="collapsed",
            )

        if docx_bytes is not None:
            st.download_button(
                "⬇️ Tải về file Word (.docx) chuẩn Nghị định 30/2020/NĐ-CP",
                data=docx_bytes,
                file_name="hop_dong_du_thao_lexdraft.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        elif _docx_build_err:
            st.warning(_docx_build_err)
