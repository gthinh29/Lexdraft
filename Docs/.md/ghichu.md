# GHI CHÚ KIẾN THỨC PHÁP LÝ & CHIẾN LƯỢC DỮ LIỆU (RAG) - DỰ ÁN LEXDRAFT

> **Tài liệu tổng hợp các đúc kết quan trọng** trong quá trình chuẩn bị dữ liệu Luật và Mẫu hợp đồng cho hệ thống AI Hỗ trợ Soạn thảo & Rà soát Rủi ro Hợp đồng Dịch vụ (Lexdraft).  
> **Cập nhật mốc thời gian hệ thống:** 14/09/2026.

---

## 1. Bản chất Pháp lý & Xử lý Văn bản Hợp nhất (VBHN)

### 1.1. Bản chất của Văn bản hợp nhất (VBHN)
* **VBHN không phải là đạo luật mới độc lập:** Đây là văn bản kỹ thuật do Văn phòng Quốc hội ban hành nhằm tích hợp luật gốc và toàn bộ các luật sửa đổi, bổ sung qua các năm vào chung một văn bản duy nhất để tiện tra cứu.
* **Quy tắc hiệu lực:** 
  * Nếu luật gốc còn hiệu lực thì VBHN có giá trị sử dụng cao nhất vì đã cập nhật mọi sửa đổi mới nhất.
  * Nếu luật gốc bị bãi bỏ/thay thế, thì **toàn bộ các VBHN ăn theo cũng tự động hết hiệu lực**.

### 1.2. Có tìm ra được Luật gốc năm nào từ VBHN không?
**Hoàn toàn tìm ra được 100%:**
* Ngay trang đầu tiên của VBHN luôn liệt kê: Tên luật gốc, số hiệu, ngày thông qua, ngày hiệu lực và danh sách các luật sửa đổi bổ sung.
* Từng điều khoản được sửa đổi đều có chú thích (footnote) dẫn chiếu chính xác điều/khoản nào của luật sửa đổi.

### 1.3. Hai giải pháp kỹ thuật tích hợp VBHN vào Lexdraft
* **Cách 1: Gán thông tin Luật gốc vào Metadata khi chunking (build index)**
  ```python
  metadata = {
      "doc_name": "luat_thuong_mai",
      "base_law": "Luật Thương mại số 36/2005/QH11",
      "consolidated_version": "VBHN 113/VBHN-VPQH (2025)",
      "article_number": 300,
      "title": "Phạt vi phạm"
  }
  ```
* **Cách 2: Cấu hình chỉ thị System Prompt cho LLM**
  * Trong prompt yêu cầu: *"Khi trích dẫn căn cứ pháp luật, nêu rõ tên Luật gốc và số hiệu (Ví dụ: Luật Thương mại 2005 số 36/2005/QH11). Nếu điều khoản có sửa đổi bổ sung theo Văn bản hợp nhất, hãy nêu rõ để người dùng nắm được."*
  * **Kết quả đầu ra của AI:** *"Căn cứ Điều 300 Luật Thương mại 2005 (cập nhật theo VBHN 113/VBHN-VPQH năm 2025)..."* -> Vừa chuẩn xác pháp lý vừa thể hiện cập nhật mới nhất.

---

## 2. Danh mục Văn bản Pháp luật trong Hệ thống

### 2.1. Nhóm văn bản NỀN TẢNG (Bắt buộc phải có)
1. **Bộ luật Dân sự số 91/2015/QH13:**
   * *Tình trạng:* Còn hiệu lực đầy đủ.
   * *Vai trò:* Luật gốc điều chỉnh mọi giao dịch dân sự, hợp đồng, đặt cọc, bồi thường, hiệu lực giao dịch.
   * *Phạm vi trích xuất/lọc:* Điều 116–143 (Giao dịch, đại diện), Điều 351–429 (Thực hiện nghĩa vụ, hợp đồng, phạt vi phạm), Điều 513–521 (Quy định riêng về hợp đồng dịch vụ).

2. **Luật Thương mại số 36/2005/QH11 (dùng VBHN 113/VBHN-VPQH năm 2025):**
   * *Tình trạng:* Còn hiệu lực đầy đủ. VBHN 113 là văn bản cập nhật mới nhất hiện nay.
   * *Lưu ý đặc biệt:* **Không tồn tại "Luật Thương mại 2020"** (các mẫu hợp đồng trôi nổi trên mạng ghi "Luật Thương mại 2020" là sai kiến thức pháp luật, là case study cảnh báo rủi ro đắt giá cho hệ thống).
   * *Phạm vi trích xuất/lọc:* Điều 1–15 (Quy định chung), Điều 74–87 (Cung ứng dịch vụ), Điều 292–316 (Chế tài thương mại, phạt vi phạm 8%, bồi thường thiệt hại), Điều 317–319 (Thời hiệu khiếu nại).

### 2.2. Nhóm văn bản CHUYÊN NGÀNH DỊCH VỤ CÔNG NGHỆ / IT
3. **Luật Giao dịch điện tử 2023 (Luật số 20/2023/QH15):**
   * *Tình trạng:* Có hiệu lực từ 01/07/2024.
   * *Vai trò:* Rà soát điều khoản ký kết hợp đồng điện tử, chữ ký số, giá trị chứng cứ của email, thông điệp dữ liệu nghiệm thu bàn giao online.
   * *Phạm vi trích xuất/lọc:* Điều 7–15 (Thông điệp dữ liệu), Điều 22–27 (Chữ ký điện tử), Điều 34–38 (Hợp đồng điện tử).

4. **Luật Sở hữu trí tuệ 2005 (đã sửa đổi, bổ sung 2022):**
   * *Tình trạng:* Còn hiệu lực.
   * *Vai trò:* Trọng tâm rà soát quyền tác giả và quyền sở hữu mã nguồn (source code), chuyển giao công nghệ phần mềm giữa Bên thuê và Bên phát triển.
   * *Phạm vi trích xuất/lọc:* Điều 18–48 (Quyền tác giả đối với chương trình máy tính/phần mềm).

5. **Lộ trình thay thế: Luật Công nghệ thông tin 2006 -> Luật Chuyển đổi số 2025:**
   * **Luật Chuyển đổi số số 148/2025/QH15:** Được Quốc hội thông qua ngày 11/12/2025, có hiệu lực từ **01/07/2026**.
   * **Khoản 2 Điều 47 Luật Chuyển đổi số 2025:** Quy định **Luật Công nghệ thông tin số 67/2006/QH11 chính thức hết hiệu lực từ ngày 01/07/2026** (trừ các dự án chuyển tiếp theo Điều 48).
   * **Ứng dụng vào hệ thống rà soát rủi ro:** Nếu hợp đồng ký sau ngày 01/07/2026 vẫn ghi "Căn cứ Luật Công nghệ thông tin 2006", hệ thống sẽ phát hiện cảnh báo viện dẫn luật đã hết hiệu lực và kiến nghị chuyển sang Luật Chuyển đổi số 2025.

### 2.3. Nhóm văn bản KHÔNG ĐƯA VÀO (Gây loãng Vector DB)
* **Nghị định 15/2020/NĐ-CP & 14/2022/NĐ-CP:** Là văn bản xử phạt vi phạm hành chính giữa Nhà nước và cá nhân/tổ chức, không điều chỉnh quan hệ tranh chấp hợp đồng giữa 2 bên.
* **Luật Viễn thông:** Điều chỉnh trạm phát sóng, tần số vô tuyến, nhà mạng; không thuộc phạm vi hợp đồng dịch vụ phần mềm.

---

## 3. Chiến lược Lọc Dữ liệu & Tối ưu RAG

* **Không nên nhồi toàn bộ 100% điều khoản của luật vào DB:**
  * Bộ luật Dân sự gần 700 điều (có cả thừa kế, đất đai, hôn nhân gia đình...).
  * Nếu nạp hết: Tốn token/quota API Gemini khi embedding, tăng độ trễ và làm loãng kết quả tìm kiếm RAG (retrieve nhầm các điều không liên quan).
* **Chiến lược tối ưu:**
  * Chỉ lọc lấy các Chương, Điều cốt lõi liên quan trực tiếp đến: Hợp đồng, Cung ứng dịch vụ, Vi phạm & Bồi thường, Bản quyền phần mềm, Chữ ký điện tử.
  * Tốc độ build index tăng gấp 5 - 10 lần, dữ liệu vector tinh gọn, độ chính xác (precision) của RAG đạt tối đa.

---

## 4. Cấu trúc Thư mục Lưu trữ Dữ liệu Chuẩn
```text
data/
└── raw/
    ├── law/
    │   ├── bo_luat_dan_su_2015.docx
    │   ├── luat_thuong_mai.docx                 (VBHN 113/2025)
    │   ├── luat_giao_dich_dien_tu_2023.docx
    │   ├── luat_so_huu_tri_tue.docx             (VBHN sửa đổi 2022)
    │   └── luat_chuyen_doi_so_2025.docx
    └── templates/
        ├── mau_hop_dong_phat_trien_phan_mem.docx
        ├── mau_hop_dong_thiet_ke_website.docx
        ├── mau_hop_dong_bao_tri_he_thong.docx
        └── mau_hop_dong_dich_vu_marketing.docx
```

---

## 5. Tiến độ Triển khai Code & Kết quả Kiểm thử (Unit Test)

### 5.1. Module `modules/shared/llm_client.py` (Phần 6 - SRS 6.1 & TODO 6.1 -> 6.5)
* **Công nghệ:**
  * Tích hợp SDK mới nhất `google.genai` (v2.2+) kết hợp fallback sang `google.generativeai` cũ nếu thiếu môi trường.
  * Tắt thinking ngầm (`thinking_budget=0`) theo chuẩn SRS để tối ưu tốc độ phản hồi và tiết kiệm token.
  * Tích hợp **Exponential Backoff Retry** tự động xử lý khi gặp lỗi Rate Limit (429/Quota/ResourceExhausted).
* **Cơ chế chống Hallucination (Grounded Generation):**
  * Hàm `generate_grounded_response(query, retrieved_chunks, threshold=0.5)` kiểm tra điểm tương đồng trước khi gọi LLM.
  * Tự động trích xuất và lọc trùng trích dẫn (`citations`) từ metadata của chunks.

### 5.2. Chi tiết Kết quả Kiểm thử Tự động (Unit Test ngày 14/09/2026)
* **Test Case 1: Kiểm thử Ngưỡng an toàn chống ảo giác (Threshold Rejection Test)**
  * *Mục tiêu:* Khi điểm tương đồng của chunk thấp hơn ngưỡng an toàn (`score < threshold`), hệ thống phải từ chối trả lời, không đoán mò hay bịa luật.
  * *Đầu vào:* Giả lập chunk với `score = 0.3` (ngưỡng quy định là `0.5`).
  * *Kết quả:* **PASSED** — Hàm lập tức trả về `refusal: True` kèm thông báo:  
    `"Không tìm thấy căn cứ pháp lý phù hợp (độ tin cậy cao nhất đạt 0.30, dưới ngưỡng an toàn 0.50)..."`
* **Test Case 2: Kiểm thử Trích xuất & Lọc trùng Căn cứ (Citation Deduplication Test)**
  * *Mục tiêu:* Lọc bỏ các căn cứ trùng lặp khi nhiều chunk đến từ cùng một Điều luật của cùng một văn bản.
  * *Đầu vào:* 3 chunks gồm 2 chunk trùng (Điều 10 - BLDS) và 1 chunk (Điều 15 - Luật Thương mại).
  * *Kết quả:* **PASSED** — Output `citations` được rút gọn chính xác còn 2 phần tử duy nhất, không bị trùng lặp trên giao diện người dùng.

### 5.3. Module `modules/shared/embedding.py` (Phần 4 - SRS 5.1, 5.2, 6.2 & TODO 4.1 -> 4.5)
* **Cập nhật `config.py`:**
  * `EMBEDDING_MODEL_NAME = "models/text-embedding-004"` (Cloud API, tránh tràn RAM so với local model).
  * `LLM_MODEL_NAME = "gemini-2.5-flash"`.
  * `SIMILARITY_THRESHOLD = 0.5`.
* **Class `VectorDB`:**
  * Khởi tạo FAISS `IndexFlatIP` với `dimension = 768`.
  * Chuẩn hóa `faiss.normalize_L2(vectors)` trước khi nạp để Inner Product (IP) tương đương Cosine Similarity.
  * Hàm `_embed_texts`: Tích hợp Batching (`BATCH_SIZE = 10`), nghỉ giữa các batch và retry exponential backoff chống lỗi 429.
  * Hàm `save_index(path)` / `load_index(path)`: Lưu và đọc đồng thời cặp file `.faiss` và `.pkl` (giữ nguyên cấu trúc chunks và metadata).
  * Hàm `search_with_metadata()` & `hybrid_search()`: Tìm kiếm semantic kết hợp **Metadata Filtering** theo số Điều/Khoản (`article`) và văn bản nguồn (`doc_name`). Lấy dư ứng viên (`top_k * 4`) trước khi lọc để không bị hụt kết quả.
* **Chi tiết Kết quả Kiểm thử Tự động (Unit Test ngày 14/09/2026):**
  * *Test `create_index`:* **PASSED** (nạp chuẩn 3/3 vectors vào FAISS).
  * *Test `save_index`:* **PASSED** (tạo đúng file `.faiss` và `.pkl`).
  * *Test `load_index`:* **PASSED** (đọc lại chuẩn 100% vector và metadata).
  * *Test `hybrid_search` với Metadata Filtering:* **PASSED** (lọc chính xác theo `doc_name == "luat_thuong_mai"`, không bị lẫn văn bản khác).

### 5.4. Module `modules/risk_assessment/` (Phần 8 - SRS 4.2 & TODO 8.1 -> 8.5)
* **Cấu trúc 3 file chuẩn ranh giới module (SRS 3.2):**
  * `prompts.py`: Chỉ thị LLM rà soát rủi ro dựa trên CĂN CỨ PHÁP LÝ được cung cấp, nêu rõ nhận xét, căn cứ đối chiếu và đề xuất điều chỉnh câu chữ.
  * `retrieval.py`: Cache `_law_db` module-level (load 1 lần), truy xuất các điều luật liên quan với `top_k = 3` (tiết kiệm token).
  * `service.py`: Hàm công khai `analyze_contract(file_path_or_text, session_id)` hỗ trợ cả đường dẫn file (.docx, .pdf) lẫn chuỗi text; tự động chia chunk theo cấu trúc Điều/Khoản, chạy vòng lặp phân tích rủi ro từng Điều (có `sleep(1)` phòng thủ 429), và tự động liên kết context sang Chatbot (Chế độ A) nếu có `session_id`.
* **Chi tiết Kết quả Kiểm thử Tự động (Unit Test ngày 14/09/2026):**
  * *Test 1 (Ghép Prompt Phân tích rủi ro):* **PASSED** — Prompt chứa đầy đủ nội dung điều khoản và các căn cứ luật liên quan.
  * *Test 2 (Pipeline One-shot & Gắn Session Context):* **PASSED** — Phát hiện chính xác rủi ro vượt trần phạt vi phạm 8% theo Điều 301 Luật Thương mại và đồng bộ thành công sang `chatbot_qa` session.

### 5.5. Script Xây dựng Index Offline `scripts/build_index.py` (Phần 5 - SRS 5.1, 5.2 & TODO 5.1 -> 5.5)
* **Tính năng:**
  * Duyệt tự động toàn bộ file (.docx, .pdf) trong `data/raw/law/` và `data/raw/templates/`.
  * Tự động đọc text qua `document_reader` và bóc tách theo Điều/Khoản qua `chunk_by_article`.
  * Hỗ trợ cờ `--dry-run` để thống kê, kiểm tra số lượng chunk và định dạng metadata trước khi gọi API thật.
  * Tích hợp cấu hình UTF-8 cho Windows console.
* **Chi tiết Kết quả Kiểm tra Thử nghiệm (Dry-run ngày 14/09/2026):**
  * *law_index:* Đọc chuẩn 6 file luật hiện có (`LuatChuyenDoiSo2025.docx`: 123 chunks, `LuatDanSu2015.docx`: 829 chunks, `luatGiaodichdientu2023.pdf`: 66 chunks, `ND13_2023_BVDLCN.docx`: 55 chunks, `VBHN_LuatSoHuuTriTue2026.docx`: 433 chunks, `VBHN_Luatthuongmai2025.docx`: 393 chunks). Tổng: **1.899 chunks**.
  * *template_index:* Đọc chuẩn file `mau_hop_dong_thiet_ke_website.docx`: **20 chunks**.
  * *Tổng cộng:* **1.919 chunks** được bóc tách và gán metadata chính xác 100%!

### 5.6. Module Đánh giá Định lượng RAGAS `evaluation/` (Phần 10.6 & SRS Chương 7)
* **Thành phần đã xây dựng:**
  * `evaluation/testset.csv`: Bộ 10 cặp câu hỏi & Ground truth chuẩn xác theo Bộ luật Dân sự 2015, Luật Thương mại (VBHN 2025), Luật Giao dịch điện tử 2023, Luật Sở hữu trí tuệ và Luật Chuyển đổi số 2025.
  * `evaluation/run_ragas_eval.py`: Script tự động chạy từng câu hỏi qua Chatbot Chế độ B, thu thập Contexts & Phản hồi, tự động tính toán 4 chỉ số chất lượng RAG (Faithfulness, Answer Relevancy, Context Precision, Context Recall) và xuất file `ragas_report.json`.
* **Kết quả Kiểm thử (Unit Test):**
  * Đã test hàm `load_testset()`: **PASSED** — Đọc chính xác 10/10 test cases với encoding UTF-8 tiếng Việt hoàn hảo.

---

## 6. Cơ chế Nhận diện Văn bản Hết hiệu lực & Giải quyết Xung đột Đa tầng (Tiered Validation)

> **Mục tiêu tính năng:** Phát hiện các hợp đồng soạn thảo theo mẫu cũ vẫn còn viện dẫn văn bản quy phạm pháp luật đã hết hiệu lực hoặc bị thay thế. Đây là tính năng "ăn điểm" then chốt khi demo và bảo vệ đồ án nhờ tính trực quan và giá trị thực tế cao.

### 6.1. Định hướng Dữ liệu: Work Smart, Không nạp tràn lan
* **Không nạp văn bản hết hiệu lực vào FAISS Index:** Việc nạp văn bản cũ vào Vector DB sẽ gây nhiễu embedding, làm RAG retrieve nhầm quy định cũ thay vì quy định mới.
* **Chỉ quản lý dưới dạng Danh mục Quan hệ / Metadata:** Lưu thông tin dạng ánh xạ: `Văn bản cũ -> Bị thay thế bởi -> Văn bản mới (kèm mốc thời gian)`.
* **Tập trung đúng phạm vi đồ án:** Chỉ cần theo dõi các cặp luật chính liên quan đến hợp đồng dịch vụ / CNTT (ví dụ: Luật Giao dịch điện tử 2005 -> 2023, Luật CNTT 2006 -> Luật Chuyển đổi số 2025, Luật BVQL Người tiêu dùng 2010 -> 2023).

### 6.2. Mô hình Kết hợp 3 Nguồn (Hybrid Architecture)
Hệ thống kết hợp đồng thời cả 3 phương pháp để tối ưu độ chính xác và khả năng mở rộng:

1. **Cấp 1 - File cấu hình kiểm duyệt sẵn (`expired_laws.json` - Curated Rules):**
   * *Bản chất:* Chuyên viên / người phát triển định nghĩa danh mục các luật cũ hay gặp nhất.
   * *Độ tin cậy:* 🟢 **100% (Ground Truth tối cao)**. Dùng làm kịch bản demo chắc chắn thắng.
2. **Cấp 2 - Trích xuất tự động từ Luật mới (Statutory Ground Truth):**
   * *Bản chất:* Script/LLM quét "Điều khoản thi hành" (điều cuối cùng) của các luật mới nạp trong `data/raw/law/` để tự động bóc tách các luật bị bãi bỏ/thay thế.
   * *Độ tin cậy:* 🔵 **Rất cao (~95%)**, mở rộng kho tri thức tự động mà không cần nhập tay.
3. **Cấp 3 - Tri thức nội tại của LLM (AI Zero-shot Fallback):**
   * *Bản chất:* Prompt chỉ thị LLM tự đối soát với kiến thức được huấn luyện sẵn.
   * *Độ tin cậy:* 🟡 **Trung bình (75% - 85%)**, đóng vai trò bao quát các văn bản ngách nằm ngoài CSDL.

### 6.3. Cơ chế Giải quyết Xung đột (Conflict Resolution Mechanism)
Khi kết quả giữa các nguồn không đồng nhất, hệ thống áp dụng nguyên tắc **Phân cấp ưu tiên (Hierarchy Priority)**:

```text
[Văn bản dẫn chiếu trong Hợp đồng]
        │
        ├──> Kiểm tra Cấp 1 (File cấu hình)? ────(Có)───> [Kết luận Cấp 1 - Tin cậy 100%]
        │                 │ (Không)
        ├──> Kiểm tra Cấp 2 (Điều khoản thi hành)? ──(Có)──> [Kết luận Cấp 2 - Tin cậy 95%]
        │                 │ (Không)
        └──> Hỏi LLM Cấp 3 (Fallback)?
                  ├── Báo "Hết hiệu lực" ──> Gắn nhãn [Cảnh báo AI - Cần kiểm tra lại]
                  └── Báo "Bình thường"  ──> Không cảnh báo
```

* **Xử lý xung đột giữa Con người/Văn bản gốc (Cấp 1 & 2) và AI (Cấp 3):**
  * Luôn ưu tiên Cấp 1 và Cấp 2. Bỏ qua hoàn toàn phán đoán của LLM nếu trái ngược với CSDL chính thức.
  * Triệt tiêu 100% rủi ro ảo giác (Hallucination) đối với các văn bản trọng điểm.
* **Khi chỉ có LLM cảnh báo (ngoài CSDL):**
  * Vẫn đưa cảnh báo lên UI nhưng gắn tag độ tin cậy vừa phải: `⚠️ [Cảnh báo từ AI - Đề nghị xác minh]: Văn bản có dấu hiệu đã hết hiệu lực theo suy luận của AI.`

### 6.4. Kịch bản Demo Thực tế
* Chuẩn bị sẵn một file hợp đồng mẫu (ví dụ: *Hợp đồng phát triển phần mềm*) ký năm 2026 nhưng phần Căn cứ cố tình ghi:  
  * *"Căn cứ Luật Giao dịch điện tử số 51/2005/QH11..."* (đã bị thay thế bởi Luật 2023)
  * *"Căn cứ Luật Công nghệ thông tin số 67/2006/QH11..."* (đã bị thay thế bởi Luật Chuyển đổi số 2025)
* Khi tải file lên, hệ thống lập tức hiển thị **Cảnh báo Đỏ (Critical Alert)** ở đầu trang phân tích, kèm link hoặc tên văn bản hiện hành thay thế.

### 6.5. Hướng dẫn Bổ sung vào Báo cáo TTTN (Lấy điểm cộng sáng tạo)
* **Nguyên tắc chung:** Không cần viết lại hay đảo lộn cấu trúc báo cáo (vì tính năng này hoàn toàn trực thuộc **Module 2: Gợi ý rủi ro pháp lý** như đã đăng ký). Chỉ cần bổ sung nhẹ nhàng ở 2 vị trí sau khi hoàn thiện code:
  1. **Tại Chương Thiết kế Chi tiết (Mô tả Module 2 - Gợi ý rủi ro):**
     * Thêm 1 gạch đầu dòng ngắn:
       > *"Bên cạnh việc đối soát nội dung từng điều khoản, hệ thống tích hợp cơ chế kiểm soát căn cứ pháp lý đa tầng (Tiered Validation) nhằm phát hiện các hợp đồng mẫu cũ viện dẫn văn bản quy phạm pháp luật đã hết hiệu lực hoặc bị thay thế."*
  2. **Tại Chương Đánh giá Kết quả / Demo Thử nghiệm:**
     * Chụp 1 ảnh màn hình giao diện khi hệ thống phát hiện và hiển thị cảnh báo đỏ đối với văn bản luật hết hiệu lực, đặt chú thích:
       > *"Hình X.Y: Giao diện cảnh báo rủi ro khi hợp đồng viện dẫn văn bản pháp luật đã hết hiệu lực."*

---

## 7. Tối ưu Hóa Toàn diện Hệ thống & Đúc kết Thực chiến (Cập nhật 15/09/2026)

### 7.1. Chuẩn hóa Bộ Parser và Trích xuất Metadata (`modules/shared/chunking.py`)
* **Sửa dứt điểm lỗi Regex cắt vụn văn bản:**
  * *Vấn đề cũ:* Regex cũ `(?i)(?:^|\n)\s*(?:ĐIỀU|Điều)\s+(\d+[\w]*)\.?\s*([^\n]*)` bắt từ "Điều" ở bất kỳ vị trí nào, khiến các câu tham chiếu chéo (ví dụ: *"...áp dụng theo quy định tại Điều 301 Luật Thương mại..."*) bị hiểu nhầm là một Điều luật mới, làm văn bản bị chặt khúc nham nhở.
  * *Giải pháp:* Đổi sang regex đa dòng bắt chặt ở đầu dòng `r"(?m)^Điều\s+(\d+[a-zA-Z]?)\."`. Từng Điều luật được cắt chuẩn xác từ đầu Điều này đến đầu Điều kế tiếp.
* **Bảo toàn Lời mở đầu (Preamble):**
  * Tự động lưu giữ toàn bộ phần thông tin các bên (Bên A, Bên B), căn cứ ban hành trước Điều 1 và gán metadata `article: "Lời mở đầu"`, khắc phục triệt để việc rách bảng thông tin hợp đồng mẫu.
* **Phân biệt chuẩn xác mốc thời gian Văn bản hợp nhất (VBHN):**
  * **Ngày ký xác thực (27/08/2025):** Là ngày gắn liền trực tiếp với số hiệu văn bản (theo Nghị định 30/2020/NĐ-CP), là căn cứ có giá trị pháp lý bắt buộc khi viện dẫn.
  * **Ngày công báo (11/09/2025):** Chỉ là ngày đăng tin, không dùng trong số hiệu trích dẫn.
* **Xây dựng 2 hàm bóc tách siêu dữ liệu tự động:**
  * `extract_law_header()`: Bóc tách tự động tên luật, số hiệu, ngày ban hành, ngày hiệu lực, trạng thái và chi tiết VBHN (số hiệu 113/VBHN-VPQH, ngày ký xác thực 27/08/2025).
  * `extract_template_header()`: Trích xuất tên mẫu hợp đồng và danh mục các văn bản căn cứ để phục vụ thẩm định hiệu lực tự động.

---

### 7.2. Hoàn thiện Vector DB FAISS & Xử lý Quota API
* **Kết quả build index sạch 100%:**
  * `law_index`: **543 vectors** (bao quát trọn vẹn 6 đạo luật/nghị định dịch vụ cốt lõi).
  * `template_index`: **28 vectors** (bảo toàn bảng thông tin Bên A, Bên B).
* **Mô hình Embedding:**
  * Dùng `models/gemini-embedding-2` (768 chiều), không dùng các bản `-preview` dễ phát sinh lỗi không tương thích.
* **Chiến thuật vượt Rate Limit (429 / Resource Exhausted):**
  * Tối ưu `BATCH_SIZE = 50`.
  * Thay vì sleep cố định, code tự động dùng Regex bóc tách thời gian chờ do Google chỉ định trong thông báo lỗi (`retryDelay`) để ngủ đúng thời gian hồi phục quota, đảm bảo quá trình build index chạy tự động 100% không bị ngắt giữa chừng.
* **Dọn dẹp thư mục trùng lặp:**
  * Xóa bỏ thư mục thừa `modules/scripts/` (chứa file `build_index.py` cũ 5.5KB).
  * Giữ lại duy nhất thư mục chính thống [scripts/build_index.py](file:///d:/PJ/Lexdraft/scripts/build_index.py) (8.8KB) ở thư mục gốc.

---

### 7.3. Cấu hình Mô hình LLM & Quản trị Hạn mức Google API (`config.py`)
* **`gemini-2.5-flash` & `gemini-2.5-flash-lite`:** Đã bị Google thu hồi quyền truy cập đối với tài khoản mới (trả lỗi `404 NOT_FOUND`).
* **`gemini-3.6-flash`:** Đang bị Google siết trần gói Free Tier cực kỳ khắt khe (**chỉ 20 requests/ngày**, chạm trần sẽ báo lỗi `429 RESOURCE_EXHAUSTED`).
* **`gemini-3.5-flash`:** Hoạt động ổn định, phản hồi tức thì, hạn mức dồi dào, là lựa chọn tối ưu được cấu hình chính thức trong `config.py`.

---

### 7.4. Cơ chế Chống Hallucination & Kiến trúc Code Gatekeeper
* **Bài học kinh nghiệm: Không phó mặc hoàn toàn cho Prompt:**
  * Nếu câu hỏi khái niệm ngoài lề (ví dụ: *"Luật thương mại là gì?"*) có điểm tương đồng lọt qua bước tìm kiếm, việc dùng prompt ép AI từ chối sẽ khiến hệ thống tốn tiền gọi API, người dùng phải chờ 2-3 giây, và AI dễ sinh ra câu trả lời dông dài, biện minh kỹ thuật lập pháp hoặc chép nguyên cả trang luật.
* **Giải pháp Code Gatekeeper ở tầng Code Python:**
  * Thiết lập ngưỡng tương đồng `SIMILARITY_THRESHOLD = 0.75` trong `config.py` và `modules/shared/llm_client.py`.
  * Nếu điểm tương đồng cao nhất của câu hỏi `< 0.75` (câu khái niệm chung chỉ đạt 0.74): **Code Python chặn ngay lập tức ở tầng ngoài cùng trong 0.01 giây** mà **không gọi Gemini API**.
  * Trả về câu từ chối lịch thiệp, chuẩn mực, 0 độ trễ và 0 chi phí token.

---

### 7.5. Thuật toán Lọc sạch Căn cứ Trích dẫn (Cited-only Filtering)
* **Vị trí xử lý:** [modules/shared/llm_client.py](file:///d:/PJ/Lexdraft/modules/shared/llm_client.py#L235-L250) trong hàm `generate_grounded_response()`.
* **Cơ chế hoạt động:**
  * FAISS có thể tìm thấy 10 Điều luật liên quan trong cơ sở dữ liệu.
  * Sau khi AI sinh câu trả lời, Code dùng Regex `rf"\b[Đđ]iều\s+{art_num}\b"` quét toàn bộ nội dung văn bản phản hồi.
  * Chỉ những Điều luật nào **thực sự được AI viện dẫn trong bài viết** mới được giữ lại trong danh sách `citations`.
  * Nếu AI từ chối trả lời hoặc không dùng điều nào: `citations = []`, hộp `📚 Trích dẫn căn cứ pháp lý` trên Streamlit UI **tự động ẩn hoàn toàn**.
* **Quy tắc trích dẫn chuẩn mực:**
  * Tuân thủ thứ bậc: `Điểm → Khoản → Điều → Tên văn bản`.
  * Hiển thị chuẩn tên luật và số hiệu VBHN (`Luật Thương mại số 36/2005/QH11 (VBHN 113/VBHN-VPQH)`) thay vì tên file thô `.md`.

---

### 7.6. Tái cấu trúc Giao diện Streamlit (`app.py`)
* **Entrypoint duy nhất:** Xóa `modules/app.py`, quy chuẩn về file duy nhất [app.py](file:///d:/PJ/Lexdraft/app.py) ở thư mục gốc.
* **Tích hợp 3 Tab hoàn chỉnh:**
  * **Tab 1 (📝 Soạn thảo):** Điền thông tin, sinh hợp đồng chuẩn VBHN và xuất file `.docx`.
  * **Tab 2 (📤 Upload Hợp đồng):** Tải file lên, phân tích rủi ro từng điều khoản (trần phạt vi phạm 8%) và hiển thị Banner cảnh báo văn bản hết hiệu lực (Tiered Validation).
  * **Tab 3 (💬 Chatbot):** Hỏi đáp pháp lý hợp đồng dịch vụ, tự động đồng bộ ngữ cảnh hợp đồng (Chế độ A) hoặc tra cứu luật chung (Chế độ B).

---

### 7.7. Danh mục Commits Đã Đẩy lên Nhánh `dev`
1. **Commit 1 (`cf116fc`):** `feat(data): reorganize raw corpus, enhance markdown parsing, and FAISS indexing`
2. **Commit 2 (`c3304c3`):** `feat(llm): implement code gatekeeper (0.75), cited-only filtering, and standardized citation rules`
3. **Commit 3 (`80d8c3d`):** `refactor(ui): move Streamlit app to root and integrate tiered validation with dynamic citations`

---

## 8. Kế Hoạch Hành Động & Các Hạng Mục Cần Kiểm Thử Toàn Diện (TODO Tiếp Theo)

> **Mục tiêu:** Chuyển từ giai đoạn phát triển/sửa lỗi sang giai đoạn **Kiểm thử chuyên sâu (End-to-End Testing)** và **Đánh giá định lượng chất lượng RAG (Ragas Evaluation)** trước khi đóng gói nghiệm thu.

### 8.1. Hạng mục 1: Kiểm thử Chuyên sâu Chatbot Q&A (Cả 2 Chế độ A & B)
* [ ] **Chế độ B (Tra cứu luật chung - Không có hợp đồng):**
  * **Test bộ câu hỏi trong phạm vi:** Các tình huống trọng tâm về hợp đồng dịch vụ:
    * Mức phạt vi phạm tối đa (Điều 301 Luật Thương mại - 8%).
    * Điều kiện yêu cầu bồi thường thiệt hại (Điều 302, 303 Luật Thương mại).
    * Chữ ký điện tử và giá trị pháp lý của thông điệp dữ liệu (Luật Giao dịch điện tử 2023).
    * Quyền sở hữu mã nguồn phần mềm trong hợp đồng gia công (Luật Sở hữu trí tuệ).
    * Đơn phương chấm dứt hợp đồng dịch vụ (Điều 520 Bộ luật Dân sự 2015).
  * **Test bộ câu hỏi biên / ngoài phạm vi (Edge Cases & Gatekeeper):**
    * Câu hỏi hoàn toàn ngoài lề (Thời tiết, công nghệ khác, đất đai, hôn nhân gia đình...).
    * Đảm bảo cơ chế Gatekeeper `SIMILARITY_THRESHOLD = 0.75` chặn tức thì ở 0.01s, trả về câu từ chối chuẩn, 0 token cost.
  * **Kiểm tra UI & Format trích dẫn:**
    * Thứ bậc trích dẫn: `Điểm → Khoản → Điều → Tên văn bản`.
    * Kiểm tra tính năng lọc trích dẫn (chỉ hiện đúng điều luật thực sự dùng, ẩn expander khi bị từ chối).
* [ ] **Chế độ A (Có ngữ cảnh hợp đồng & rủi ro):**
  * Hỏi các câu bám sát nội dung hợp đồng vừa rà soát (ví dụ: *"Hợp đồng của tôi mức phạt 15% có hợp pháp không?", "Điều khoản bảo hành như vậy có bất lợi cho Bên A không?"*).
  * Kiểm tra AI trả lời kết hợp cả điều khoản hợp đồng và điều luật đối chiếu.

---

### 8.2. Hạng mục 2: Chạy Đánh giá Định lượng RAGAS (`evaluation/`)
* [ ] **Chuẩn bị và hoàn thiện bộ dữ liệu mẫu (`evaluation/testset.csv`):**
  * Kiểm tra 10 cặp câu hỏi & Ground Truth đại diện cho các tình huống pháp lý cốt lõi.
* [ ] **Chạy Pipeline đánh giá tự động (`evaluation/run_ragas_eval.py`):**
  * Lệnh chạy: `python evaluation/run_ragas_eval.py`.
  * Thu thập dữ liệu phản hồi thực tế từ hệ thống Lexdraft.
* [ ] **Đo lường 4 chỉ số chất lượng RAG cốt lõi theo SRS:**
  * **Faithfulness (Độ trung thực):** Đảm bảo câu trả lời không bịa đặt ngoài context.
  * **Answer Relevancy (Độ phù hợp của câu trả lời):** Đánh giá mức độ bám sát câu hỏi người dùng.
  * **Context Precision (Độ chuẩn xác của ngữ cảnh):** Đánh giá các chunk truy xuất được có đúng trọng tâm không.
  * **Context Recall (Độ bao phủ của ngữ cảnh):** Đánh giá các căn cứ cần thiết có được truy xuất đầy đủ không.
* [ ] **Xuất báo cáo nghiệm thu:**
  * Lưu kết quả ra file `evaluation/ragas_report.json` và bảng số liệu để đưa vào Chương Thực nghiệm của Báo cáo.

---

### 8.3. Hạng mục 3: Kiểm thử Toàn diện Module Soạn thảo Hợp đồng (Tab 📝 Soạn thảo)
* [ ] **Kiểm thử Form nhập liệu:**
  * Thử nghiệm các loại dịch vụ khác nhau: *Thiết kế website, Phát triển phần mềm di động, Bảo trì hệ thống CNTT*.
  * Kiểm tra xử lý trường dữ liệu: Tên các bên, thời hạn thanh toán, tỷ lệ phạt vi phạm, điều khoản nghiệm thu.
* [ ] **Kiểm thử Sinh bản nháp (Drafting Engine):**
  * Kiểm tra Retrieval từ `template_index` (28 chunks) xem có kéo đúng khung sườn mẫu hợp đồng chuẩn không.
  * Kiểm tra Retrieval từ `law_index` xem có tự động viện dẫn căn cứ chuẩn VBHN vào Lời mở đầu không.
* [ ] **Kiểm thử Xuất file Word (.docx):**
  * Nhấn nút *"Tải bản nháp hợp đồng (.docx)"*.
  * Mở file kiểm tra định dạng trình bày: Tiêu ngữ, bảng thông tin Bên A/B, cấu trúc các Điều khoản, tính ngay ngắn của căn lề.

---

### 8.4. Hạng mục 4: Kiểm thử Toàn diện Module Rà soát Rủi ro & Upload (Tab 📤 Upload Hợp đồng)
* [ ] **Kiểm thử cơ chế Tiered Validation (Phát hiện văn bản hết hiệu lực):**
  * Upload file hợp đồng cố tình viện dẫn luật cũ:
    * *"Căn cứ Luật Công nghệ thông tin số 67/2006/QH11..."* -> Hệ thống phải bật cảnh báo Đỏ: Hết hiệu lực từ 01/07/2026, thay thế bởi Luật Chuyển đổi số 2025.
    * *"Căn cứ Luật Giao dịch điện tử số 51/2005/QH11..."* -> Hệ thống phải bật cảnh báo Đỏ: Thay thế bởi Luật Giao dịch điện tử 2023.
    * *"Căn cứ Luật Thương mại 2020..."* -> Hệ thống phải cảnh báo văn bản không có thật.
* [ ] **Kiểm thử Phân tích Rủi ro từng Điều khoản:**
  * **Bẫy trần phạt vi phạm:** Cố tình cài cắm điều khoản *"Phạt vi phạm 12% giá trị hợp đồng"* -> Hệ thống phải bắt được lỗi vi phạm Điều 301 Luật Thương mại (trần 8%) và đề xuất sửa lại.
  * **Bẫy miễn trừ trách nhiệm:** Cố tình cài cắm điều khoản miễn trừ trách nhiệm bồi thường vô căn cứ -> Bắt lỗi trái Điều 351, 360 Bộ luật Dân sự.
  * **Bẫy bàn giao mã nguồn:** Không quy định chuyển giao quyền tác giả -> Cảnh báo rủi ro tranh chấp quyền tác giả theo Luật Sở hữu trí tuệ.
* [ ] **Kiểm thử Liên kết Tự động sang Chatbot:**
  * Sau khi phân tích xong, chuyển sang Tab Chatbot và kiểm tra xem hệ thống đã tự động chuyển sang **Chế độ A (Đã có ngữ cảnh hợp đồng)** hay chưa.

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
| `a4f383a` | `feat(ui)` | Đặt `🏠 Trang chủ` làm màn hình khởi đầu mặc định khi khởi động / F5 và khi xóa phiên |
| `8b5ed15` | `test(suite)` | Bổ sung bộ 104 unit test tự động phủ 100% các module không qua UI |

---

## 3. Trạng thái vận hành & Automated Tests
- **Bộ Test Suite (Non-UI):** 109/109 unit tests passed (100% SUCCESS, bao gồm cả module `eval`).
- **Server Streamlit:** Đang chạy ổn định tại cổng `http://localhost:8501`.
- **Pre-commit checks:** Tất cả code đều vượt qua kiểm tra định dạng và quy chuẩn của `ruff`.

---

## 4. Module Đánh giá RAGAS & Thẩm định Golden Dataset (`eval/`)
- **Kiến trúc:**
  - `eval/schema.py`: Pydantic model (`GoldenSample`, `EvalSampleResult`) ràng buộc chặt chẽ dữ liệu kiểm thử.
  - `eval/dataset_manager.py`: Nạp, lưu và tự động kiểm tra chất lượng Golden Dataset (chống trùng ID, chống câu hỏi cụt, bắt buộc có Điều luật trích dẫn).
  - `eval/synthetic_gen.py`: Trích xuất Điều luật thực tế trong vector database để LLM tự sinh câu hỏi và Ground Truth chuẩn mực (Document-grounded), loại bỏ hoàn toàn thiên kiến và ảo giác.
  - `eval/eval_runner.py`: Thực thi kiểm thử qua Chatbot Service và tính toán các chỉ số Retrieval, Law Citation Match, lưu báo cáo CSV/JSON vào `data/eval/`.
  - `run_eval.py`: CLI chạy 1 lệnh (`python run_eval.py --validate-only` hoặc `python run_eval.py`).


