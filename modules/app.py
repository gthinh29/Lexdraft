"""
app.py

Entry point Streamlit cho hệ thống hỗ trợ soạn thảo & gợi ý rủi ro hợp đồng
dịch vụ (Phần 10.1 - 10.5).

Chạy: streamlit run app.py
"""

import io
import logging
import tempfile
import uuid
from pathlib import Path

import streamlit as st

try:
    from modules.drafting import service as drafting_service
except ImportError:
    drafting_service = None

try:
    from modules.chatbot_qa import service as chatbot_service
except ImportError:
    chatbot_service = None

try:
    from modules.risk_assessment import service as risk_assessment_service  # Phần 8 - chưa build
except ImportError:
    risk_assessment_service = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Trợ lý Hợp đồng Dịch vụ", page_icon="📄", layout="wide")


# ---------------------------------------------------------------------------
# 10.2: Nạp 1 lần các FAISS index nặng khi app khởi động (@st.cache_resource).
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Đang nạp cơ sở tri thức (FAISS index)...")
def warmup_indexes() -> dict:
    """
    Kích hoạt sớm việc load law_index / template_index ngay khi app start,
    thay vì đợi tới lượt gọi service đầu tiên của người dùng (giảm độ trễ
    lần thao tác đầu). Mỗi module (drafting, chatbot_qa) tự cache VectorDB
    ở cấp module-level trong retrieval.py riêng của nó - hàm này chỉ "chạm"
    vào để trigger load sớm.
    """
    status = {"law_index": False, "template_index": False}

    if drafting_service is None:
        return status

    try:
        from modules.drafting import retrieval as drafting_retrieval

        drafting_retrieval._get_law_db()
        status["law_index"] = True
    except Exception:
        logger.warning("Chưa load được law_index (Phần 4/5 có thể chưa sẵn sàng).")

    try:
        from modules.drafting import retrieval as drafting_retrieval

        drafting_retrieval._get_template_db()
        status["template_index"] = True
    except Exception:
        logger.warning("Chưa load được template_index (Phần 4/5 có thể chưa sẵn sàng).")

    return status


warmup_status = warmup_indexes()


# ---------------------------------------------------------------------------
# Khởi tạo state cho phiên làm việc hiện tại của người dùng.
# ---------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history_ui" not in st.session_state:
    # Bản sao hiển thị cho UI - độc lập với ChatSession nội bộ của chatbot_qa (Phần 9).
    st.session_state.chat_history_ui = []

if "last_draft" not in st.session_state:
    st.session_state.last_draft = None

if "last_risk_report" not in st.session_state:
    st.session_state.last_risk_report = None


# ---------------------------------------------------------------------------
# 10.1: Sidebar điều hướng 3 tab
# ---------------------------------------------------------------------------
st.sidebar.title("📄 Trợ lý Hợp đồng Dịch vụ")
st.sidebar.caption("Soạn thảo & gợi ý rủi ro hợp đồng dịch vụ dựa trên RAG + Gemini")

page = st.sidebar.radio(
    "Chọn chức năng",
    ["📝 Soạn thảo", "📤 Upload Hợp đồng", "💬 Chatbot"],
)

with st.sidebar.expander("Trạng thái hệ thống"):
    st.write(f"session_id: `{st.session_state.session_id[:8]}...`")
    st.write("law_index:", "✅" if warmup_status.get("law_index") else "⚠️ chưa sẵn sàng")
    st.write("template_index:", "✅" if warmup_status.get("template_index") else "⚠️ chưa sẵn sàng")
    st.write("Module Gợi ý rủi ro (Phần 8):", "✅" if risk_assessment_service else "⚠️ chưa build")


# ---------------------------------------------------------------------------
# Helper dùng chung
# ---------------------------------------------------------------------------
def build_docx_bytes(draft_text: str) -> bytes:
    """Chuyển text bản nháp thành file .docx (bytes) để tải về."""
    if DocxDocument is None:
        raise RuntimeError("python-docx chưa được cài đặt (pip install python-docx).")

    document = DocxDocument()
    for line in draft_text.split("\n"):
        document.add_paragraph(line)

    buffer = io.BytesIO()
    document.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


def render_risk_report(risk_report) -> None:
    """
    Hiển thị báo cáo rủi ro dạng Card/Expander - dùng chung cho Tab Soạn thảo
    và Tab Upload.

    Format kỳ vọng (Phần 8): [{"dieu_khoan": ..., "rui_ro": ..., "can_cu": [...]}]
    """
    if not risk_report:
        st.info("Chưa có báo cáo rủi ro (Module Gợi ý rủi ro - Phần 8 - có thể chưa sẵn sàng).")
        return

    for i, item in enumerate(risk_report, start=1):
        dieu_khoan = item.get("dieu_khoan", f"Điều khoản #{i}")
        rui_ro = item.get("rui_ro", "Không xác định")
        can_cu = item.get("can_cu", [])

        with st.expander(f"⚖️ {dieu_khoan}"):
            st.markdown(f"**Đánh giá rủi ro:** {rui_ro}")
            if can_cu:
                st.markdown("**Căn cứ pháp lý:**")
                for cc in can_cu:
                    if isinstance(cc, dict):
                        label = cc.get("article", "N/A")
                        source = cc.get("source", "N/A")
                        st.markdown(f"- {label} ({source})")
                    else:
                        st.markdown(f"- {cc}")


def render_citations(citations) -> None:
    if not citations:
        return
    with st.expander("📚 Trích dẫn căn cứ"):
        for c in citations:
            if isinstance(c, dict):
                label = c.get("article", "N/A")
                source = c.get("source", "N/A")
                st.markdown(f"- {label} ({source})")
            else:
                st.markdown(f"- {c}")


def sync_context_to_chatbot(risk_report, contract_chunks=None) -> None:
    """
    Đồng bộ ngữ cảnh hợp đồng vừa có (từ soạn thảo hoặc upload) sang chatbot,
    để chuyển phiên sang Chế độ A ngay lập tức.
    """
    if chatbot_service is None or not risk_report:
        return
    try:
        chatbot_service.attach_contract_context(
            session_id=st.session_state.session_id,
            # TODO: risk_assessment.service.analyze_contract (Phần 8) hiện chỉ trả
            # về mảng rủi ro, chưa trả kèm contract_chunks. Khi Phần 8 hoàn thiện,
            # nên trả thêm contract_chunks để chatbot Chế độ A search được đúng
            # nội dung hợp đồng, không chỉ dựa vào risk_report tóm tắt.
            contract_chunks=contract_chunks or [],
            risk_report=risk_report,
        )
    except Exception:
        logger.exception("Không thể đồng bộ context sang chatbot_qa.")


# ---------------------------------------------------------------------------
# 10.3: TAB SOẠN THẢO
# ---------------------------------------------------------------------------
if page == "📝 Soạn thảo":
    st.header("📝 Soạn thảo hợp đồng dịch vụ")
    st.caption("Điền thông tin bên dưới, hệ thống sẽ sinh bản nháp kèm gợi ý rủi ro tự động.")

    with st.form("drafting_form"):
        contract_type = st.text_input(
            "Loại hợp đồng *",
            placeholder="VD: hợp đồng thiết kế website, hợp đồng tư vấn...",
        )

        col1, col2 = st.columns(2)
        with col1:
            party_a = st.text_input("Bên A (Bên thuê dịch vụ)")
            party_a_address = st.text_input("Địa chỉ Bên A")
        with col2:
            party_b = st.text_input("Bên B (Bên cung cấp dịch vụ)")
            party_b_address = st.text_input("Địa chỉ Bên B")

        scope_of_work = st.text_area("Phạm vi công việc", height=100)
        contract_value = st.text_input("Giá trị hợp đồng (VNĐ)")
        duration = st.text_input(
            "Thời hạn hợp đồng", placeholder="VD: 6 tháng, từ 01/01/2027 đến 30/06/2027"
        )

        submitted = st.form_submit_button("🚀 Sinh bản nháp")

    if submitted:
        if not contract_type.strip():
            st.error("Vui lòng nhập Loại hợp đồng.")
        elif drafting_service is None:
            st.error("Module Soạn thảo chưa sẵn sàng.")
        else:
            user_input_dict = {
                "contract_type": contract_type,
                "session_id": st.session_state.session_id,
                "ben_a": party_a,
                "dia_chi_ben_a": party_a_address,
                "ben_b": party_b,
                "dia_chi_ben_b": party_b_address,
                "pham_vi_cong_viec": scope_of_work,
                "gia_tri_hop_dong": contract_value,
                "thoi_han": duration,
            }
            # Loại field rỗng để prompt gọn hơn, tránh nhiễu LLM.
            user_input_dict = {k: v for k, v in user_input_dict.items() if v}

            with st.spinner("Đang truy xuất mẫu, luật liên quan và sinh bản nháp..."):
                try:
                    result = drafting_service.generate_contract_draft(user_input_dict)
                    st.session_state.last_draft = result.get("draft")
                    st.session_state.last_risk_report = result.get("risk_report")
                    sync_context_to_chatbot(result.get("risk_report"))
                except RuntimeError as e:
                    st.error(f"Hệ thống chưa sẵn sàng: {e}")
                except ValueError as e:
                    st.error(f"Dữ liệu đầu vào không hợp lệ: {e}")
                except Exception:
                    logger.exception("Lỗi không xác định khi sinh bản nháp.")
                    st.error("Đã có lỗi xảy ra, vui lòng thử lại.")

    if st.session_state.last_draft:
        st.subheader("📄 Bản nháp hợp đồng")
        st.text_area("Nội dung", st.session_state.last_draft, height=400)

        try:
            docx_bytes = build_docx_bytes(st.session_state.last_draft)
            st.download_button(
                label="⬇️ Tải về (.docx)",
                data=docx_bytes,
                file_name="hop_dong_du_thao.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        except RuntimeError as e:
            st.warning(str(e))

        st.subheader("⚠️ Gợi ý rủi ro cho bản nháp")
        render_risk_report(st.session_state.last_risk_report)


# ---------------------------------------------------------------------------
# 10.4: TAB UPLOAD HỢP ĐỒNG
# ---------------------------------------------------------------------------
elif page == "📤 Upload Hợp đồng":
    st.header("📤 Upload hợp đồng để phân tích rủi ro")
    st.caption("Hỗ trợ file .pdf (dạng text, không OCR) và .docx.")

    uploaded_file = st.file_uploader("Chọn file hợp đồng", type=["pdf", "docx"])

    if uploaded_file is not None and st.button("🔍 Phân tích rủi ro"):
        if risk_assessment_service is None:
            st.error("Module Gợi ý rủi ro (Phần 8) chưa sẵn sàng.")
        else:
            with st.spinner("Đang trích xuất, đối chiếu luật và phân tích từng điều khoản..."):
                tmp_path = None
                try:
                    # risk_assessment.service (Phần 8) đọc file qua document_reader,
                    # nên cần ghi tạm ra đĩa trước khi truyền path vào.
                    suffix = Path(uploaded_file.name).suffix
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name

                    risk_report = risk_assessment_service.analyze_contract(
                        file_path_or_text=tmp_path,
                        session_id=st.session_state.session_id,
                    )
                    st.session_state.last_risk_report = risk_report
                    sync_context_to_chatbot(risk_report)
                except Exception:
                    logger.exception("Lỗi khi phân tích rủi ro hợp đồng upload.")
                    st.error("Đã có lỗi xảy ra khi phân tích hợp đồng, vui lòng thử lại.")
                finally:
                    if tmp_path:
                        Path(tmp_path).unlink(missing_ok=True)

    if st.session_state.last_risk_report:
        st.subheader("⚖️ Kết quả phân tích rủi ro")
        render_risk_report(st.session_state.last_risk_report)


# ---------------------------------------------------------------------------
# 10.5: TAB CHATBOT
# ---------------------------------------------------------------------------
elif page == "💬 Chatbot":
    st.header("💬 Hỏi đáp pháp luật hợp đồng")

    if st.session_state.last_risk_report:
        st.success("Đang ở **Chế độ A**: chatbot có ngữ cảnh hợp đồng & báo cáo rủi ro vừa phân tích.")
    else:
        st.info("Đang ở **Chế độ B**: chatbot chỉ tra cứu luật chung (chưa có hợp đồng nào được soạn/upload).")

    for turn in st.session_state.chat_history_ui:
        with st.chat_message(turn["role"]):
            st.markdown(turn["text"])
            render_citations(turn.get("citations"))

    user_message = st.chat_input("Nhập câu hỏi của bạn...")

    if user_message:
        if chatbot_service is None:
            st.error("Module Chatbot chưa sẵn sàng.")
        else:
            st.session_state.chat_history_ui.append({"role": "user", "text": user_message})
            with st.chat_message("user"):
                st.markdown(user_message)

            with st.chat_message("assistant"):
                with st.spinner("Đang tra cứu và soạn câu trả lời..."):
                    try:
                        result = chatbot_service.handle_chat(
                            message=user_message,
                            session_id=st.session_state.session_id,
                        )
                        answer = result.get("answer", "")
                        citations = result.get("citations", [])

                        st.markdown(answer)
                        render_citations(citations)

                        st.session_state.chat_history_ui.append(
                            {"role": "assistant", "text": answer, "citations": citations}
                        )
                    except RuntimeError as e:
                        error_msg = f"Hệ thống chưa sẵn sàng: {e}"
                        st.error(error_msg)
                        st.session_state.chat_history_ui.append(
                            {"role": "assistant", "text": error_msg}
                        )
                    except Exception:
                        logger.exception("Lỗi không xác định trong chatbot.")
                        error_msg = "Đã có lỗi xảy ra, vui lòng thử lại."
                        st.error(error_msg)
                        st.session_state.chat_history_ui.append(
                            {"role": "assistant", "text": error_msg}
                        )
