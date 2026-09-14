"""
scripts/build_index.py

Script chạy offline một lần để xây dựng Vector Database (FAISS Index)
cho toàn bộ văn bản luật (law_index) và mẫu hợp đồng (template_index).

Tuân thủ:
- Implementation Plan Phần 5
- SRS 5.1, 5.2
- Hỗ trợ chế độ dry-run (--dry-run) để kiểm tra số lượng chunk và nội dung
  trước khi kích hoạt API embedding thật.
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Thêm thư mục gốc dự án vào PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config  # noqa: E402
from modules.shared.chunking import (  # noqa: E402
    chunk_by_article,
    extract_law_header,
    extract_template_header,
)
from modules.shared.document_reader import read_document  # noqa: E402
from modules.shared.embedding import VectorDB  # noqa: E402

# Thiết lập logging hỗ trợ UTF-8 trên Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("build_index")


def process_directory(raw_dir: Path) -> List[Dict[str, Any]]:
    """
    Duyệt toàn bộ file Markdown (.md) trong thư mục (ưu tiên thư mục con .md),
    đọc text và cắt theo Điều/Khoản.
    """
    if not raw_dir.exists():
        logger.warning("Thư mục '%s' không tồn tại.", raw_dir)
        return []

    # Ưu tiên tìm trong thư mục con .md nếu có (vd: data/raw/law/.md)
    md_subfolder = raw_dir / ".md"
    search_dir = md_subfolder if md_subfolder.exists() else raw_dir

    files = sorted(
        [
            f
            for f in search_dir.glob("**/*.md")
            if f.is_file() and not f.name.startswith("~") and not f.name.startswith(".")
        ]
    )

    if not files:
        logger.warning("Không tìm thấy file .md hợp lệ nào trong '%s'.", search_dir)
        return []

    all_chunks: List[Dict[str, Any]] = []
    logger.info(
        "Tìm thấy %d file .md trong '%s'. Bắt đầu xử lý...", len(files), search_dir
    )

    for file_path in files:
        logger.info("--> Đang đọc file: %s", file_path.name)
        try:
            text = read_document(file_path)
            if not text.strip():
                logger.warning(
                    "File '%s' rỗng hoặc không trích xuất được chữ.", file_path.name
                )
                continue

            # Phân biệt xử lý metadata giữa Mẫu Hợp Đồng và Văn Bản Luật
            is_template = "template" in str(raw_dir).lower()
            if is_template:
                tpl_header = extract_template_header(text, filename=file_path.name)
                enriched_metadata = {
                    "source": file_path.name,
                    "doc_name": file_path.stem.lower(),
                    **{
                        k: v for k, v in tpl_header.items() if v is not None and v != ""
                    },
                }
                logger.info(
                    "    Mẫu: %s | Căn cứ: %d văn bản | Thẩm định: %s",
                    tpl_header.get("template_name", "?"),
                    len(tpl_header.get("legal_bases", [])),
                    tpl_header.get("basis_validity", "?"),
                )
            else:
                law_header = extract_law_header(text, filename=file_path.name)
                enriched_metadata = {
                    "source": file_path.name,
                    "doc_name": file_path.stem.lower(),
                    "doc_type": "law",
                    **{k: v for k, v in law_header.items() if v},
                }
                logger.info(
                    "    Pháp lý: %s | Số: %s | Hiệu lực: %s%s",
                    law_header.get("law_name", "?"),
                    law_header.get("law_number", "?"),
                    law_header.get("effective_date", "?"),
                    f" (VBHN {law_header.get('vbhn_number') or law_header.get('consolidated_year', '')})"
                    if law_header.get("is_consolidated")
                    else "",
                )

            # Chunk theo cấu trúc Điều/Khoản
            chunks = chunk_by_article(
                text=text,
                source_metadata=enriched_metadata,
            )
            logger.info(
                "    Trích xuất thành công %d chunks từ '%s'.",
                len(chunks),
                file_path.name,
            )
            all_chunks.extend(chunks)
        except Exception as e:
            logger.exception("    Lỗi khi đọc file '%s': %s", file_path.name, e)

    return all_chunks


def build_one_index(
    raw_dir: Path,
    index_path: Path,
    dry_run: bool = False,
) -> int:
    """
    Xây dựng một index cụ thể (law_index hoặc template_index).
    """
    logger.info("==================================================")
    logger.info("XÂY DỰNG INDEX: %s", index_path.name)
    logger.info("Nguồn dữ liệu: %s", raw_dir)
    logger.info("==================================================")

    chunks = process_directory(raw_dir)
    logger.info("Tổng số chunks trích xuất được: %d", len(chunks))

    if not chunks:
        logger.warning(
            "Không có chunks nào để lập chỉ mục cho '%s'. Bỏ qua.", index_path.name
        )
        return 0

    if dry_run:
        logger.info("[DRY-RUN] Chế độ kiểm tra (Dry Run). Sẽ KHÔNG gọi API embedding.")
        # In mẫu 3 chunks đầu tiên để kiểm tra cấu trúc
        for idx, c in enumerate(chunks[:3], 1):
            meta = c.get("metadata", {})
            logger.info(
                "  [Sample Chunk %d] File: %s | Điều: %s | Độ dài text: %d chars",
                idx,
                meta.get("source"),
                meta.get("article"),
                len(c.get("content", "")),
            )
        logger.info("[DRY-RUN] Kiểm tra hoàn tất cho %s.", index_path.name)
        return len(chunks)

    # Chạy nạp embedding thật và lưu FAISS
    start_time = time.time()
    db = VectorDB()
    logger.info("Đang tạo embeddings và nạp vào FAISS Index...")
    db.create_index(chunks)

    logger.info("Đang lưu index ra đĩa tại '%s'...", index_path)
    db.save_index(str(index_path))

    elapsed = time.time() - start_time
    logger.info(
        "✅ THÀNH CÔNG: %s (%d vectors) - Thời gian: %.1fs",
        index_path,
        len(chunks),
        elapsed,
    )
    return len(chunks)


def main():
    parser = argparse.ArgumentParser(
        description="Build offline FAISS VectorDB index cho Lexdraft."
    )
    parser.add_argument(
        "--target",
        choices=["all", "law", "template"],
        default="all",
        help="Chọn index cần build: all, law, hoặc template (mặc định: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Chạy thử nghiệm kiểm tra cắt chunk và metadata, không gọi API embedding thật.",
    )
    args = parser.parse_args()

    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    raw_dir = Path(getattr(config, "RAW_DATA_DIR", data_dir / "raw"))
    index_dir = Path(getattr(config, "FAISS_INDEX_DIR", data_dir / "faiss_index"))

    law_raw_dir = raw_dir / "law"
    template_raw_dir = raw_dir / "templates"

    law_index_path = index_dir / "law_index"
    template_index_path = index_dir / "template_index"

    total_chunks = 0

    # 1. Build Law Index
    if args.target in ("all", "law"):
        count = build_one_index(law_raw_dir, law_index_path, dry_run=args.dry_run)
        total_chunks += count

    # 2. Build Template Index
    if args.target in ("all", "template"):
        count = build_one_index(
            template_raw_dir, template_index_path, dry_run=args.dry_run
        )
        total_chunks += count

    logger.info("==================================================")
    status_str = (
        "KIỂM TRA (DRY-RUN) HOÀN TẤT"
        if args.dry_run
        else "BUILD TOÀN BỘ INDEX THÀNH CÔNG"
    )
    logger.info("%s! Tổng cộng: %d chunks.", status_str, total_chunks)
    logger.info("==================================================")


if __name__ == "__main__":
    main()
