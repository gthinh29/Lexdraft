"""
modules/shared/chunking.py

Module dùng chung: chia văn bản pháp lý / hợp đồng thành các chunk theo
đơn vị "Điều" (structure-aware chunking), đúng theo SRS Chương 5.2.

Không dùng Fixed-size / Recursive / Semantic chunking vì văn bản luật
và hợp đồng đã có ranh giới cấu trúc rõ ràng theo Điều/Khoản.
"""

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Nhãn dùng cho các đoạn không xác định được số Điều cụ thể (Phần 3.6).
FALLBACK_ARTICLE_LABEL = "Quy định chung"

# Regex mở rộng (Phần 3.5): bắt được cả "Điều 1.", "Điều 1:", "ĐIỀU 1", "điều 1"...
# re.IGNORECASE xử lý đúng hoa/thường có dấu tiếng Việt (đã kiểm chứng thực nghiệm).
# re.DOTALL để khớp nội dung nhiều dòng trong 1 Điều.
ARTICLE_PATTERN = re.compile(
    r"(Điều\s+\d+[\.:]?.*?)(?=Điều\s+\d+|\Z)",
    re.DOTALL | re.IGNORECASE,
)

# Regex phụ để lấy số Điều ra khỏi nội dung, dùng chuẩn hóa metadata.
ARTICLE_NUMBER_PATTERN = re.compile(r"Điều\s+(\d+)", re.IGNORECASE)


def chunk_by_article(
    text: str,
    source_metadata: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Chia văn bản thành các chunk theo từng "Điều".

    Args:
        text: text thô (đã đọc từ document_reader.read_document).
        source_metadata: metadata gốc của văn bản, vd:
            {"source": "BoLuatDanSu2015.pdf"}
            Sẽ được merge vào metadata của từng chunk.

    Returns:
        Danh sách dict theo format:
        [
            {
                "content": "Điều 1. Nội dung...",
                "metadata": {"source": "...", "article": "Điều 1"}
            },
            ...
        ]

        Fallback (Phần 3.6): nếu văn bản không chứa từ khóa "Điều" nào (vd: một
        số mẫu hợp đồng tự do không đánh số Điều), toàn bộ text được trả về
        như MỘT chunk duy nhất với "article": "Quy định chung", để không mất
        dữ liệu và tránh giá trị None gây lỗi khi hiển thị/trích dẫn về sau.
    """
    source_metadata = dict(source_metadata) if source_metadata else {}

    if not text or not text.strip():
        logger.warning(
            "chunk_by_article nhận text rỗng (source=%s) - trả về mảng rỗng.",
            source_metadata.get("source", "unknown"),
        )
        return []

    matches = list(ARTICLE_PATTERN.finditer(text))

    if not matches:
        logger.warning(
            "Không tìm thấy cấu trúc 'Điều' trong văn bản (source=%s). "
            "Áp dụng fallback: trả về toàn văn bản dưới dạng 1 chunk với "
            "article='%s'.",
            source_metadata.get("source", "unknown"),
            FALLBACK_ARTICLE_LABEL,
        )
        return [
            {
                "content": text.strip(),
                "metadata": {**source_metadata, "article": FALLBACK_ARTICLE_LABEL},
            }
        ]

    chunks: List[Dict[str, Any]] = []

    for match in matches:
        raw_content = match.group(1).strip()

        if not raw_content:
            continue

        # Chuẩn hóa nhãn về dạng "Điều X" dù văn bản gốc viết "ĐIỀU X", "điều X:"...
        # để metadata trích dẫn nhất quán, không phụ thuộc cách viết hoa/thường gốc.
        number_match = ARTICLE_NUMBER_PATTERN.search(raw_content)
        article_label = f"Điều {number_match.group(1)}" if number_match else FALLBACK_ARTICLE_LABEL

        chunks.append(
            {
                "content": raw_content,
                "metadata": {**source_metadata, "article": article_label},
            }
        )

    if not chunks:
        # Trường hợp hiếm: có match nhưng nội dung rỗng sau khi strip.
        logger.warning(
            "Regex khớp nhưng không tạo được chunk hợp lệ nào (source=%s).",
            source_metadata.get("source", "unknown"),
        )

    return chunks


# ---------------------------------------------------------------------------
# Phần 3.7 - BLIND TEST: chạy trực tiếp file này để in kết quả chunking ra
# terminal, kiểm tra bằng mắt việc cắt Điều và gán metadata có đúng không,
# TRƯỚC KHI kích hoạt gọi API Embedding (Phần 4) trên dữ liệu thật.
#
# Cách chạy: python -m modules.shared.chunking
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    _SAMPLE_TEXT = """
Điều 1. Phạm vi điều chỉnh
Luật này quy định về hợp đồng dịch vụ giữa các bên.

ĐIỀU 2: Đối tượng áp dụng
Áp dụng cho cá nhân, tổ chức có hoạt động cung cấp dịch vụ.

điều 3 Giải thích từ ngữ
Trong Luật này, các từ ngữ dưới đây được hiểu như sau...

Điều 10. Quyền và nghĩa vụ của các bên
1. Bên cung cấp dịch vụ có quyền...
2. Bên sử dụng dịch vụ có nghĩa vụ...
"""

    _SAMPLE_TEXT_NO_STRUCTURE = """
Đây là một đoạn văn bản tự do, không được đánh số theo cấu trúc Điều/Khoản,
ví dụ như phần lời mở đầu hoặc mô tả tổng quan của một mẫu hợp đồng.
"""

    print("=" * 80)
    print("BLIND TEST 1: Văn bản có cấu trúc Điều (hoa/thường/dấu câu khác nhau)")
    print("=" * 80)
    result_1 = chunk_by_article(_SAMPLE_TEXT, {"source": "test_luat_mau.txt"})
    for idx, chunk in enumerate(result_1, start=1):
        print(f"\n--- Chunk {idx} ---")
        print("Metadata:", chunk["metadata"])
        print("Content :", chunk["content"][:120].replace("\n", " "), "...")

    print("\n" + "=" * 80)
    print("BLIND TEST 2: Văn bản KHÔNG có cấu trúc Điều (kiểm tra fallback)")
    print("=" * 80)
    result_2 = chunk_by_article(_SAMPLE_TEXT_NO_STRUCTURE, {"source": "test_tu_do.txt"})
    for idx, chunk in enumerate(result_2, start=1):
        print(f"\n--- Chunk {idx} ---")
        print("Metadata:", chunk["metadata"])
        print("Content :", chunk["content"][:120].replace("\n", " "), "...")

    print("\n" + "=" * 80)
    print(f"Tổng kết: Test 1 -> {len(result_1)} chunks | Test 2 -> {len(result_2)} chunks")
    print("=" * 80)
