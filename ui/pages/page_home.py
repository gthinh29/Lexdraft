"""
ui/pages/page_home.py
Giao diện trang chủ gọn gàng theo bố cục lưới 2x2.
"""

import streamlit as st


def render():
    """Render giao diện Trang chủ tối giản, dễ quét thông tin."""
    st.subheader("🏠 Không gian Làm việc Pháp lý Lexdraft")
    st.caption(
        "Trợ lý soạn thảo, thẩm định rủi ro hợp đồng dịch vụ và tra cứu luật Việt Nam (BLDS 2015, LTM VBHN 2025, SHTT VBHN 2026, Luật 2025)."
    )

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown(
            "<div class='feature-card' style='min-height:135px;border-left:4px solid #ef4444;'>"
            "<div class='feature-card-title'>📤 1. Rà soát Rủi ro & Tự động Vá lỗi (Redline)</div>"
            "<div class='feature-card-desc'>Upload .pdf/.docx → Quét luật hết hiệu lực 3 tầng → Đối chiếu điều khoản → Xuất bản đã vá lỗi.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "🚀 Mở Rà soát Rủi ro", use_container_width=True, key="home_nav_risk"
        ):
            st.session_state["nav_page"] = "📤 Gợi ý Rủi ro Pháp lý"
            st.rerun()

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        st.markdown(
            "<div class='feature-card' style='min-height:135px;border-left:4px solid #a855f7;'>"
            "<div class='feature-card-title'>💬 3. Chatbot Hỏi – Đáp Pháp lý (Q&A)</div>"
            "<div class='feature-card-desc'>Tra cứu điều luật kèm trích dẫn chuẩn VBHN hoặc hỏi đáp trực tiếp trên hợp đồng đang mở.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "💬 Mở Chatbot Q&A", use_container_width=True, key="home_nav_chat"
        ):
            st.session_state["nav_page"] = "💬 Chatbot Hỏi – Đáp (Q&A)"
            st.rerun()

    with col2:
        st.markdown(
            "<div class='feature-card' style='min-height:135px;border-left:4px solid #38bdf8;'>"
            "<div class='feature-card-title'>📝 2. Soạn thảo theo Phân loại & Vị thế Pháp lý</div>"
            "<div class='feature-card-desc'>5 loại hợp đồng dịch vụ + 3 vị thế bảo vệ (Bên A / Bên B / Cân bằng) → Xem & tải chuẩn A4 (.docx).</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "📝 Mở Soạn thảo Hợp đồng", use_container_width=True, key="home_nav_draft"
        ):
            st.session_state["nav_page"] = "📝 Hỗ trợ Soạn thảo Hợp đồng"
            st.rerun()

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        st.markdown(
            "<div class='feature-card' style='min-height:135px;border-left:4px solid #10b981;'>"
            "<div class='feature-card-title'>⚔️ 4. Đối sánh Trực tiếp: LLM Thuần vs. Lexdraft</div>"
            "<div class='feature-card-desc'>Kiểm chứng song song trên 5 kịch bản bẫy pháp lý 2026 & chốt chặn Gatekeeper τ=0.75.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "⚔️ Mở Phòng Đối sánh A/B",
            use_container_width=True,
            type="primary",
            key="home_nav_ab_arena",
        ):
            st.session_state["nav_page"] = "⚔️ Đối sánh LLM Thuần vs. Lexdraft"
            st.rerun()
