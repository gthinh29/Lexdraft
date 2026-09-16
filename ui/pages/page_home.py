"""ui/pages/page_home.py

Màn hình "🏠 Trang chủ" — Tổng quan hệ thống Lexdraft và điều hướng nhanh.
"""

import streamlit as st


def render():
    """Render giao diện Trang chủ."""
    st.subheader("🏠 Chào mừng bạn đến với Lexdraft")

    st.markdown(
        "<div class='feature-card' style='border-left:4px solid #38bdf8;margin-bottom:16px;'>"
        "<div class='feature-card-title' style='font-size:1rem;'>Hệ thống Trợ lý Pháp lý Toàn diện cho Doanh nghiệp & Luật sư</div>"
        "<div class='feature-card-desc' style='font-size:0.85rem;line-height:1.7;'>"
        "Lexdraft ứng dụng mô hình ngôn ngữ lớn (LLM) kết hợp kỹ thuật truy xuất tăng cường (RAG) "
        "và cơ sở dữ liệu pháp luật Việt Nam (Bộ luật Dân sự 2015, Luật Thương mại 2005) "
        "nhằm chuẩn hóa quy trình soạn thảo, rà soát rủi ro và giải đáp câu hỏi pháp lý."
        "</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            "<div class='feature-card' style='min-height:180px;'>"
            "<div class='feature-card-icon'>📤</div>"
            "<div class='feature-card-title'>Gợi ý Rủi ro Pháp lý</div>"
            "<div class='feature-card-desc'>Tải lên file hợp đồng (.pdf, .docx), tự động rà soát từng điều khoản, phát hiện rủi ro và cảnh báo văn bản hết hiệu lực.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "🚀 Bắt đầu Rà soát", use_container_width=True, key="home_nav_risk"
        ):
            st.session_state["page"] = "📤 Gợi ý Rủi ro Pháp lý"
            st.rerun()

    with col2:
        st.markdown(
            "<div class='feature-card' style='min-height:180px;'>"
            "<div class='feature-card-icon'>📝</div>"
            "<div class='feature-card-title'>Soạn thảo Hợp đồng</div>"
            "<div class='feature-card-desc'>Nhập thông tin giao dịch cốt lõi, hệ thống tự động sinh bản nháp hợp đồng dịch vụ chuẩn mẫu A4 và xuất file Word (.docx).</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button(
            "📝 Soạn thảo ngay", use_container_width=True, key="home_nav_draft"
        ):
            st.session_state["page"] = "📝 Hỗ trợ Soạn thảo Hợp đồng"
            st.rerun()

    with col3:
        st.markdown(
            "<div class='feature-card' style='min-height:180px;'>"
            "<div class='feature-card-icon'>💬</div>"
            "<div class='feature-card-title'>Chatbot Hỏi – Đáp</div>"
            "<div class='feature-card-desc'>Tra cứu quy định pháp luật thương mại - dân sự, hoặc trao đổi chuyên sâu về nội dung hợp đồng đang làm việc.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        if st.button("💬 Mở Chatbot", use_container_width=True, key="home_nav_chat"):
            st.session_state["page"] = "💬 Chatbot Hỏi – Đáp (Q&A)"
            st.rerun()
