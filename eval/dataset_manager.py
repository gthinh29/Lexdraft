"""eval/dataset_manager.py

Quản lý nạp, thẩm định (validation) và lưu trữ Golden Dataset.
Đảm bảo 100% dữ liệu đầu vào đáp ứng đúng tiêu chuẩn kiểm thử Ragas.
"""

import json
import logging
from pathlib import Path
from typing import List, Tuple

from eval.schema import GoldenSample

logger = logging.getLogger(__name__)

DEFAULT_DATASET_PATH = Path("data/eval/golden_dataset.json")


class DatasetManager:
    """Quản lý Golden Dataset cho pipeline đánh giá RAG."""

    def __init__(self, file_path: Path = DEFAULT_DATASET_PATH):
        self.file_path = Path(file_path)

    def load_dataset(self) -> List[GoldenSample]:
        """Đọc và validate dataset từ file JSON."""
        if not self.file_path.exists():
            logger.warning(
                f"File {self.file_path} không tồn tại. Trả về danh sách rỗng."
            )
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            samples = [GoldenSample(**item) for item in raw_data]
            logger.info(
                f"Đã nạp thành công {len(samples)} mẫu kiểm thử từ {self.file_path}."
            )
            return samples
        except Exception as e:
            logger.error(f"Lỗi khi đọc file {self.file_path}: {e}")
            raise

    def save_dataset(self, samples: List[GoldenSample]) -> None:
        """Lưu danh sách GoldenSample xuống file JSON."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        data = [s.model_dump() for s in samples]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Đã lưu {len(samples)} mẫu kiểm thử vào {self.file_path}.")

    def validate_quality(self, samples: List[GoldenSample]) -> Tuple[bool, List[str]]:
        """
        Thẩm định chất lượng của Golden Dataset:
        1. ID không được trùng lặp.
        2. Question phải có độ dài tối thiểu 10 ký tự.
        3. Ground truth phải có độ dài tối thiểu 20 ký tự.
        4. Bắt buộc phải có ít nhất 1 Điều luật tham chiếu (expected_laws).
        """
        issues = []
        seen_ids = set()

        for s in samples:
            if s.id in seen_ids:
                issues.append(f"[{s.id}] ID bị trùng lặp.")
            seen_ids.add(s.id)

            if len(s.question.strip()) < 10:
                issues.append(
                    f"[{s.id}] Câu hỏi quá ngắn ({len(s.question.strip())} ký tự)."
                )

            if len(s.ground_truth.strip()) < 20:
                issues.append(
                    f"[{s.id}] Ground truth quá ngắn hoặc thiếu căn cứ ({len(s.ground_truth.strip())} ký tự)."
                )

            if not s.expected_laws and s.category != "Negative / Law Validity":
                issues.append(
                    f"[{s.id}] Thiếu danh sách Điều luật tham chiếu (expected_laws)."
                )

        is_valid = len(issues) == 0
        return is_valid, issues
