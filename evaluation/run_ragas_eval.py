"""
evaluation/run_ragas_eval.py

Script đánh giá định lượng chất lượng RAG bằng framework RAGAS (SRS Chương 7).
Đánh giá 3 chỉ số cốt lõi (Sử dụng Gemini Judge LLM: gemini-3.5-flash-lite):
1. Faithfulness (Độ trung thực, chống ảo giác)
2. Context Precision (Độ chính xác và độ liên quan của ngữ cảnh pháp lý truy xuất)
3. Context Recall (Độ bao phủ của ngữ cảnh pháp lý so với ground truth)

Quy trình:
- Đọc bộ câu hỏi & ground truth từ evaluation/testset.csv (hoặc data/eval/golden_dataset.json)
- Chạy từng câu hỏi qua Module Chatbot Chế độ B (handle_chat) và retrieval (search_context)
- Thu thập question, answer, contexts, ground_truth
- Đưa vào Ragas Dataset và tính điểm đánh giá với GeminiRagasLLM (gemini-3.5-flash-lite)
- Xuất báo cáo kết quả ra terminal và file evaluation/ragas_report.json
"""

import argparse
import asyncio
import csv
import json
import logging
import sys
import typing as t
from pathlib import Path
from typing import Dict, List, Optional

# Thêm thư mục gốc vào path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Cấu hình UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ragas_eval")

from config import Config  # noqa: E402
from modules.shared.llm_client import GeminiClient  # noqa: E402
from ragas.llms.base import BaseRagasLLM  # noqa: E402
from langchain_core.outputs import Generation, LLMResult  # noqa: E402
from langchain_core.prompt_values import PromptValue  # noqa: E402


class GeminiRagasLLM(BaseRagasLLM):
    """
    Subclass của BaseRagasLLM để tích hợp Google Gemini (mặc định: gemini-3.5-flash-lite)
    làm LLM Judge cho framework RAGAS mà không phụ thuộc vào OpenAI API.
    """

    def __init__(self, model_name: Optional[str] = None):
        super().__init__()
        self.model_name = model_name or getattr(
            Config, "LLM_MODEL_NAME", "gemini-3.5-flash-lite"
        )
        self.gemini_client = GeminiClient(model_name=self.model_name, temperature=0.0)
        logger.info(
            f"Khởi tạo GeminiRagasLLM Judge thành công với model: {self.model_name}"
        )

    def generate_text(
        self,
        prompt: PromptValue,
        n: int = 1,
        temperature: t.Optional[float] = 0.01,
        stop: t.Optional[t.List[str]] = None,
        callbacks=None,
    ) -> LLMResult:
        text_prompt = prompt.to_string()
        resp_text = self.gemini_client.generate_text(text_prompt)
        return LLMResult(generations=[[Generation(text=resp_text)]])

    async def agenerate_text(
        self,
        prompt: PromptValue,
        n: int = 1,
        temperature: t.Optional[float] = 0.01,
        stop: t.Optional[t.List[str]] = None,
        callbacks=None,
    ) -> LLMResult:
        return await asyncio.to_thread(
            self.generate_text, prompt, n, temperature, stop, callbacks
        )

    def is_finished(self, response: LLMResult) -> bool:
        return True


def load_testset(csv_path: Path) -> List[Dict[str, str]]:
    """Đọc file testset.csv hoặc golden_dataset.json."""
    if not csv_path.exists():
        json_path = PROJECT_ROOT / "data" / "eval" / "golden_dataset.json"
        if json_path.exists():
            logger.info(f"Không thấy {csv_path}, nạp từ {json_path}")
            with open(json_path, mode="r", encoding="utf-8") as f:
                raw = json.load(f)
            return [
                {
                    "question": item["question"].strip(),
                    "ground_truth": item["ground_truth"].strip(),
                }
                for item in raw
            ]
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


def run_evaluation(
    testset_file: str = "testset.csv",
    sample_limit: Optional[int] = None,
    batch_size: int = 5,
):
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

        logger.info("[%d/%d] Đang xử lý: '%s'", idx, len(test_cases), q[:60] + "...")

        # 1. Truy xuất context từ law_index
        context_chunks = chatbot_retrieval.search_context(
            query=q, has_session=False, top_k=5
        )
        contexts = [c.get("content", "") for c in context_chunks if c.get("content")]
        if not contexts:
            contexts = ["Không có ngữ cảnh pháp lý liên quan."]

        # 2. Gọi service sinh câu trả lời
        res = handle_chat(message=q, session_id=session_id)
        answer = res.get("answer", "")

        eval_data["question"].append(q)
        eval_data["answer"].append(answer)
        eval_data["contexts"].append(contexts)
        eval_data["ground_truth"].append(gt)

    logger.info("Hoàn tất thu thập dữ liệu phản hồi từ hệ thống!")

    # Đánh giá qua thư viện Ragas với Gemini Judge
    logger.info(
        "Đang khởi tạo Ragas Metrics và Gemini Judge (gemini-3.5-flash-lite)..."
    )
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            context_precision,
            context_recall,
            faithfulness,
        )

        dataset = Dataset.from_dict(eval_data)
        metrics = [
            faithfulness,
            context_precision,
            context_recall,
        ]

        ragas_judge_llm = GeminiRagasLLM()

        logger.info(
            "Đang tính toán chỉ số Ragas (Faithfulness, Context Precision, Context Recall)..."
        )
        results = evaluate(
            dataset=dataset,
            metrics=metrics,
            llm=ragas_judge_llm,
        )

        logger.info("==================================================")
        logger.info("KẾT QUẢ ĐÁNH GIÁ ĐỊNH LƯỢNG RAGAS (GEMINI JUDGE):")
        logger.info("==================================================")
        print(results)

        # Trích xuất dataframe / dict chi tiết
        results_df = results.to_pandas()
        import pandas as pd

        scores = {}
        for m in ["faithfulness", "context_precision", "context_recall"]:
            if m in results_df.columns:
                val = results_df[m].mean()
                scores[m] = round(float(val), 4) if not pd.isna(val) else 0.0

        final_report = {
            "judge_model": getattr(Config, "LLM_MODEL_NAME", "gemini-3.5-flash-lite"),
            "num_samples": len(test_cases),
            "summary_scores": scores,
            "details": json.loads(
                results_df.to_json(orient="records", force_ascii=False)
            ),
        }

        # Lưu kết quả ra file JSON
        report_file = eval_dir / "ragas_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(final_report, f, ensure_ascii=False, indent=2)
        logger.info("Đã lưu báo cáo đánh giá ra file: %s", report_file)

        return final_report

    except Exception as e:
        logger.error(f"Lỗi trong quá trình đánh giá Ragas: {e}", exc_info=True)
        # Lưu dữ liệu thô để phục vụ phân tích
        raw_output_file = eval_dir / "eval_collected_data.json"
        with open(raw_output_file, "w", encoding="utf-8") as f:
            json.dump(eval_data, f, ensure_ascii=False, indent=2)
        logger.info("Đã lưu dữ liệu thu thập ra file: %s", raw_output_file)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chạy Ragas Evaluation")
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Giới hạn số mẫu đánh giá (VD: --limit 10 để test nhanh)",
    )
    args = parser.parse_args()

    run_evaluation(sample_limit=args.limit)
