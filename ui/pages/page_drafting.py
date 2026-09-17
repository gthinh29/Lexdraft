"""ui/pages/page_drafting.py

Màn hình "📝 Hỗ trợ Soạn thảo Hợp đồng":
- Studio soạn thảo hợp đồng dịch vụ chuẩn mẫu
- 1-Click Preset & Clear
- Tự động điền ký hiệu giữ chỗ [●]
- Xem trước tài liệu chuẩn A4 Paper View (chuẩn Nghị định 30/2020/NĐ-CP)
- Tùy chỉnh tỷ lệ Zoom preview và Tải về file Word (.docx)
"""

import logging

import streamlit as st

try:
    from modules.drafting import service as drafting_service
except ImportError:
    drafting_service = None

from modules.drafting.document_utils import (
    build_docx_bytes,
    docx_bytes_to_preview_html,
    format_draft_as_a4_html,
)

logger = logging.getLogger(__name__)


def render():
    """Render giao diện chính của trang Hỗ trợ Soạn thảo Hợp đồng."""
    st.subheader("📝 Studio Soạn thảo Hợp đồng Dịch vụ Chuyên nghiệp")

    # SECURITY & PRIVACY GUARANTEE BANNER
    st.markdown(
        "<div class='feature-card' style='border-left:4px solid #10b981;margin-bottom:14px;background:#064e3b22;'>"
        "<div class='feature-card-title' style='color:#6ee7b7;'>🛡️ CAM KẾT BẢO MẬT & TRẢI NGHIỆM TỐI GIẢN CHUẨN MẪU MAUHOPDONGDICHVU.MD</div>"
        "<div class='feature-card-desc' style='color:#a7f3d0;'>"
        "• <b>Xử lý bộ nhớ tạm (In-Memory Session):</b> Dữ liệu xử lý hoàn toàn trên RAM phiên duyệt, KHÔNG lưu đĩa CSDL hay chia sẻ bên thứ 3.<br>"
        "• <b>Tối giản tối đa:</b> Chỉ cần điền các thông tin cốt lõi nhất. Mọi ô bỏ trống sẽ tự động dùng ký hiệu giữ chỗ <code>[●]</code> theo mẫu pháp lý."
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    # QUICK ACTION CHIPS
    st.markdown("**💡 Thao tác nhanh (1-Click Fill & Clear):**")
    q1, q2, q_clear = st.columns([1.5, 1.5, 1])
    with q1:
        if st.button(
            "⚡ Mẫu thử HĐ Thiết kế Web", use_container_width=True, key="preset_web"
        ):
            st.session_state["preset_contract_type"] = "Hợp đồng Thiết kế Website"
            st.session_state["fill_party_a"] = "Công ty TNHH Công nghệ Lexdraft"
            st.session_state["fill_party_b"] = "Công ty Cổ phần Giải pháp Số Việt"
            st.session_state["fill_value"] = "150.000.000 VNĐ"
            st.session_state["fill_duration"] = "06 tháng kể từ ngày ký"
            st.session_state["fill_notes"] = (
                "Bên B có nghĩa vụ bảo hành kỹ thuật 12 tháng sau khi nghiệm thu và bàn giao source code."
            )
            st.rerun()
    with q2:
        if st.button(
            "⚡ Mẫu thử HĐ Phần mềm", use_container_width=True, key="preset_sw"
        ):
            st.session_state["preset_contract_type"] = "Hợp đồng Phát triển Phần mềm"
            st.session_state["fill_party_a"] = "Tập đoàn Đầu tư & Thương mại Alpha"
            st.session_state["fill_party_b"] = "Công ty TNHH Phần mềm Beta Tech"
            st.session_state["fill_value"] = "350.000.000 VNĐ"
            st.session_state["fill_duration"] = "09 tháng chia làm 3 đợt nghiệm thu"
            st.session_state["fill_notes"] = (
                "Yêu cầu bên B triển khai trên hạ tầng Cloud AWS của bên A và cam kết Uptime 99.9%."
            )
            st.rerun()
    with q_clear:
        if st.button("🧹 Xóa sạch form", use_container_width=True, key="demo_clear"):
            for k in [
                "preset_contract_type",
                "fill_party_a",
                "fill_party_b",
                "fill_value",
                "fill_duration",
                "fill_notes",
            ]:
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()

    st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

    default_type = st.session_state.get(
        "preset_contract_type", "Hợp đồng Dịch vụ Thiết kế Website"
    )

    with st.form("drafting_form"):
        st.markdown("#### 📌 1. Thông tin Cốt lõi Hợp đồng")
        col_c1, col_c2 = st.columns([3, 1])
        with col_c1:
            contract_type = st.text_input(
                "Loại hợp đồng dịch vụ *",
                value=default_type,
                placeholder="VD: Hợp đồng Thiết kế Website, Hợp đồng Phát triển Phần mềm...",
            )
        with col_c2:
            contract_num = st.text_input("Số Hợp đồng", value="01/HĐDV/2026")

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

        st.markdown("#### 📝 2. Phạm vi Công việc & Ghi chú / Yêu cầu Đặc thù Bổ sung")
        custom_notes = st.text_area(
            "Nhập bất kỳ yêu cầu, phạm vi công việc hay điều khoản riêng bạn muốn đưa vào hợp đồng:",
            value=st.session_state.get("fill_notes", ""),
            height=100,
            placeholder="VD: Bên B phải bảo hành 12 tháng sau khi bàn giao; Bên A tạm ứng 30% khi ký hợp đồng; Yêu cầu bàn giao đầy đủ mã nguồn và tài liệu kỹ thuật...",
        )

        st.markdown("#### 🛡️ 3. Điều khoản Pháp lý Chuyên sâu & Tuân thủ Luật 2025/2026")
        opt_pdp = st.checkbox(
            "🔒 Tuân thủ Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15 & Nghĩa vụ Bảo mật 02 năm",
            value=True,
        )
        opt_ip = st.checkbox(
            "🧠 Chuyển giao toàn bộ Quyền Sở hữu trí tuệ sản phẩm đầu ra khi thanh toán 100% (Bao gồm AI)",
            value=True,
        )
        opt_penalty = st.checkbox(
            "⚡ Phạt vi phạm 8% (Luật Thương mại 2005) & Giới hạn trách nhiệm bồi thường (Cap Liability 100%)",
            value=True,
        )
        opt_dispute = st.checkbox(
            "⚖️ Giải quyết tranh chấp tại Tòa án nhân dân nơi Bên A đặt trụ sở / Trọng tài VIAC",
            value=True,
        )

        submitted = st.form_submit_button(
            "🚀 Sinh bản nháp hợp đồng dịch vụ chuẩn mẫu mauhopdongdichvu.md",
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
                    "Bảo vệ dữ liệu cá nhân theo Luật 91/2025/QH15 và bảo mật thông tin 02 năm"
                )
            if opt_ip:
                safeguards.append(
                    "Chuyển giao toàn quyền sở hữu trí tuệ kết quả dịch vụ khi thanh toán 100% kể cả sản phẩm AI"
                )
            if opt_penalty:
                safeguards.append(
                    "Phạt vi phạm 8% theo Luật Thương mại 2005 và Giới hạn bồi thường Cap Liability 100% giá trị hợp đồng"
                )
            if opt_dispute:
                safeguards.append(
                    "Giải quyết tranh chấp tại Tòa án nhân dân nơi Bên A đặt trụ sở hoặc VIAC"
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
                else "[●] VNĐ (Đã bao gồm VAT)"
            )
            dur_str = (
                duration.strip() if duration.strip() else "[●] tháng kể từ ngày ký"
            )
            notes_str = (
                custom_notes.strip()
                if custom_notes.strip()
                else "Soạn theo các điều khoản dịch vụ chuẩn."
            )

            user_input = {
                "contract_type": contract_type,
                "so_hop_dong": contract_num,
                "session_id": st.session_state.session_id,
                "ben_a": name_a,
                "ben_b": name_b,
                "gia_tri_hop_dong": val_str,
                "thoi_han": dur_str,
                "pham_vi_cong_viec_va_ghi_chu": notes_str,
                "dieu_khoan_bo_sung": ", ".join(safeguards) if safeguards else None,
            }

            with st.spinner(
                "Đang truy xuất mẫu FAISS VectorDB và sinh bản nháp hợp đồng..."
            ):
                try:
                    result = drafting_service.generate_contract_draft(user_input)
                    draft = result.get("draft")
                    st.session_state.last_draft = draft
                    st.session_state.last_risk_report = None
                    st.session_state.last_expired_alerts = []
                    st.session_state.pending_risk_draft = False
                except Exception:
                    logger.exception("Lỗi khi sinh bản nháp.")
                    st.error("Đã có lỗi trong quá trình sinh bản nháp.")

    if st.session_state.last_draft:
        st.divider()
        st.markdown(
            "<div class='feature-card' style='border-left:4px solid #38bdf8;margin-bottom:12px;'>"
            "<div class='feature-card-title'>📄 VĂN BẢN HỢP ĐỒNG DỰ THẢO (HỒ SƠ CHUẨN A4)</div>"
            "<div class='feature-card-desc'>Đã tổng hợp thành công các điều khoản chuẩn dựa trên mẫu FAISS và quy định của Bộ luật Dân sự 2015 & Luật Thương mại 2005.</div>"
            "</div>",
            unsafe_allow_html=True,
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
                    # Fallback về markdown renderer
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
                "⬇️ Tải về file Word (.docx) chuẩn mẫu",
                data=docx_bytes,
                file_name="hop_dong_du_thao.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        elif _docx_build_err:
            st.warning(_docx_build_err)
