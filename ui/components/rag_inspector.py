"""
ui/components/rag_inspector.py
Component White-Box RAG & Prompt Inspector dùng chung cho cả 3 phân hệ (Soạn thảo, Rủi ro, Chatbot).
Cho phép giảng viên/người dùng kiểm tra trực tiếp trên giao diện:
1. Các chunks thực tế được truy xuất từ FAISS VectorDB kèm Cosine Similarity Score & Metadata.
2. Trạng thái kiểm tra của Code Gatekeeper (max_score vs threshold).
3. Toàn văn Exact Prompt (System Instruction + RAG Context + User Query) gửi vào LLM.
4. Raw Response từ LLM và kết quả lọc Regex Citations.
"""

from typing import Any, Dict, Optional
import streamlit as st


def render_rag_inspector(
    debug_trace: Optional[Dict[str, Any]],
    title: str = "🔍 X-Ray Inspector: Xem dữ liệu RAG & Prompt thực tế gửi cho LLM",
    expanded: bool = False,
    key_prefix: str = "inspector",
) -> None:
    """
    Hiển thị hộp kiểm tra (White-Box Inspector) cho một lần gọi LLM + RAG.
    """
    if not debug_trace:
        return

    with st.expander(title, expanded=expanded):
        model_name = debug_trace.get("model", "gemini-3.5-flash-lite")
        threshold = debug_trace.get("threshold", 0.0)
        max_score = debug_trace.get("max_similarity_score")
        passed = debug_trace.get("gatekeeper_passed", True)
        reason = debug_trace.get("gatekeeper_reason", "")
        chunks = debug_trace.get("retrieved_chunks", [])
        final_prompt = debug_trace.get("final_prompt_sent_to_llm", "")
        raw_resp = debug_trace.get("raw_llm_response", "")
        filtered_cits = debug_trace.get("filtered_citations", [])

        # Thanh thông số tổng quan
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("🤖 LLM Engine", model_name)
        with c2:
            st.metric("📚 Chunks từ FAISS", f"{len(chunks)} chunks")
        with c3:
            score_str = (
                f"{max_score:.3f}" if isinstance(max_score, (int, float)) else "N/A"
            )
            st.metric(
                "🎯 Max Cosine Score", score_str, delta=f"Ngưỡng τ = {threshold:.2f}"
            )
        with c4:
            status_txt = "✅ PASS (Gọi LLM)" if passed else "🛑 BLOCKED (0 Token)"
            st.metric("🛡️ Code Gatekeeper", status_txt)

        if reason:
            st.caption(f"ℹ️ **Gatekeeper Log:** `{reason}`")

        tab_chunks, tab_prompt, tab_raw = st.tabs(
            [
                f"📦 1. Dữ liệu RAG Truy xuất ({len(chunks)} Chunks)",
                "📝 2. Toàn văn Prompt gửi LLM (Exact Prompt)",
                "⚙️ 3. Raw LLM Output & Lọc Citation",
            ]
        )

        with tab_chunks:
            if not chunks:
                st.warning("Không có chunk nào được truy xuất từ VectorDB.")
            else:
                st.caption(
                    "Dưới đây là chính xác các đoạn văn bản luật/hợp đồng được FAISS trả về và bơm vào ngữ cảnh cho LLM:"
                )
                for idx, ch in enumerate(chunks, 1):
                    art = ch.get("article", "N/A")
                    law = ch.get("law_name", "N/A")
                    num = ch.get("law_number", "")
                    vbhn = ch.get("vbhn_number", "")
                    sc = ch.get("score")
                    sc_badge = (
                        f"Score: {sc:.4f}"
                        if isinstance(sc, (int, float))
                        else "Score: N/A"
                    )
                    vbhn_badge = f" | VBHN: {vbhn}" if vbhn else ""
                    st.markdown(
                        f"**#{idx}. [{art}] — {law} {num}{vbhn_badge}** (`{sc_badge}`)"
                    )
                    st.code(ch.get("content", ""), language="markdown")

        with tab_prompt:
            st.caption(
                "Đây là chuỗi văn bản cuối cùng (sau khi ghép System Instruction + Căn cứ pháp lý RAG + Yêu cầu) được truyền vào hàm `client.models.generate_content()`:"
            )
            st.text_area(
                "Exact Final Prompt",
                value=final_prompt,
                height=320,
                key=f"{key_prefix}_final_prompt",
                label_visibility="collapsed",
            )

        with tab_raw:
            st.markdown("**1. Phản hồi thô từ Gemini (`raw_llm_response`):**")
            st.text_area(
                "Raw LLM Response",
                value=raw_resp,
                height=200,
                key=f"{key_prefix}_raw_resp",
                label_visibility="collapsed",
            )
            st.markdown(
                f"**2. Căn cứ pháp lý giữ lại sau bộ lọc Regex Cited-Only (`{len(filtered_cits)}` điều luật thực sự được nhắc tới):**"
            )
            st.json(filtered_cits)
