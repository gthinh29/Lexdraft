"""
scripts/prune_laws.py

Script tiện ích hỗ trợ kiểm tra và lọc dữ liệu văn bản pháp luật (.md)
trong thư mục data/raw/law/.md/ theo phạm vi hợp đồng dịch vụ.
"""

import logging
from pathlib import Path

logger = logging.getLogger("prune_laws")


def verify_law_files(law_dir: Path) -> None:
    """Kiểm tra các file markdown văn bản luật có tồn tại và đọc được."""
    if not law_dir.exists():
        logger.warning("Thư mục %s không tồn tại.", law_dir)
        return

    md_files = list(law_dir.glob("*.md"))
    logger.info("Tìm thấy %d file .md trong %s", len(md_files), law_dir)
    for f in md_files:
        content = f.read_text(encoding="utf-8")
        logger.info("- %s: %d ký tự", f.name, len(content))


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    base_dir = Path(__file__).resolve().parent.parent
    law_dir = base_dir / "data" / "raw" / "law" / ".md"
    verify_law_files(law_dir)


if __name__ == "__main__":
    main()
