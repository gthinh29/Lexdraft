"""
scripts/prune_laws.py

Script tiện ích hỗ trợ kiểm tra và lọc dữ liệu văn bản pháp luật (.md)
trong thư mục data/raw/law/.md/ theo phạm vi hợp đồng dịch vụ.
Hỗ trợ kiểm tra đơn lẻ 1 file (--file) hoặc toàn bộ thư mục.
"""

import argparse
import logging
import re
import sys
from pathlib import Path

# Thêm thư mục gốc dự án vào sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.shared.chunking import chunk_by_article, extract_law_header  # noqa: E402
from modules.shared.document_reader import read_document  # noqa: E402

# Thiết lập encoding UTF-8 cho Windows console
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
logger = logging.getLogger("prune_laws")


def inspect_single_law_file(file_path: Path) -> bool:
    """
    Kiểm tra chi tiết cấu trúc, metadata và các điều khoản của 1 file luật.
    """
    if not file_path.exists():
        logger.error("❌ File không tồn tại: %s", file_path)
        return False

    logger.info("==================================================")
    logger.info("KIỂM TRA TẬP TIN LUẬT: %s", file_path.name)
    logger.info("Đường dẫn: %s", file_path)
    logger.info("==================================================")

    try:
        text = read_document(file_path)
        if not text.strip():
            logger.error("❌ File rỗng hoặc không đọc được nội dung chữ.")
            return False

        char_count = len(text)
        line_count = len(text.splitlines())
        logger.info(
            "📊 Thống kê: %d dòng | %d ký tự | Kích thước: %.2f KB",
            line_count,
            char_count,
            file_path.stat().st_size / 1024,
        )

        # 1. Trích xuất metadata tiêu đề luật
        header = extract_law_header(text, filename=file_path.name)
        logger.info("📋 Thông tin pháp lý trích xuất:")
        logger.info("   - Tên luật: %s", header.get("law_name") or "(Chưa nhận diện)")
        logger.info("   - Số hiệu: %s", header.get("law_number") or "(Không có)")
        logger.info("   - Ngày ban hành: %s", header.get("issued_date") or "(Không có)")
        logger.info(
            "   - Ngày hiệu lực: %s", header.get("effective_date") or "(Không có)"
        )
        logger.info("   - Trạng thái: %s", header.get("status", "Còn hiệu lực"))
        if header.get("is_consolidated"):
            logger.info("   - Loại văn bản: Văn bản hợp nhất (VBHN)")

        # 2. Kiểm tra các Điều khoản
        articles = re.findall(r"(\*\*Điều\s+\d+[^.\n]*\.[^\n]*)", text)
        if not articles:
            articles = re.findall(r"(Điều\s+\d+[^.\n]*\.[^\n]*)", text)

        logger.info("🔍 Phát hiện %d Điều luật trong văn bản.", len(articles))
        if articles:
            logger.info("   - Điều đầu: %s", articles[0])
            logger.info("   - Điều cuối: %s", articles[-1])

        # 3. Thử nghiệm cắt chunk
        metadata = {
            "source": file_path.name,
            "doc_name": file_path.stem.lower(),
            "doc_type": "law",
            **{k: v for k, v in header.items() if v},
        }
        chunks = chunk_by_article(text=text, source_metadata=metadata)
        logger.info(
            "✂️  Cắt chunk thành công: %d chunks trích xuất sẵn sàng cho FAISS.",
            len(chunks),
        )

        logger.info("✅ File hợp lệ và sẵn sàng để lập chỉ mục (indexing)!")
        return True

    except Exception as e:
        logger.exception("❌ Lỗi khi kiểm tra file '%s': %s", file_path.name, e)
        return False


def verify_law_files(law_dir: Path) -> None:
    """Kiểm tra toàn bộ các file markdown văn bản luật trong thư mục."""
    if not law_dir.exists():
        logger.warning("Thư mục %s không tồn tại.", law_dir)
        return

    md_files = sorted(list(law_dir.glob("*.md")))
    logger.info("Tìm thấy %d file .md trong %s", len(md_files), law_dir)
    for f in md_files:
        content = f.read_text(encoding="utf-8")
        logger.info("- %s: %d ký tự", f.name, len(content))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tiện ích kiểm tra và lọc dữ liệu văn bản pháp luật (.md)."
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        default=None,
        help="Đường dẫn hoặc tên file luật cụ thể cần kiểm tra (ví dụ: LuatBaoVeDuLieuCaNhan91_2025.md).",
    )
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    law_dir = base_dir / "data" / "raw" / "law" / ".md"

    if args.file:
        target_path = Path(args.file)
        if not target_path.exists():
            # Thử tìm trong thư mục data/raw/law/.md/
            candidate = law_dir / target_path.name
            if candidate.exists():
                target_path = candidate
            else:
                candidate2 = base_dir / "data" / "raw" / "law" / target_path.name
                if candidate2.exists():
                    target_path = candidate2

        inspect_single_law_file(target_path)
    else:
        verify_law_files(law_dir)


if __name__ == "__main__":
    main()
