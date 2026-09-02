# Lexdraft — Legal Contract Drafting & Risk Assessment System ⚖️🤖

![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-121212?style=flat)
![Gemini](https://img.shields.io/badge/Gemini_API-8E75B2?style=flat&logo=googlebard&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-green)
![RAG](https://img.shields.io/badge/Architecture-RAG-orange)

> **Lexdraft** là hệ thống ứng dụng Web hỗ trợ người dùng **soạn thảo**, **rà soát**, và **gợi ý rủi ro pháp lý** đối với hợp đồng dịch vụ. Hệ thống ứng dụng mô hình ngôn ngữ lớn (LLM) kết hợp kỹ thuật **Retrieval-Augmented Generation (RAG)** để cung cấp nội dung có tính xác thực cao, chống hiện tượng Hallucination bằng cách bắt buộc trích dẫn rõ ràng căn cứ pháp lý.

## 🌟 Tính năng cốt lõi (Core Features)

Hệ thống được thiết kế theo kiến trúc **Modular Monolith**, bao gồm 3 Module nghiệp vụ chính:

1. 📝 **Module Soạn thảo Hợp đồng (Drafting)**
   - Nhập liệu qua form thông tin cơ bản (bên A/B, giá trị, thời hạn, điều khoản bảo mật, v.v.).
   - Tự động sinh bản nháp hợp đồng dịch vụ hoàn chỉnh dựa trên kho mẫu (`template_index`) và luật (`law_index`).
   - Tự động chạy kiểm tra rủi ro pháp lý ngay sau khi sinh bản nháp.

2. 🔍 **Module Gợi ý rủi ro (Risk Assessment - One-shot Pipeline)**
   - Cho phép tải lên hợp đồng có sẵn dưới dạng PDF hoặc DOCX.
   - Tự động trích xuất, chia Điều/Khoản (`Structure-aware chunking`).
   - Đối chiếu quy định pháp luật bằng **FAISS** (sử dụng Metadata Filtering để truy xuất chính xác số Điều/Khoản).
   - Gợi ý rủi ro cho **toàn bộ hợp đồng** kèm theo trích dẫn căn cứ pháp lý cụ thể.

3. 💬 **Module Chatbot Hỏi-Đáp (Q&A)**
   - **Chế độ có ngữ cảnh:** Cho phép người dùng đặt câu hỏi đào sâu về hợp đồng vừa soạn thảo hoặc vừa tải lên (Ví dụ: *"Vì sao điều khoản 5 bị đánh giá là rủi ro?"*).
   - **Chế độ không ngữ cảnh:** Hoạt động độc lập như một trợ lý tra cứu luật pháp tổng quát dựa trên kho tri thức.

## 🏗️ Kiến trúc Hệ thống & Tech Stack

Hệ thống tuân thủ nghiêm ngặt chuẩn **Modular Monolith**, phân tách ranh giới rõ ràng thông qua `service.py`.

- **Giao diện (UI):** Streamlit.
- **Điều phối (Orchestration):** LangChain.
- **Xử lý File (Parser):** `pdfplumber`, `python-docx`.
- **Cơ sở dữ liệu (Vector DB):** FAISS (bản CPU, sử dụng Metadata Filtering thay thế Hybrid Search).
- **Mô hình Nhúng (Embedding):** Gemini API (`text-embedding-004`).
- **Mô hình Sinh (LLM):** Gemini API (`gemini-2.5-flash`).
- **Kiểm thử (Evaluation):** `ragas`.

## 🚀 Hướng dẫn Cài đặt & Chạy dự án (Local Setup)

Vui lòng tham khảo kỹ [CONTRIBUTING.md](./CONTRIBUTING.md) để biết các chuẩn mực khi đóng góp code.

### 1. Yêu cầu hệ thống
- Python 3.10+
- Git

### 2. Cài đặt
```bash
# Clone repository
git clone https://github.com/gthinh29/Lexdraft.git
cd Lexdraft

# Tạo và kích hoạt môi trường ảo (Virtual Environment)
# Windows:
python -m venv venv
.\venv\Scripts\activate
# Mac/Linux:
python3 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Cài đặt pre-commit hooks (Bắt buộc cho Developer)
pre-commit install
```

### 3. Cấu hình Biến Môi Trường
Tạo file `.env` tại thư mục gốc của dự án (ngang hàng với `config.py`) và cung cấp API Key của Google Gemini:
```env
GEMINI_API_KEY="your_google_gemini_api_key_here"
```

### 4. Khởi chạy Ứng dụng
*(UI Streamlit đang trong quá trình phát triển)*
```bash
streamlit run app.py
```

## 📂 Cấu trúc Thư mục

```text
Lexdraft/
├── data/                  # Nơi chứa dữ liệu luật gốc (raw) và faiss_index
├── modules/               # Core backend 
│   ├── drafting/          # Module 1: Soạn thảo
│   ├── risk_assessment/   # Module 2: Gợi ý rủi ro (one-shot)
│   ├── chatbot_qa/        # Module 3: Chatbot Q&A (multi-turn)
│   └── shared/            # Tiện ích hạ tầng (chunking, llm_client, logger)
├── scripts/               # Các kịch bản chạy 1 lần (ví dụ: build_index.py)
├── evaluation/            # Bộ testset.csv và script đánh giá bằng Ragas
├── config.py              # File cấu hình trung tâm (quản lý đường dẫn, Model)
├── app.py                 # Streamlit App Entrypoint
└── CONTRIBUTING.md        # Hướng dẫn quy tắc code & Git workflow
```

## 🛡️ Cơ chế chống Hallucination (Nền tảng)
Dự án áp dụng chiến lược chống "bịa đặt thông tin" cực kỳ khắt khe:
1. **Chia 3 kho tri thức (FAISS Index)** độc lập để tránh gây nhiễu (`law_index`, `template_index`, `contract_index`).
2. **Structure-aware chunking**: Cắt văn bản theo ranh giới cấu trúc Điều/Khoản bằng Regex, đảm bảo 1 chunk = 1 đơn vị ý nghĩa trọn vẹn.
3. **Truy vết nguồn gốc**: Prompt luôn ép LLM phải sử dụng Metadata đi kèm để trích dẫn số Điều, nguồn luật. Nếu FAISS trả về điểm tương đồng quá thấp, LLM sẽ tự động từ chối trả lời.

---
**Disclaimer:** *Hệ thống chỉ mang tính chất tham khảo dựa trên thuật toán tìm kiếm RAG và LLM. Kết quả không có giá trị thay thế sự tư vấn pháp lý chuyên nghiệp từ luật sư.*