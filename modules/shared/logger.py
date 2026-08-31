import logging
import sys
from pathlib import Path

# Đảm bảo thư mục logs tồn tại
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

def setup_logger(name: str) -> logging.Logger:
    """
    Khởi tạo logger chuẩn cho toàn bộ project.
    Sử dụng:
    from modules.shared.logger import setup_logger
    logger = setup_logger(__name__)
    """
    logger = logging.getLogger(name)
    
    # Chỉ setup nếu logger chưa có handler để tránh log lặp lại
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Ghi log ra Console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Ghi log ra file
        file_handler = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
