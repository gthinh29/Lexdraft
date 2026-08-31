# TÀI LIỆU ĐẶC TẢ YÊU CẦU PHẦN MỀM (SRS) & KIẾN TRÚC HỆ THỐNG
**Dự án:** Xây dựng hệ thống hỗ trợ soạn thảo và gợi ý rủi ro hợp đồng dịch vụ bằng LLM kết hợp RAG
**Phiên bản:** 2.0 (Bao gồm chi tiết toàn diện từ Báo cáo TTTN & Tài liệu Kiến trúc)

---

## CHƯƠNG 1: TỔNG QUAN DỰ ÁN

### 1.1. Lý do chọn đề tài
Trong bối cảnh hiện nay, doanh nghiệp nhỏ và cá nhân thường dùng mẫu hợp đồng trên Internet mà thiếu kiến thức pháp lý, dẫn đến điều khoản mâu thuẫn, trái luật, hoặc bỏ sót quyền lợi. Thuê luật sư tốn kém, trong khi các AI chatbot thông thường lại hay mắc lỗi "hallucination" (bịa đặt thông tin). Do đó, cần một hệ thống ứng dụng kỹ thuật Retrieval-Augmented Generation (RAG) để sinh hợp đồng, tra cứu và gợi ý rủi ro **dựa trên căn cứ pháp lý được truy xuất thật**, giúp người dùng kiểm chứng thông tin dễ dàng.

### 1.2. Mục đích của dự án
- **Tổng quát:** Xây dựng ứng dụng Web hỗ trợ người dùng soạn thảo và gợi ý rủi ro pháp lý hợp đồng dịch vụ bằng LLM + RAG, cung cấp nội dung có căn cứ và trích dẫn cụ thể.
- **Cụ thể về hệ thống:**
  - Thu thập, xây dựng cơ sở tri thức pháp luật liên quan hợp đồng dịch vụ.
  - Sinh bản nháp hợp đồng từ form nhập liệu.
  - Tự động phân tích từng điều khoản hợp đồng tải lên (PDF/DOCX) để gợi ý rủi ro kèm trích dẫn.
  - Xây dựng module chatbot Q&A pháp luật hoạt động có hoặc không có ngữ cảnh hợp đồng.
  - Cài đặt cơ chế bắt buộc mô hình từ chối trả lời nếu thiếu căn cứ.
- **Đánh giá:** Dùng Ragas đo lường độ chính xác, trung thực và liên quan của câu trả lời.

### 1.3. Đối tượng và Phạm vi
- **Phạm vi nghiệp vụ:** Hợp đồng dịch vụ (thiết kế website, phát triển phần mềm, bảo trì, tư vấn, đào tạo, marketing). KHÔNG hỗ trợ: lao động, mua bán hàng hóa, xây dựng, tín dụng, bảo hiểm, hôn nhân...
- **Phạm vi dữ liệu:** Bộ luật Dân sự 2015, Luật Thương mại 2005, nghị định liên quan, các mẫu hợp đồng công khai. KHÔNG dùng dữ liệu nội bộ doanh nghiệp.
- **Giới hạn hệ thống:** Kết quả mang tính chất tham khảo, không thay thế luật sư. Chatbot Q&A chỉ phân tích hợp đồng nếu đang ở chế độ có ngữ cảnh. Chỉ hỗ trợ đọc file PDF dạng text.

### 1.4. Giả thiết khoa học
1. Việc kết hợp LLM với RAG giúp cải thiện khả năng trả lời chính xác so với LLM đơn thuần.
2. Tổ chức dữ liệu theo Điều/Khoản và lưu metadata giúp hệ thống trích dẫn chính xác.
3. Cơ chế yêu cầu LLM "chỉ dùng thông tin truy xuất và từ chối khi thiếu căn cứ" giúp giảm hallucination.

---

## CHƯƠNG 2: CƠ SỞ LÝ THUYẾT VÀ CÔNG NGHỆ

### 2.1. RAG (Retrieval-Augmented Generation) là gì
RAG kết hợp bộ truy xuất (retriever) để tìm văn bản liên quan từ vector DB, sau đó cấp cho mô hình sinh (generator/LLM) làm ngữ cảnh để trả lời. Khác với Fine-tuning, RAG cho phép cập nhật tri thức dễ dàng bằng cách thêm tài liệu vào index và bắt buộc LLM chỉ trả lời trong phạm vi văn bản đó, giúp trích dẫn ngược lại nguồn gốc văn bản.

### 2.2. Text Embedding & Độ tương đồng (Cosine Similarity)
Embedding là quá trình chuyển văn bản thành vector số học. Hệ thống tìm kiếm các đoạn luật/hợp đồng dựa trên khoảng cách vector, dùng công thức Cosine Similarity:
`Cosine_Similarity(A,B) = (A · B) / (||A|| × ||B||)`
Khoảng cách càng gần 1, hai đoạn văn bản càng tương đồng về ngữ nghĩa.
**Bắt buộc:** Phải dùng CÙNG MỘT embedding model cho cả bước index văn bản và bước người dùng đặt câu hỏi.

### 2.3. Hallucination
Là hiện tượng LLM tạo ra thông tin không có thật. Nghiên cứu thực nghiệm cho thấy ngay cả hệ thống có RAG vẫn có tỷ lệ bịa đặt 17-33%. Do đó, hệ thống này cần một lớp prompt engineering chặt chẽ (được quy định ở Chương 5) để giảm thiểu tối đa hiện tượng này.

---

## CHƯƠNG 3: KIẾN TRÚC HỆ THỐNG PHẦN MỀM

### 3.1. Kiến trúc Modular Monolith
Toàn bộ chạy trong 1 tiến trình duy nhất (không tách microservices), nhưng tổ chức code theo domain nghiệp vụ.

```text
┌───────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Streamlit)                           │
│  - Form nhập thông tin soạn thảo                                      │
│  - Upload hợp đồng (PDF/DOCX) → hiển thị kết quả gợi ý rủi ro tự động │
│  - Giao diện chatbot hỏi-đáp (độc lập hoặc tiếp nối từ module 1/2)    │
└───────────────────────────┬─────────────────────────────────────────┘
                             │ gọi qua service.py (interface công khai)
        ┌────────────────────┼────────────────────────┐
        ▼                    ▼                         ▼
┌───────────────────┐ ┌────────────────────────┐ ┌─────────────────────────┐
│ MODULE: DRAFTING  │ │ MODULE: RISK_ASSESSMENT│ │ MODULE: CHATBOT_QA      │
│ (domain: soạn thảo)│ │ (domain: gợi ý rủi ro) │ │ (domain: hỏi-đáp Q&A)   │
│                    │ │                        │ │                        │
│ service.py ◄────── │ │ service.py ◄────────── │ │ service.py ◄────────── │
│ retrieval.py       │ │ retrieval.py (private) │ │ retrieval.py (private) │
│  (private)         │ │ prompts.py             │ │ prompts.py             │
│ prompts.py         │ │ (pipeline tự động)     │ │ chat_session.py        │
└──────────┬─────────┘ └───────────┬────────────┘ └────────────┬─────────┘
           │                       │                            │
           └───────────────────────┼────────────────────────────┘
                                    ▼
                    ┌──────────────────────────────┐
                    │   MODULE: SHARED (dùng chung)│
                    │   - embedding.py             │
                    │   - llm_client.py            │
                    │   - document_reader.py       │
                    │   - chunking.py              │
                    └──────────────┬────────────────┘
                                   │
        ┌──────────────────────────┼───────────────────────────┐
        ▼                                                       ▼
┌─────────────────────────┐                       ┌───────────────────────────┐
│   RETRIEVAL LAYER       │                       │    GENERATION LAYER       │
│ - FAISS: law_index      │                       │ Gemini API (LLM)          │
│ - FAISS: template_index │                       │ - Sinh bản nháp hợp đồng  │
│ - FAISS: contract_index │                       │ - Phân tích điều khoản    │
│ - BM25 (keyword search) │                       │ - Trả lời hội thoại Q&A   │
└──────────────────────────┘                       └───────────────────────────┘
```

### 3.2. Nguyên tắc ranh giới Module
- Các module domain (`drafting`, `risk_assessment`, `chatbot_qa`) CHỈ giao tiếp với bên ngoài qua `service.py`. Các file khác là private.
- Module 2 (Gợi ý rủi ro) là quy trình one-shot (chạy tự động 1 lần khi có hợp đồng). Mọi tương tác hội thoại thuộc về Module 3. Module 2 **không** chứa `chat_session.py`.
- Module 3 nhận context từ Module 2 qua interface công khai, không tự ý đọc state nội bộ của Module 2.

### 3.3. Bảng công nghệ (Tech Stack)

| Layer | Công nghệ | Vai trò & Lý do |
|---|---|---|
| Ngôn ngữ | Python 3.10 | Toàn bộ backend xử lý |
| Giao diện | Streamlit | UI & chatbot interface |
| Điều phối | LangChain | Orchestration luồng retrieval -> prompt -> gen |
| **Embedding** | `bkai-foundation-models/vietnamese-bi-encoder` | Mã hóa văn bản tiếng Việt. **Lý do chọn:** Tối ưu tiếng Việt, nhẹ, chạy tốt CPU, không mất phí API như `text-embedding-3` hay đòi hỏi GPU như `Qwen3-Embedding`. |
| Vector DB | FAISS | Lưu trữ & tìm kiếm ngữ nghĩa (Cosine similarity) |
| Keyword search | `rank_bm25` | Khớp từ khóa / số Điều-Khoản |
| LLM | Gemini API | Sinh văn bản. Dùng 1 model duy nhất để giảm phức tạp, đủ đáp ứng cả 3 module |
| Đọc File | `pdfplumber`, `PyPDF`, `python-docx` | Trích xuất text |
| Đánh giá | Ragas | Đo lường hệ thống tự động |

### 3.4. Cấu trúc thư mục dự án
```text
project/
├── app.py                          # Entry point Streamlit
├── config.py                       # API keys, đường dẫn index
├── data/
│   ├── raw/                        # Văn bản luật gốc, mẫu hợp đồng gốc
│   ├── processed/                  # Sau khi chunking
│   └── faiss_index/                # Lưu law_index, template_index
├── modules/
│   ├── drafting/                   # Soạn thảo (service.py, retrieval.py, prompts.py)
│   ├── risk_assessment/            # Gợi ý rủi ro (service.py, retrieval.py, prompts.py)
│   ├── chatbot_qa/                 # Hỏi-đáp (service.py, retrieval.py, prompts.py, chat_session.py)
│   └── shared/                     # Dùng chung (embedding, llm_client, document_reader, chunking)
├── evaluation/                     # testset.csv, run_ragas_eval.py
└── scripts/                        # build_index.py
```

---

## CHƯƠNG 4: YÊU CẦU CHỨC NĂNG & LUỒNG XỬ LÝ (FLOWS)

### 4.1. Module 1: Soạn thảo hợp đồng (Drafting)
Người dùng điền form thông tin -> Module sinh bản nháp.
**Luồng xử lý (Flow):**
1. Người dùng submit form -> `drafting/service.py` nhận request.
2. Module xác định loại hợp đồng, lấy mẫu từ `template_index`.
3. `drafting/retrieval.py` lấy luật liên quan từ `law_index`.
4. `drafting/prompts.py` ghép prompt: *"Dựa trên mẫu cấu trúc: {template}... luật: {law}... soạn hợp đồng với thông tin: {user_input}"*
5. `shared/llm_client.py` gọi Gemini API sinh bản nháp.
6. `drafting/service.py` gọi TỰ ĐỘNG `risk_assessment/service.py` để chạy pipeline gợi ý rủi ro ngay lập tức cho bản nháp.

### 4.2. Module 2: Gợi ý rủi ro pháp lý (Risk Assessment)
Hoạt động TỰ ĐỘNG (One-shot) khi upload hợp đồng (PDF/DOCX) hoặc nhận bản nháp từ Module 1.
**Luồng xử lý (Flow):**
1. `risk_assessment/service.py` nhận request.
2. `shared/document_reader.py` & `chunking.py` trích xuất, chia Điều/Khoản, nhúng vào `contract_index` (phiên hiện tại).
3. Lặp qua TỪNG điều khoản:
   - `risk_assessment/retrieval.py` tìm luật bằng Hybrid (FAISS + BM25) trong `law_index`.
   - `risk_assessment/prompts.py` ghép prompt đối chiếu.
   - LLM phân tích, gợi ý rủi ro và trích dẫn.
4. Trả về mảng: [Điều khoản, Rủi ro, Trích dẫn căn cứ]. Kết quả lưu làm context cho Module 3.

### 4.3. Module 3: Chatbot Hỏi-Đáp (Q&A)
Đảm nhiệm hội thoại nhiều lượt.
**Chế độ A (Có ngữ cảnh hợp đồng - Kế tiếp từ Module 1,2):**
1. `chatbot_qa/service.py` nhận request kèm `session_id`.
2. `chat_session.py` nạp context ban đầu (Hợp đồng + kết quả gợi ý rủi ro).
3. Người dùng hỏi sâu -> `retrieval.py` tìm thêm trong `contract_index` và `law_index`.
4. LLM trả lời, bám sát cả luật và bối cảnh hợp đồng.
5. Lịch sử được lưu tại `chat_session.py`.

**Chế độ B (Không có ngữ cảnh - Độc lập):**
1. Khởi tạo phiên không context hợp đồng.
2. Chỉ truy vấn `law_index`.
3. Hoạt động như tra cứu pháp luật chung (Không phân tích hợp đồng cụ thể).

---

## CHƯƠNG 5: CHIẾN LƯỢC DỮ LIỆU & CHỐNG HALLUCINATION

### 5.1. Ba kho tri thức (FAISS Indexes)
Hệ thống **không gộp chung** index để tránh nhiễu:
| Index | Dữ liệu | Khi nào tạo | Vai trò |
|---|---|---|---|
| `law_index` | Luật DS, Luật TM, Nghị định | Tĩnh (Offline) | Căn cứ đối chiếu pháp lý (Cả 3 module dùng) |
| `template_index` | Các mẫu hợp đồng dịch vụ | Tĩnh (Offline) | Khung cấu trúc (Chỉ Module 1 dùng) |
| `contract_index` | Hợp đồng upload / tự sinh | Động (Mỗi phiên) | Nội dung cần phân tích (Module 2, 3 dùng) |

### 5.2. Kỹ thuật Chunking (Structure-aware chunking)
**Không dùng Fixed-size, Recursive hay Semantic chunking** vì văn bản luật/hợp đồng đã có ranh giới cấu trúc rõ ràng. Phải chia theo **Điều/Khoản** bằng Regex để giữ nguyên 1 đơn vị ý nghĩa:
```python
PATTERN = r"(Điều\s+\d+[\.:]?.*?)(?=Điều\s+\d+|\Z)"
# Mỗi chunk sẽ lưu lại metadata: {"article": article_no, "source_document": ...}
```
Metadata này là bắt buộc để hệ thống sau đó có thể trích dẫn lại chính xác số Điều cho người dùng.

### 5.3. Kỹ thuật chống Hallucination (BẮT BUỘC)
Cài đặt tại `shared/llm_client.py` và áp dụng cho toàn bộ lệnh gọi LLM:
1. LLM chỉ được phép trả lời dựa trên context đã truy xuất.
2. Phải kèm trích dẫn (citations) lấy từ metadata.
3. Nếu score truy xuất thấp, hệ thống chủ động cắt luồng và báo "Không tìm thấy căn cứ pháp lý".
**Code mô phỏng Prompt:**
```python
prompt = f"""Chỉ sử dụng thông tin trong phần CĂN CỨ dưới đây để trả lời.
Nếu không đủ căn cứ để trả lời, hãy nói rõ là không có thông tin.

CĂN CỨ:
{context}

CÂU HỎI: {query}"""
```

---

## CHƯƠNG 6: TỐI ƯU HÓA ĐỘ TRỄ VÀ ĐIỂM LƯU Ý KỸ THUẬT

### 6.1. Tối ưu Token và Độ trễ (LLM Cloud API)
- **Quản lý lịch sử hội thoại:** Module 3 KHÔNG được tích lũy toàn bộ context của các lượt trước. Lịch sử (`chat_session.py`) chỉ giữ lại văn bản hỏi-đáp, còn context RAG (tài liệu truy xuất được) chỉ đính kèm cho câu hỏi hiện tại.
- **Tắt chế độ "Thinking":** Các dòng mô hình Gemini mới có khả năng extended thinking tự động bật, làm tăng token/độ trễ. Cần config `thinking_budget=0` tắt mặc định cho 3 module.
- **Giới hạn truy xuất:** Top-K duy trì ở 3-5. Chỉ tăng nếu đánh giá Context Recall thấp.
- **Cô lập Index:** Module nào cần index nào thì chỉ query index đó.

### 6.2. Các lưu ý triển khai khác
| Vấn đề | Giải pháp |
|---|---|
| Semantic search bỏ sót số Điều chính xác | Kết hợp BM25 (keyword) song song với FAISS (Semantic) (Hybrid search) |
| LLM trích dẫn sai số Điều | Luôn ép metadata (article) đi cùng chunk, không cho LLM tự "nhớ" số Điều |
| 3 module dễ code lẫn lộn | Giữ kỷ luật: mọi lệnh gọi qua `service.py`, không gọi thẳng file nội bộ của nhau |
| Quản lý phiên hội thoại | Module 3 có `chat_session.py` gắn với session tương ứng, không đặt file này bên trong `risk_assessment` |

---

## CHƯƠNG 7: KIỂM THỬ VÀ ĐÁNH GIÁ (EVALUATION)

Dùng framework **Ragas** (Reference-free) kết hợp bộ `testset.csv` (câu hỏi + đáp án tham khảo).
Các chỉ số đo lường:
1. **Context Precision:** Đo lường bao nhiêu chunk truy xuất thực sự liên quan.
2. **Context Recall:** Đo lường hệ thống có bỏ sót thông tin quan trọng nào không.
3. **Faithfulness:** Câu trả lời có bám sát context truy xuất không, hay LLM tự suy diễn.
4. **Answer Relevancy:** Câu trả lời có đúng trọng tâm câu hỏi không.

---

## CHƯƠNG 8: KỸ THUẬT MỞ RỘNG THAM KHẢO (NẾU CÒN THỜI GIAN)
*(Các tính năng không bắt buộc, chỉ áp dụng nếu có thời gian dư sau khi hoàn thành kiến trúc cốt lõi)*
1. **Sub-query decomposition:** Module 3 tự bóc tách câu hỏi phức tạp thành nhiều câu truy vấn nhỏ trước khi search.
2. **Tool-calling (Tra cứu chéo):** LLM tự phát hiện 1 luật dẫn chiếu luật khác và gọi truy vấn thêm 1 lượt nữa.
3. **Enrichment embedding:** Nhồi thẳng metadata vào chuỗi text trước khi mã hóa vector: `embed_text = f"[{ten_van_ban}] - [Điều {so_dieu}] : {noi_dung}"` để vector giữ vị trí ngữ cảnh.
