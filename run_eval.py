"""run_eval.py

Script 1 lệnh tiện lợi để thẩm định Golden Dataset và chạy kiểm thử RAG.
Cách sử dụng:
    python run_eval.py --validate-only    # Chỉ kiểm tra chất lượng file dataset
    python run_eval.py                    # Chạy toàn bộ pipeline kiểm thử và xuất báo cáo CSV
"""

import argparse
import sys

# Đảm bảo in tiếng Việt trên console Windows không bị lỗi UnicodeEncodeError
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from eval.dataset_manager import DatasetManager
from eval.eval_runner import EvaluationRunner


def main():
    parser = argparse.ArgumentParser(
        description="Chạy kiểm thử và đánh giá chất lượng RAG Lexdraft."
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/eval/golden_dataset.json",
        help="Đường dẫn tới file Golden Dataset JSON",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Chỉ kiểm tra tính hợp lệ và chất lượng của Golden Dataset mà không chạy suy luận",
    )
    args = parser.parse_args()

    dm = DatasetManager(file_path=args.dataset)
    samples = dm.load_dataset()

    if not samples:
        print(f"[!] Chua co du lieu kiem thu tai '{args.dataset}'.")
        print(
            "[*] Vui long tao file mau hoac xem huong dan tai 'eval/synthetic_gen.py'."
        )
        sys.exit(1)

    print(f"\n[+] Da nap {len(samples)} mau kiem thu tu: {args.dataset}")

    # Thẩm định chất lượng dataset
    is_valid, issues = dm.validate_quality(samples)
    if not is_valid:
        print("\n[!] CANH BAO CHAT LUONG GOLDEN DATASET:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(
            "[V] Golden Dataset dat chuan chat luong (khong trung ID, cau hoi & can cu day du)."
        )

    if args.validate_only:
        return

    print("\n[*] Bat dau thuc thi pipeline kiem thu qua Lexdraft Chatbot Service...")
    runner = EvaluationRunner(dataset_path=args.dataset)
    results = runner.run_inference(samples)

    metrics = runner.compute_rule_metrics(samples, results)
    csv_report = runner.export_reports(results, metrics)

    print("\n" + "=" * 55)
    print("TONG KET KET QUA DANH GIA:")
    print(f"   - Tong so cau hoi kiem thu:        {metrics.get('total_samples', 0)}")
    print(
        f"   - Ty le truy xuat co Context:      {metrics.get('retrieval_success_rate', 0.0) * 100:.1f}%"
    )
    print(
        f"   - Ty le trich dan dung Dieu luat:  {metrics.get('law_citation_match_rate', 0.0) * 100:.1f}%"
    )
    print("=" * 55)
    print(f"Bao cao chi tiet da duoc luu tai:\n   -> {csv_report}\n")


if __name__ == "__main__":
    main()
