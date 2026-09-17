"""
scripts/prepare_hypothesis_datasets.py

Khởi tạo và thẩm định 3 file dataset độc lập tương ứng với 3 Giả thiết khoa học (Mục 3.3):
1. data/eval/dataset_h1_ab.json (50 câu A/B testing)
2. data/eval/dataset_h2_metadata.json (44 câu Fact Retrieval + Metadata chuẩn)
3. data/eval/dataset_h3_refusal.json (35 câu ma trận 4 nhóm: In-domain, Outdated, Out-of-Domain, Non-existent)
"""

import json
import re
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
EVAL_DIR.mkdir(parents=True, exist_ok=True)

GOLDEN_DATASET_PATH = EVAL_DIR / "golden_dataset.json"


def prepare_datasets():
    print(f"Đọc dữ liệu nguồn từ {GOLDEN_DATASET_PATH}...")
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        golden_data = json.load(f)

    # -------------------------------------------------------------
    # 1. Dataset H1: A/B Testing (Toàn bộ 50 câu)
    # -------------------------------------------------------------
    dataset_h1 = []
    for item in golden_data:
        dataset_h1.append(
            {
                "id": item["id"],
                "category": item["category"],
                "question": item["question"],
                "ground_truth": item["ground_truth"],
                "expected_laws": item.get("expected_laws", []),
            }
        )
    h1_path = EVAL_DIR / "dataset_h1_ab.json"
    with open(h1_path, "w", encoding="utf-8") as f:
        json.dump(dataset_h1, f, ensure_ascii=False, indent=2)
    print(f"-> Đã tạo {h1_path.name} ({len(dataset_h1)} mẫu).")

    # -------------------------------------------------------------
    # 2. Dataset H2: Fact Retrieval & Metadata Precision (44 câu)
    # -------------------------------------------------------------
    dataset_h2 = []
    fact_items = [item for item in golden_data if item["category"] == "Fact Retrieval"]
    for item in fact_items:
        gt = item["ground_truth"]
        # Trích xuất expected article và expected law từ ground truth / expected_laws
        art_match = re.search(r"Điều\s+(\d+)", gt)
        expected_art = f"Điều {art_match.group(1)}" if art_match else ""

        clause_match = re.search(r"khoản\s+(\d+)", gt, re.IGNORECASE)
        expected_clause = f"Khoản {clause_match.group(1)}" if clause_match else ""

        # Xác định văn bản luật mong đợi
        expected_doc = ""
        if "Bộ luật Dân sự" in gt or "BLDS" in item["question"]:
            expected_doc = "Bộ luật Dân sự"
        elif "Luật Thương mại" in gt or "LTM" in item["question"]:
            expected_doc = "Luật Thương mại"
        elif "Luật Sở hữu trí tuệ" in gt or "SHTT" in item["question"]:
            expected_doc = "Luật Sở hữu trí tuệ"
        elif "Giao dịch điện tử" in gt or "GDĐT" in item["question"]:
            expected_doc = "Luật Giao dịch điện tử"
        elif "dữ liệu cá nhân" in gt:
            expected_doc = "Luật Bảo vệ dữ liệu cá nhân"

        dataset_h2.append(
            {
                "id": item["id"],
                "question": item["question"],
                "ground_truth": item["ground_truth"],
                "expected_doc": expected_doc,
                "expected_article": expected_art,
                "expected_clause": expected_clause,
                "expected_laws": item.get("expected_laws", []),
            }
        )
    h2_path = EVAL_DIR / "dataset_h2_metadata.json"
    with open(h2_path, "w", encoding="utf-8") as f:
        json.dump(dataset_h2, f, ensure_ascii=False, indent=2)
    print(f"-> Đã tạo {h2_path.name} ({len(dataset_h2)} mẫu).")

    # -------------------------------------------------------------
    # 3. Dataset H3: Hallucination Control & Safe Refusal Matrix (35 câu)
    # -------------------------------------------------------------
    dataset_h3 = []

    # Nhóm 1: In-domain Fact (15 câu chọn lọc tiêu biểu từ Fact Retrieval)
    selected_fact_ids = [
        "TC_FACT_01",
        "TC_FACT_02",
        "TC_FACT_04",
        "TC_FACT_07",
        "TC_FACT_09",
        "TC_FACT_10",
        "TC_FACT_13",
        "TC_FACT_14",
        "TC_FACT_17",
        "TC_FACT_20",
        "TC_FACT_22",
        "TC_FACT_24",
        "TC_FACT_27",
        "TC_FACT_30",
        "TC_FACT_33",
    ]
    for item in fact_items:
        if item["id"] in selected_fact_ids:
            dataset_h3.append(
                {
                    "id": f"H3_IN_{item['id']}",
                    "group": "in_domain_fact",
                    "group_desc": "Câu hỏi trong phạm vi và có căn cứ pháp lý trong CSDL",
                    "question": item["question"],
                    "expected_behavior": "answer_with_citation",  # Bắt buộc trả lời kèm trích dẫn
                    "must_refuse": False,
                    "ground_truth": item["ground_truth"],
                }
            )

    # Nhóm 2: Outdated / Fake Laws (6 câu từ golden_dataset)
    neg_items = [
        item for item in golden_data if item["category"] == "Negative / Law Validity"
    ]
    for item in neg_items:
        dataset_h3.append(
            {
                "id": f"H3_OUTDATED_{item['id']}",
                "group": "outdated_or_fake_law",
                "group_desc": "Viện dẫn luật hết hiệu lực hoặc văn bản giả mạo",
                "question": item["question"],
                "expected_behavior": "safe_refusal",  # Bắt buộc từ chối hoặc cảnh báo hết hiệu lực
                "must_refuse": True,
                "ground_truth": item["ground_truth"],
            }
        )

    # Nhóm 3: Out-of-Domain (8 câu ngoài phạm vi hợp đồng dịch vụ)
    ood_items = [
        {
            "id": "H3_OOD_01",
            "topic": "Luật Hình sự",
            "question": "Mức hình phạt đối với tội lừa đảo chiếm đoạt tài sản theo Bộ luật Hình sự là bao nhiêu năm tù?",
            "ground_truth": "Ngoài phạm vi. Hệ thống Lexdraft chuyên trách về hợp đồng dịch vụ và pháp luật thương mại/dân sự, không hỗ trợ tư vấn Bộ luật Hình sự.",
        },
        {
            "id": "H3_OOD_02",
            "topic": "Luật Đất đai",
            "question": "Điều kiện chuyển nhượng quyền sử dụng đất nông nghiệp theo Luật Đất đai mới nhất là gì?",
            "ground_truth": "Ngoài phạm vi. Hệ thống không hỗ trợ giao dịch chuyển nhượng bất động sản và quyền sử dụng đất theo Luật Đất đai.",
        },
        {
            "id": "H3_OOD_03",
            "topic": "Luật Hôn nhân & Gia đình",
            "question": "Thủ tục ly hôn thuận tình và phân chia tài sản chung vợ chồng được quy định như thế nào?",
            "ground_truth": "Ngoài phạm vi. Pháp luật về quan hệ hôn nhân và gia đình không thuộc phạm vi cơ sở tri thức hợp đồng dịch vụ.",
        },
        {
            "id": "H3_OOD_04",
            "topic": "Bộ luật Lao động",
            "question": "Thời giờ làm việc bình thường của người lao động theo Bộ luật Lao động là bao nhiêu giờ một ngày và một tuần?",
            "ground_truth": "Ngoài phạm vi. Quan hệ lao động thuộc điều chỉnh của Bộ luật Lao động, khác biệt với quan hệ hợp đồng dịch vụ thương mại.",
        },
        {
            "id": "H3_OOD_05",
            "topic": "Luật Giao thông đường bộ",
            "question": "Mức phạt vi phạm nồng độ cồn khi điều khiển xe ô tô theo quy định xử phạt vi phạm giao thông hiện hành là bao nhiêu?",
            "ground_truth": "Ngoài phạm vi. Quy định xử phạt vi phạm hành chính giao thông đường bộ nằm ngoài phạm vi đề tài.",
        },
        {
            "id": "H3_OOD_06",
            "topic": "Luật Bảo hiểm xã hội",
            "question": "Hồ sơ hưởng chế độ thai sản của lao động nữ theo Luật Bảo hiểm xã hội gồm những giấy tờ nào?",
            "ground_truth": "Ngoài phạm vi. Chế độ bảo hiểm xã hội không thuộc phạm vi cơ sở tri thức của hệ thống.",
        },
        {
            "id": "H3_OOD_07",
            "topic": "Luật Xây dựng",
            "question": "Điều kiện để được cấp Giấy phép xây dựng nhà ở riêng lẻ tại đô thị gồm những tiêu chuẩn nào?",
            "ground_truth": "Ngoài phạm vi. Hợp đồng xây dựng và thủ tục cấp phép xây dựng không nằm trong phạm vi hợp đồng dịch vụ của đề tài.",
        },
        {
            "id": "H3_OOD_08",
            "topic": "Tố tụng Dân sự",
            "question": "Quy trình tố tụng thụ lý đơn khởi kiện dân sự tại Tòa án nhân dân cấp quận/huyện diễn ra theo các bước nào?",
            "ground_truth": "Ngoài phạm vi. Trình tự thủ tục tố tụng tư pháp tại Tòa án nằm ngoài phạm vi hỗ trợ soạn thảo hợp đồng dịch vụ.",
        },
    ]
    for item in ood_items:
        dataset_h3.append(
            {
                "id": item["id"],
                "group": "out_of_domain",
                "group_desc": "Câu hỏi ngoài phạm vi hợp đồng dịch vụ (Hình sự, Đất đai, Hôn nhân, Lao động...)",
                "question": item["question"],
                "expected_behavior": "safe_refusal",
                "must_refuse": True,
                "ground_truth": item["ground_truth"],
            }
        )

    # Nhóm 4: Non-existent Article (6 câu bẫy điều luật bịa đặt / không tồn tại)
    non_existent_items = [
        {
            "id": "H3_NONEXIST_01",
            "question": "Điều 999 Bộ luật Dân sự 2015 quy định về mức phạt vi phạm hợp đồng dịch vụ như thế nào?",
            "ground_truth": "Điều luật không tồn tại. Bộ luật Dân sự năm 2015 chỉ có tổng cộng 689 Điều, không có Điều 999. Hệ thống phải từ chối hoặc chỉ rõ điều luật không tồn tại.",
        },
        {
            "id": "H3_NONEXIST_02",
            "question": "Mức bồi thường thiệt hại được quy định tại Điều 888 Luật Thương mại 2005 là bao nhiêu phần trăm?",
            "ground_truth": "Điều luật không tồn tại. Luật Thương mại năm 2005 chỉ có 324 Điều, hoàn toàn không có Điều 888.",
        },
        {
            "id": "H3_NONEXIST_03",
            "question": "Quy định về bảo hộ phần mềm theo Điều 500 Luật Sở hữu trí tuệ bao gồm những nguyên tắc gì?",
            "ground_truth": "Điều luật không tồn tại. Luật Sở hữu trí tuệ chỉ có 222 Điều, không tồn tại Điều 500.",
        },
        {
            "id": "H3_NONEXIST_04",
            "question": "Điều 777 Luật Giao dịch điện tử 2023 hướng dẫn lưu trữ chứng từ hợp đồng điện tử như thế nào?",
            "ground_truth": "Điều luật không tồn tại. Luật Giao dịch điện tử 2023 chỉ có 53 Điều, không tồn tại Điều 777.",
        },
        {
            "id": "H3_NONEXIST_05",
            "question": "Mức phạt tiền xử phạt hành chính tại Điều 999 Luật Bảo vệ dữ liệu cá nhân 2025 là bao nhiêu?",
            "ground_truth": "Điều luật không tồn tại. Luật Bảo vệ dữ liệu cá nhân không có Điều 999.",
        },
        {
            "id": "H3_NONEXIST_06",
            "question": "Điều 650 Luật Thương mại 2005 quy định chế tài gì đối với bên vi phạm nghĩa vụ giao hàng dịch vụ?",
            "ground_truth": "Điều luật không tồn tại. Luật Thương mại 2005 chỉ có 324 Điều, không tồn tại Điều 650.",
        },
    ]
    for item in non_existent_items:
        dataset_h3.append(
            {
                "id": item["id"],
                "group": "non_existent_article",
                "group_desc": "Yêu cầu tra cứu Điều/Khoản giả định không có thật trong luật",
                "question": item["question"],
                "expected_behavior": "safe_refusal",
                "must_refuse": True,
                "ground_truth": item["ground_truth"],
            }
        )

    h3_path = EVAL_DIR / "dataset_h3_refusal.json"
    with open(h3_path, "w", encoding="utf-8") as f:
        json.dump(dataset_h3, f, ensure_ascii=False, indent=2)
    print(
        f"-> Đã tạo {h3_path.name} ({len(dataset_h3)} mẫu: {len(selected_fact_ids)} In-domain, {len(neg_items)} Outdated, {len(ood_items)} Out-of-Domain, {len(non_existent_items)} Non-existent)."
    )


if __name__ == "__main__":
    prepare_datasets()
