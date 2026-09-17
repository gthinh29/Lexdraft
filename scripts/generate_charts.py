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


if __name__ == "__main__":
    plot_bo_test_1()
    plot_bo_test_2()
    plot_bo_test_3()
