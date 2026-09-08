"""
scripts/build_index.py

Script chạy ĐỘC LẬP, 1 lần (offline), để build FAISS + BM25 index cho:
  1. law_index       <- data/raw/law/
  2. template_index  <- data/raw/templates/

Cách chạy (từ thư mục gốc project):
    python -m scripts.build_index

LƯU Ý PHỤ THUỘC:
Script này gọi:
  - modules.shared.document_reader.read_document   (Phần 3)
  - modules.shared.chunking.chunk_by_article        (Phần 3)
  - modules.shared.embedding.VectorDB               (Phần 4 - chưa build)

VectorDB (Phần 4) được giả định có interface:
  - VectorDB()                       -> khởi tạo, load embedding model
  - .create_index(chunks: List[dict]) -> mã hóa vector + build FAISS + BM25
  - .save_index(path: str)            -> lưu ra file .faiss và .pkl

Nếu Dev B code embedding.py với tên hàm/tham số khác, hãy chỉnh lại
phần gọi VectorDB bên dưới cho khớp.

Đường dẫn thư mục được lấy từ config.py. Nếu config.py của bạn dùng tên
biến khác với RAW_LAW_DIR / RAW_TEMPLATE_DIR / FAISS_INDEX_DIR, hãy sửa
lại phần đọc config trong hàm main() cho khớp.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

from modules.shared.chunking import chunk_by_article
from modules.shared.document_reader import read_document

try:
    from modules.shared.embedding import VectorDB  # Phần 4 - Dev B
except ImportError:
    VectorDB = None  # cho phép import script này trước khi Phần 4 xong, để test Phần 3 riêng

import config

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def build_chunks_from_folder(folder_path: Path) -> List[Dict[str, Any]]:
    """
    Đọc toàn bộ file .pdf/.docx hợp lệ trong 1 thư mục, chunk theo Điều,
    và gộp tất cả chunk lại thành 1 mảng duy nhất.

    Lỗi ở từng file riêng lẻ sẽ được log và bỏ qua, không làm dừng cả script.
    """
    all_chunks: List[Dict[str, Any]] = []

    if not folder_path.exists():
        logger.warning("Thư mục không tồn tại: %s - bỏ qua.", folder_path)
        return all_chunks

    files = sorted(
        f for f in folder_path.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS
    )

    if not files:
        logger.warning(
            "Không tìm thấy file .pdf/.docx nào trong %s", folder_path
        )
        return all_chunks

    for file_path in files:
        logger.info("Đang xử lý: %s", file_path.name)

        try:
            text = read_document(file_path)
        except Exception:
            logger.exception(
                "Lỗi khi đọc file '%s' - bỏ qua file này.", file_path.name
            )
            continue

        if not text.strip():
            logger.warning(
                "File '%s' không trích xuất được nội dung - bỏ qua.",
                file_path.name,
            )
            continue

        source_metadata = {"source": file_path.name}
        chunks = chunk_by_article(text, source_metadata)

        if not chunks:
            logger.warning("File '%s' không tạo được chunk nào.", file_path.name)
            continue

        logger.info("  -> %d chunks", len(chunks))
        all_chunks.extend(chunks)

    return all_chunks


def build_and_save_index(
    chunks: List[Dict[str, Any]],
    save_dir: Path,
    index_name: str,
) -> None:
    """
    Build FAISS + BM25 index từ danh sách chunk, và lưu ra đĩa.
    """
    if VectorDB is None:
        logger.error(
            "modules.shared.embedding.VectorDB chưa tồn tại (Phần 4 chưa build). "
            "Bỏ qua bước build index '%s'. Chunks đã sẵn sàng (%d chunks).",
            index_name,
            len(chunks),
        )
        return

    if not chunks:
        logger.warning(
            "Không có chunk nào để build index '%s' - bỏ qua.", index_name
        )
        return

    logger.info("Building index '%s' với %d chunks...", index_name, len(chunks))

    vector_db = VectorDB()
    vector_db.create_index(chunks)

    save_dir.mkdir(parents=True, exist_ok=True)
    save_path = save_dir / index_name
    vector_db.save_index(str(save_path))

    logger.info("Đã lưu index '%s' tại %s", index_name, save_path)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # Đường dẫn lấy từ config.py, có fallback mặc định nếu tên biến chưa khớp.
    law_folder = Path(getattr(config, "RAW_LAW_DIR", "data/raw/law"))
    template_folder = Path(getattr(config, "RAW_TEMPLATE_DIR", "data/raw/templates"))
    index_dir = Path(getattr(config, "FAISS_INDEX_DIR", "data/faiss_index"))

    # 5.1 - 5.3: Build law_index
    logger.info("=== BUILD LAW INDEX (data/raw/law/) ===")
    law_chunks = build_chunks_from_folder(law_folder)
    build_and_save_index(law_chunks, index_dir, "law_index")

    # 5.4: Build template_index
    logger.info("=== BUILD TEMPLATE INDEX (data/raw/templates/) ===")
    template_chunks = build_chunks_from_folder(template_folder)
    build_and_save_index(template_chunks, index_dir, "template_index")

    logger.info("Hoàn tất build index.")


if __name__ == "__main__":
    main()
