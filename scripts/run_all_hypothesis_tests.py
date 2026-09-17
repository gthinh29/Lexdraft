"""
scripts/run_all_hypothesis_tests.py

Master Runner thực thi toàn bộ 3 bộ test tương ứng với 3 Giả thiết khoa học (Mục 3.3):
- Bộ Test 1: evaluation/test_h1_ab_comparison.py (Giả thiết 1: A/B Testing Zero-shot vs RAG)
- Bộ Test 2: evaluation/test_h2_metadata_ablation.py (Giả thiết 2: Ablation Study Có vs Không Metadata)
- Bộ Test 3: evaluation/test_h3_hallucination_refusal.py (Giả thiết 3: Ma trận Từ chối an toàn & Hallucination)

Và tự động tổng hợp kết quả, vẽ biểu đồ so sánh xuất ra thư mục data/eval/.
"""

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path

# Cấu hình UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVAL_DIR = PROJECT_ROOT / "data" / "eval"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("run_all_tests")

PYTHON_EXEC = sys.executable


def run_command(cmd_args):
    logger.info("Chạy lệnh: %s", " ".join(cmd_args))
    proc = subprocess.run(cmd_args, cwd=str(PROJECT_ROOT))
    if proc.returncode != 0:
        logger.error("Lệnh thất bại với exit code %d", proc.returncode)
    else:
        logger.info("Hoàn tất lệnh thành công.")


def generate_summary_chart():
    """Tạo biểu đồ trực quan hóa kết quả của cả 3 bộ test."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.rcParams["font.family"] = "sans-serif"
        plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

        # -------------------------------------------------------------
        # 1. Biểu đồ Bộ Test 1: A/B Testing
        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # 1. Biểu đồ Bộ Test 1: A/B Testing
        # -------------------------------------------------------------
        rep1_path = EVAL_DIR / "bao_cao_ket_qua" / "report_h1_ab.json"
        if not rep1_path.exists():
            rep1_path = EVAL_DIR / "report_h1_ab.json"
        if rep1_path.exists():
            with open(rep1_path, "r", encoding="utf-8") as f:
                d1 = json.load(f)["summary"]
            labels1 = [
                "Độ bao phủ luật\n(Law Coverage)",
                "Trích dẫn Điều/Khoản\n(Article Citation)",
            ]
            zero_shot = [
                d1["branch_a_zero_shot"]["law_coverage_rate"],
                d1["branch_a_zero_shot"]["article_citation_rate"],
            ]
            rag = [
                d1["branch_b_lexdraft_rag"]["law_coverage_rate"],
                d1["branch_b_lexdraft_rag"]["article_citation_rate"],
            ]
            x = range(len(labels1))
            width = 0.35
            ax1.bar(
                [i - width / 2 for i in x],
                zero_shot,
                width=width,
                label="Zero-shot LLM",
                color="#e74c3c",
            )
            ax1.bar(
                [i + width / 2 for i in x],
                rag,
                width=width,
                label="Lexdraft (LLM+RAG)",
                color="#2ecc71",
            )
            ax1.set_title("Giả thiết 1: A/B Testing (Zero-shot vs RAG)")
            ax1.set_ylabel("Tỷ lệ (%)")
            ax1.set_ylim(0, 115)
            ax1.set_xticks(x)
            ax1.set_xticklabels(labels1)
            ax1.legend()
            for i in x:
                ax1.text(
                    i - width / 2,
                    zero_shot[i] + 2,
                    f"{zero_shot[i]}%",
                    ha="center",
                    fontsize=9,
                )
                ax1.text(
                    i + width / 2,
                    rag[i] + 2,
                    f"{rag[i]}%",
                    ha="center",
                    fontsize=9,
                    fontweight="bold",
                )

        # -------------------------------------------------------------
        # 2. Biểu đồ Bộ Test 2: Ablation Study Metadata
        # -------------------------------------------------------------
        rep2_path = EVAL_DIR / "bao_cao_ket_qua" / "report_h2_metadata.json"
        if not rep2_path.exists():
            rep2_path = EVAL_DIR / "report_h2_metadata.json"
        if rep2_path.exists():
            with open(rep2_path, "r", encoding="utf-8") as f:
                d2 = json.load(f)["metadata_ablation_study"]["summary"]
            labels2 = [
                "Xác định đúng Luật",
                "Trích dẫn đúng Điều",
                "Bóc tách Citation Cấu trúc",
            ]
            no_meta = [
                d2["branch_a_no_metadata"]["law_name_accuracy_rate"],
                d2["branch_a_no_metadata"]["article_accuracy_rate"],
                d2["branch_a_no_metadata"]["structured_citation_rate"],
            ]
            with_meta = [
                d2["branch_b_with_metadata"]["law_name_accuracy_rate"],
                d2["branch_b_with_metadata"]["article_accuracy_rate"],
                d2["branch_b_with_metadata"]["structured_citation_rate"],
            ]
            x = range(len(labels2))
            width = 0.35
            ax2.bar(
                [i - width / 2 for i in x],
                no_meta,
                width=width,
                label="Không có Metadata",
                color="#f39c12",
            )
            ax2.bar(
                [i + width / 2 for i in x],
                with_meta,
                width=width,
                label="Có Metadata (Lexdraft)",
                color="#3498db",
            )
            ax2.set_title("Giả thiết 2: Ablation Study (Tác dụng Metadata)")
            ax2.set_ylabel("Tỷ lệ (%)")
            ax2.set_ylim(0, 115)
            ax2.set_xticks(x)
            ax2.set_xticklabels(labels2)
            ax2.legend()
            for i in x:
                ax2.text(
                    i - width / 2,
                    no_meta[i] + 2,
                    f"{no_meta[i]}%",
                    ha="center",
                    fontsize=9,
                )
                ax2.text(
                    i + width / 2,
                    with_meta[i] + 2,
                    f"{with_meta[i]}%",
                    ha="center",
                    fontsize=9,
                    fontweight="bold",
                )

        # -------------------------------------------------------------
        # 3. Biểu đồ Bộ Test 3: Safe Refusal
        # -------------------------------------------------------------
        rep3_path = EVAL_DIR / "bao_cao_ket_qua" / "report_h3_refusal.json"
        if not rep3_path.exists():
            rep3_path = EVAL_DIR / "report_h3_refusal.json"
        if rep3_path.exists():
            with open(rep3_path, "r", encoding="utf-8") as f:
                d3 = json.load(f)["summary"]
            groups = [
                "In-domain\n(Trả lời đúng)",
                "Luật cũ / Giả\n(Safe Refusal)",
                "Ngoài phạm vi\n(Safe Refusal)",
                "Điều không có\n(Safe Refusal)",
            ]
            rates = [
                d3["in_domain_fact"]["correct_answered_rate"],
                d3["outdated_or_fake_law"]["safe_refusal_rate"],
                d3["out_of_domain"]["safe_refusal_rate"],
                d3["non_existent_article"]["safe_refusal_rate"],
            ]
            colors = ["#2ecc71", "#9b59b6", "#1abc9c", "#34495e"]
            bars = ax3.bar(groups, rates, color=colors, width=0.5)
            ax3.set_title("Giả thiết 3: Kiểm soát Hallucination & Từ chối an toàn")
            ax3.set_ylabel("Tỷ lệ thành công (%)")
            ax3.set_ylim(0, 115)
            for bar, rate in zip(bars, rates):
                ax3.text(
                    bar.get_x() + bar.get_width() / 2,
                    rate + 2,
                    f"{rate}%",
                    ha="center",
                    fontsize=9,
                    fontweight="bold",
                )

        plt.tight_layout()
        chart_dir = EVAL_DIR / "bieu_do"
        chart_dir.mkdir(parents=True, exist_ok=True)
        chart_path = chart_dir / "bieu_do_kiem_chung_3_gia_thiet.png"
        plt.savefig(str(chart_path), dpi=300)
        logger.info("Đã lưu biểu đồ tổng hợp 3 giả thiết tại: %s", chart_path)
    except Exception as e:
        logger.error("Lỗi khi vẽ biểu đồ tổng hợp: %s", e)


def main():
    parser = argparse.ArgumentParser(description="Runner chạy toàn bộ 3 bộ test")
    parser.add_argument("--h1-samples", type=int, default=30, help="Số mẫu test H1")
    parser.add_argument("--h2-samples", type=int, default=20, help="Số mẫu test H2")
    args = parser.parse_args()

    # Chạy Bộ test 1
    run_command(
        [
            PYTHON_EXEC,
            "evaluation/test_h1_ab_comparison.py",
            "--sample-limit",
            str(args.h1_samples),
        ]
    )

    # Chạy Bộ test 2
    run_command(
        [
            PYTHON_EXEC,
            "evaluation/test_h2_metadata_ablation.py",
            "--sample-limit",
            str(args.h2_samples),
        ]
    )

    # Chạy Bộ test 3
    run_command([PYTHON_EXEC, "evaluation/test_h3_hallucination_refusal.py"])

    # Tạo biểu đồ tổng hợp
    generate_summary_chart()


if __name__ == "__main__":
    main()
