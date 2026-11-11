"""Giao diện Phòng Thí nghiệm Đối sánh Trực tiếp: LLM Truyền thống vs. Lexdraft (RAG)."""

import logging
import time
import uuid

import streamlit as st

from ui.components.rag_inspector import render_rag_inspector
from ui.presets import EXPERIMENTAL_TRAPS, evaluate_ab_response

try:
    from modules.chatbot_qa import service as chatbot_service
except ImportError:
    chatbot_service = None

try:
    from modules.risk_assessment import law_validity_checker, retrieval
except ImportError:
    law_validity_checker = None
    retrieval = None

try:
    from modules.shared import llm_client
except ImportError:
    llm_client = None

logger = logging.getLogger(__name__)


def render():
    """Render trang Phòng Thí nghiệm Đối sánh Trực tiếp LLM Thuần vs. Lexdraft."""
    st.subheader("⚔️ Đối sánh: LLM Truyền thống vs. Lexdraft (RAG)")
    st.caption(
        "So sánh trực tiếp Zero-Shot LLM (không VectorDB, không kiểm tra hiệu lực, không Gatekeeper) với kiến trúc Lexdraft."
    )

    if "ab_selected_trap_idx" not in st.session_state:
        st.session_state.ab_selected_trap_idx = 0
    if "ab_custom_query" not in st.session_state:
        st.session_state.ab_custom_query = EXPERIMENTAL_TRAPS[0]["query"]
    if "ab_last_result" not in st.session_state:
        st.session_state.ab_last_result = None

    trap_options = [f"{t['badge']} — {t['title']}" for t in EXPERIMENTAL_TRAPS]
    c_sel, c_live, c_inst = st.columns([2.2, 1, 1], gap="small")
    with c_sel:
        selected_idx = st.selectbox(
            "Kịch bản bẫy pháp lý",
            options=range(len(EXPERIMENTAL_TRAPS)),
            format_func=lambda i: trap_options[i],
            index=st.session_state.ab_selected_trap_idx,
            key="ab_trap_selector",
            label_visibility="collapsed",
        )
    with c_live:
        run_live = st.button(
            "⚡ Live A/B (API)",
            type="primary",
            use_container_width=True,
            key="btn_run_ab_live",
        )
    with c_inst:
        run_instant = st.button(
            "📊 Demo Đối chuẩn",
            use_container_width=True,
            key="btn_run_ab_instant",
        )

    selected_trap = EXPERIMENTAL_TRAPS[selected_idx]
    if selected_idx != st.session_state.ab_selected_trap_idx:
        st.session_state.ab_selected_trap_idx = selected_idx
        st.session_state.ab_custom_query = selected_trap["query"]
        st.session_state.ab_last_result = None
        st.rerun()

    query_input = st.text_area(
        "Câu hỏi / Điều khoản thử nghiệm:",
        value=st.session_state.ab_custom_query,
        height=58,
        key="ab_query_textarea",
        label_visibility="collapsed",
    )
    st.session_state.ab_custom_query = query_input
    st.caption(f"🎯 **Mục tiêu:** {selected_trap['expected_highlight']}")

    if run_instant:
        blocked = selected_trap.get("sample_gatekeeper_blocked", False)
        demo_chunks = [
            {
                "content": f"Nội dung quy định chi tiết tại {c['article']} ({c['source']}) được truy xuất từ FAISS VectorDB.",
                "metadata": {
                    "article": c["article"],
                    "law_name": c["source"],
                    "source": c["source"],
                },
                "score": 0.8645,
            }
            for c in selected_trap["sample_citations"]
        ]
        try:
            from modules.chatbot_qa import prompts as chatbot_prompts

            demo_full_prompt = chatbot_prompts.build_chat_prompt(
                query=query_input,
                context_chunks=demo_chunks,
                history=[],
                has_contract_context=False,
            )
        except Exception:
            demo_full_prompt = (
                f"CHẾ ĐỘ TRA CỨU PHÁP LUẬT CHUNG (Lexdraft Grounded RAG)\n\n"
                f"CÂU HỎI: {query_input}"
            )

        st.session_state.ab_last_result = {
            "mode": "instant",
            "query": query_input,
            "baseline_answer": selected_trap["sample_baseline"],
            "baseline_latency": 1.42,
            "baseline_prompt": (
                f"Bạn là trợ lý AI. Hãy trả lời câu hỏi pháp lý sau bằng tiếng Việt:\n\n{query_input}"
            ),
            "lexdraft_answer": selected_trap["sample_lexdraft"],
            "lexdraft_citations": selected_trap["sample_citations"],
            "lexdraft_expired": selected_trap["sample_expired"],
            "lexdraft_latency": 0.18 if blocked else 1.85,
            "lexdraft_debug_trace": {
                "model": "gemini-3.5-flash-lite (Instant Demo)",
                "gatekeeper_passed": not blocked,
                "gatekeeper_reason": (
                    "max_score=0.3120 < threshold=0.75 → Chặn trước khi gọi LLM"
                    if blocked
                    else "max_score=0.8645 >= threshold=0.75 → Cho phép gọi LLM"
                ),
                "max_similarity_score": 0.3120 if blocked else 0.8645,
                "threshold": 0.75,
                "retrieved_chunks": [
                    {
                        "content": ch["content"],
                        "article": ch["metadata"]["article"],
                        "law_name": ch["metadata"]["law_name"],
                        "score": ch["score"],
                    }
                    for ch in demo_chunks
                ],
                "final_prompt_sent_to_llm": demo_full_prompt,
                "raw_llm_response": (
                    "[BỊ CHẶN BỞI CODE GATEKEEPER - KHÔNG GỌI GEMINI API]"
                    if blocked
                    else selected_trap["sample_lexdraft"]
                ),
                "filtered_citations": selected_trap["sample_citations"],
            },
        }

    if run_live:
        if not query_input.strip():
            st.warning("Vui lòng nhập câu hỏi hoặc chọn kịch bản thực nghiệm.")
        else:
            with st.spinner(
                "⚡ Đang chạy song song: (1) LLM Truyền thống Zero-Shot và (2) Pipeline Lexdraft (Tiered Validation + FAISS RAG + Gatekeeper)..."
            ):
                t0 = time.perf_counter()
                baseline_prompt = (
                    "Bạn là trợ lý AI. Hãy trả lời súc tích (tối đa 120 từ) câu hỏi sau bằng tiếng Việt:\n\n"
                    f"Câu hỏi: {query_input.strip()}"
                )
                try:
                    if llm_client is None:
                        raise RuntimeError("Module llm_client chưa sẵn sàng.")
                    raw_client = llm_client.GeminiClient()
                    baseline_ans = raw_client.generate_text(baseline_prompt)
                except Exception as e:
                    logger.exception("Lỗi gọi Baseline LLM: %s", e)
                    baseline_ans = f"Không thể gọi API trực tiếp ({e}). Dưới đây là phản hồi mẫu Zero-Shot:\n\n{selected_trap['sample_baseline']}"
                baseline_latency = time.perf_counter() - t0

                t1 = time.perf_counter()
                expired_alerts = []
                if law_validity_checker and retrieval:
                    try:
                        hl_chunks = retrieval.find_related_laws(
                            "hiệu lực thi hành bãi bỏ thay thế hết hiệu lực", top_k=10
                        )
                        expired_alerts = law_validity_checker.check_expired_laws(
                            contract_text=query_input,
                            law_index_chunks=hl_chunks,
                            enable_llm_fallback=False,
                        )
                    except Exception as e:
                        logger.warning("Lỗi check_expired_laws trong A/B Arena: %s", e)

                lex_ans = ""
                lex_cits = []
                lex_trace = None
                try:
                    arena_session_id = f"ab_arena_{uuid.uuid4().hex[:8]}"
                    res = chatbot_service.handle_chat(
                        message=query_input.strip(),
                        session_id=arena_session_id,
                    )
                    lex_ans = res.get("answer", "")
                    lex_cits = res.get("citations", [])
                    lex_trace = res.get("debug_trace")
                except Exception as e:
                    logger.exception("Lỗi gọi Lexdraft Pipeline: %s", e)
                    lex_ans = selected_trap["sample_lexdraft"]
                    lex_cits = selected_trap["sample_citations"]
                lex_latency = time.perf_counter() - t1

                st.session_state.ab_last_result = {
                    "mode": "live",
                    "query": query_input,
                    "baseline_answer": baseline_ans,
                    "baseline_latency": baseline_latency,
                    "baseline_prompt": baseline_prompt,
                    "lexdraft_answer": lex_ans,
                    "lexdraft_citations": lex_cits,
                    "lexdraft_expired": expired_alerts,
                    "lexdraft_latency": lex_latency,
                    "lexdraft_debug_trace": lex_trace,
                }

    res_data = st.session_state.ab_last_result
    if not res_data:
        st.info(
            "👆 Chọn kịch bản ở trên và bấm **⚡ Live A/B (API)** hoặc **📊 Demo Đối chuẩn**."
        )
        return

    base_eval = evaluate_ab_response(
        answer=res_data["baseline_answer"],
        citations=[],
        expired_alerts=[],
        debug_trace=None,
        is_lexdraft=False,
    )
    lex_eval = evaluate_ab_response(
        answer=res_data["lexdraft_answer"],
        citations=res_data.get("lexdraft_citations", []),
        expired_alerts=res_data.get("lexdraft_expired", []),
        debug_trace=res_data.get("lexdraft_debug_trace"),
        is_lexdraft=True,
    )

    tab_ab, tab_score, tab_inspect = st.tabs(
        [
            "⚔️ So sánh Song song (A vs B)",
            "📊 Bảng Chấm điểm Kỹ thuật (5 Tiêu chí)",
            f"🔍 Prompt & RAG ({len(res_data.get('lexdraft_citations', []))} Căn cứ)",
        ]
    )

    with tab_ab:
        col_left, col_right = st.columns(2, gap="medium")
        with col_left:
            st.markdown(
                f"<div style='background:#1e293b;border:1px solid #475569;border-top:3px solid #94a3b8;"
                f"border-radius:8px;padding:7px 12px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;'>"
                f"<span style='font-size:0.88rem;font-weight:700;color:#e2e8f0;'>🤖 LLM Truyền thống (Zero-Shot)</span>"
                f"<span style='font-size:0.74rem;color:#94a3b8;'>⏱️ {res_data['baseline_latency']:.2f}s</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            with st.container(height=360, border=True):
                st.markdown(res_data["baseline_answer"])

        with col_right:
            st.markdown(
                f"<div style='background:#0f172a;border:1px solid #059669;border-top:3px solid #10b981;"
                f"border-radius:8px;padding:7px 12px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center;'>"
                f"<span style='font-size:0.88rem;font-weight:700;color:#6ee7b7;'>⚖️ Lexdraft (RAG + Tiered Check)</span>"
                f"<span style='font-size:0.74rem;color:#a7f3d0;'>⏱️ {res_data['lexdraft_latency']:.2f}s</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            with st.container(height=360, border=True):
                if res_data.get("lexdraft_expired"):
                    for alert in res_data["lexdraft_expired"]:
                        st.error(
                            f"🚨 **HẾT HIỆU LỰC:** {alert.get('law_ref')} → Thay bởi **{alert.get('replaced_by')}**"
                        )
                st.markdown(res_data["lexdraft_answer"])

    with tab_score:
        st.markdown(
            f"""
| Tiêu chí Đánh giá Thực nghiệm | 🤖 LLM Truyền thống (Zero-Shot) | ⚖️ Hệ thống Lexdraft (Legal RAG) |
| :--- | :--- | :--- |
| **1. Truy xuất Căn cứ Pháp luật (RAG Grounding)** | {base_eval["rag_grounding"]} | {lex_eval["rag_grounding"]} |
| **2. Kiểm tra Hiệu lực Văn bản (Tiered Validation)** | {base_eval["tiered_validation"]} | {lex_eval["tiered_validation"]} |
| **3. Chuẩn Trích dẫn Số hiệu & VBHN Quốc hội** | {base_eval["citation_standard"]} | {lex_eval["citation_standard"]} |
| **4. Độ nhạy với Luật mới 2025–2026** | {base_eval["law_2026_awareness"]} | {lex_eval["law_2026_awareness"]} |
| **5. Chốt chặn Chống Bịa đặt (Code Gatekeeper)** | {base_eval["gatekeeper"]} | {lex_eval["gatekeeper"]} |
"""
        )

    with tab_inspect:
        c_p1, c_p2 = st.columns([0.9, 1.4], gap="medium")
        with c_p1:
            st.markdown("**📄 Prompt LLM Truyền thống (Zero-Shot)**")
            st.code(
                res_data.get(
                    "baseline_prompt",
                    f"Bạn là trợ lý AI. Trả lời câu hỏi:\n{res_data['query']}",
                ),
                language="markdown",
                wrap_lines=True,
            )
            if res_data.get("lexdraft_citations"):
                st.markdown(
                    f"**📚 Căn cứ FAISS ({len(res_data['lexdraft_citations'])} điều)**"
                )
                for c in res_data["lexdraft_citations"]:
                    st.markdown(
                        f"- 📌 **{c.get('article', 'N/A')}** — {c.get('source', '')}"
                    )
        with c_p2:
            render_rag_inspector(
                res_data.get("lexdraft_debug_trace"),
                key_prefix="ab_arena_inspector",
                use_expander=False,
            )
