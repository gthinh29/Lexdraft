# HƯỚNG DẪN DÀNH CHO NHÀ PHÁT TRIỂN (DEVELOPER GUIDE)

Chào mừng bạn đến với dự án **Lexdraft** (LLM + RAG Hợp đồng dịch vụ). Tài liệu này quy định các tiêu chuẩn làm việc nhóm, setup môi trường và quy tắc viết code để đảm bảo dự án chuyên nghiệp, dễ bảo trì và không bị conflict.

## 1. Cài đặt Môi trường Phát triển

Bắt buộc sử dụng môi trường ảo (Virtual Environment) để không ảnh hưởng đến máy thật.

### Bước 1: Khởi tạo và kích hoạt venv
**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```
**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Bước 2: Cài đặt thư viện
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Bước 3: Cài đặt Pre-commit hooks (Bắt buộc)
```bash
pre-commit install
```
*Lý do:* Hệ thống tự động chạy `ruff` để format và kiểm tra lỗi code mỗi khi bạn gõ lệnh `git commit`. Code sai chuẩn sẽ bị chặn lại để bạn sửa.

### Bước 4: File `.env`
Tạo file `.env` ở thư mục gốc (ngang hàng `config.py`) và thêm:
```env
GEMINI_API_KEY="your_api_key_here"
```
*(File này đã được ignore trong git, không bao giờ commit file này lên)*

---

## 2. Quy tắc Git (Branch & Commit)

### 2.1. Quy ước đặt tên Branch
Không code trực tiếp trên nhánh `main`. Hãy tạo nhánh mới từ `main` theo cú pháp:
- `feature/<tên-chức-năng>`: Thêm tính năng mới (vd: `feature/drafting-ui`)
- `bugfix/<tên-lỗi>`: Sửa lỗi (vd: `bugfix/fix-faiss-load-error`)
- `refactor/<tên-module>`: Tối ưu lại code (vd: `refactor/clean-prompts`)

### 2.2. Quy ước viết Commit Message (Conventional Commits)
Cấu trúc: `type(scope): description`
- `feat`: Thêm tính năng mới (vd: `feat(drafting): thêm logic sinh hợp đồng`)
- `fix`: Sửa lỗi (vd: `fix(shared): sửa lỗi đường dẫn load index`)
- `docs`: Cập nhật tài liệu (vd: `docs: cập nhật hướng dẫn setup`)
- `style`: Format code (vd: `style: format code bằng ruff`)
- `refactor`: Viết lại code không làm đổi chức năng (vd: `refactor(chatbot): tách class LLM`)

---

## 3. Kiến trúc & Quy tắc Code (Nghiêm ngặt)

### 3.1. Ranh giới Module
Hệ thống áp dụng kiến trúc **Modular Monolith**. Có 3 module chính: `drafting`, `risk_assessment`, `chatbot_qa` và 1 module dùng chung `shared`.
- **LUẬT:** Nếu bạn làm việc ở module `A`, bạn **KHÔNG ĐƯỢC** import trực tiếp các file nội bộ (như `retrieval.py` hay `prompts.py`) của module `B`.
- Giao tiếp giữa các module phải đi qua `service.py` của module đó.
- Ví dụ: `drafting` muốn lấy kết quả rủi ro, phải gọi `risk_assessment.service.analyze_risk()`.

### 3.2. Quản lý Logging
Tuyệt đối **KHÔNG** dùng `print()` để debug trên server. Hãy dùng module logger chuẩn đã cấu hình sẵn.
```python
from modules.shared.logger import setup_logger

logger = setup_logger(__name__)

def my_func():
    logger.info("Đang bắt đầu xử lý...")
    try:
        # logic
        pass
    except Exception as e:
        logger.error(f"Lỗi xảy ra: {str(e)}", exc_info=True)
```

### 3.3. Đường dẫn File
Không dùng đường dẫn cứng dạng chuỗi (vd: `"data/raw/luat.pdf"`). Hãy dùng các hằng số đã định nghĩa trong `config.py`:
```python
from config import Config
import os

file_path = os.path.join(Config.RAW_DATA_DIR, "luat.pdf")
```
---

*Hãy đọc kỹ `SRS_He_Thong.md` để hiểu luồng nghiệp vụ trước khi code!*
