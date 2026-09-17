"""
evaluation/test_h2_metadata_ablation.py

Bộ Test 2 - Kiểm chứng Giả thiết 2 (Mục 3.3.2):
"Việc tổ chức dữ liệu pháp luật theo Điều/Khoản và lưu metadata nguồn giúp hệ thống
truy xuất và cung cấp căn cứ pháp lý chính xác hơn."

Phương pháp: Thử nghiệm bóc tách (Ablation Study)
- Cùng 44 câu hỏi Fact Retrieval
- Nhánh B (With Metadata - Lexdraft): Context có gắn thẻ [Nguồn: law_name | article | clause], trích xuất structured citations.
- Nhánh A (Without Metadata): Strip bỏ toàn bộ thẻ metadata, chỉ cung cấp nội dung text thô.
- Đo lường:
  1. Hit Rate@1, Hit Rate@3, Hit Rate@5 trên FAISS law_index
  2. Law Title Accuracy (% xác định đúng tên luật, tránh nhầm BLDS & LTM)
  3. Article/Clause Accuracy (% trích dẫn đúng số hiệu Điều/Khoản)
  4. Structured Citation Rate (% xuất được căn cứ đối soát có cấu trúc)
"""

import argparse
import json
import logging
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

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
_LOG_FILE = (
    _LOG_DIR / f"test_h2_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
)

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_fmt)
_file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
_file_handler.setFormatter(_fmt)

logging.basicConfig(level=logging.INFO, handlers=[_console_handler, _file_handler])
logger = logging.getLogger("test_h2_metadata")
logger.info("Log file: %s", _LOG_FILE)

from modules.chatbot_qa import prompts, retrieval  # noqa: E402
from modules.shared.llm_client import GeminiClient, extract_citations_from_chunks  # noqa: E402


def normalize_law_name(name: str) -> str:
    if not name:
        return ""
    s = name.lower()
    s = s.replace("bộ luật", "luật")
    s = s.replace("blds", "luật dân sự")
    s = s.replace("ltm", "luật thương mại")
    s = s.replace("shtt", "luật sở hữu trí tuệ")
    s = s.replace("gddt", "luật giao dịch điện tử")
    s = s.replace("bảo vệ dữ liệu", "dữ liệu cá nhân")
    return re.sub(r"\s+", " ", s).strip()


def evaluate_retrieval_hit_rates(
    test_cases: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Đo đếm năng lực truy xuất tầng vector database:
    Hit Rate@1, Hit Rate@3, Hit Rate@5 đối với Điều/Khoản mục tiêu.
    """
    logger.info("--- BẮT ĐẦU ĐO ĐẾM HIT RATE TRUY XUẤT CỦA CẤU TRÚC ĐIỀU/KHOẢN ---")
    hit_at_1 = 0
    hit_at_3 = 0
    hit_at_5 = 0
    total = len(test_cases)

    retrieval_details = []

    for idx, item in enumerate(test_cases, 1):
        q = item["question"]
        expected_art = item.get("expected_article", "")  # e.g. "Điều 301"
        expected_doc = item.get("expected_doc", "")  # e.g. "Luật Thương mại"

        art_num = ""
        m = re.search(r"\d+", expected_art)
        if m:
            art_num = m.group()

        # Truy xuất top-5 từ FAISS
        hits = retrieval.search_context(query=q, has_session=False, top_k=5)

        h1 = False
        h3 = False
        h5 = False

        norm_expected = normalize_law_name(expected_doc)

        for rank, chunk in enumerate(hits):
            meta = chunk.get("metadata", {})
            content = chunk.get("content", "")
            chunk_art = meta.get("article", "") or meta.get("article_number", "")
            chunk_law = meta.get("law_name", "") or meta.get("source", "")

            # Kiểm tra xem chunk có đúng là Điều cần tìm không
            match_art = False
            if art_num:
                if re.search(rf"\b[Đđ]iều\s+{art_num}\b", chunk_art) or re.search(
                    rf"\b[Đđ]iều\s+{art_num}\b", content[:150]
                ):
                    match_art = True
            else:
                match_art = True

            match_doc = False
            norm_chunk_law = normalize_law_name(chunk_law)
            norm_content = normalize_law_name(content[:250])
            if norm_expected:
                if norm_expected in norm_chunk_law or norm_expected in norm_content:
                    match_doc = True
            else:
                match_doc = True

            if match_art and match_doc:
                if rank == 0:
                    h1 = True
                if rank < 3:
                    h3 = True
                if rank < 5:
                    h5 = True
                break

        if h1:
            hit_at_1 += 1
        if h3:
            hit_at_3 += 1
        if h5:
            hit_at_5 += 1

        retrieval_details.append(
            {
                "id": item["id"],
                "question": q,
                "expected_article": expected_art,
                "expected_doc": expected_doc,
                "hit_at_1": h1,
                "hit_at_3": h3,
                "hit_at_5": h5,
                "top_hit_meta": hits[0].get("metadata", {}) if hits else {},
            }
        )

    return {
        "total_queries": total,
        "hit_at_1": hit_at_1,
        "hit_at_1_rate": round(hit_at_1 / total * 100, 2) if total else 0,
        "hit_at_3": hit_at_3,
        "hit_at_3_rate": round(hit_at_3 / total * 100, 2) if total else 0,
        "hit_at_5": hit_at_5,
        "hit_at_5_rate": round(hit_at_5 / total * 100, 2) if total else 0,
        "details": retrieval_details,
    }


def run_metadata_ablation_study(
    test_cases: List[Dict[str, Any]], sample_limit: int = 20
) -> Dict[str, Any]:
    """
    Chạy thực nghiệm đối chứng (Ablation Study):
    So sánh Nhánh A (Không Metadata) vs Nhánh B (Có Metadata).
    """
    logger.info(
        "--- BẮT ĐẦU ABLATION STUDY: WITH METADATA VS. W/O METADATA (Mẫu: %d) ---",
        min(len(test_cases), sample_limit),
    )

    client = GeminiClient(temperature=0.0)

    subset = test_cases[:sample_limit]

    branch_a_results = []
    branch_b_results = []

    # Thống kê tích lũy
    stats_a = {"law_match": 0, "art_match": 0, "structured_cit": 0, "total": 0}
    stats_b = {"law_match": 0, "art_match": 0, "structured_cit": 0, "total": 0}

    for idx, item in enumerate(subset, 1):
        q = item["question"]
        expected_art = item.get("expected_article", "")
        expected_doc = item.get("expected_doc", "")
        art_num = (
            re.search(r"\d+", expected_art).group()
            if re.search(r"\d+", expected_art)
            else ""
        )

        logger.info(
            "[%d/%d] Đang đối chứng câu hỏi: %s", idx, len(subset), q[:60] + "..."
        )

        # 1. Truy xuất top-3 chunks từ FAISS
        raw_chunks = retrieval.search_context(query=q, has_session=False, top_k=3)

        # -------------------------------------------------------------
        # NHÁNH B: CÓ METADATA (Lexdraft Chuẩn)
        # -------------------------------------------------------------
        prompt_b = prompts.build_chat_prompt(
            query=q,
            context_chunks=raw_chunks,
            history="",
            has_contract_context=False,
        )
        citations_b = extract_citations_from_chunks(raw_chunks)
        try:
            resp_b = client.generate_text(prompt_b)
        except Exception as e:
            logger.error("Lỗi sinh text nhánh B: %s", e)
            resp_b = ""

        # Đánh giá nhánh B
        law_match_b = expected_doc.lower() in resp_b.lower() if expected_doc else True
        art_match_b = (
            re.search(rf"\b[Đđ]iều\s+{art_num}\b", resp_b) is not None
            if art_num
            else True
        )
        struct_cit_b = any(
            c.get("article") not in ("N/A", "", None)
            and c.get("source") not in ("N/A", "", None)
            for c in citations_b
        )

        if law_match_b:
            stats_b["law_match"] += 1
        if art_match_b:
            stats_b["art_match"] += 1
        if struct_cit_b:
            stats_b["structured_cit"] += 1
        stats_b["total"] += 1

        branch_b_results.append(
            {
                "id": item["id"],
                "answer": resp_b,
                "law_matched": law_match_b,
                "article_matched": art_match_b,
                "structured_citations_count": len(citations_b) if struct_cit_b else 0,
            }
        )

        # -------------------------------------------------------------
        # NHÁNH A: KHÔNG CÓ METADATA (Strip bỏ metadata, chỉ để text thô)
        # -------------------------------------------------------------
        stripped_chunks = [
            {"content": c.get("content", ""), "metadata": {}} for c in raw_chunks
        ]
        # Format context không có nhãn [Nguồn: ...]
        raw_text_context = "\n\n".join(c["content"] for c in stripped_chunks)
        prompt_a = (
            f"{prompts.CHATBOT_BASE_INSTRUCTION}\n\n"
            f"=== CĂN CỨ PHÁP LÝ (VĂN BẢN THÔ KHÔNG METADATA) ===\n{raw_text_context}\n\n"
            f"=== CÂU HỎI CỦA NGƯỜI DÙNG ===\n{q}\n\n"
            f"=== TRẢ LỜI CỦA BẠN ==="
        )
        citations_a = extract_citations_from_chunks(stripped_chunks)  # Có article="N/A"
        try:
            resp_a = client.generate_text(prompt_a)
        except Exception as e:
            logger.error("Lỗi sinh text nhánh A: %s", e)
            resp_a = ""

        # Đánh giá nhánh A
        law_match_a = expected_doc.lower() in resp_a.lower() if expected_doc else True
        art_match_a = (
            re.search(rf"\b[Đđ]iều\s+{art_num}\b", resp_a) is not None
            if art_num
            else True
        )
        struct_cit_a = any(
            c.get("article") not in ("N/A", "", None)
            and c.get("source") not in ("N/A", "", None)
            for c in citations_a
        )

        if law_match_a:
            stats_a["law_match"] += 1
        if art_match_a:
            stats_a["art_match"] += 1
        if struct_cit_a:
            stats_a["structured_cit"] += 1
        stats_a["total"] += 1

        branch_a_results.append(
            {
                "id": item["id"],
                "answer": resp_a,
                "law_matched": law_match_a,
                "article_matched": art_match_a,
                "structured_citations_count": len(citations_a),
            }
        )

        time.sleep(0.5)  # Tránh vượt rate limit

    total_s = stats_a["total"]
    summary = {
        "sample_evaluated": total_s,
        "branch_a_no_metadata": {
            "law_name_accuracy_rate": round(stats_a["law_match"] / total_s * 100, 2)
            if total_s
            else 0,
            "article_accuracy_rate": round(stats_a["art_match"] / total_s * 100, 2)
            if total_s
            else 0,
            "structured_citation_rate": round(
                stats_a["structured_cit"] / total_s * 100, 2
            )
            if total_s
            else 0,
            "correct_law_count": stats_a["law_match"],
            "correct_art_count": stats_a["art_match"],
        },
        "branch_b_with_metadata": {
            "law_name_accuracy_rate": round(stats_b["law_match"] / total_s * 100, 2)
            if total_s
            else 0,
            "article_accuracy_rate": round(stats_b["art_match"] / total_s * 100, 2)
            if total_s
            else 0,
            "structured_citation_rate": round(
                stats_b["structured_cit"] / total_s * 100, 2
            )
            if total_s
            else 0,
            "correct_law_count": stats_b["law_match"],
            "correct_art_count": stats_b["art_match"],
        },
    }
    return {
        "summary": summary,
        "details_branch_a": branch_a_results,
        "details_branch_b": branch_b_results,
    }


def main():
    parser = argparse.ArgumentParser(description="Chạy Bộ Test 2: Giả thiết 2")
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/eval/tap_du_lieu/dataset_h2_metadata.json",
        help="Đường dẫn file dataset H2",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=25,
        help="Số lượng mẫu chạy Ablation Study LLM",
    )
    args = parser.parse_args()

    ds_path = PROJECT_ROOT / args.dataset
    if not ds_path.exists():
        fallback_path = PROJECT_ROOT / "data" / "eval" / "dataset_h2_metadata.json"
        if fallback_path.exists():
            ds_path = fallback_path
        else:
            logger.error("Không tìm thấy file: %s", ds_path)
            sys.exit(1)

    with open(ds_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    # 1. Đo năng lực Retrieval trên toàn bộ 44 câu
    retrieval_metrics = evaluate_retrieval_hit_rates(test_cases)
    logger.info("KẾT QUẢ RETRIEVAL METRICS (TOÀN BỘ 44 CÂU):")
    logger.info(
        "  Hit Rate@1: %.2f%% (%d/%d)",
        retrieval_metrics["hit_at_1_rate"],
        retrieval_metrics["hit_at_1"],
        retrieval_metrics["total_queries"],
    )
    logger.info(
        "  Hit Rate@3: %.2f%% (%d/%d)",
        retrieval_metrics["hit_at_3_rate"],
        retrieval_metrics["hit_at_3"],
        retrieval_metrics["total_queries"],
    )
    logger.info(
        "  Hit Rate@5: %.2f%% (%d/%d)",
        retrieval_metrics["hit_at_5_rate"],
        retrieval_metrics["hit_at_5"],
        retrieval_metrics["total_queries"],
    )

    # 2. Chạy Ablation Study Có vs Không Metadata
    ablation_metrics = run_metadata_ablation_study(
        test_cases, sample_limit=args.sample_limit
    )
    summary = ablation_metrics["summary"]

    logger.info("KẾT QUẢ ABLATION STUDY (CÓ METADATA VS. KHÔNG METADATA):")
    logger.info(
        "  Nhánh A (Không Metadata): Law Acc = %.2f%% | Article Acc = %.2f%% | Structured Citations = %.2f%%",
        summary["branch_a_no_metadata"]["law_name_accuracy_rate"],
        summary["branch_a_no_metadata"]["article_accuracy_rate"],
        summary["branch_a_no_metadata"]["structured_citation_rate"],
    )
    logger.info(
        "  Nhánh B (Có Metadata):    Law Acc = %.2f%% | Article Acc = %.2f%% | Structured Citations = %.2f%%",
        summary["branch_b_with_metadata"]["law_name_accuracy_rate"],
        summary["branch_b_with_metadata"]["article_accuracy_rate"],
        summary["branch_b_with_metadata"]["structured_citation_rate"],
    )

    # 3. Xuất báo cáo JSON
    report = {
        "test_name": "Bộ Test 2: Kiểm chứng Giả thiết 2 (Metadata & Article Chunking Precision)",
        "hypothesis": "Việc tổ chức dữ liệu pháp luật theo Điều/Khoản và lưu metadata nguồn giúp hệ thống truy xuất và cung cấp căn cứ pháp lý chính xác hơn.",
        "retrieval_hit_rates": retrieval_metrics,
        "metadata_ablation_study": ablation_metrics,
    }

    report_dir = PROJECT_ROOT / "data" / "eval" / "bao_cao_ket_qua"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report_h2_metadata.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info("Đã lưu báo cáo đầy đủ tại: %s", report_path)


if __name__ == "__main__":
    main()
