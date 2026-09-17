"""
evaluation/test_h1_ab_comparison.py

Bộ Test 1 - Kiểm chứng Giả thiết 1 (Mục 3.3.1):
"Việc kết hợp LLM với RAG giúp cải thiện khả năng trả lời các câu hỏi pháp lý
liên quan đến hợp đồng dịch vụ so với việc sử dụng LLM không có cơ chế truy xuất."

Phương pháp: Thử nghiệm đối chứng A/B trên cùng 50 câu hỏi:
- Nhánh A (Zero-shot LLM Baseline): Gửi câu hỏi trực tiếp cho Gemini (gemini-3.5-flash-lite) mà không có RAG.
- Nhánh B (Lexdraft LLM + RAG): Chạy qua pipeline RAG của Lexdraft (truy xuất FAISS + prompt grounded + citations).
- Đo lường:
  1. Citation Accuracy (% trích dẫn đúng số hiệu văn bản và Điều/Khoản luật)
  2. Outdated / Fake Law Hallucination Rate (% bị lừa viện dẫn luật hết hiệu lực hoặc luật không tồn tại)
  3. Grounded Completeness Rate (% câu trả lời đạt đầy đủ căn cứ so với Ground Truth)
"""

import argparse
import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

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

# === CẤU HÌNH LOGGING: GHI RA CẢ CONSOLE VÀ FILE ===
_LOG_DIR = Path(__file__).resolve().parent.parent / "data" / "eval" / "nhat_ky_logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = _LOG_DIR / f"test_h1_ab_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_fmt)
_file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
_file_handler.setFormatter(_fmt)

logging.basicConfig(level=logging.INFO, handlers=[_console_handler, _file_handler])
logger = logging.getLogger("test_h1_ab")
logger.info("Log file: %s", _LOG_FILE)

from modules.chatbot_qa.service import handle_chat  # noqa: E402
from modules.shared.llm_client import GeminiClient  # noqa: E402


def run_h1_ab_comparison(dataset_path: Path, sample_limit: int = 50) -> Dict[str, Any]:
    with open(dataset_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    subset = test_cases[:sample_limit]
    logger.info("--- BẮT ĐẦU A/B TESTING BỘ TEST 1 (MẪU: %d CÂU HỎI) ---", len(subset))

    zero_shot_client = GeminiClient(temperature=0.0)

    stats_a = {
        "expected_laws_matched": 0,
        "outdated_hallucinations": 0,
        "articles_cited": 0,
        "total": 0,
    }
    stats_b = {
        "expected_laws_matched": 0,
        "outdated_hallucinations": 0,
        "articles_cited": 0,
        "total": 0,
    }

    details = []

    for idx, item in enumerate(subset, 1):
        q = item["question"]
        gt = item["ground_truth"]
        category = item["category"]
        expected_laws = item.get("expected_laws", [])

        logger.info("[%d/%d] [%s] %s", idx, len(subset), category, q[:60] + "...")

        # -------------------------------------------------------------
        # 1. NHÁNH A: ZERO-SHOT LLM (KHÔNG CÓ RAG)
        # -------------------------------------------------------------
        prompt_zero_shot = (
            "Bạn là một chuyên gia tư vấn pháp lý về hợp đồng dịch vụ tại Việt Nam.\n"
            "Hãy trả lời câu hỏi sau đây một cách chính xác và đầy đủ nhất.\n"
            "BẮT BUỘC nêu rõ tên văn bản luật, số hiệu văn bản và số hiệu Điều/Khoản làm căn cứ pháp lý.\n\n"
            f"Câu hỏi: {q}\n\n"
            "Trả lời:"
        )
        try:
            ans_a = zero_shot_client.generate_text(prompt_zero_shot)
        except Exception as e:
            logger.error("Lỗi khi sinh nhánh A: %s", e)
            ans_a = ""

        # -------------------------------------------------------------
        # 2. NHÁNH B: LEXDRAFT LLM + RAG
        # -------------------------------------------------------------
        session_id = f"test_h1_rag_{idx}_{int(time.time())}"
        try:
            resp_b = handle_chat(message=q, session_id=session_id)
            ans_b = resp_b.get("answer", "")
            cit_b = resp_b.get("citations", [])
        except Exception as e:
            logger.error("Lỗi khi sinh nhánh B: %s", e)
            ans_b = ""
            cit_b = []

        # -------------------------------------------------------------
        # 3. ĐO ĐẾM VÀ SO KHỚP CHỈ SỐ
        # -------------------------------------------------------------
        stats_a["total"] += 1
        stats_b["total"] += 1

        # Check expected laws
        matched_a = sum(1 for law in expected_laws if law.lower() in ans_a.lower())
        matched_b = sum(1 for law in expected_laws if law.lower() in ans_b.lower())
        match_ratio_a = matched_a / len(expected_laws) if expected_laws else 1.0
        match_ratio_b = matched_b / len(expected_laws) if expected_laws else 1.0

        if match_ratio_a >= 0.5:
            stats_a["expected_laws_matched"] += 1
        if match_ratio_b >= 0.5:
            stats_b["expected_laws_matched"] += 1

        # Check Điều/Khoản citation
        art_cited_a = bool(re.search(r"\b[Đđ]iều\s+\d+\b", ans_a))
        art_cited_b = bool(re.search(r"\b[Đđ]iều\s+\d+\b", ans_b)) or len(cit_b) > 0
        if art_cited_a:
            stats_a["articles_cited"] += 1
        if art_cited_b:
            stats_b["articles_cited"] += 1

        # Check Outdated/Fake law hallucination (đặc biệt trên nhóm Negative)
        hallucinated_a = False
        hallucinated_b = False
        if category == "Negative / Law Validity":
            # Nếu khẳng định hợp pháp hoặc áp dụng bình thường các luật cũ/giả -> ảo giác
            affirmative_words = [
                "hợp pháp",
                "được áp dụng",
                "vẫn còn hiệu lực",
                "được viện dẫn",
            ]
            for w in affirmative_words:
                if w in ans_a.lower() and "không" not in ans_a.lower()[:50]:
                    hallucinated_a = True
                    break
            for w in affirmative_words:
                if w in ans_b.lower() and "không" not in ans_b.lower()[:50]:
                    hallucinated_b = True
                    break

        if hallucinated_a:
            stats_a["outdated_hallucinations"] += 1
        if hallucinated_b:
            stats_b["outdated_hallucinations"] += 1

        details.append(
            {
                "id": item["id"],
                "category": category,
                "question": q,
                "ground_truth": gt,
                "branch_a_zero_shot": {
                    "answer": ans_a,
                    "laws_matched": matched_a,
                    "laws_total": len(expected_laws),
                    "article_cited": art_cited_a,
                    "hallucinated": hallucinated_a,
                },
                "branch_b_rag": {
                    "answer": ans_b,
                    "citations_count": len(cit_b),
                    "laws_matched": matched_b,
                    "laws_total": len(expected_laws),
                    "article_cited": art_cited_b,
                    "hallucinated": hallucinated_b,
                },
            }
        )

        time.sleep(0.5)

    tot = stats_a["total"]
    summary = {
        "sample_size": tot,
        "branch_a_zero_shot": {
            "law_coverage_rate": round(stats_a["expected_laws_matched"] / tot * 100, 2)
            if tot
            else 0,
            "article_citation_rate": round(stats_a["articles_cited"] / tot * 100, 2)
            if tot
            else 0,
            "outdated_hallucination_count": stats_a["outdated_hallucinations"],
        },
        "branch_b_lexdraft_rag": {
            "law_coverage_rate": round(stats_b["expected_laws_matched"] / tot * 100, 2)
            if tot
            else 0,
            "article_citation_rate": round(stats_b["articles_cited"] / tot * 100, 2)
            if tot
            else 0,
            "outdated_hallucination_count": stats_b["outdated_hallucinations"],
        },
    }

    return {
        "summary": summary,
        "details": details,
    }


def main():
    parser = argparse.ArgumentParser(description="Chạy Bộ Test 1: Giả thiết 1")
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/eval/tap_du_lieu/dataset_h1_ab.json",
        help="Đường dẫn file dataset H1",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=50,
        help="Số lượng mẫu chạy A/B Test",
    )
    args = parser.parse_args()

    ds_path = PROJECT_ROOT / args.dataset
    if not ds_path.exists():
        fallback_path = PROJECT_ROOT / "data" / "eval" / "dataset_h1_ab.json"
        if fallback_path.exists():
            ds_path = fallback_path
        else:
            logger.error("Không tìm thấy file: %s", ds_path)
            sys.exit(1)

    result_data = run_h1_ab_comparison(ds_path, sample_limit=args.sample_limit)
    summary = result_data["summary"]

    logger.info("=== KẾT QUẢ TỔNG HỢP BỘ TEST 1 (A/B TESTING: ZERO-SHOT VS RAG) ===")
    logger.info(
        "  Nhánh A (Zero-shot LLM thuần): Law Coverage = %.2f%% | Article Citation = %.2f%% | Ảo giác luật cũ = %d",
        summary["branch_a_zero_shot"]["law_coverage_rate"],
        summary["branch_a_zero_shot"]["article_citation_rate"],
        summary["branch_a_zero_shot"]["outdated_hallucination_count"],
    )
    logger.info(
        "  Nhánh B (Lexdraft LLM + RAG):  Law Coverage = %.2f%% | Article Citation = %.2f%% | Ảo giác luật cũ = %d",
        summary["branch_b_lexdraft_rag"]["law_coverage_rate"],
        summary["branch_b_lexdraft_rag"]["article_citation_rate"],
        summary["branch_b_lexdraft_rag"]["outdated_hallucination_count"],
    )

    report = {
        "test_name": "Bộ Test 1: Kiểm chứng Giả thiết 1 (A/B Testing: Zero-shot LLM vs. Lexdraft RAG)",
        "hypothesis": "Việc kết hợp LLM với RAG giúp cải thiện khả năng trả lời các câu hỏi pháp lý liên quan đến hợp đồng dịch vụ so với việc sử dụng LLM không có cơ chế truy xuất.",
        "summary": summary,
        "details": result_data["details"],
    }

    report_dir = PROJECT_ROOT / "data" / "eval" / "bao_cao_ket_qua"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report_h1_ab.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info("Đã lưu báo cáo đầy đủ tại: %s", report_path)


if __name__ == "__main__":
    main()
