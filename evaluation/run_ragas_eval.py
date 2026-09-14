"""
evaluation/run_ragas_eval.py

Script đánh giá định lượng chất lượng RAG bằng framework RAGAS (SRS Chương 7).
Đánh giá 4 chỉ số cốt lõi:
1. Faithfulness (Độ trung thực, không ảo giác)
2. Answer Relevancy (Độ phù hợp của câu trả lời so với câu hỏi)
3. Context Precision (Độ chính xác của ngữ cảnh pháp lý truy xuất)
4. Context Recall (Độ bao phủ của ngữ cảnh so với chân thực tế - ground truth)

Quy trình:
- Đọc bộ câu hỏi & ground truth từ evaluation/testset.csv
- Chạy từng câu hỏi qua Module Chatbot Chế độ B (handle_chat)
- Thu thập question, answer, contexts, ground_truth
- Đưa vào Ragas Dataset và tính điểm đánh giá
- Xuất báo cáo kết quả ra terminal và file evaluation/ragas_report.json
"""

import csv
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

# Thêm thư mục gốc vào path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Cấu hình UTF-8 cho Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ragas_eval")


def load_testset(csv_path: Path) -> List[Dict[str, str]]:
    """Đọc file testset.csv."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Không tìm thấy file testset tại: {csv_path}")

    items = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("question") and row.get("ground_truth"):
                items.append(
                    {
                        "question": row["question"].strip(),
                        "ground_truth": row["ground_truth"].strip(),
                    }
                )
    return items


def run_evaluation(testset_file: str = "testset.csv", sample_limit: int | None = None):
    eval_dir = Path(__file__).parent
    testset_path = eval_dir / testset_file

    logger.info("Đang nạp dữ liệu đánh giá từ: %s", testset_path)
    test_cases = load_testset(testset_path)
    if sample_limit:
        test_cases = test_cases[:sample_limit]

    logger.info("Tổng số câu hỏi đánh giá: %d", len(test_cases))

    # Import modules hệ thống
    from modules.chatbot_qa.service import handle_chat
    from modules.chatbot_qa import retrieval as chatbot_retrieval

    eval_data = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": [],
    }

    logger.info("Bắt đầu chạy câu hỏi qua hệ thống RAG (Module Chatbot Chế độ B)...")

    for idx, item in enumerate(test_cases, 1):
        q = item["question"]
        gt = item["ground_truth"]
        session_id = f"eval_session_{idx}"

        logger.info("[%d/%d] Đang xử lý: '%s'", idx, len(test_cases), q)

        # 1. Truy xuất context từ law_index
        context_chunks = chatbot_retrieval.search_context(
            query=q, has_session=False, top_k=3
        )
        contexts = [c.get("content", "") for c in context_chunks if c.get("content")]

        # 2. Gọi service sinh câu trả lời
        res = handle_chat(message=q, session_id=session_id)
        answer = res.get("answer", "")

        eval_data["question"].append(q)
        eval_data["answer"].append(answer)
        eval_data["contexts"].append(contexts if contexts else ["Không có context"])
        eval_data["ground_truth"].append(gt)

    logger.info("Hoàn tất thu thập dữ liệu phản hồi từ hệ thống!")

    # Đánh giá qua thư viện Ragas
    logger.info("Đang khởi tạo Ragas Metrics...")
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )

        dataset = Dataset.from_dict(eval_data)
        metrics = [
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ]

        logger.info(
            "Đang tính toán chỉ số Ragas (Faithfulness, Relevancy, Precision, Recall)..."
        )
        results = evaluate(
            dataset=dataset,
            metrics=metrics,
        )

        logger.info("==================================================")
        logger.info("KẾT QUẢ ĐÁNH GIÁ ĐỊNH LƯỢNG RAGAS:")
        logger.info("==================================================")
        print(results)

        # Lưu kết quả ra file JSON
        report_file = eval_dir / "ragas_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(dict(results), f, ensure_ascii=False, indent=2)
        logger.info("Đã lưu báo cáo đánh giá ra file: %s", report_file)

    except ImportError:
        logger.warning(
            "Thư viện 'ragas' hoặc 'datasets' chưa sẵn sàng để tính toán tự động."
        )
        # Lưu dữ liệu thô để đánh giá sau
        raw_output_file = eval_dir / "eval_collected_data.json"
        with open(raw_output_file, "w", encoding="utf-8") as f:
            json.dump(eval_data, f, ensure_ascii=False, indent=2)
        logger.info("Đã lưu dữ liệu thu thập ra file: %s", raw_output_file)


if __name__ == "__main__":
    run_evaluation()
