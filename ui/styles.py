"""ui/styles.py

Toàn bộ CSS giao diện Ultra Clean & Sleek Dark Modern Theme của Lexdraft.
"""

import streamlit as st

CSS_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Main App background */
.stApp { background-color: #0b1329; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0f172a;
    border-right: 1px solid #1e293b;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stRadio label {
    padding: 10px 14px; border-radius: 8px; cursor: pointer; transition: all 0.2s ease;
    font-weight: 500; font-size: 0.9rem; margin-bottom: 2px;
}
section[data-testid="stSidebar"] .stRadio label:hover {
    background: #1e293b;
}

/* Page Subheaders */
h3 {
    font-size: 1.25rem !important; font-weight: 700 !important; color: #f8fafc !important;
    margin-bottom: 16px !important; letter-spacing: -0.01em !important;
}

/* System Header Banner */
.system-header-banner {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}
.system-title {
    font-size: 1.25rem;
    font-weight: 800;
    color: #f8fafc;
    letter-spacing: -0.01em;
}
.system-subtitle {
    font-size: 0.82rem;
    color: #94a3b8;
    margin-top: 4px;
}
.system-status-pills {
    display: flex;
    gap: 8px;
    margin-top: 10px;
    flex-wrap: wrap;
}
.status-pill {
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    background: #0f172a;
    border: 1px solid #334155;
    color: #38bdf8;
}

/* Feature Info Grid */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}
.feature-card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 14px;
    text-align: left;
}
.feature-card-icon {
    font-size: 1.4rem;
    margin-bottom: 6px;
}
.feature-card-title {
    font-size: 0.85rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 4px;
}
.feature-card-desc {
    font-size: 0.78rem;
    color: #94a3b8;
    line-height: 1.5;
}

/* A4 Paper Document Viewer */
.a4-paper-container {
    background-color: #ffffff !important;
    color: #1e293b !important;
    font-family: 'Times New Roman', Times, serif !important;
    padding: 55px 75px !important;
    margin: 15px auto !important;
    max-width: 920px !important;
    border-radius: 4px !important;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.45), 0 0 1px rgba(0, 0, 0, 0.2) !important;
    border: 1px solid #cbd5e1 !important;
    line-height: 1.65 !important;
    max-height: 750px !important;
    overflow-y: auto !important;
}
.a4-paper-container p, .a4-paper-container div, .a4-paper-container td, .a4-paper-container li {
    color: #1e293b !important;
    font-family: 'Times New Roman', Times, serif !important;
    font-size: 1.05rem !important;
    line-height: 1.65 !important;
}
.a4-paper-container p {
    text-align: justify !important;
    text-indent: 2em !important;
    margin-bottom: 8px !important;
}
.a4-paper-container h1, .a4-paper-container .contract-title {
    text-align: center !important;
    font-size: 1.4rem !important;
    font-weight: bold !important;
    color: #0f172a !important;
    text-transform: uppercase !important;
    margin: 24px 0 6px 0 !important;
    display: block !important;
    width: 100% !important;
    text-indent: 0 !important;
    font-family: 'Times New Roman', Times, serif !important;
    box-sizing: border-box !important;
}
.a4-paper-container .contract-number {
    text-align: center !important;
    font-style: italic !important;
    font-size: 1.02rem !important;
    color: #334155 !important;
    margin: 0 0 20px 0 !important;
    display: block !important;
    width: 100% !important;
    text-indent: 0 !important;
    font-family: 'Times New Roman', Times, serif !important;
    box-sizing: border-box !important;
}
.a4-paper-container h2, .a4-paper-container h3, .a4-paper-container h4, .a4-paper-container h5, .a4-paper-container h6 {
    text-align: left !important;
    font-size: 1.1rem !important;
    font-weight: bold !important;
    color: #0f172a !important;
    text-transform: uppercase !important;
    margin: 18px 0 6px 0 !important;
    font-family: 'Times New Roman', Times, serif !important;
}
.a4-paper-container ul, .a4-paper-container ol {
    margin-bottom: 10px !important;
    padding-left: 28px !important;
}
.a4-paper-container table {
    width: 100% !important;
    margin-top: 16px !important;
    margin-bottom: 16px !important;
    border-collapse: collapse !important;
}
.a4-paper-container td, .a4-paper-container th {
    text-align: left !important;
    vertical-align: top !important;
    padding: 6px 10px !important;
    font-size: 1.02rem !important;
    width: auto !important;
}
.a4-paper-container td p, .a4-paper-container th p {
    text-indent: 0 !important;
    margin-bottom: 2px !important;
    text-align: left !important;
}
.a4-paper-container table.signature-table td, .a4-paper-container table.signature-table th {
    text-align: center !important;
    width: 50% !important;
}
.a4-paper-container table.signature-table td p {
    text-align: center !important;
}
/* Override Streamlit injected styles for centered paragraphs from docx renderer */
.a4-paper-container p[style*="text-align:center"] {
    text-align: center !important;
    text-indent: 0 !important;
    margin-left: 0 !important;
    margin-right: 0 !important;
    display: block !important;
    width: 100% !important;
}
/* Override Streamlit stMarkdown NOT to reset text-align on centered A4 paragraphs */
[data-testid="stMarkdownContainer"] .a4-paper-container p[style*="text-align:center"] {
    text-align: center !important;
    text-indent: 0 !important;
}
[data-testid="stMarkdownContainer"] .a4-paper-container p[style*="text-align:justify"] {
    text-align: justify !important;
}
[data-testid="stMarkdownContainer"] .a4-paper-container p {
    margin: 0 !important;
}
/* CSS classes cho docx paragraph renderer — line-height 1.5 chuẩn Word */
.a4-paper-container .a4p-center {
    text-align: center !important;
    text-indent: 0 !important;
    display: block !important;
    width: 100% !important;
    margin: 6px 0 !important;
    line-height: 1.5 !important;
    font-family: 'Times New Roman', Times, serif !important;
}
.a4-paper-container .a4p-justify {
    text-align: justify !important;
    text-indent: 2em !important;
    margin: 0 0 6px 0 !important;
    line-height: 1.5 !important;
    font-family: 'Times New Roman', Times, serif !important;
}
.a4-paper-container .a4p-left {
    text-align: left !important;
    text-indent: 0 !important;
    margin: 12px 0 4px 0 !important;
    line-height: 1.5 !important;
    font-family: 'Times New Roman', Times, serif !important;
    font-weight: bold !important;
    text-transform: uppercase !important;
}

/* Stepper Pipeline */
.stepper-container {
    display: flex; gap: 6px; margin: 12px 0; background: #0f172a;
    padding: 8px 12px; border-radius: 8px; border: 1px solid #1e293b;
    font-size: 0.75rem; font-weight: 600; color: #94a3b8; justify-content: space-between;
}
.stepper-step { color: #38bdf8; }

/* Custom Tabs Styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    background-color: #0f172a;
    padding: 6px;
    border-radius: 10px;
    border: 1px solid #1e293b;
}
.stTabs [data-baseweb="tab"] {
    height: 38px;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 600;
    color: #94a3b8;
    background-color: transparent;
    border: none !important;
    padding: 0 10px;
}
.stTabs [aria-selected="true"] {
    background-color: #1e293b !important;
    color: #38bdf8 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* Risk Panel Header */
.risk-panel-header {
    font-size: 1.05rem; font-weight: 700; color: #f8fafc;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 12px;
}

/* Overall Risk Meter Card */
.risk-meter-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid #334155; border-radius: 12px;
    padding: 14px 16px; margin-bottom: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}
.risk-meter-title {
    font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.05em; color: #94a3b8; margin-bottom: 6px;
}
.risk-level-badge {
    display: inline-block; padding: 4px 10px; border-radius: 20px;
    font-size: 0.8rem; font-weight: 700; text-transform: uppercase;
}
.risk-badge-high { background: #450a0a; color: #fca5a5; border: 1px solid #ef4444; }
.risk-badge-medium { background: #422006; color: #fde047; border: 1px solid #eab308; }
.risk-badge-safe { background: #064e3b; color: #6ee7b7; border: 1px solid #10b981; }

.risk-summary-metrics {
    display: flex; gap: 8px; margin-top: 10px; padding-top: 10px;
    border-top: 1px solid #1e293b; font-size: 0.78rem; font-weight: 600;
}
.metric-pill {
    flex: 1; text-align: center; padding: 6px 4px; border-radius: 6px; background: #0f172a;
}
.metric-pill-red { color: #fca5a5; border: 1px solid #450a0a; }
.metric-pill-yellow { color: #fde047; border: 1px solid #422006; }
.metric-pill-green { color: #6ee7b7; border: 1px solid #064e3b; }

/* Risk Card */
.risk-card {
    background: #131f37; border-left: 4px solid #ef4444;
    border-radius: 8px; padding: 14px 16px;
    margin-bottom: 12px; border-top: 1px solid #1e293b;
    border-right: 1px solid #1e293b; border-bottom: 1px solid #1e293b;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.risk-card:hover {
    border-color: #334155;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
.risk-card-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 8px;
}
.risk-card-title {
    font-size: 0.9rem; font-weight: 700; color: #f8fafc;
}
.risk-tag {
    font-size: 0.7rem; font-weight: 600; padding: 2px 8px; border-radius: 4px;
    background: #450a0a; color: #fca5a5; border: 1px solid #991b1b;
}
.risk-card-body {
    font-size: 0.83rem; color: #cbd5e1; line-height: 1.6; margin-bottom: 12px;
}
.risk-card-citations {
    font-size: 0.78rem; color: #94a3b8;
    background: #0f172a; border: 1px solid #1e293b; border-radius: 6px;
    padding: 8px 12px; line-height: 1.6;
}
.risk-card-citations b { color: #38bdf8; }

/* Expired Law Banner */
.expired-banner {
    background: linear-gradient(135deg, #450a0a, #2a0808);
    border: 1px solid #dc2626; border-radius: 10px;
    padding: 14px 16px; margin-bottom: 14px;
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.15);
}
.expired-banner-title { font-size: 0.9rem; font-weight: 700; color: #fca5a5; margin-bottom: 8px; }
.expired-banner-item { font-size: 0.8rem; color: #fecaca; margin: 4px 0; padding-left: 8px; }
.expired-banner-item b { color: #ffffff; }

/* Empty state */
.panel-empty {
    text-align: center; padding: 36px 20px; color: #64748b; font-size: 0.85rem;
    line-height: 1.6; background: #0f172a; border: 1px dashed #1e293b; border-radius: 12px;
    margin-top: 8px;
}
.panel-empty .icon { font-size: 2.2rem; margin-bottom: 10px; }

/* Safe Clause Card */
.safe-card {
    background: #0f172a; border-left: 4px solid #10b981;
    border-radius: 8px; padding: 12px 14px; margin-bottom: 8px;
    border-top: 1px solid #1e293b; border-right: 1px solid #1e293b; border-bottom: 1px solid #1e293b;
}
.safe-card-title { font-size: 0.85rem; font-weight: 600; color: #6ee7b7; }
.safe-card-body { font-size: 0.8rem; color: #94a3b8; margin-top: 4px; }

/* File uploader dropzone - minimalist centered text */
[data-testid="stFileUploaderDropzone"] svg {
    display: none !important;
}
[data-testid="stFileUploaderDropzone"] {
    text-align: center !important;
    justify-content: center !important;
    align-items: center !important;
    padding: 24px 16px !important;
    border: 1px dashed #334155 !important;
    border-radius: 10px !important;
}
/* Uniform Streamlit Buttons */
div[data-testid="stButton"] > button {
    height: 44px !important;
    min-height: 44px !important;
    max-height: 44px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 0 16px !important;
    margin: 0 !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] > button:hover {
    transform: translateY(-1px) !important;
}
</style>
"""


def inject_styles():
    """Nạp CSS toàn cục vào Streamlit app."""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
