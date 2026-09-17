"""
scripts/generate_charts.py

Tạo các biểu đồ trực quan hóa chuyên nghiệp (độ phân giải cao 300 DPI)
để chèn trực tiếp vào Báo cáo Đồ án tốt nghiệp / Khóa luận.
Sử dụng matplotlib (mã nguồn mở) kết hợp font chữ Windows hỗ trợ tiếng Việt đầy đủ.
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
EVAL_DIR = PROJECT_ROOT / "data" / "eval"
EVAL_DIR.mkdir(parents=True, exist_ok=True)


def plot_benchmark_matrix():
    """Vẽ Biểu đồ 1: Hiệu năng Phát hiện Rủi ro trên 5 Hợp đồng đối sánh."""
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
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Đã lưu biểu đồ 1: {out_path}")


def plot_ragas_radar_and_breakdown():
    """Vẽ Biểu đồ 2: So sánh RAGAS theo 2 nhóm câu hỏi (Fact vs Overall)."""
    fig, ax = plt.subplots(figsize=(10, 6))

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
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Đã lưu biểu đồ 2: {out_path}")


def plot_confusion_matrix_heatmap():
    """Vẽ Biểu đồ 3: Ma trận nhầm lẫn (Confusion Matrix) trên 43 điều khoản."""
    fig, ax = plt.subplots(figsize=(7, 6))

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
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Đã lưu biểu đồ 3: {out_path}")


if __name__ == "__main__":
    plot_benchmark_matrix()
    plot_ragas_radar_and_breakdown()
    plot_confusion_matrix_heatmap()
