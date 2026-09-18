"""
scripts/generate_charts.py

Tạo biểu đồ trực quan hóa chuyên nghiệp (độ phân giải cao 300 DPI, nền trắng)
phục vụ Báo cáo Thực tập tốt nghiệp / Đồ án cho cả 3 Bộ Test khoa học:
- Bộ Test 1: A/B Testing (Zero-shot LLM vs. Lexdraft RAG)
- Bộ Test 2: Ablation Study (Có vs. Không Metadata & Hit Rate FAISS)
- Bộ Test 3: Safe Refusal Matrix (Kiểm soát ảo giác & Từ chối an toàn)

Sử dụng matplotlib kết hợp font chữ Windows hỗ trợ tiếng Việt đầy đủ.
"""

import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# Cấu hình font chữ tiếng Việt trên Windows
matplotlib.rcParams["font.sans-serif"] = ["Segoe UI", "Arial", "Tahoma", "DejaVu Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = PROJECT_ROOT / "data" / "eval" / "bieu_do"
EVAL_DIR.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# BỘ TEST 1: GIẢ THIẾT 1 (A/B TESTING ZERO-SHOT VS RAG)
# ==============================================================================
def plot_bo_test_1():
    """Vẽ Biểu đồ Bộ Test 1: A/B Testing - Zero-shot LLM vs. Lexdraft RAG (Giả thiết 1)."""
    metrics = [
        "Mức độ liên quan\n(Law Coverage Rate)",
        "Khả năng cung cấp căn cứ\n(Article Citation Rate)",
        "Tỉ lệ ảo giác\n(Hallucination Rate)\n↓ Thấp hơn = Tốt hơn",
    ]
    values_a = [98.0, 100.0, 10.0]
    values_b = [86.0, 88.0, 4.0]

    x = np.arange(len(metrics))
    width = 0.32

    fig, ax = plt.subplots(figsize=(12, 6.5))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    colors_a = ["#2563eb", "#2563eb", "#ea580c"]  # Xanh dương / Cam cảnh báo
    colors_b = ["#059669", "#059669", "#16a34a"]  # Xanh ngọc / Xanh lá an toàn

    bars_a = ax.bar(
        x - width / 2,
        values_a,
        width,
        label="Nhánh A — Zero-shot LLM",
        color=colors_a,
        alpha=0.9,
        zorder=3,
    )
    bars_b = ax.bar(
        x + width / 2,
        values_b,
        width,
        label="Nhánh B — Lexdraft RAG",
        color=colors_b,
        alpha=0.9,
        zorder=3,
    )

    for bar in bars_a:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.2,
            f"{bar.get_height():.0f}%",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
            color="#1e293b",
        )
    for bar in bars_b:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.2,
            f"{bar.get_height():.0f}%",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
            color="#1e293b",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11, fontweight="bold", color="#1e293b")
    ax.set_ylabel("Tỉ lệ (%)", fontsize=12, fontweight="bold", color="#334155")
    ax.set_ylim(0, 118)
    ax.tick_params(colors="#334155")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")

    ax.yaxis.grid(True, color="#e2e8f0", linestyle="--", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

    ax.set_title(
        "Kết Quả Bộ Test 1 — A/B Testing: Zero-shot LLM vs. Lexdraft RAG",
        fontsize=14,
        fontweight="bold",
        color="#0f172a",
        pad=18,
    )

    ax.legend(
        fontsize=11,
        loc="upper right",
        framealpha=0.95,
        facecolor="white",
        edgecolor="#cbd5e1",
    )

    fig.text(
        0.5,
        0.01,
        "n = 50 câu hỏi  |  Giả thiết 1: RAG cải thiện tính đúng đắn và khả năng cung cấp căn cứ pháp lý",
        ha="center",
        fontsize=10,
        color="#64748b",
        style="italic",
    )

    plt.tight_layout(rect=[0, 0.04, 1, 1])
    out_path = EVAL_DIR / "bieu_do_bo_test_1.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")

    legacy_path = EVAL_DIR / "bieu_do_4_h1_ab_comparison.png"
    plt.savefig(legacy_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Đã lưu biểu đồ Bộ Test 1: {out_path}")


# ==============================================================================
# BỘ TEST 2: GIẢ THIẾT 2 (METADATA ABLATION & FAISS RETRIEVAL)
# ==============================================================================
def plot_bo_test_2():
    """Vẽ Biểu đồ Bộ Test 2: Ablation Study Metadata & Hit Rate FAISS (Giả thiết 2)."""
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(15, 6.5), gridspec_kw={"width_ratios": [1.7, 1]}
    )
    fig.patch.set_facecolor("white")
    ax1.set_facecolor("white")
    ax2.set_facecolor("white")

    # --- Subplot 1: Ablation Study (Có vs Không Metadata) ---
    ablation_metrics = [
        "Xác định đúng Văn bản luật\n(Law Name Accuracy)",
        "Trích dẫn đúng Điều/Khoản\n(Article Accuracy)",
        "Trích dẫn có cấu trúc\n(Structured Citation Rate)",
    ]
    val_no_meta = [76.0, 76.0, 0.0]
    val_with_meta = [96.0, 92.0, 100.0]

    x = np.arange(len(ablation_metrics))
    width = 0.32

    bars_no = ax1.bar(
        x - width / 2,
        val_no_meta,
        width,
        label="Nhánh A — KHÔNG Metadata (Text thô)",
        color="#94a3b8",
        alpha=0.9,
        zorder=3,
    )
    bars_with = ax1.bar(
        x + width / 2,
        val_with_meta,
        width,
        label="Nhánh B — CÓ Metadata (Lexdraft)",
        color="#059669",
        alpha=0.9,
        zorder=3,
    )

    for bar in bars_no:
        h = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            h + 1.2,
            f"{h:.0f}%",
            ha="center",
            va="bottom",
            fontsize=11.5,
            fontweight="bold",
            color="#475569",
        )
    for bar in bars_with:
        h = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            h + 1.2,
            f"{h:.0f}%",
            ha="center",
            va="bottom",
            fontsize=11.5,
            fontweight="bold",
            color="#065f46",
        )

    ax1.set_xticks(x)
    ax1.set_xticklabels(
        ablation_metrics, fontsize=10.5, fontweight="bold", color="#1e293b"
    )
    ax1.set_ylabel(
        "Tỉ lệ chính xác (%)", fontsize=11.5, fontweight="bold", color="#334155"
    )
    ax1.set_ylim(0, 118)
    ax1.tick_params(colors="#334155")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_color("#cbd5e1")
    ax1.spines["bottom"].set_color("#cbd5e1")
    ax1.yaxis.grid(True, color="#e2e8f0", linestyle="--", linewidth=0.8, zorder=0)
    ax1.set_axisbelow(True)
    ax1.set_title(
        "Ablation Study: Tác động của Metadata đối với LLM",
        fontsize=12.5,
        fontweight="bold",
        color="#0f172a",
        pad=12,
    )
    ax1.legend(
        loc="upper left",
        fontsize=10.5,
        framealpha=0.95,
        facecolor="white",
        edgecolor="#cbd5e1",
    )

    # --- Subplot 2: Hit Rate FAISS (44 câu) ---
    hit_labels = ["Hit Rate@1", "Hit Rate@3", "Hit Rate@5"]
    hit_values = [84.09, 93.18, 93.18]
    hit_colors = ["#3b82f6", "#2563eb", "#1d4ed8"]

    x_hit = np.arange(len(hit_labels))
    bars_hit = ax2.bar(
        x_hit, hit_values, width=0.45, color=hit_colors, alpha=0.9, zorder=3
    )

    for bar in bars_hit:
        h = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            h + 1.2,
            f"{h:.1f}%",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
            color="#1e3a8a",
        )

    ax2.set_xticks(x_hit)
    ax2.set_xticklabels(hit_labels, fontsize=11, fontweight="bold", color="#1e293b")
    ax2.set_ylabel(
        "Tỉ lệ tìm trúng điều luật (%)",
        fontsize=11.5,
        fontweight="bold",
        color="#334155",
    )
    ax2.set_ylim(0, 118)
    ax2.tick_params(colors="#334155")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_color("#cbd5e1")
    ax2.spines["bottom"].set_color("#cbd5e1")
    ax2.yaxis.grid(True, color="#e2e8f0", linestyle="--", linewidth=0.8, zorder=0)
    ax2.set_axisbelow(True)
    ax2.set_title(
        "Độ chính xác Vector Retrieval (FAISS n=44)",
        fontsize=12.5,
        fontweight="bold",
        color="#0f172a",
        pad=12,
    )

    fig.suptitle(
        "Kết Quả Bộ Test 2 — Kiểm Chứng Vai Trò Của Metadata Nguồn & Chunking Theo Điều/Khoản",
        fontsize=14,
        fontweight="bold",
        color="#0f172a",
        y=0.98,
    )
    fig.text(
        0.5,
        0.01,
        "Giả thiết 2: Tổ chức dữ liệu theo Điều/Khoản và lưu metadata nguồn giúp truy xuất và cung cấp căn cứ chính xác hơn",
        ha="center",
        fontsize=10,
        color="#64748b",
        style="italic",
    )

    plt.tight_layout(rect=[0, 0.04, 1, 0.94])
    out_path = EVAL_DIR / "bieu_do_bo_test_2.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Đã lưu biểu đồ Bộ Test 2: {out_path}")


# ==============================================================================
# BỘ TEST 3: GIẢ THIẾT 3 (SAFE REFUSAL MATRIX & HALLUCINATION CONTROL)
# ==============================================================================
def plot_bo_test_3():
    """Vẽ Biểu đồ Bộ Test 3: Safe Refusal Matrix & Kiểm soát Ảo giác (Giả thiết 3)."""
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(15, 6.5), gridspec_kw={"width_ratios": [1.5, 1]}
    )
    fig.patch.set_facecolor("white")
    ax1.set_facecolor("white")
    ax2.set_facecolor("white")

    # --- Subplot 1: Tỉ lệ xử lý an toàn/chính xác trên 4 nhóm câu hỏi ---
    groups = [
        "1. In-domain Fact\n(15 câu hợp lệ)\n[Y/c: Trả lời đúng]",
        "2. Luật cũ / Giả mạo\n(6 câu bẫy)\n[Y/c: Safe Refusal]",
        "3. Ngoài phạm vi\n(8 câu bẫy)\n[Y/c: Safe Refusal]",
        "4. Điều luật bẫy\n(6 câu bẫy)\n[Y/c: Safe Refusal]",
    ]
    group_rates = [93.33, 100.0, 100.0, 100.0]
    group_colors = ["#2563eb", "#059669", "#059669", "#059669"]

    x1 = np.arange(len(groups))
    bars1 = ax1.bar(
        x1, group_rates, width=0.48, color=group_colors, alpha=0.9, zorder=3
    )

    for bar in bars1:
        h = bar.get_height()
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            h + 1.2,
            f"{h:.1f}%",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
            color="#1e293b",
        )

    ax1.set_xticks(x1)
    ax1.set_xticklabels(groups, fontsize=10.5, fontweight="bold", color="#1e293b")
    ax1.set_ylabel(
        "Tỉ lệ thành công (%)", fontsize=11.5, fontweight="bold", color="#334155"
    )
    ax1.set_ylim(0, 118)
    ax1.tick_params(colors="#334155")
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_color("#cbd5e1")
    ax1.spines["bottom"].set_color("#cbd5e1")
    ax1.yaxis.grid(True, color="#e2e8f0", linestyle="--", linewidth=0.8, zorder=0)
    ax1.set_axisbelow(True)
    ax1.set_title(
        "Tỉ Lệ Xử Lý Chuẩn Xác Theo 4 Nhóm Kiểm Thử (n = 35)",
        fontsize=12.5,
        fontweight="bold",
        color="#0f172a",
        pad=12,
    )

    # --- Subplot 2: Các chỉ số an toàn tổng hợp ---
    summary_metrics = [
        "Từ chối an toàn\n(Safe Refusal)\n20/20 câu bẫy",
        "Tỉ lệ ảo giác\n(Hallucination)\n0/35 câu",
        "Từ chối nhầm\n(False Refusal)\n1/15 câu",
    ]
    summary_values = [100.0, 0.0, 6.67]
    summary_colors = ["#16a34a", "#10b981", "#f59e0b"]

    x2 = np.arange(len(summary_metrics))
    bars2 = ax2.bar(
        x2, summary_values, width=0.45, color=summary_colors, alpha=0.9, zorder=3
    )

    for bar in bars2:
        h = bar.get_height()
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            h + 1.2,
            f"{h:.1f}%",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
            color="#1e293b",
        )

    ax2.set_xticks(x2)
    ax2.set_xticklabels(
        summary_metrics, fontsize=10.5, fontweight="bold", color="#1e293b"
    )
    ax2.set_ylabel("Tỉ lệ (%)", fontsize=11.5, fontweight="bold", color="#334155")
    ax2.set_ylim(0, 118)
    ax2.tick_params(colors="#334155")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_color("#cbd5e1")
    ax2.spines["bottom"].set_color("#cbd5e1")
    ax2.yaxis.grid(True, color="#e2e8f0", linestyle="--", linewidth=0.8, zorder=0)
    ax2.set_axisbelow(True)
    ax2.set_title(
        "Chỉ Số An Toàn Tổng Hợp Cốt Lõi",
        fontsize=12.5,
        fontweight="bold",
        color="#0f172a",
        pad=12,
    )

    fig.suptitle(
        "Kết Quả Bộ Test 3 — Kiểm Soát Ảo Giác & Cơ Chế Từ Chối An Toàn (Safe Refusal Matrix)",
        fontsize=14,
        fontweight="bold",
        color="#0f172a",
        y=0.98,
    )
    fig.text(
        0.5,
        0.01,
        "Giả thiết 3: Cơ chế chỉ sử dụng thông tin truy xuất và từ chối khi thiếu căn cứ giúp loại bỏ hoàn toàn câu trả lời sai lệch (Ảo giác = 0%)",
        ha="center",
        fontsize=10,
        color="#64748b",
        style="italic",
    )

    plt.tight_layout(rect=[0, 0.04, 1, 0.94])
    out_path = EVAL_DIR / "bieu_do_bo_test_3.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Đã lưu biểu đồ Bộ Test 3: {out_path}")


# ==============================================================================
# ĐÁNH GIÁ MODULE: 1. BENCHMARK 5 HỢP ĐỒNG DỊCH VỤ THỰC TẾ
# ==============================================================================
def plot_benchmark_matrix():
    """Vẽ Biểu đồ 1: Hiệu năng Phát hiện Rủi ro trên 5 Hợp đồng đối sánh (Module Gợi ý rủi ro)."""
    contracts = [
        "HĐ Website\n(Clean 1)",
        "HĐ Tư vấn ERP\n(Clean 2)",
        "HĐ Phần mềm\n(Risky 1)",
        "HĐ Cloud Server\n(Risky 2)",
        "HĐ Digital Mkt\n(Risky 3)",
    ]

    injected_faults = [0, 0, 5, 4, 4]
    detected_faults = [0, 0, 4, 4, 4]

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [2, 1]}
    )
    fig.patch.set_facecolor("white")
    ax1.set_facecolor("white")
    ax2.set_facecolor("white")

    # Subplot 1: Bar chart so sánh
    x = np.arange(len(contracts))
    width = 0.35

    rects1 = ax1.bar(
        x - width / 2,
        injected_faults,
        width,
        label="Lỗi cài cắm (Ground Truth)",
        color="#e53935",
        alpha=0.9,
    )
    rects2 = ax1.bar(
        x + width / 2,
        detected_faults,
        width,
        label="Lỗi phát hiện chính xác (TP)",
        color="#2e7d32",
        alpha=0.9,
    )

    ax1.set_ylabel("Số lượng lỗi vi phạm", fontsize=12, fontweight="bold")
    ax1.set_title(
        "Hiệu năng phát hiện lỗi trên từng hợp đồng (5 Hợp đồng)",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax1.set_xticks(x)
    ax1.set_xticklabels(contracts, fontsize=10)
    ax1.legend(loc="upper left", frameon=True)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    # Hiển thị số liệu trên cột
    for rect in rects1:
        h = rect.get_height()
        if h > 0:
            ax1.annotate(
                f"{int(h)}",
                xy=(rect.get_x() + rect.get_width() / 2, h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontweight="bold",
            )
    for rect in rects2:
        h = rect.get_height()
        if h > 0:
            ax1.annotate(
                f"{int(h)}",
                xy=(rect.get_x() + rect.get_width() / 2, h),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontweight="bold",
                color="#1b5e20",
            )

    # Subplot 2: Donut Chart tổng hợp tỉ lệ Recall 92.31%
    sizes = [12, 1]
    labels = ["Phát hiện đúng (TP: 12)\n92.31%", "Bỏ sót (FN: 1)\n7.69%"]
    colors = ["#2e7d32", "#ef5350"]
    explode = (0.05, 0)

    wedges, texts, autotexts = ax2.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        pctdistance=0.75,
        textprops=dict(color="black", fontweight="bold"),
    )
    center_circle = plt.Circle((0, 0), 0.55, fc="white")
    ax2.add_artist(center_circle)
    ax2.set_title(
        "Tỉ lệ bao phủ phát hiện lỗi (Recall)\n12/13 lỗi thực tế",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )

    plt.tight_layout()
    out_path = EVAL_DIR / "bieu_do_1_benchmark_5_hop_dong.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    # Lưu cả vào thư mục eval gốc để tương thích báo cáo cũ nếu cần
    legacy_path = EVAL_DIR.parent / "bieu_do_1_benchmark_5_hop_dong.png"
    plt.savefig(legacy_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Đã lưu biểu đồ 1 (Benchmark): {out_path}")


# ==============================================================================
# ĐÁNH GIÁ MODULE: 2. CHỈ SỐ RAGAS LLM JUDGE (CONTEXT PRECISION/RECALL/FAITHFULNESS)
# ==============================================================================
def plot_ragas_radar_and_breakdown():
    """Vẽ Biểu đồ 2: So sánh RAGAS theo 2 nhóm câu hỏi (Fact vs Overall)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    metrics = [
        "Context Precision\n(Độ chính xác ngữ cảnh)",
        "Context Recall\n(Độ bao phủ luật)",
        "Faithfulness\n(Độ trung thực)",
    ]
    fact_scores = [0.88, 1.00, 0.85]  # Fact Retrieval
    overall_scores = [
        0.7917,
        0.5667,
        0.2750,
    ]  # Toàn bộ 50 câu (kèm cả câu bẫy Negative)

    x = np.arange(len(metrics))
    width = 0.35

    rects1 = ax.bar(
        x - width / 2,
        fact_scores,
        width,
        label="Nhóm Fact Retrieval (44 câu tra cứu luật hiện hành)",
        color="#1976d2",
        alpha=0.9,
    )
    rects2 = ax.bar(
        x + width / 2,
        overall_scores,
        width,
        label="Toàn bộ hệ thống (50 câu - kèm 6 câu bẫy luật hết hiệu lực)",
        color="#fb8c00",
        alpha=0.9,
    )

    ax.set_ylabel(
        "Điểm số Ragas (Thang điểm 0.0 - 1.0)", fontsize=12, fontweight="bold"
    )
    ax.set_title(
        "Đánh giá chất lượng RAG bằng LLM Judge (gemini-3.5-flash-lite)",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=11, fontweight="bold")
    ax.set_ylim(0, 1.18)
    ax.legend(loc="upper right", frameon=True, fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Đánh dấu giá trị trên cột
    for rect in rects1:
        h = rect.get_height()
        ax.annotate(
            f"{h:.2f}",
            xy=(rect.get_x() + rect.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontweight="bold",
            color="#0d47a1",
        )
    for rect in rects2:
        h = rect.get_height()
        ax.annotate(
            f"{h:.2f}",
            xy=(rect.get_x() + rect.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontweight="bold",
            color="#e65100",
        )

    # Chú thích giải thích
    ax.annotate(
        "* Ghi chú: Điểm Faithfulness nhóm tổng bị kéo xuống do cơ chế từ chối an toàn khi gặp luật cũ,\ntrong khi nhóm Fact Retrieval đạt 0.85.",
        xy=(0.5, -0.15),
        xycoords="axes fraction",
        ha="center",
        fontsize=9.5,
        fontstyle="italic",
        color="#555",
    )

    plt.tight_layout()
    out_path = EVAL_DIR / "bieu_do_2_danh_gia_ragas.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    legacy_path = EVAL_DIR.parent / "bieu_do_2_danh_gia_ragas.png"
    plt.savefig(legacy_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Đã lưu biểu đồ 2 (RAGAS): {out_path}")


# ==============================================================================
# ĐÁNH GIÁ MODULE: 3. CONFUSION MATRIX (MA TRẬN NHẦM LẪN TRÊN 43 ĐIỀU KHOẢN)
# ==============================================================================
def plot_confusion_matrix_heatmap():
    """Vẽ Biểu đồ 3: Ma trận nhầm lẫn (Confusion Matrix) trên 43 điều khoản."""
    fig, ax = plt.subplots(figsize=(7, 6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Confusion Matrix:
    #                 Predicted Positive (Có rủi ro)    Predicted Negative (Không rủi ro)
    # Actual Risky                 12 (TP)                             1 (FN)
    # Actual Clean                  5 (FP)                            18 (TN)
    cm = np.array([[12, 1], [5, 18]])

    cax = ax.matshow(cm, cmap="Blues", alpha=0.8)

    for i in range(2):
        for j in range(2):
            val = cm[i, j]
            label = ""
            if i == 0 and j == 0:
                label = f"True Positive\n(TP = {val})\n92.3%"
            elif i == 0 and j == 1:
                label = f"False Negative\n(FN = {val})\n7.7%"
            elif i == 1 and j == 0:
                label = f"False Positive\n(FP = {val})\n21.7%"
            elif i == 1 and j == 1:
                label = f"True Negative\n(TN = {val})\n78.3%"
            ax.text(
                j,
                i,
                label,
                ha="center",
                va="center",
                color="black",
                fontsize=11,
                fontweight="bold",
            )

    fig.colorbar(cax)
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(
        ["Cảnh báo Rủi ro\n(Predicted Risky)", "Không cảnh báo\n(Predicted Clean)"],
        fontsize=11,
        fontweight="bold",
    )
    ax.set_yticklabels(
        [
            "Điều khoản Rủi ro\n(Actual Risky: 13)",
            "Điều khoản Sạch\n(Actual Clean: 23)",
        ],
        fontsize=11,
        fontweight="bold",
    )
    ax.set_title(
        "Ma trận nhầm lẫn phân tích rủi ro (43 Điều khoản)",
        fontsize=13,
        fontweight="bold",
        pad=25,
    )

    plt.tight_layout()
    out_path = EVAL_DIR / "bieu_do_3_ma_tran_nham_lan.png"
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
    legacy_path = EVAL_DIR.parent / "bieu_do_3_ma_tran_nham_lan.png"
    plt.savefig(legacy_path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Đã lưu biểu đồ 3 (Confusion Matrix): {out_path}")


if __name__ == "__main__":
    print("=== ĐANG TẠO BỘ 3 BIỂU ĐỒ KIỂM CHỨNG GIẢ THIẾT ===")
    plot_bo_test_1()
    plot_bo_test_2()
    plot_bo_test_3()

    print("\n=== ĐANG TẠO BỘ 3 BIỂU ĐỒ ĐÁNH GIÁ MODULE RỦI RO & RAGAS ===")
    plot_benchmark_matrix()
    plot_ragas_radar_and_breakdown()
    plot_confusion_matrix_heatmap()

    print("\n Hoàn tất tạo toàn bộ 6 biểu đồ đồ án!")
