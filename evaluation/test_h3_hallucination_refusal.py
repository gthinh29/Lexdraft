"""
evaluation/test_h3_hallucination_refusal.py

Bộ Test 3 - Kiểm chứng Giả thiết 3 (Mục 3.3.3):
"Cơ chế yêu cầu LLM chỉ sử dụng thông tin được truy xuất và từ chối khi không có căn cứ
phù hợp giúp giảm các câu trả lời không có căn cứ pháp lý."

Phương pháp: Ma trận kiểm thử 4 nhóm câu hỏi (35 mẫu):
1. In-domain Fact (15 mẫu): Bắt buộc trả lời có căn cứ, KHÔNG được từ chối nhầm.
2. Outdated / Fake Law (6 mẫu): Bắt buộc từ chối an toàn hoặc cảnh báo hết hiệu lực/giả mạo.
3. Out-of-Domain (8 mẫu): Hỏi về Đất đai, Hình sự, Hôn nhân... -> Bắt buộc từ chối ngoài phạm vi.
4. Non-existent Article (6 mẫu): Hỏi về Điều 999 BLDS, Điều 888 Luật TM... -> Bắt buộc từ chối, KHÔNG bịa nội dung.
"""

import argparse
import json
import logging
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
_LOG_FILE = _LOG_DIR / f"test_h3_refusal_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_console_handler = logging.StreamHandler(sys.stdout)
_console_handler.setFormatter(_fmt)
_file_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
_file_handler.setFormatter(_fmt)

logging.basicConfig(level=logging.INFO, handlers=[_console_handler, _file_handler])
logger = logging.getLogger("test_h3_refusal")
logger.info("Log file: %s", _LOG_FILE)

from modules.chatbot_qa.service import handle_chat  # noqa: E402


def is_safe_refusal_response(answer: str) -> bool:
    """
    Kiểm tra xem câu trả lời của chatbot có phải là một hành vi từ chối an toàn
    (Safe Refusal / Out-of-scope Warning / Non-existent Notice) hay không.
    """
    normalized = answer.lower()
    refusal_keywords = [
        "chưa có quy định",
        "chưa có thông tin",
        "chưa có căn cứ",
        "chưa được quy định",
        "không có quy định",
        "không có căn cứ",
        "không thuộc phạm vi",
        "ngoài phạm vi",
        "nằm ngoài phạm vi",
        "hết hiệu lực",
        "không còn hiệu lực",
        "không tồn tại",
        "không có thực",
        "không có thật",
        "không có điều",
        "chỉ có tối đa",
        "chỉ có 689 điều",
        "chỉ có 324 điều",
        "chỉ có 222 điều",
        "chỉ có 53 điều",
        "tham vấn chuyên gia",
        "vui lòng tra cứu thêm",
    ]
    for kw in refusal_keywords:
        if kw in normalized:
            return True
    return False


def run_h3_test(dataset_path: Path) -> Dict[str, Any]:
    with open(dataset_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    logger.info(
        "--- BẮT ĐẦU KIỂM THỬ BỘ TEST 3: MA TRẬN 4 NHÓM CÂU HỎI (%d MẪU) ---",
        len(test_cases),
    )

    group_stats = {
        "in_domain_fact": {"total": 0, "correct": 0, "false_refusal": 0},
        "outdated_or_fake_law": {"total": 0, "correct": 0, "hallucinated": 0},
        "out_of_domain": {"total": 0, "correct": 0, "hallucinated": 0},
        "non_existent_article": {"total": 0, "correct": 0, "hallucinated": 0},
    }

    results = []

    for idx, item in enumerate(test_cases, 1):
        q = item["question"]
        group = item["group"]
        must_refuse = item["must_refuse"]
        session_id = f"test_h3_{idx}_{int(time.time())}"

        logger.info(
            "[%d/%d] Nhóm [%s]: %s", idx, len(test_cases), group, q[:60] + "..."
        )

        try:
            resp = handle_chat(message=q, session_id=session_id)
            answer = resp.get("answer", "")
            citations = resp.get("citations", [])
        except Exception as e:
            logger.error("Lỗi khi gọi handle_chat: %s", e)
            answer = ""
            citations = []

        is_refusal = is_safe_refusal_response(answer)

        is_correct = False
        outcome_status = ""

        if group == "in_domain_fact":
            group_stats[group]["total"] += 1
            # In-domain: mong muốn KHÔNG từ chối, có câu trả lời nội dung
            if not is_refusal and len(answer.strip()) > 50:
                is_correct = True
                outcome_status = "CORRECT_ANSWERED"
                group_stats[group]["correct"] += 1
            else:
                is_correct = False
                outcome_status = "FALSE_REFUSAL"
                group_stats[group]["false_refusal"] += 1

        else:  # Các nhóm 2, 3, 4: mong muốn BẮT BUỘC TỪ CHỐI / CẢNH BÁO AN TOÀN
            group_stats[group]["total"] += 1
            if is_refusal:
                is_correct = True
                outcome_status = "SAFE_REFUSAL_SUCCESS"
                group_stats[group]["correct"] += 1
            else:
                is_correct = False
                outcome_status = "HALLUCINATED_LEAK"
                group_stats[group]["hallucinated"] += 1

        logger.info(
            "   -> Kết quả: %s (Từ chối: %s, Trích dẫn: %d)",
            outcome_status,
            is_refusal,
            len(citations),
        )

        results.append(
            {
                "id": item["id"],
                "group": group,
                "question": q,
                "must_refuse": must_refuse,
                "answer": answer,
                "is_refusal": is_refusal,
                "outcome_status": outcome_status,
                "is_correct": is_correct,
                "citations": citations,
            }
        )

        time.sleep(0.5)

    # Tính toán chỉ số tổng hợp
    in_stat = group_stats["in_domain_fact"]
    outdated_stat = group_stats["outdated_or_fake_law"]
    ood_stat = group_stats["out_of_domain"]
    nonexist_stat = group_stats["non_existent_article"]

    neg_total = outdated_stat["total"] + ood_stat["total"] + nonexist_stat["total"]
    neg_correct = (
        outdated_stat["correct"] + ood_stat["correct"] + nonexist_stat["correct"]
    )

    summary = {
        "total_samples": len(test_cases),
        "in_domain_fact": {
            "total": in_stat["total"],
            "correct_answered_rate": round(
                in_stat["correct"] / in_stat["total"] * 100, 2
            )
            if in_stat["total"]
            else 0,
            "false_refusal_rate": round(
                in_stat["false_refusal"] / in_stat["total"] * 100, 2
            )
            if in_stat["total"]
            else 0,
        },
        "outdated_or_fake_law": {
            "total": outdated_stat["total"],
            "safe_refusal_rate": round(
                outdated_stat["correct"] / outdated_stat["total"] * 100, 2
            )
            if outdated_stat["total"]
            else 0,
            "hallucination_rate": round(
                outdated_stat["hallucinated"] / outdated_stat["total"] * 100, 2
            )
            if outdated_stat["total"]
            else 0,
        },
        "out_of_domain": {
            "total": ood_stat["total"],
            "safe_refusal_rate": round(ood_stat["correct"] / ood_stat["total"] * 100, 2)
            if ood_stat["total"]
            else 0,
            "hallucination_rate": round(
                ood_stat["hallucinated"] / ood_stat["total"] * 100, 2
            )
            if ood_stat["total"]
            else 0,
        },
        "non_existent_article": {
            "total": nonexist_stat["total"],
            "safe_refusal_rate": round(
                nonexist_stat["correct"] / nonexist_stat["total"] * 100, 2
            )
            if nonexist_stat["total"]
            else 0,
            "hallucination_rate": round(
                nonexist_stat["hallucinated"] / nonexist_stat["total"] * 100, 2
            )
            if nonexist_stat["total"]
            else 0,
        },
        "overall_safe_refusal_on_unanswerable": {
            "total_unanswerable": neg_total,
            "total_safe_refused": neg_correct,
            "rate": round(neg_correct / neg_total * 100, 2) if neg_total else 0,
        },
    }

    return {
        "summary": summary,
        "details": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Chạy Bộ Test 3: Giả thiết 3")
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/eval/tap_du_lieu/dataset_h3_refusal.json",
        help="Đường dẫn file dataset H3",
    )
    args = parser.parse_args()

    ds_path = PROJECT_ROOT / args.dataset
    if not ds_path.exists():
        fallback_path = PROJECT_ROOT / "data" / "eval" / "dataset_h3_refusal.json"
        if fallback_path.exists():
            ds_path = fallback_path
        else:
            logger.error("Không tìm thấy file: %s", ds_path)
            sys.exit(1)

    result_data = run_h3_test(ds_path)
    summary = result_data["summary"]

    logger.info("=== KẾT QUẢ TỔNG HỢP BỘ TEST 3 (GIẢ THIẾT 3) ===")
    logger.info(
        "1. Nhóm In-domain Fact (15 câu): Trả lời đúng: %.2f%% | Từ chối nhầm: %.2f%%",
        summary["in_domain_fact"]["correct_answered_rate"],
        summary["in_domain_fact"]["false_refusal_rate"],
    )
    logger.info(
        "2. Nhóm Luật hết hiệu lực/Giả mạo (6 câu): Safe Refusal: %.2f%% | Hallucination: %.2f%%",
        summary["outdated_or_fake_law"]["safe_refusal_rate"],
        summary["outdated_or_fake_law"]["hallucination_rate"],
    )
    logger.info(
        "3. Nhóm Ngoài phạm vi (8 câu): Safe Refusal: %.2f%% | Hallucination: %.2f%%",
        summary["out_of_domain"]["safe_refusal_rate"],
        summary["out_of_domain"]["hallucination_rate"],
    )
    logger.info(
        "4. Nhóm Điều không tồn tại (6 câu): Safe Refusal: %.2f%% | Hallucination: %.2f%%",
        summary["non_existent_article"]["safe_refusal_rate"],
        summary["non_existent_article"]["hallucination_rate"],
    )
    logger.info(
        "--> TỶ LỆ TỪ CHỐI AN TOÀN CHUNG TRÊN CÂU HỎI KHÔNG CÓ CĂN CỨ: %.2f%% (%d/%d)",
        summary["overall_safe_refusal_on_unanswerable"]["rate"],
        summary["overall_safe_refusal_on_unanswerable"]["total_safe_refused"],
        summary["overall_safe_refusal_on_unanswerable"]["total_unanswerable"],
    )

    report = {
        "test_name": "Bộ Test 3: Kiểm chứng Giả thiết 3 (Hallucination Control & Safe Refusal Matrix)",
        "hypothesis": "Cơ chế yêu cầu LLM chỉ sử dụng thông tin được truy xuất và từ chối khi không có căn cứ phù hợp giúp giảm các câu trả lời không có căn cứ pháp lý.",
        "summary": summary,
        "details": result_data["details"],
    }

    report_dir = PROJECT_ROOT / "data" / "eval" / "bao_cao_ket_qua"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "report_h3_refusal.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info("Đã lưu báo cáo đầy đủ tại: %s", report_path)


if __name__ == "__main__":
    main()
