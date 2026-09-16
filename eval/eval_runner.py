"""eval/eval_runner.py

Runner chính thực thi pipeline đánh giá RAG trong Lexdraft:
1. Đọc Golden Dataset từ data/eval/golden_dataset.json.
2. Chạy từng câu hỏi qua Chatbot Service (chế độ tra cứu luật).
3. Thu thập: câu trả lời thực tế (system_answer), các chunk trích dẫn (retrieved_contexts).
4. Tính toán các chỉ số cơ bản (Keyword/Law Citation Match, Length, Relevance).
5. Xuất báo cáo chi tiết ra file CSV/JSON trong data/eval/.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from eval.dataset_manager import DatasetManager
from eval.schema import EvalSampleResult, GoldenSample
from modules.chatbot_qa import retrieval
from modules.chatbot_qa.service import handle_chat

logger = logging.getLogger(__name__)

DEFAULT_REPORT_DIR = Path("data/eval")


def _format_citation(c: Any) -> str:
    """Format một item citation từ dict hoặc str sang dạng chuỗi dễ đọc."""
    if isinstance(c, dict):
        art = c.get("article", "")
        law = c.get("law_name") or c.get("source") or ""
        return f"{art} ({law})".strip() if law else (art or str(c))
    return str(c)


class EvaluationRunner:
    """Điều phối toàn bộ quá trình chạy kiểm thử và đánh giá RAG."""

    def __init__(self, dataset_path: Path = Path("data/eval/golden_dataset.json")):
        self.dataset_manager = DatasetManager(dataset_path)
        self.report_dir = DEFAULT_REPORT_DIR
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def run_inference(self, samples: List[GoldenSample]) -> List[EvalSampleResult]:
        """Chạy từng mẫu kiểm thử qua Chatbot Service của Lexdraft."""
        results = []
        logger.info(f"Bắt đầu chạy suy luận cho {len(samples)} câu hỏi...")

        for s in samples:
            try:
                # 1. Gọi trực tiếp Chatbot Service (Chế độ B: tra cứu luật chung)
                chat_res = handle_chat(
                    message=s.question,
                    session_id="ragas_eval_session",
                )

                system_answer = chat_res.get("answer", "")
                citations = chat_res.get("citations", [])

                # 2. Lấy danh sách context chunks đã được truy xuất từ VectorDB
                chunks = retrieval.search_context(query=s.question, has_session=False)
                retrieved_contexts = [c.get("content", "") for c in chunks]

                max_score = 0.0
                if chunks:
                    max_score = max(c.get("score", 0.0) for c in chunks)

                res_sample = EvalSampleResult(
                    id=s.id,
                    question=s.question,
                    ground_truth=s.ground_truth,
                    system_answer=system_answer,
                    retrieved_contexts=retrieved_contexts,
                    citations=citations,
                    similarity_score_max=round(max_score, 4),
                )
                results.append(res_sample)
            except Exception as e:
                logger.error(f"Lỗi khi xử lý câu hỏi {s.id}: {e}")
                results.append(
                    EvalSampleResult(
                        id=s.id,
                        question=s.question,
                        ground_truth=s.ground_truth,
                        system_answer=f"ERROR: {e}",
                        retrieved_contexts=[],
                        citations=[],
                        similarity_score_max=0.0,
                    )
                )

        return results

    def compute_rule_metrics(
        self, samples: List[GoldenSample], results: List[EvalSampleResult]
    ) -> Dict[str, float]:
        """Tính toán các chỉ số kiểm chứng căn cứ trước khi đưa qua LLM Evaluator."""
        sample_map = {s.id: s for s in samples}
        total = len(results)
        if total == 0:
            return {}

        law_match_count = 0
        has_context_count = 0

        for r in results:
            golden = sample_map.get(r.id)
            if not golden:
                continue

            # Kiểm tra xem ít nhất 1 expected_law có xuất hiện trong câu trả lời hoặc trích dẫn không
            expected = golden.expected_laws
            if not expected:
                law_match_count += 1
            else:
                matched = any(
                    law.lower() in r.system_answer.lower()
                    or any(
                        law.lower() in _format_citation(c).lower() for c in r.citations
                    )
                    for law in expected
                )
                if matched:
                    law_match_count += 1

            if len(r.retrieved_contexts) > 0:
                has_context_count += 1

        return {
            "total_samples": total,
            "retrieval_success_rate": round(has_context_count / total, 4),
            "law_citation_match_rate": round(law_match_count / total, 4),
        }

    def export_reports(
        self, results: List[EvalSampleResult], metrics: Dict[str, float]
    ) -> Path:
        """Xuất báo cáo chi tiết ra file CSV và JSON."""
        csv_path = self.report_dir / "eval_report_latest.csv"
        json_path = self.report_dir / "eval_report_latest.json"

        # Xuất CSV
        rows = []
        for r in results:
            rows.append(
                {
                    "id": r.id,
                    "question": r.question,
                    "ground_truth": r.ground_truth,
                    "system_answer": r.system_answer,
                    "context_count": len(r.retrieved_contexts),
                    "citations": "; ".join(_format_citation(c) for c in r.citations),
                    "similarity_score_max": r.similarity_score_max,
                }
            )
        df = pd.DataFrame(rows)
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")

        # Xuất JSON
        report_data = {
            "metrics": metrics,
            "results": [r.model_dump() for r in results],
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        logger.info(f"Đã xuất báo cáo đánh giá tại: {csv_path}")
        return csv_path
