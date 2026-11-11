"""
ui/components/rag_inspector.py
Component White-Box RAG & Prompt Inspector gọn nhẹ dùng chung cho cả 3 phân hệ.
"""

from typing import Any, Dict, Optional
import streamlit as st


def _render_inspector_body(debug_trace: Dict[str, Any], key_prefix: str) -> None:
    model_name = debug_trace.get("model", "gemini-3.5-flash-lite")
    threshold = debug_trace.get("threshold", 0.0)
    max_score = debug_trace.get("max_similarity_score")
    passed = debug_trace.get("gatekeeper_passed", True)
    chunks = debug_trace.get("retrieved_chunks", [])
    final_prompt = debug_trace.get("final_prompt_sent_to_llm") or debug_trace.get(
        "prompt", ""
    )
    raw_resp = debug_trace.get("raw_llm_response", "")
    filtered_cits = debug_trace.get("filtered_citations", [])

    score_str = f"{max_score:.3f}" if isinstance(max_score, (int, float)) else "N/A"
    is_api_error = isinstance(raw_resp, str) and raw_resp.startswith("ERROR:")
    if passed:
        status_badge = "<span style='color:#6ee7b7;font-weight:700;'>✅ PASS</span>"
    elif is_api_error:
        status_badge = "<span style='color:#fbbf24;font-weight:700;'>⚠️ API ERROR</span>"
    else:
        status_badge = "<span style='color:#fca5a5;font-weight:700;'>🛑 BLOCKED</span>"

    # 1 thanh thông số siêu gọn (thay thế 4 metric card cồng kềnh)
    st.markdown(
        f"<div style='background:#0f172a;border:1px solid #1e293b;border-radius:7px;"
        f"padding:6px 12px;margin-bottom:6px;font-size:0.78rem;color:#cbd5e1;"
        f"display:flex;flex-wrap:wrap;gap:14px;align-items:center;'>"
        f"<span>🤖 <b>{model_name}</b></span>"
        f"<span>📚 <b>{len(chunks)}</b> chunks</span>"
        f"<span>🎯 Score: <b>{score_str}</b> (τ={threshold:.2f})</span>"
        f"<span>{status_badge}</span>"
        f"<span>📎 <b>{len(filtered_cits)}</b> căn cứ giữ lại</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    tab_chunks, tab_prompt, tab_raw = st.tabs(
        [
            f"📦 RAG Chunks ({len(chunks)})",
            f"📝 Prompt ({len(final_prompt):,} ký tự)",
            f"⚙️ Output & Căn cứ ({len(filtered_cits)})",
        ]
    )

    with tab_chunks:
        if not chunks:
            st.caption("Không có chunk nào từ VectorDB.")
        else:
            with st.container(height=280, border=False):
                for idx, ch in enumerate(chunks, 1):
                    art = ch.get("article", "N/A")
                    law = ch.get("law_name", "N/A")
                    vbhn = ch.get("vbhn_number", "")
                    sc = ch.get("score")
                    sc_txt = f"{sc:.3f}" if isinstance(sc, (int, float)) else "N/A"
                    vbhn_txt = f" • {vbhn}" if vbhn else ""
                    with st.expander(
                        f"#{idx} [{art}] {law}{vbhn_txt} — Score {sc_txt}",
                        expanded=False,
                    ):
                        st.code(
                            ch.get("content", ""),
                            language="markdown",
                            wrap_lines=True,
                        )

    with tab_prompt:
        if final_prompt:
            with st.container(height=280, border=False):
                st.code(final_prompt, language="markdown", wrap_lines=True)
        else:
            st.caption("Chưa có nội dung Prompt.")

    with tab_raw:
        with st.container(height=280, border=False):
            if filtered_cits:
                st.markdown("**Căn cứ trích xuất:**")
                for c in filtered_cits:
                    if isinstance(c, dict):
                        st.markdown(
                            f"- 📌 **{c.get('article', 'N/A')}** — {c.get('source', '')}"
                        )
                    else:
                        st.markdown(f"- 📌 {c}")
            else:
                st.caption("Không có căn cứ trích xuất.")

            st.markdown("**Raw LLM Output:**")
            if raw_resp:
                st.code(raw_resp, language="markdown", wrap_lines=True)
            else:
                st.caption("Không có phản hồi thô.")


def render_rag_inspector(
    debug_trace: Optional[Dict[str, Any]],
    title: str = "🔍 RAG & Prompt Inspector",
    expanded: bool = False,
    key_prefix: str = "inspector",
    use_expander: bool = True,
) -> None:
    """Hiển thị hộp kiểm tra White-Box gọn nhẹ cho một lần gọi LLM + RAG."""
    if not debug_trace:
        return

    if use_expander:
        with st.expander(title, expanded=expanded):
            _render_inspector_body(debug_trace, key_prefix)
    else:
        _render_inspector_body(debug_trace, key_prefix)
