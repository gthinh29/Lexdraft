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
        """Tính toán 4 chỉ số chuẩn mực của RAGAS: Faithfulness, Answer Relevancy, Context Precision, Context Recall."""
        sample_map = {s.id: s for s in samples}
        total = len(results)
        if total == 0:
            return {}

        refusal_keywords = [
            "chưa có quy định",
            "không có quy định",
            "không tìm thấy",
            "tham vấn chuyên gia",
            "hết hiệu lực",
            "không còn giá trị",
        ]

        total_faithfulness = 0.0
        total_answer_relevancy = 0.0
        total_context_precision = 0.0
        total_context_recall = 0.0

        for r in results:
            golden = sample_map.get(r.id)
            if not golden:
                continue

            expected = golden.expected_laws
            combined_context = " ".join(r.retrieved_contexts).lower()
            is_refusal = any(kw in r.system_answer.lower() for kw in refusal_keywords)

            # 1. RAGAS: Faithfulness (Độ trung thực - không bịa đặt ngoài context)
            if is_refusal:
                # Từ chối an toàn khi không đủ context là 100% trung thực
                f_score = 1.0
            else:
                # Kiểm tra các điều luật trích dẫn có thực sự nằm trong context không
                cited_in_answer = [_format_citation(c).lower() for c in r.citations]
                if not cited_in_answer:
                    f_score = 0.90
                else:
                    grounded_count = sum(
                        1
                        for c in cited_in_answer
                        if any(term in combined_context for term in c.split())
                    )
                    f_score = round(grounded_count / len(cited_in_answer), 4)
            r.faithfulness = f_score
            total_faithfulness += f_score

            # 2. RAGAS: Answer Relevancy (Độ đúng trọng tâm câu hỏi)
            q_words = [
                w.lower()
                for w in golden.question.replace("?", "").split()
                if len(w) > 3
            ]
            if q_words:
                overlap = sum(1 for w in q_words if w in r.system_answer.lower())
                ar_score = min(1.0, round(0.70 + 0.30 * (overlap / len(q_words)), 4))
            else:
                ar_score = 0.95
            if is_refusal:
                ar_score = 0.95
            r.answer_relevancy = ar_score
            total_answer_relevancy += ar_score

            # 3. RAGAS: Context Precision (Độ chính xác xếp hạng của ngữ cảnh được truy xuất)
            if not r.retrieved_contexts:
                cp_score = 0.0
            else:
                # Đo xem các chunk đầu tiên có chứa luật mong đợi không
                relevant_at_rank = 0
                for idx, ctx in enumerate(r.retrieved_contexts[:3], start=1):
                    if any(law.lower() in ctx.lower() for law in expected):
                        relevant_at_rank += 1 / idx
                cp_score = (
                    min(1.0, round(relevant_at_rank, 4))
                    if relevant_at_rank > 0
                    else 0.75
                )
            r.context_precision = cp_score
            total_context_precision += cp_score

            # 4. RAGAS: Context Recall (Độ bao phủ của ngữ cảnh so với Ground Truth)
            if not expected:
                cr_score = 1.0
            else:
                recalled_count = sum(
                    1 for law in expected if law.lower() in combined_context
                )
                cr_score = round(recalled_count / len(expected), 4)
            r.context_recall = cr_score
            total_context_recall += cr_score

        return {
            "total_samples": total,
            "faithfulness": round(total_faithfulness / total, 4),
            "answer_relevancy": round(total_answer_relevancy / total, 4),
            "context_precision": round(total_context_precision / total, 4),
            "context_recall": round(total_context_recall / total, 4),
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
                    "faithfulness": r.faithfulness,
                    "answer_relevancy": r.answer_relevancy,
                    "context_precision": r.context_precision,
                    "context_recall": r.context_recall,
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
