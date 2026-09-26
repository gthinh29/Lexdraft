"""ui/pages/page_chatbot.py

Màn hình "💬 Chatbot Hỏi – Đáp (Q&A)":
- Chatbot Trợ lý Tra cứu Pháp lý & Phân tích Hợp đồng
- Dual Mode:
  + Chế độ A: Theo dõi ngữ cảnh hợp đồng vừa tải lên / phân tích rủi ro
  + Chế độ B: Tra cứu Pháp luật Chung (Bộ luật Dân sự 2015 & Luật Thương mại 2005)
- Hiển thị trích dẫn pháp lý Grounded Citations
"""

import logging
from pathlib import Path

import streamlit as st

try:
    from modules.chatbot_qa import service as chatbot_service
except ImportError:
    chatbot_service = None

logger = logging.getLogger(__name__)


def render():
    """Render giao diện chính của trang Chatbot Hỏi – Đáp (Q&A)."""
    st.subheader("💬 Chatbot Trợ lý Tra cứu Pháp lý (Q&A)")

    # Thẻ trạng thái chế độ Chatbot
    if st.session_state.last_risk_report or st.session_state.upload_file_name:
        src = (
            st.session_state.upload_file_name
            or st.session_state.risk_source_name
            or "Hợp đồng hiện tại"
        )
        st.info(
            f"🟢 **Chế độ A — Trợ lý đang theo dõi ngữ cảnh:** **{src}**\n\n"
            f"Chatbot sẽ ưu tiên đối chiếu đúng file hợp đồng này kết hợp với quy định pháp luật."
        )
    else:
        st.caption(
            "🔵 **Chế độ B — Tra cứu Pháp luật Chung:** Chatbot sẵn sàng giải đáp các quy định pháp luật Thương mại & Dân sự."
        )

    # KHUNG CHAT HISTORY
    for turn in st.session_state.chat_history_ui:
        with st.chat_message(turn["role"]):
            st.markdown(turn["text"])
            if turn.get("citations"):
                cit_md = "\n".join(
                    "- 📎 **{}** — {}".format(
                        c.get("article", "N/A"), c.get("source", "")
                    )
                    if isinstance(c, dict)
                    else f"- 📎 {c}"
                    for c in turn["citations"]
                )
                with st.expander("📚 Căn cứ pháp lý trích xuất", expanded=False):
                    st.markdown(cit_md)

    user_message = st.chat_input(
        "Nhập câu hỏi của bạn về hợp đồng hoặc quy định pháp luật..."
    )

    if user_message:
        if chatbot_service is None:
            st.error("Module Chatbot chưa sẵn sàng.")
        else:
            st.session_state.chat_history_ui.append(
                {"role": "user", "text": user_message}
            )
            with st.chat_message("user"):
                st.markdown(user_message)

            # Đảm bảo context hợp đồng luôn được đồng bộ nếu người dùng vừa upload file ở tab Risk
            if chatbot_service and (
                st.session_state.get("contract_chunks")
                or (
                    st.session_state.get("upload_tmp_path")
                    and Path(st.session_state.upload_tmp_path).exists()
                )
            ):
                chunks = st.session_state.get("contract_chunks")
                if not chunks and st.session_state.get("upload_tmp_path"):
                    try:
                        from modules.shared.document_reader import read_document
                        from modules.shared.chunking import chunk_by_article

                        parsed_text = read_document(st.session_state.upload_tmp_path)
                        if parsed_text and parsed_text.strip():
                            chunks = chunk_by_article(
                                parsed_text,
                                {
                                    "source": st.session_state.get(
                                        "upload_file_name", "contract"
                                    ),
                                    "doc_type": "contract",
                                },
                            )
                            st.session_state.contract_chunks = chunks
                    except Exception as e:
                        logger.warning(
                            "Không thể parse contract trong page_chatbot: %s", e
                        )

                if chunks:
                    chatbot_service.attach_contract_context(
                        session_id=st.session_state.session_id,
                        contract_chunks=chunks,
                        risk_report=st.session_state.get("last_risk_report") or [],
                    )

            with (
                st.chat_message("assistant"),
                st.spinner("Đang tra cứu cơ sở tri thức và suy luận..."),
            ):
                try:
                    result = chatbot_service.handle_chat(
                        message=user_message,
                        session_id=st.session_state.session_id,
                    )
                    answer = result.get("answer", "")
                    citations = result.get("citations", [])

                    st.markdown(answer)

                    if citations:
                        cit_md = "\n".join(
                            "- 📎 **{}** — {}".format(
                                c.get("article", "N/A"), c.get("source", "")
                            )
                            if isinstance(c, dict)
                            else f"- 📎 {c}"
                            for c in citations
                        )
                        with st.expander(
                            "📚 Căn cứ pháp lý trích xuất", expanded=False
                        ):
                            st.markdown(cit_md)

                    st.session_state.chat_history_ui.append(
                        {
                            "role": "assistant",
                            "text": answer,
                            "citations": citations,
                        }
                    )
                except Exception:
                    logger.exception("Lỗi chatbot.")
                    err = "Đã có lỗi trong quá trình tra cứu. Vui lòng thử lại."
                    st.error(err)
                    st.session_state.chat_history_ui.append(
                        {"role": "assistant", "text": err}
                    )
