"""app.py

Lexdraft — Legal Contract Drafting & Risk Assessment System
Hệ thống Hỗ trợ Soạn thảo và Gợi ý Rủi ro Hợp đồng Dịch vụ bằng LLM kết hợp RAG.

Entry point ứng dụng Streamlit (Modular Architecture).
"""

import logging
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st  # noqa: E402

from ui.pages import page_chatbot, page_drafting, page_home, page_risk  # noqa: E402
from ui.styles import inject_styles  # noqa: E402

try:
    from modules.chatbot_qa import service as chatbot_service  # noqa: E402
except ImportError:
    chatbot_service = None

try:
    from modules.risk_assessment import service as risk_assessment_service  # noqa: E402
except ImportError:
    risk_assessment_service = None

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Streamlit Page Config & Styles
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Lexdraft — Legal Contract Drafting & Risk Assessment System",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()


# ---------------------------------------------------------------------------
# Warmup VectorDB
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Đang nạp dữ liệu pháp luật FAISS VectorDB...")
def warmup_indexes():
    status = {"law_index": False, "template_index": False}
    try:
        from modules.risk_assessment import law_validity_checker as lvc
        from modules.risk_assessment import retrieval

        retrieval._get_law_db()
        lvc.check_expired_laws("Luật Thương mại 2005")
        status["law_index"] = True
    except Exception:  # noqa: BLE001, S110
        pass
    try:
        from modules.drafting import retrieval as dr

        dr._get_template_db()
        status["template_index"] = True
    except Exception:  # noqa: BLE001, S110
        pass
    return status


warmup_status = warmup_indexes()


# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
def _init_state():
    defaults = {
        "session_id": str(uuid.uuid4()),
        "chat_history_ui": [],
        "last_draft": None,
        "last_risk_report": None,
        "last_expired_alerts": [],
        "risk_source_name": None,
        "page": "🏠 Trang chủ",
        "previous_page": None,
        "pending_risk_draft": False,
        "pending_risk_upload": False,
        "upload_tmp_path": None,
        "upload_file_name": None,
        "preview_zoom": 100,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_init_state()

# ---------------------------------------------------------------------------
# Page Definitions
# ---------------------------------------------------------------------------
PAGES = {
    "🏠 Trang chủ": page_home.render,
    "📤 Gợi ý Rủi ro Pháp lý": page_risk.render,
    "📝 Hỗ trợ Soạn thảo Hợp đồng": page_drafting.render,
    "💬 Chatbot Hỏi – Đáp (Q&A)": page_chatbot.render,
}

# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        "<h2 style='margin:0;padding:12px 0 2px 0;font-size:1.15rem;"
        "font-weight:700;color:#f1f5f9;'>⚖️ LEXDRAFT</h2>"
        "<div style='font-size:0.75rem;color:#94a3b8;margin-bottom:12px;'>"
        "Legal Contract System</div>",
        unsafe_allow_html=True,
    )
    st.divider()

    if "nav_page" in st.session_state:
        st.session_state["page"] = st.session_state.pop("nav_page")

    page = st.radio(
        "Chức năng chính",
        list(PAGES.keys()),
        key="page",
        label_visibility="collapsed",
    )

    # Tự động dọn báo cáo rủi ro khi chuyển sang màn hình Soạn thảo hợp đồng
    if (
        page == "📝 Hỗ trợ Soạn thảo Hợp đồng"
        and st.session_state.get("previous_page") != "📝 Hỗ trợ Soạn thảo Hợp đồng"
    ):
        st.session_state.last_risk_report = None
        st.session_state.last_expired_alerts = []
        st.session_state.risk_source_name = None
        st.session_state.pending_risk_draft = False
        st.session_state.pending_risk_upload = False
        st.session_state.upload_file_name = None
        st.session_state.upload_tmp_path = None
        if chatbot_service:
            chatbot_service.attach_contract_context(
                session_id=st.session_state.session_id,
                contract_chunks=[],
                risk_report=[],
            )

    st.session_state["previous_page"] = page

    st.divider()
    with st.expander("🔧 Trạng thái Hệ thống", expanded=False):
        st.write(f"Session: `{st.session_state.session_id[:8]}...`")
        st.write(
            "FAISS Law Index:",
            "✅ Active" if warmup_status.get("law_index") else "⚠️ Inactive",
        )
        st.write(
            "Template Index:",
            "✅ Active" if warmup_status.get("template_index") else "⚠️ Inactive",
        )
        st.write(
            "Risk Assessment:", "✅ Ready" if risk_assessment_service else "⚠️ Disabled"
        )
        st.write("LLM Engine:", "🟢 Gemini 3.6 Flash")

    st.divider()
    if st.button("🗑️ Xóa phiên làm việc", use_container_width=True):
        for k in ["chat_history_ui", "last_expired_alerts"]:
            st.session_state[k] = []
        for k in [
            "last_draft",
            "last_risk_report",
            "risk_source_name",
            "upload_tmp_path",
            "upload_file_name",
        ]:
            st.session_state[k] = None
        st.session_state.pending_risk_draft = False
        st.session_state.pending_risk_upload = False
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state["nav_page"] = "🏠 Trang chủ"
        st.rerun()
        if chatbot_service:
            chatbot_service.attach_contract_context(
                session_id=st.session_state.session_id,
                contract_chunks=[],
                risk_report=[],
            )
        st.rerun()

# ---------------------------------------------------------------------------
# Header Banner
# ---------------------------------------------------------------------------
st.markdown(
    "<div class='system-header-banner'>"
    "<div class='system-title'>Lexdraft — Legal Contract Drafting & Risk Assessment System</div>"
    "<div class='system-subtitle'>Hệ thống Hỗ trợ Soạn thảo và Gợi ý Rủi ro Hợp đồng Dịch vụ bằng LLM kết hợp RAG</div>"
    "<div class='system-status-pills'>"
    "<span class='status-pill'>⚡ LLM Engine: Gemini 3.6 Flash</span>"
    "<span class='status-pill'>📚 Knowledge: FAISS VectorDB (Dân sự & Thương mại)</span>"
    "<span class='status-pill'>🛡️ Validation: Tiered Expired Laws Checker</span>"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Page Routing
# ---------------------------------------------------------------------------
render_fn = PAGES.get(page)
if render_fn:
    render_fn()
else:
    st.error(f"Không tìm thấy trang: {page}")
