# Ghi Chú Phát Triển & Tiến Độ Dự Án Lexdraft

---

## 1. Tóm tắt công việc đã thực hiện

### 1.1. Chuẩn hóa A4 Paper View & Xuất Word (.docx)
- **Tự động căn giữa tiêu đề và số hợp đồng:**
  - Thay vì dùng regex hay thư viện chuyển đổi trung gian (mammoth), hệ thống đọc trực tiếp thuộc tính `paragraph.alignment` từ đối tượng `python-docx` (`WD_ALIGN_PARAGRAPH.CENTER`).
  - Sử dụng class CSS `.a4p-center`, `.a4p-justify`, `.a4p-left` kết hợp `!important` để tránh bị Streamlit container style ghi đè.
- **Lọc bỏ ký tự ngăn cách:** Tự động loại bỏ các dấu gạch ngang Markdown thừa (`---`, `***`) giữa các chunk nội dung.
- **Khoảng cách dòng chuẩn:** Thiết lập `line-height: 1.5` chuẩn soạn thảo văn bản Word.
- **Thanh trượt Zoom Preview:** Cho phép phóng to / thu nhỏ khung xem trước A4 từ 50% đến 150% (mặc định 100%).

---

### 1.2. Refactor cấu trúc mã nguồn `app.py` (Modular Architecture)
Từ file `app.py` nguyên khối **~1640 dòng**, dự án đã được chia nhỏ thành kiến trúc module chuyên biệt:

```
Lexdraft/
├── app.py                          # ~180 dòng: Entry point Streamlit, cache warmup, routing
├── .streamlit/
│   └── config.toml                 # Cấu hình theme tối & headless mode
├── ui/
│   ├── styles.py                   # CSS toàn cục Dark Modern Theme & định dạng A4
│   └── pages/
│       ├── page_home.py            # 🏠 Trang chủ (Tổng quan & Điều hướng nhanh)
│       ├── page_risk.py            # 📤 Gợi ý Rủi ro Pháp lý & Panel đánh giá
│       ├── page_drafting.py        # 📝 Soạn thảo Hợp đồng, 1-Click preset, Zoom, Tải Word
│       └── page_chatbot.py         # 💬 Chatbot Hỏi – Đáp (Q&A Dual Mode)
└── modules/
    └── drafting/
        └── document_utils.py       # Xử lý xuất Word (.docx) và render HTML preview
```

---

### 1.3. Tối ưu hóa Backend & Quota API
- **Batch Risk Evaluation:** Phân tích rủi ro gộp theo lô (Batch mode) giúp giảm số lượng cuộc gọi API đến Gemini từ N lần xuống 1 lần.
- **Streaming Pipeline:** Cung cấp hàm generator `stream_analyze_contract` phát sự kiện real-time (`meta`, `result`, `progress`, `done`) kèm thanh tiến trình.
- **Batch Tier-3 Law Validity:** Gom các văn bản chưa đối chiếu được ở Cấp 1 & 2 để hỏi LLM 1 lần duy nhất thay vì hỏi rời rạc.
- **Bắt lỗi 429 Quota Exceeded:** Tự động nhận diện thời gian chờ từ thông báo của Google API (`retry in Xs`) và cung cấp thông báo rõ ràng cho người dùng.

---

## 2. Nhật ký Commit (Branch: `dev`)

Toàn bộ các thay đổi trên đã được phân tách và đẩy lên GitHub branch `dev`:

| Commit Hash | Loại commit | Nội dung |
|:---|:---|:---|
| `3271d7c` | `feat(data)` | Bổ sung Luật Bảo vệ dữ liệu cá nhân 91/2025 và file test hợp đồng `data/test_contract_risky.docx` |
| `ed55a05` | `feat(shared)` | Nâng cấp GeminiClient xử lý retry rate-limit động và thông báo lỗi 429 quota |
| `34d53f7` | `feat(risk_assessment)` | Cài đặt đánh giá rủi ro dạng batch và generator streaming kèm Tier-3 batch |
| `553302a` | `feat(drafting,chatbot)` | Tinh chỉnh quy tắc tách dòng điều khoản và cơ chế reset context chatbot về Chế độ B |
| `888d134` | `feat(drafting)` | Tạo `document_utils.py` đóng gói logic tạo Word và preview A4 HTML |
| `4f73ca5` | `refactor(ui)` | Modular hóa giao diện Streamlit: tách `styles.py`, thư mục `ui/pages/` và rút gọn `app.py` |

---

## 3. Trạng thái vận hành
- **Server Streamlit:** Đang chạy ổn định tại cổng `http://localhost:8501`.
- **Pre-commit checks:** Tất cả code đều vượt qua kiểm tra định dạng và quy chuẩn của `ruff`.
