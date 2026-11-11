"""Quản lý tập trung trạng thái phiên làm việc (st.session_state) cho toàn bộ giao diện."""

import uuid
from typing import Any

import streamlit as st


def init_app_state() -> None:
    """Khởi tạo các khóa mặc định của session_state khi mở ứng dụng."""
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


def reset_workspace_state(chatbot_service: Any = None) -> None:
    """Xóa toàn bộ dữ liệu phiên làm việc và đưa người dùng về Trang chủ."""
    for k in ("chat_history_ui", "last_expired_alerts"):
        st.session_state[k] = []
    for k in (
        "last_draft",
        "last_draft_citations",
        "last_draft_debug_trace",
        "last_draft_meta",
        "last_risk_report",
        "last_risk_debug_trace",
        "last_redraft_debug_trace",
        "risk_source_name",
        "upload_tmp_path",
        "upload_file_name",
        "contract_chunks",
    ):
        st.session_state[k] = None
    st.session_state.pop("drafting_persisted", None)
    st.session_state.pending_risk_draft = False
    st.session_state.pending_risk_upload = False
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state["nav_page"] = "🏠 Trang chủ"
    if chatbot_service:
        chatbot_service.attach_contract_context(
            session_id=st.session_state.session_id,
            contract_chunks=[],
            risk_report=[],
        )


def clear_active_risk_contract(chatbot_service: Any = None) -> None:
    """Gỡ bỏ hợp đồng đang rà soát và đặt lại ngữ cảnh Chatbot."""
    for k in (
        "upload_file_name",
        "upload_tmp_path",
        "last_risk_report",
        "last_risk_debug_trace",
        "last_redraft_debug_trace",
        "risk_source_name",
        "contract_chunks",
    ):
        st.session_state[k] = None
    st.session_state.last_expired_alerts = []
    st.session_state.pending_risk_upload = False
    st.session_state["_uploader_key"] = st.session_state.get("_uploader_key", 0) + 1
    if chatbot_service:
        chatbot_service.attach_contract_context(
            session_id=st.session_state.session_id,
            contract_chunks=[],
            risk_report=[],
        )


def persist_drafting_keys(keys_dict: dict) -> None:
    """Lưu bản sao không gắn widget vào session_state['drafting_persisted'] để giữ dữ liệu khi chuyển trang."""
    persisted = st.session_state.setdefault("drafting_persisted", {})
    persisted.update(keys_dict)


def on_drafting_category_change(categories: dict) -> None:
    """Đồng bộ tiêu đề, số hợp đồng và thông số đặc thù khi người dùng đổi Phân loại."""
    cat_id = st.session_state.get("selected_taxonomy_cat")
    cat = categories.get(cat_id, {})
    stance_id = st.session_state.get("selected_taxonomy_stance", "protect_party_a")
    title = cat.get("name", "Hợp đồng Dịch vụ")
    code = f"01/2026/{cat.get('default_code_suffix', 'HĐDV')}"
    st.session_state["draft_contract_type"] = title
    st.session_state["draft_contract_num"] = code
    updates = {
        "selected_taxonomy_cat": cat_id,
        "selected_taxonomy_stance": stance_id,
        "draft_contract_type": title,
        "draft_contract_num": code,
    }
    persisted = st.session_state.get("drafting_persisted", {})
    for sf in cat.get("specific_fields", []):
        sf_widget_key = f"dyn_{cat_id}_{sf['key']}"
        if sf_widget_key not in st.session_state:
            val = persisted.get(sf_widget_key, sf.get("default", ""))
            st.session_state[sf_widget_key] = val
            updates[sf_widget_key] = val
    persist_drafting_keys(updates)


def apply_drafting_preset(categories: dict, preset: dict) -> None:
    """Điền nhanh một kịch bản mẫu vào form soạn thảo."""
    cat_id = preset["cat_id"]
    cat = categories.get(cat_id, {})
    opts = preset.get("opts", {})

    updates = {
        "selected_taxonomy_cat": cat_id,
        "selected_taxonomy_stance": preset["stance_id"],
        "draft_contract_type": cat.get("name", "Hợp đồng Dịch vụ"),
        "draft_contract_num": preset["contract_num"],
        "draft_party_a": preset["party_a"],
        "draft_party_b": preset["party_b"],
        "draft_value": preset["value"],
        "draft_duration": preset["duration"],
        "draft_notes": preset["notes"],
        "draft_opt_pdp": opts.get("pdp", True),
        "draft_opt_ip": opts.get("ip", True),
        "draft_opt_penalty": opts.get("penalty", True),
        "draft_opt_dispute": opts.get("dispute", True),
    }

    preset_spec = preset.get("specific_fields", {})
    for sf in cat.get("specific_fields", []):
        sf_key = sf["key"]
        updates[f"dyn_{cat_id}_{sf_key}"] = preset_spec.get(
            sf_key, sf.get("default", "")
        )

    for k, v in updates.items():
        st.session_state[k] = v
    persist_drafting_keys(updates)


def clear_draft_form(categories: dict) -> None:
    """Xóa trắng các trường văn bản trong form soạn thảo."""
    cat_id = st.session_state.get("selected_taxonomy_cat")
    cat = categories.get(cat_id, {})

    updates = {
        "draft_contract_type": cat.get("name", "Hợp đồng Dịch vụ"),
        "draft_contract_num": f"01/2026/{cat.get('default_code_suffix', 'HĐDV')}",
        "draft_party_a": "",
        "draft_party_b": "",
        "draft_value": "",
        "draft_duration": "",
        "draft_notes": "",
    }
    for sf in cat.get("specific_fields", []):
        updates[f"dyn_{cat_id}_{sf['key']}"] = ""

    for k, v in updates.items():
        st.session_state[k] = v
    persist_drafting_keys(updates)


def init_drafting_form_state(categories: dict, stances: dict) -> None:
    """Khởi tạo và khôi phục các khóa session_state cho form soạn thảo từ bản sao bền vững."""
    cat_keys = list(categories.keys()) if categories else ["software_dev"]
    stance_keys = list(stances.keys()) if stances else ["balanced"]
    persisted = st.session_state.setdefault("drafting_persisted", {})

    if "selected_taxonomy_cat" not in st.session_state:
        saved_cat = persisted.get("selected_taxonomy_cat")
        st.session_state["selected_taxonomy_cat"] = (
            saved_cat if saved_cat in cat_keys else cat_keys[0]
        )
    elif st.session_state["selected_taxonomy_cat"] not in cat_keys:
        st.session_state["selected_taxonomy_cat"] = cat_keys[0]

    if "selected_taxonomy_stance" not in st.session_state:
        saved_stance = persisted.get("selected_taxonomy_stance")
        st.session_state["selected_taxonomy_stance"] = (
            saved_stance if saved_stance in stance_keys else stance_keys[0]
        )
    elif st.session_state["selected_taxonomy_stance"] not in stance_keys:
        st.session_state["selected_taxonomy_stance"] = stance_keys[0]

    cat_id = st.session_state["selected_taxonomy_cat"]
    cat = categories.get(cat_id, {})

    st.session_state.setdefault(
        "draft_contract_type",
        persisted.get("draft_contract_type", cat.get("name", "Hợp đồng Dịch vụ")),
    )
    st.session_state.setdefault(
        "draft_contract_num",
        persisted.get(
            "draft_contract_num", f"01/2026/{cat.get('default_code_suffix', 'HĐDV')}"
        ),
    )
    for k in (
        "draft_party_a",
        "draft_party_b",
        "draft_value",
        "draft_duration",
        "draft_notes",
    ):
        st.session_state.setdefault(k, persisted.get(k, ""))

    for opt_k in (
        "draft_opt_pdp",
        "draft_opt_ip",
        "draft_opt_penalty",
        "draft_opt_dispute",
    ):
        st.session_state.setdefault(opt_k, persisted.get(opt_k, True))

    for sf in cat.get("specific_fields", []):
        sf_wkey = f"dyn_{cat_id}_{sf['key']}"
        st.session_state.setdefault(
            sf_wkey, persisted.get(sf_wkey, sf.get("default", ""))
        )

    st.session_state.setdefault("preview_zoom", persisted.get("preview_zoom", 100))
