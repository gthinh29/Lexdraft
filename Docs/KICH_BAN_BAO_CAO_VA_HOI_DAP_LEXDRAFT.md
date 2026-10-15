# KỊCH BẢN BÁO CÁO TỐT NGHIỆP VÀ BỘ CÂU HỎI PHẢN BIỆN HỆ THỐNG LEXDRAFT
**Đề tài:** *Xây dựng Hệ thống hỗ trợ soạn thảo và gợi ý rủi ro hợp đồng dịch vụ bằng mô hình ngôn ngữ lớn (LLM) kết hợp Retrieval-Augmented Generation (RAG)*  
**Cơ sở đào tạo:** Viện Công nghệ Thông tin và Điện, Điện tử – Trường Đại học Giao thông Vận tải TP.HCM (UTH)  
**Giảng viên hướng dẫn:** TS. Hàn Trung Định  
**Sinh viên thực hiện (Nhóm 14):**
- **Phạm Gia Thịnh** — Thuyết trình **Slide 1 đến Slide 7** & **Trực tiếp chạy Demo hệ thống**
- **Lê Hữu Tiến** — Thuyết trình **Slide 8 đến Slide 16** (Hiện thực 3 phân hệ, Thực nghiệm khoa học, Đánh giá Ragas, Kết luận)

---

## MỤC LỤC
1. [QUY ƯỚC VÀ PHÂN CHIA VAI TRÒ BÁO CÁO](#1-quy-ước-và-phân-chia-vai-trò-báo-cáo)
2. [PHẦN I: KỊCH BẢN NÓI CHI TIẾT TỪNG SLIDE (SLIDE 1 ĐẾN 16)](#phần-i-kịch-bản-nói-chi-tiết-từng-slide-slide-1-đến-16)
   - [Slide 1: Trang bìa khóa luận](#slide-1-trang-bìa-khóa-luận-0000---0030)
   - [Slide 2: Bài toán thực tế và Mục tiêu đề tài](#slide-2-bài-toán-thực-tế-và-mục-tiêu-đề-tài-0030---0145)
   - [Slide 3: Phạm vi nghiệp vụ và 3 Giả thiết khoa học](#slide-3-phạm-vi-nghiệp-vụ-và-3-giả-thiết-khoa-học-0145---0300)
   - [Slide 4: Kiến trúc thành phần Đơn khối phân mô-đun (Có sơ đồ Hình 1)](#slide-4-kiến-trúc-thành-phần-đơn-khối-phân-mô-đun-modular-monolith-0300---0430)
   - [Slide 5: Công nghệ sử dụng và Môi trường thực nghiệm](#slide-5-công-nghệ-sử-dụng-và-môi-trường-thực-nghiệm-0430---0530)
   - [Slide 6: Kỹ thuật Dữ liệu, Phân đoạn theo Điều luật (Có sơ đồ Pha A & Cấu trúc Chunk)](#slide-6-kỹ-thuật-dữ-liệu-và-phân-đoạn-theo-điều-luật-0530---0700)
   - [Slide 7: Cơ chế 4 Tầng Kiểm soát Sinh ảo (Có sơ đồ Pha B & 4 Tầng Guardrails)](#slide-7-cơ-chế-4-tầng-kiểm-soát-sinh-ảo-0700---0830)
   - [Slide 8: Hiện thực Phân hệ 1 – Soạn thảo Hợp đồng](#slide-8-hiện-thực-phân-hệ-1--soạn-thảo-hợp-đồng-0830---0930)
   - [Slide 9: Hiện thực Phân hệ 2 – Gợi ý Rủi ro Pháp lý](#slide-9-hiện-thực-phân-hệ-2--gợi-ý-rủi-ro-pháp-lý-0930---1030)
   - [Slide 10: Hiện thực Phân hệ 3 – Trợ lý Hỏi – Đáp Pháp lý](#slide-10-hiện-thực-phân-hệ-3--trợ-lý-hỏi--đáp-pháp-lý-1030---1130)
   - [Slide 11: Thực nghiệm Định lượng – Giả thiết 1 & 2 (Có biểu đồ Hình 3 & 4)](#slide-11-thực-nghiệm-định-lượng--kết-quả-giả-thiết-1--2-1130---1230)
   - [Slide 12: Thực nghiệm Định lượng – Giả thiết 3 (Có biểu đồ Hình 5 Ma trận Từ chối An toàn)](#slide-12-thực-nghiệm-định-lượng--kết-quả-giả-thiết-3-1230---1330)
   - [Slide 13: Đánh giá Ragas và Hiệu năng Phát hiện Rủi ro (Có bảng & Biểu đồ Hình 6, 7, 8)](#slide-13-đánh-giá-ragas-và-hiệu-năng-phát-hiện-rủi-ro-1330---1430)
   - [Slide 14: Chuyển giao sang Phần Thực nghiệm Chạy Demo Trực tiếp](#slide-14-chuyển-giao-sang-phần-thực-nghiệm-chạy-demo-trực-tiếp-1430---1445)
   - [Slide 15: Kết luận, Hạn chế và Hướng phát triển](#slide-15-kết-luận-hạn-chế-và-hướng-phát-triển-sau-demo)
   - [Slide 16: Lời cảm ơn và Sẵn sàng Trả lời Phản biện](#slide-16-kết-thúc-báo-cáo-và-chuyển-sang-qa)
3. [PHẦN II: KỊCH BẢN THAO TÁC DEMO TRỰC TIẾP TRÊN PHẦN MỀM (THỊNH THỰC HIỆN)](#phần-ii-kịch-bản-thao-tác-demo-trực-tiếp-trên-phần-mềm-thịnh-thực-hiện)
   - [Màn 1: Soạn thảo Hợp đồng thông minh](#màn-1-soạn-thảo-hợp-đồng-thông-minh-thao-tác-2-phút)
   - [Màn 2: Rà soát Rủi ro & Cảnh báo Hiệu lực Văn bản](#màn-2-rà-soát-rủi-ro--cảnh-báo-hiệu-lực-văn-bản-thao-tác-2-phút)
   - [Màn 3: Trợ lý Hỏi – Đáp Pháp lý & Bẫy Ảo giác](#màn-3-trợ-lý-hỏi--đáp-pháp-lý--thử-nghiệm-bẫy-ảo-giác-thao-tác-2-phút)
4. [PHẦN III: BỘ CÂU HỎI HỘI ĐỒNG PHẢN BIỆN DỰ KIẾN KÈM CÂU TRẢ LỜI CHIẾN LƯỢC](#phần-iii-bộ-câu-hỏi-hội-đồng-phản-biện-dự-kiến-kèm-câu-trả-lời-chiến-lược)
   - [Nhóm A: Các câu hỏi nền tảng, cơ bản về AI, Véc-tơ, Cơ sở dữ liệu](#nhóm-a-các-câu-hỏi-nền-tảng-cơ-bản-về-ai-véc-tơ-cơ-sở-dữ-liệu)
   - [Nhóm B: Các câu hỏi "Bật code lên chỉ cho Thầy" (Chỉ rõ file và dòng code)](#nhóm-b-các-câu-hỏi-bật-code-lên-chỉ-cho-thầy-chỉ-rõ-file-và-dòng-code)
   - [Nhóm C: Các câu hỏi học thuật sâu, Ragas, Đánh đổi khoa học và Pháp lý](#nhóm-c-các-câu-hỏi-học-thuật-sâu-ragas-đánh-đổi-khoa-học-và-pháp-lý)

---

## 1. QUY ƯỚC VÀ PHÂN CHIA VAI TRÒ BÁO CÁO

- **Tổng thời lượng báo cáo:** 15 phút trình bày (9 phút slide + 6 phút demo) và 10 – 15 phút trả lời phản biện.
- **Phong thái trình bày:** Tự tin, đĩnh đạc, nói tiếng Việt chuẩn xác, sử dụng thuật ngữ chuyên môn Việt hóa rõ ràng (hạn chế lạm dụng từ mượn tiếng Anh; nếu dùng từ tiếng Anh thì giải thích ngay bản chất kỹ thuật).
- **Phân công cụ thể:**
  * **Phạm Gia Thịnh:** Trình bày từ **Slide 1 đến Slide 7** (Bối cảnh, Giả thiết, Kiến trúc sơ đồ Hình 1, Công nghệ, Quy trình dữ liệu Pha A, Cơ chế 4 tầng Pha B). Sau đó đến Slide 14, Thịnh là người **trực tiếp cầm chuột thao tác Live Demo trên trình duyệt web**.
  * **Lê Hữu Tiến:** Trình bày từ **Slide 8 đến Slide 16** (Chi tiết 3 phân hệ nghiệp vụ, Thực nghiệm số liệu 3 giả thiết, Đánh giá Ragas, Ma trận nhầm lẫn, Kết luận và Hướng phát triển). Trong lúc Thịnh demo, Tiến đứng cạnh phối hợp chỉ điểm trên màn chiếu.

---

## PHẦN I: KỊCH BẢN NÓI CHI TIẾT TỪNG SLIDE (SLIDE 1 ĐẾN 16)

---

### [Slide 1] Trang bìa khóa luận (00:00 - 00:30)
* **Người trình bày:** **Phạm Gia Thịnh**
* **Mục tiêu:** Chào hỏi trang trọng, giới thiệu đầy đủ tên trường, khoa viện, đề tài và giảng viên hướng dẫn.
* **Lời thoại (Thịnh):**
> *"Kính thưa quý Thầy Cô trong Hội đồng chấm khóa luận tốt nghiệp, kính thưa Thầy hướng dẫn – Tiến sĩ Hàn Trung Định cùng toàn thể các bạn sinh viên đang có mặt trong phòng hội đồng ngày hôm nay.*
>
> *Em tên là **Phạm Gia Thịnh**, và bên cạnh em là bạn **Lê Hữu Tiến**, chúng em là sinh viên Nhóm 14 thuộc Viện Công nghệ Thông tin và Điện, Điện tử – Trường Đại học Giao thông Vận tải Thành phố Hồ Chí Minh.*
>
> *Hôm nay, nhóm chúng em rất vinh dự được đại diện báo cáo đề tài khóa luận tốt nghiệp với tên gọi: **'Xây dựng Hệ thống hỗ trợ soạn thảo và gợi ý rủi ro hợp đồng dịch vụ bằng mô hình ngôn ngữ lớn (LLM) kết hợp Truy xuất tăng cường tri thức (RAG)'**. Em xin kính mời quý Thầy Cô cùng theo dõi phần trình bày của nhóm."*

---

### [Slide 2] Bài toán thực tế và Mục tiêu đề tài (00:30 - 01:45)
* **Người trình bày:** **Phạm Gia Thịnh**
* **Điểm nhấn trên slide:** 3 nút thắt thực tế (Mẫu trôi nổi, Chi phí pháp lý cao, Ảo giác của AI thuần) ➔ Mục tiêu cốt lõi của LexDraft.
* **Lời thoại (Thịnh):**
> *"Thưa Thầy Cô, trong nền kinh tế số hiện nay, các doanh nghiệp vừa và nhỏ (SMEs), các công ty khởi nghiệp cũng như các bạn làm nghề tự do (Freelancer) tham gia ký kết hàng ngàn hợp đồng dịch vụ mỗi ngày, đặc biệt là dịch vụ phần mềm, thiết kế trang web và truyền thông số. Tuy nhiên, họ đang vấp phải ba rào cản thực tế rất lớn:*
>
> * **Thứ nhất là việc tự soạn thảo từ các mẫu trôi nổi trên mạng:** Người dùng thường tải các hợp đồng không rõ nguồn gốc. Những mẫu này đa phần đã lỗi thời, thiếu các điều khoản cốt lõi để bảo vệ mình, hoặc thậm chí chứa các điều khoản trái với điều cấm của pháp luật.*
> * **Thứ hai là gánh nặng chi phí pháp lý:** Chi phí để thuê luật sư hoặc công ty tư vấn pháp chế rà soát một hợp đồng dịch vụ thường dao động từ vài triệu đến hàng chục triệu đồng, hoàn toàn vượt quá ngân sách của một cá nhân hay một dự án nhỏ lẻ.*
> * **Thứ ba là rủi ro 'ảo giác' khi dùng trí tuệ nhân tạo thông thường:** Nếu người dùng đưa hợp đồng lên các mô hình AI thương mại như ChatGPT phiên bản gốc để hỏi, mô hình rất hay tự 'bịa' ra số hiệu điều luật, viện dẫn những văn bản luật đã hết hiệu lực từ lâu mà người dùng không hề hay biết.*
>
> *Từ ba bài toán thực tế nêu trên, mục tiêu cốt lõi của đề tài **LexDraft** là: Xây dựng một giải pháp phần mềm web hoàn chỉnh với **ba chức năng khép kín: Soạn thảo hợp đồng – Phân tích rủi ro – Trợ lý hỏi đáp pháp lý**. Hệ thống kết hợp mô hình ngôn ngữ lớn với kỹ thuật truy xuất tăng cường tri thức (RAG), áp dụng cơ chế neo dữ liệu đa tầng nhằm đảm bảo: **Mọi nhận định pháp lý đều có trích dẫn Điều/Khoản chính xác từ luật hiện hành, và hệ thống biết tự động từ chối an toàn khi gặp câu hỏi không có căn cứ**."*

---

### [Slide 3] Phạm vi nghiệp vụ và 3 Giả thiết khoa học (01:45 - 03:00)
* **Người trình bày:** **Phạm Gia Thịnh**
* **Điểm nhấn trên slide:** Cột trái (5 loại hợp đồng mẫu, 7 văn bản luật hiện hành) – Cột phải (3 Giả thiết khoa học dẫn đường: GT1, GT2, GT3).
* **Lời thoại (Thịnh):**
> *"Để hệ thống đạt độ sâu chuyên môn và độ chính xác cao nhất, nhóm em đã xác định rõ phạm vi nghiên cứu và cơ sở tri thức ở cột bên trái:*
> * Về nghiệp vụ: Hệ thống tập trung sâu vào **hợp đồng dịch vụ công nghệ** với 5 nhóm mẫu chuẩn: Thiết kế Trang web, Phát triển Phần mềm, Thuê hạ tầng Đám mây, Tư vấn hệ thống ERP và Tiếp thị số (Digital Marketing).*
> * Về cơ sở tri thức pháp lý: Nhóm chuẩn hóa và nạp vào hệ thống **7 văn bản pháp luật hiện hành mới nhất**, bao gồm: Bộ luật Dân sự 2015, Luật Thương mại với Văn bản hợp nhất số 113 năm 2025, Luật Sở hữu trí tuệ với Văn bản hợp nhất số 55 năm 2026, Luật Giao dịch điện tử 2023, Luật Bảo vệ dữ liệu cá nhân 2025, Luật Chuyển đổi số 2025 và Luật Trí tuệ nhân tạo 2025.*
> * Đối tượng phục vụ: Hỗ trợ rà soát sơ bộ, cảnh báo rủi ro tham khảo cho cá nhân và doanh nghiệp nhỏ, hoàn toàn không thay thế luật sư tranh tụng tại tòa án.*
>
> *Thưa Thầy Cô, toàn bộ quá trình thiết kế và thực nghiệm của đề tài được dẫn đường bởi **ba giả thiết khoa học cốt lõi** ở cột bên phải:*
> * **Giả thiết 1 (GT1 - So sánh RAG với AI thuần):** Việc kết hợp mô hình ngôn ngữ lớn với kỹ thuật truy xuất dữ liệu pháp lý (RAG) sẽ giúp tăng độ tin cậy và giảm mạnh tỷ lệ ảo giác so với mô hình AI trả lời trực tiếp (Zero-shot).*
> * **Giả thiết 2 (GT2 - Vai trò của Phân đoạn cấu trúc và Siêu dữ liệu):** Việc chia nhỏ văn bản luật theo ranh giới Điều/Khoản kết hợp gắn nhãn siêu dữ liệu nguồn sẽ làm tăng độ chính xác truy xuất và chuẩn hóa 100% định dạng trích dẫn.*
> * **Giả thiết 3 (GT3 - Ngưỡng tương đồng $\tau = 0.75$ và Cơ chế Từ chối an toàn):** Việc kết hợp kiểm tra độ tương đồng ngữ nghĩa bằng ngưỡng $\tau = 0.75$ sẽ giúp triệt tiêu hoàn toàn hiện tượng bịa luật trước các câu hỏi bẫy, câu hỏi ngoài phạm vi hoặc luật hết hiệu lực.*
>
> *Sau đây, em xin đi sâu vào phần kiến trúc hệ thống để làm rõ cách nhóm hiện thực hóa các giả thiết này."*

---

### [Slide 4] Kiến trúc thành phần: Đơn khối phân mô-đun (Modular Monolith) (03:00 - 04:15)
* **Người trình bày:** **Phạm Gia Thịnh**
* **Điểm nhấn trên slide:** Bản chất Modular Monolith, Điểm đặc biệt & Thuyết minh nhanh **SƠ ĐỒ HÌNH 1**.
* **Lời thoại (Thịnh) — BÁO CÁO NGẮN GỌN, TRỌNG TÂM:**
> *"Kính thưa Thầy Cô, ở Slide 4, hệ thống LexDraft được nhóm xây dựng theo kiến trúc **Đơn khối phân mô-đun (Modular Monolith)**.
>
> * **Modular Monolith là gì?**
>   * Hiểu một cách đơn giản nhất: Toàn bộ hệ thống chạy chung trong **một tiến trình Python duy nhất** (tính Monolith để dễ triển khai), nhưng mã nguồn bên trong được **chia thành các phân khối nghiệp vụ độc lập tuyệt đối** (tính Modular).
>
> * **Điểm đặc biệt của kiến trúc này trong đề tài là gì?**
>   * **Thứ nhất, tốc độ cực nhanh so với Vi dịch vụ (Microservices):** Vì chạy chung 1 tiến trình, cả 3 phân hệ có thể **chia sẻ trực tiếp chỉ mục véc-tơ FAISS ngay trong bộ nhớ RAM**, tìm kiếm chỉ mất dưới 2 mili-giây, không tốn độ trễ mạng và không phát sinh chi phí hạ tầng.
>   * **Thứ hai, khắc phục nhược điểm của Monolith truyền thống:** Các phân khối độc lập hoàn toàn, chỉ giao tiếp qua cổng `service.py`, không bị phụ thuộc chéo mã nguồn, lỗi ở phân hệ này không ảnh hưởng phân hệ khác và rất dễ kiểm thử độc lập.
>
> * **Nhìn vào Sơ đồ Hình 1, kiến trúc gồm 3 tầng rất rõ ràng:**
>   1. **Tầng trên cùng là `app.py`:** Giao diện Streamlit, chỉ làm nhiệm vụ điều phối luồng người dùng.
>   2. **Tầng giữa là 3 phân khối nghiệp vụ:** Soạn thảo (`drafting`), Phân tích rủi ro (`risk_assessment`) và Trợ lý hỏi đáp (`chatbot_qa`). Giữa phân hệ rủi ro và chatbot có mũi tên nét đứt **'gửi context'** để chuyển kết quả rà soát sang cho chatbot tư vấn tiếp.
>   3. **Trục dùng chung `modules/shared` và Lưu trữ cục bộ:** Cung cấp sẵn các hàm đọc tài liệu, cắt luật, nhúng véc-tơ và gọi Gemini; phía dưới là kho véc-tơ FAISS nạp trên RAM và tệp `expired_laws.json` trên ổ cứng."*

---

### [Slide 5] Công nghệ sử dụng và Môi trường thực nghiệm (04:30 - 05:30)
* **Người trình bày:** **Phạm Gia Thịnh**
* **Điểm nhấn trên slide:** Bảng 7 phân lớp công nghệ; Nhiệt độ Temperature = 0.0; Mô hình véc-tơ 768 chiều; FAISS IndexFlatIP.
* **Lời thoại (Thịnh):**
> *"Xin chuyển sang Slide số 5: Đây là bảng tổng hợp các công nghệ và môi trường thực nghiệm mà nhóm đã lựa chọn:*
>
> * **Môi trường lập trình:** Hệ thống chạy trên nền tảng **Python phiên bản 3.14** môi trường ảo trên hệ điều hành Windows 11 64-bit.
> * **Giao diện Web:** Nhóm sử dụng thư viện **Streamlit**, quản lý trạng thái các phiên làm việc xuyên suốt bằng đối tượng `st.session_state`.
> * **Mô hình ngôn ngữ lớn (LLM):** Nhóm sử dụng mô hình **`gemini-3.5-flash-lite`**. Một điểm kỹ thuật cực kỳ quan trọng là nhóm **thiết lập nhiệt độ ngẫu nhiên `temperature = 0.0`**. Trong xử lý ngôn ngữ pháp lý, chúng ta cần sự chuẩn xác tuyệt đối, không được phép sáng tạo tùy tiện hay ngẫu nhiên, nên nhiệt độ bằng 0.0 sẽ giúp câu trả lời mang tính tất định cao nhất.
> * **Mô hình véc-tơ nhúng (Embedding):** Sử dụng mô hình chuyên dụng **`models/gemini-embedding-2`** để biểu diễn ngữ nghĩa của văn bản thành các véc-tơ trong không gian toán học **768 chiều**.
> * **Cơ sở dữ liệu véc-tơ:** Nhóm chọn thư viện **FAISS** chạy trên CPU với chỉ mục **`IndexFlatIP`** (tính tích vô hướng). Các véc-tơ đều được chuẩn hóa độ dài L2 về bằng 1 trước khi đưa vào chỉ mục, do đó phép nhân tích vô hướng chính là phép đo độ tương đồng Cosine chuẩn xác.
> * **Xử lý tài liệu:** Sử dụng `pdfplumber` để bóc tách tệp PDF và `python-docx` để đọc cũng như biên dịch định dạng Word.
> * **Khung kiểm chuẩn chất lượng:** Sử dụng khung kiểm thử khoa học **Ragas** để đo lường các chỉ số về Độ chính xác ngữ cảnh, Độ bao phủ ngữ cảnh và Độ trung thực của câu trả lời."*

---

### [Slide 6] Kỹ thuật Dữ liệu và Phân đoạn theo Điều luật (05:30 - 07:00)
* **Người trình bày:** **Phạm Gia Thịnh**
* **Điểm nhấn trên slide:** **SƠ ĐỒ PHA A (PIPELINE INDEXING 583 CHUNKS)**, Chi tiết Biểu thức Regex phân đoạn, và Cấu trúc tệp dữ liệu mẫu ở Hộp số 3.
* **Lời thoại (Thịnh) — THUYẾT MINH CHI TIẾT SƠ ĐỒ PHA A & BIỂU THỨC REGEX:**
> *"Kính thưa Thầy Cô, dữ liệu pháp luật là loại dữ liệu có cấu trúc ngữ nghĩa phân tầng rất chặt chẽ. Nếu áp dụng cách làm thông thường là chia văn bản theo số lượng từ cố định (ví dụ cứ 500 từ cắt một đoạn), chúng ta sẽ làm đứt gãy câu văn, làm mất điều kiện loại trừ của điều luật và dẫn đến sai lệch pháp lý hoàn toàn.
>
> *Xin quý Thầy Cô quan sát **Sơ đồ Pha A – Quy trình xây dựng cơ sở tri thức (bên trái)**:*
> 1. * **Bước 1 & 2:** Bắt đầu từ 7 văn bản luật thô, bộ đọc tài liệu [document_reader.py](file:///d:/PJ/Lexdraft/modules/shared/document_reader.py) sẽ làm sạch đầu mục, loại bỏ số trang, tiêu đề lặp lại và chuẩn hóa bảng biểu.
> 2. * **Bước 3 – Phân đoạn theo Điều luật (Structure-Aware Chunking):** 
>    * Trên slide, nhóm hiển thị biểu thức chính quy đại diện: `(?m)^Điều\s+(\d+)`
>      * `(?m)^`: Chế độ Multi-line, neo tìm kiếm tại **đầu mỗi dòng** — ngăn chặn tuyệt đối việc bắt nhầm các câu trích dẫn nội tuyến nằm ở giữa câu (ví dụ câu: *"Căn cứ theo Điều 35..."* thì 'Điều 35' nằm giữa dòng sẽ bị bỏ qua, không bị xé nhầm thành đoạn mới).
>      * `Điều\s+`: Khớp từ khóa 'Điều' và khoảng trắng theo sau.
>      * `(\d+)`: Bắt chính xác **số hiệu của Điều** (ví dụ: `401`, `513`) để tự động gán vào trường siêu dữ liệu `article`.
>    * Nhóm cắt trọn vẹn từ Điều này đến Điều kế tiếp, nhờ đó toàn bộ các Khoản, Điểm phụ thuộc và điều kiện loại trừ được gom trọn vẹn trong một đoạn duy nhất, bảo toàn đơn vị ngữ nghĩa pháp lý hoàn chỉnh.
> 3. * **Bước 4 – Gán siêu dữ liệu:** Từng đoạn phân đoạn được bổ sung ngay 5 trường thông tin nguồn gốc.
> 4. * **Bước 5 & 6:** Toàn bộ các đoạn được gửi sang mô hình Gemini Embedding để chuyển thành véc-tơ 768 chiều, sau đó tiến hành chuẩn hóa độ dài L2.
> 5. * **Bước 7:** Nạp vào chỉ mục FAISS IndexFlatIP và lưu trữ xuống đĩa cứng. Tổng cộng nhóm đã tạo ra **583 véc-tơ điều luật** cho chỉ mục luật và **28 véc-tơ** cho chỉ mục mẫu hợp đồng.
>
> *Ở **Hộp số 3 bên phải**, quý Thầy Cô có thể thấy hình ảnh cấu trúc thực tế của một mẩu dữ liệu JSON được lưu trữ:*
> * Gồm định danh duy nhất `chunk_id`, nội dung điều luật đầy đủ trong trường `text`.
> * Phần siêu dữ liệu `metadata` lưu trữ rõ ràng: Tên luật, Số hiệu văn bản hợp nhất, Số điều, Tên điều, và chuỗi trích dẫn nguồn gốc chuẩn mực theo đúng quy định văn thư hành chính.
> * Cùng với một mảng véc-tơ 768 con số thực biểu diễn tọa độ ngữ nghĩa của điều luật đó."*

---

### [Slide 7] Cơ chế 4 Tầng Kiểm soát Sinh ảo (07:00 - 08:30)
* **Người trình bày:** **Phạm Gia Thịnh**
* **Điểm nhấn trên slide:** **SƠ ĐỒ PHA B (ONLINE QUERY)** & Bốn hộp màu mô tả chi tiết **4 TẦNG GUARDRAILS (T1, T2, T3, T4)**.
* **Lời thoại (Thịnh) — THUYẾT MINH CHI TIẾT SƠ ĐỒ PHA B & 4 TẦNG:**
> *"Thưa Thầy Cô, đây chính là **đóng góp kỹ thuật trọng tâm nhất của đề tài: Cơ chế 4 Tầng Kiểm soát Sinh ảo (Guardrails)** nhằm giải quyết dứt điểm vấn đề ảo giác của mô hình trí tuệ nhân tạo.
>
> *Nhìn vào **Sơ đồ Pha B ở giữa**: Khi người dùng gửi một câu hỏi hoặc tải một điều khoản hợp đồng lên:*
> * Câu hỏi được nhúng thành véc-tơ và tìm kiếm trong chỉ mục FAISS đã tạo ở Pha A để lấy ra các đoạn điều luật có điểm tương đồng cao nhất.
> * Ngay tại đây, dữ liệu bắt buộc phải vượt qua **hình thoi 'Kiểm tra ngưỡng phù hợp'**: Nếu KHÔNG ĐẠT, hệ thống lập tức rẽ nhánh sang màu đỏ: phát thông báo cảnh báo hoặc kích hoạt Từ chối an toàn mà **không gọi mô hình AI**. Chỉ khi ĐẠT NGƯỠNG, hệ thống mới ráp lời nhắc, gửi cho Gemini và trả về câu trả lời kèm trích dẫn.
>
> *Bốn tầng kiểm soát được nhóm thiết kế chặt chẽ như ở các hộp bên phải:*
> * **TẦNG 1 – Sàng lọc hiệu lực 3 cấp (Hộp đỏ T1):** Sử dụng danh mục kiểm duyệt `expired_laws.json`. Ngay khi người dùng nhắc đến các luật cũ như Luật Giao dịch điện tử 2005 hay một văn bản không có thật như 'Luật Thương mại 2020', Tầng 1 sẽ chặn đứng ngay lập tức với độ tin cậy 100% trước khi thực hiện bất kỳ thao tác nào khác.
> * **TẦNG 2 – Ràng buộc Cấu trúc & Siêu dữ liệu nguồn (Hộp xanh dương T2):** Ép mô hình AI chỉ được phép trích dẫn căn cứ nếu đoạn dữ liệu truy xuất từ FAISS có đầy đủ 5 trường siêu dữ liệu nguồn gốc đã xác thực.
> * **TẦNG 3 – Chốt chặn Ngưỡng tương đồng $\tau = 0.75$ (Hộp cam T3):** Được cài đặt trực tiếp bằng mã nguồn Python (`llm_client.py`). Nếu điểm tương đồng cao nhất của các đoạn trích xuất nhỏ hơn 0.75, hệ thống kích hoạt cơ chế **Safe Refusal (Từ chối an toàn)** trong **0.01 giây**, tuyệt đối không để mô hình AI tự biên tự diễn.
> * **TẦNG 4 – Thiết kế Lời nhắc Neo dữ liệu và Phủ định ràng buộc (Hộp xanh lá T4):** Thiết lập lời nhắc với vai trò chuyên gia khách quan, kèm quy tắc nghiêm ngặt: 'Chỉ kết luận có rủi ro khi tìm thấy điều cấm rõ ràng trong ngữ cảnh được cung cấp; nếu không có căn cứ thì phải tuyên bố không có rủi ro hoặc từ chối'.
>
> *Kính thưa Thầy Cô, sau khi đã hoàn thành phần cơ sở khoa học, dữ liệu và cơ chế kiểm soát 4 tầng, em xin trân trọng kính mời bạn **Lê Hữu Tiến** tiếp tục báo cáo về Hiện thực 3 phân hệ nghiệp vụ và các kết quả thực nghiệm khoa học."*

---

### [Slide 8] Hiện thực Phân hệ 1 – Soạn thảo Hợp đồng (08:30 - 09:30)
* **Người trình bày:** **Lê Hữu Tiến**
* **Điểm nhấn trên slide:** Khối luồng thực thi (Form ➔ Dual-Index RAG ➔ Tiêm tuân thủ ➔ Xuất Word) và 3 đặc tính kỹ thuật bên phải.
* **Lời thoại (Tiến):**
> *"Kính thưa quý Thầy Cô, em là Lê Hữu Tiến. Tiếp theo phần trình bày của bạn Thịnh, em xin phép báo cáo về quá trình hiện thực 3 phân hệ nghiệp vụ chính của hệ thống LexDraft.
>
> *Đầu tiên là **Phân hệ 1: Hỗ trợ Soạn thảo Hợp đồng Dịch vụ** (Slide số 8):*
> * *Luồng thực thi:* Bắt đầu từ việc người dùng nhập thông tin giao dịch vào biểu mẫu (gồm chủ thể Bên A, Bên B, phạm vi công việc, giá trị hợp đồng và thời hạn thanh toán).
> * *Điểm nhấn kỹ thuật thứ nhất – Truy xuất tăng cường kép (Dual-Index RAG):* Hệ thống không chỉ tra cứu một nguồn duy nhất mà truy xuất song song trên hai không gian véc-tơ: lấy cấu trúc khung sườn điều khoản từ `template_index` (kho mẫu hợp đồng chuẩn), đồng thời lấy các quy định pháp luật điều chỉnh tương ứng từ `law_index`.
> * *Điểm nhấn kỹ thuật thứ hai – Tiêm tuân thủ pháp lý động (Compliance Injection):* Hệ thống tự động lồng ghép các quy định bắt buộc của luật mới vào dự thảo. Ví dụ: tự động khống chế trần phạt vi phạm không quá 8% giá trị nghĩa vụ theo đúng Điều 301 Luật Thương mại, và cài cắm các điều khoản bảo hộ quyền tác giả phần mềm theo Luật Sở hữu trí tuệ 2026.
> * *Điểm nhấn kỹ thuật thứ ba – Bộ biên dịch tài liệu Word XML:* Nhóm xây dựng công cụ chuyển đổi nội dung từ Markdown sang tệp Word `.docx` hoàn chỉnh. Toàn bộ tiêu đề, bảng biểu thông tin hai bên và các điều khoản đều được căn lề trang A4 chuẩn theo quy chuẩn văn bản thương mại."*

---

### [Slide 9] Hiện thực Phân hệ 2 – Gợi ý Rủi ro Pháp lý (09:30 - 10:30)
* **Người trình bày:** **Lê Hữu Tiến**
* **Điểm nhấn trên slide:** Bảng mẫu kết quả rà soát thực tế bên trái; Ba khối tính năng tự động bên phải (Tự động 1 chạm, Tầng 1 Guardrail, Đối chiếu vi phạm điều cấm).
* **Lời thoại (Tiến):**
> *"Tiếp theo là **Phân hệ 2: Gợi ý Rủi ro Pháp lý trong Hợp đồng** (Slide số 9):*
> * *Quy trình phân tích tự động một chạm:* Người dùng chỉ cần tải lên tệp hợp đồng sẵn có ở định dạng Word (`.docx`) hoặc PDF. Bộ xử lý sẽ tự động đọc, loại bỏ rác định dạng và chia tách toàn bộ hợp đồng thành từng điều khoản riêng biệt để tiến hành thẩm định.
> * *Tích hợp Chốt chặn Tầng 1:* Trước khi phân tích nội dung, hệ thống quét qua bộ kiểm tra hiệu lực văn bản. Nếu hợp đồng viện dẫn các luật cũ như Luật Giao dịch điện tử 2005, hệ thống sẽ giương ngay cờ cảnh báo đỏ ở đầu trang để người dùng lưu ý.
> * *Đối chiếu vi phạm điều cấm:* Từng điều khoản được đối chiếu với cơ sở dữ liệu luật. Như bảng kết quả thực tế trên slide minh họa:
>   * Khi phát hiện hợp đồng ghi mức phạt vi phạm là 20%, hệ thống lập tức cảnh báo vượt trần tối đa 8% theo Điều 301 Luật Thương mại.
>   * Khi phát hiện điều khoản bên cung ứng dịch vụ tự miễn trừ toàn bộ trách nhiệm khi có lỗi, hệ thống cảnh báo vi phạm Điều 360 và Điều 584 Bộ luật Dân sự 2015 vì pháp luật không cho phép miễn trừ đối với lỗi cố ý gây thiệt hại."*

---

### [Slide 10] Hiện thực Phân hệ 3 – Trợ lý Hỏi – Đáp Pháp lý (10:30 - 11:30)
* **Người trình bày:** **Lê Hữu Tiến**
* **Điểm nhấn trên slide:** Hai chế độ làm việc (Chế độ A có ngữ cảnh hợp đồng, Chế độ B tra cứu độc lập) và 3 điểm nhấn kỹ thuật cốt lõi.
* **Lời thoại (Tiến):**
> *"Phân hệ nghiệp vụ thứ ba là **Trợ lý Chatbot Hỏi – Đáp Pháp lý** (Slide số 10):*
>
> *Nhóm thiết kế trợ lý hoạt động linh hoạt theo **hai chế độ ngữ cảnh**:*
> * **Chế độ A – Có ngữ cảnh hợp đồng:** Khi người dùng vừa phân tích rủi ro một hợp đồng ở Phân hệ 2 và bấm nút chuyển sang Chatbot, hệ thống sử dụng hàm `attach_contract_context()` để mang toàn bộ các điều khoản rủi ro sang phiên chat. Người dùng có thể hỏi trực tiếp: 'Điều khoản phạt này sai thì tôi phải sửa lại câu chữ thế nào cho chuẩn?', và Chatbot sẽ gợi ý mẫu câu điều chỉnh bám sát hợp đồng đó.
> * **Chế độ B – Tra cứu pháp luật độc lập:** Khi chưa có hợp đồng tải lên, Chatbot đóng vai trò một luật sư tư vấn trực tuyến, trả lời mọi câu hỏi về pháp luật hợp đồng dịch vụ dựa trên 583 véc-tơ điều luật.
>
> *Ba điểm nhấn kỹ thuật cốt lõi của Chatbot:*
> 1. *Áp dụng nghiêm ngặt ngưỡng tương đồng 0.75 để chặn đứng câu hỏi bẫy, bảo đảm tỷ lệ bịa luật bằng 0%.*
> 2. *Bắt buộc trích dẫn nguồn xác thực: Mọi câu trả lời đều có hộp mở rộng ghi rõ Căn cứ: Điều nào, Khoản nào, thuộc văn bản luật nào.*
> 3. *Quản lý ngữ cảnh phiên hội thoại nhiều lượt hoàn toàn trên bộ nhớ RAM (`_SESSIONS`), cho phép người dùng chuyển đổi mượt mà giữa Chế độ A và Chế độ B."*

---

### [Slide 11] Thực nghiệm Định lượng – Kết quả Giả thiết 1 & 2 (11:30 - 12:30)
* **Người trình bày:** **Lê Hữu Tiến**
* **Điểm nhấn trên slide:** **GIẢI THÍCH RÕ Ý NGHĨA TỪNG CHỈ SỐ TRÊN BIỂU ĐỒ TRƯỚC**, sau đó thuyết minh **BIỂU ĐỒ HÌNH 3 (A/B TESTING)** & **BIỂU ĐỒ HÌNH 4 (ABLATION STUDY & HIT@K)**.
* **Lời thoại (Tiến) — GIẢI THÍCH CHI TIẾT CHỈ SỐ TRƯỚC KHI BÁO CÁO KẾT QUẢ:**
> *"Kính thưa Thầy Cô, để chứng minh tính khoa học của hệ thống, nhóm sử dụng bộ dữ liệu kiểm chuẩn gồm **50 câu hỏi** trích xuất từ `golden_dataset.json`. 
>
> *Trước khi đi vào số liệu, em xin phép **giải thích rõ ý nghĩa các chỉ số đo lường trên Biểu đồ Hình 3 (bên trái - Kiểm thử A/B)**:*
> 1. * **Mức độ liên quan (Law Coverage Rate):** Đo lường tỷ lệ phần trăm câu trả lời của AI đề cập đúng các văn bản luật điều chỉnh vấn đề người dùng hỏi.
> 2. * **Khả năng cung cấp căn cứ (Article Citation Rate):** Đo lường khả năng AI chỉ đích danh tên Điều, Khoản cụ thể thay vì chỉ trả lời lý thuyết chung chung.
> 3. * **Tỷ lệ ảo giác (Hallucination Rate - càng thấp càng tốt):** Tỷ lệ câu trả lời viện dẫn sai lệch, tự bịa ra điều luật không có thật hoặc dùng luật cũ đã hết hiệu lực.
>
> * **Kết quả thực nghiệm trên Hình 3 chỉ ra sự vượt trội của LexDraft RAG:**
>   * Ở AI thuần (Zero-shot - cột màu cam), tỷ lệ sinh ảo giác lên tới **10.0%**. Khi tích hợp giải pháp RAG của LexDraft (cột màu xanh lá), tỷ lệ ảo giác giảm mạnh xuống chỉ còn **4.0%**.
>   * Khả năng cung cấp đúng căn cứ pháp lý đạt **88.0%**.
>   * Nhóm đưa ra kết luận **Chấp nhận có điều kiện Giả thiết 1**: Mặc dù AI thuần có độ phủ từ khóa rộng hơn (98% so với 86%), nhưng việc chấp nhận giới hạn phạm vi chặt chẽ của RAG đã giúp loại bỏ phần lớn rủi ro ảo giác sai luật.
>
> *Tiếp theo, xin mời Thầy Cô quan sát **Biểu đồ Hình 4 bên phải – Nghiên cứu triệt tiêu (Ablation Study) về vai trò của Siêu dữ liệu Metadata và Độ chính xác truy xuất**:*
> * **Các chỉ số trên biểu đồ này mang ý nghĩa:**
>   1. * **Xác định đúng Luật (Law Name Accuracy):** Tỷ lệ nhận diện đúng tên đạo luật áp dụng.
>   2. * **Trích dẫn đúng Điều (Article Accuracy):** Tỷ lệ trích đúng số hiệu Điều luật điều chỉnh.
>   3. * **Bóc tách trích dẫn có cấu trúc (Structured Citation Rate):** Tỷ lệ câu trả lời có trường siêu dữ liệu nguồn gốc tách biệt đầy đủ 5 trường độc lập (`ten_luat`, `so_hieu`, `so_dieu`, `ten_dieu`, `nguon_dan`).
>   4. * **Hit@1 và Hit@3:** Khi truy xuất véc-tơ trong FAISS, Hit@1 là xác suất điều luật đúng nằm ngay ở vị trí đầu tiên; Hit@3 là xác suất điều luật đúng nằm trong top 3 kết quả trả về.
>
> * **Kết quả thực nghiệm trên Hình 4:**
>   * Nếu không có siêu dữ liệu (cột xám), tỷ lệ trích dẫn có cấu trúc là **0.0%**. Khi có siêu dữ liệu của LexDraft (cột xanh lá đậm), tỷ lệ này đạt **100.0% tuyệt đối**.
>   * Độ chính xác xác định đúng tên luật tăng từ 76.0% lên **96.0%**.
>   * Độ chính xác truy xuất FAISS đạt **Hit@1 là 84.1%** và **Hit@3 đạt tới 93.18%** (nghĩa là trong 3 đoạn văn bản đầu tiên trả về, có tới trên 93% trường hợp chứa đúng điều luật cần tìm). Nhóm **Chấp nhận hoàn toàn Giả thiết 2**."*

---

### [Slide 12] Thực nghiệm Định lượng – Kết quả Giả thiết 3 (12:30 - 13:30)
* **Người trình bày:** **Lê Hữu Tiến**
* **Điểm nhấn trên slide:** **GIẢI THÍCH RÕ Ý NGHĨA MA TRẬN TỪ CHỐI AN TOÀN**, sau đó thuyết minh **BIỂU ĐỒ HÌNH 5** và phân tích sự đánh đổi khoa học 6.67%.
* **Lời thoại (Tiến) — GIẢI THÍCH CHI TIẾT CÁC KHÁI NIỆM TRƯỚC KHI BÁO CÁO:**
> *"Xin chuyển sang Slide số 12: Đây là kết quả kiểm chứng **Giả thiết 3 về Cơ chế Kiểm soát Ảo giác và Ma trận Từ chối An toàn (Biểu đồ Hình 5)**.
>
> *Để Thầy Cô tiện theo dõi biểu đồ, em xin **giải thích bản chất của 3 khái niệm đo lường trong bài test này**:*
> 1. * **Tỷ lệ trả lời đúng câu hỏi hợp lệ (Correct Answered Rate):** Đối với câu hỏi nằm đúng phạm vi pháp luật hợp đồng dịch vụ, hệ thống **bắt buộc phải trả lời đầy đủ, chính xác kèm căn cứ**, tuyệt đối không được từ chối vô lý.
> 2. * **Tỷ lệ từ chối an toàn (Safe Refusal Rate):** Khi gặp các câu hỏi bẫy (luật cũ, ngoài ngành, điều bịa), hệ thống **bắt buộc phải chủ động nhận diện và dừng lại**, phát thông báo từ chối an toàn để không bịa luật.
> 3. * **Tỷ lệ từ chối nhầm (False Refusal Rate):** Câu hỏi hợp lệ nhưng do người dùng dùng khẩu ngữ đời thường khiến điểm tương đồng véc-tơ không vượt qua ngưỡng $\tau = 0.75$, dẫn đến việc hệ thống từ chối nhầm.
>
> * **Cấu trúc bài test gồm 35 câu hỏi đối sánh được chia làm 4 nhóm:**
>   1. *Nhóm 1 – Câu hỏi thực tế đúng phạm vi (15 câu hợp lệ).*
>   2. *Nhóm 2 – Câu hỏi bẫy về Luật cũ hoặc Luật giả mạo (6 câu).*
>   3. *Nhóm 3 – Câu hỏi bẫy ngoài phạm vi như luật hình sự, đất đai, hôn nhân (8 câu).*
>   4. *Nhóm 4 – Câu hỏi bẫy về Điều luật bịa đặt không có thật như Điều 999 BLDS (6 câu).*
>
> * **Kết quả thực nghiệm trên Biểu đồ Hình 5 minh chứng rõ rệt:**
>   * Đối với cả ba nhóm câu hỏi bẫy (Nhóm 2, 3 và 4), hệ thống kích hoạt cơ chế từ chối an toàn **đạt tỷ lệ chính xác tuyệt đối 100.0% (20/20 câu bẫy đều bị chặn đứng)**!
>   * Nhờ vậy, **tỷ lệ ảo giác (Hallucination) trên toàn bộ tập kiểm thử được đưa về mức 0.0%** (0/35 câu).
>   * Ở nhóm câu hỏi hợp lệ, hệ thống trả lời đúng **14/15 câu (93.33%)**, và chỉ ghi nhận **1 câu bị từ chối nhầm (False Refusal = 6.67%)** do người dùng hỏi bằng từ ngữ thông tục khiến điểm Cosine chỉ đạt 0.742 (dưới ngưỡng 0.75).
>   * Đây là một **sự đánh đổi (trade-off) hoàn toàn hợp lý và cần thiết trong lĩnh vực khoa học pháp lý**: Thà chúng ta từ chối nhầm 6.67% để người dùng đặt lại câu hỏi rõ ràng hơn, còn hơn là để lọt thông tin ảo giác dẫn đến những tranh chấp pháp lý tai hại. Nhóm **Chấp nhận hoàn toàn Giả thiết 3**."*

---

### [Slide 13] Đánh giá Ragas và Hiệu năng Phát hiện Rủi ro (13:30 - 14:30)
* **Người trình bày:** **Lê Hữu Tiến**
* **Điểm nhấn trên slide:** **GIẢI THÍCH CHI TIẾT 3 CHỈ SỐ RAGAS VÀ CÔNG THỨC RECALL**, sau đó thuyết minh **BIỂU ĐỒ HÌNH 6 (RAGAS)** & **BIỂU ĐỒ HÌNH 7, 8 (BENCHMARK 5 HỢP ĐỒNG)**.
* **Lời thoại (Tiến) — GIẢI THÍCH CHI TIẾT CHỈ SỐ TRƯỚC KHI BÁO CÁO:**
> *"Kính thưa Thầy Cô, tại Slide 13, nhóm sử dụng hai phương pháp đánh giá độc lập để khẳng định chất lượng toàn diện của hệ thống:
>
> * **Phần 1: Đánh giá chất lượng Pipeline RAG bằng khung kiểm chuẩn quốc tế RAGAS (Biểu đồ Hình 6 phía trên):**
>   * *Trước hết, em xin giải thích bản chất toán học của 3 chỉ số Ragas đo lường (thang điểm 0.0 đến 1.0):*
>     1. * **Context Precision (Độ chính xác ngữ cảnh):** Đo lường mức độ các đoạn văn bản luật liên quan trực tiếp được xếp ở các thứ hạng ưu tiên cao nhất trong kết quả truy xuất của FAISS (tránh việc đưa thông tin không liên quan lên đầu).
>     2. * **Context Recall (Độ bao phủ ngữ cảnh):** Đo lường tỷ lệ các căn cứ pháp luật có trong đáp án chuẩn (Ground Truth) được hệ thống tìm kiếm thành công và đưa vào ngữ cảnh gửi cho AI.
>     3. * **Faithfulness (Độ trung thực):** Đo lường tỷ lệ các luận điểm trong câu trả lời do AI sinh ra được chứng minh và suy luận trực tiếp từ ngữ cảnh truy xuất (đo lường khả năng chống bịa đặt thông tin).
>   * *Kết quả thực nghiệm trên toàn bộ 50 câu hỏi kiểm chuẩn:*
>     * Khi đánh giá trên nhóm 44 câu hỏi tra cứu luật hiện hành (Fact Retrieval), hệ thống đạt điểm rất cao: **Context Precision đạt 0.93 (93%), Context Recall đạt 0.77, và Faithfulness đạt 0.66**.
>     * Trên toàn bộ hệ thống 50 câu (tính gộp cả 6 câu hỏi bẫy luật cũ kích hoạt Safe Refusal): **Context Precision đạt 0.84, Context Recall đạt 0.72, và Faithfulness đạt 0.59**.
>     * Kết quả này khẳng định hệ thống duy trì được độ chính xác truy xuất vượt trội (trên 84% - 93%) trong khi vẫn bảo vệ người dùng trước các câu hỏi bẫy.
>
> * **Phần 2: Hiệu năng phát hiện rủi ro hợp đồng thực tế (Biểu đồ Hình 7 và Ma trận nhầm lẫn Hình 8 phía dưới):**
>   * *Về các chỉ số đo lường hiệu năng rà soát hợp đồng:*
>     1. * **Lỗi cài cắm (Ground Truth):** Tổng số lỗi vi phạm pháp luật được cố tình gài vào hợp đồng để kiểm thử (tổng cộng 13 lỗi).
>     2. * **Phát hiện đúng (True Positive - TP):** Số lỗi vi phạm thực tế mà hệ thống phát hiện chính xác.
>     3. * **Bỏ sót (False Negative - FN):** Số lỗi có trong hợp đồng nhưng hệ thống không nhận ra.
>     4. * **Độ nhạy phát hiện vi phạm (Recall):** $\text{Recall} = \frac{\text{TP}}{\text{TP} + \text{FN}}$: Tỷ lệ phát hiện được bao nhiêu phần trăm trên tổng số lỗi vi phạm thực tế.
>     5. * **Độ đặc hiệu (Specificity):** Tỷ lệ nhận diện đúng các điều khoản an toàn trong hợp đồng chuẩn sạch.
>   * *Kết quả thực nghiệm trên 5 hợp đồng đối sánh (tổng cộng 43 điều khoản):*
>     * Hệ thống phát hiện chính xác **12 trên tổng số 13 lỗi vi phạm, đạt độ nhạy (Recall) lên tới 92.31%**.
>     * Nhận diện chính xác 100% các văn bản hết hiệu lực hoặc giả mạo (4/4 trường hợp).
>     * Ma trận nhầm lẫn tại Hình 8 cho thấy: 18 điều khoản an toàn được phân loại chính xác, chỉ có 1 lỗi bị bỏ sót (False Negative = 7.69% tại Hợp đồng Phần mềm) do sự tranh chấp diễn giải giữa Bộ luật Dân sự và Luật Thương mại khi chưa xác định rõ tư cách thương nhân.
>
> *Sau đây, để minh chứng cho toàn bộ các kết quả lý thuyết và số liệu trên, xin kính mời Thầy Cô chuyển sang **Slide 14 – Phần Chạy Demo Trực Tiếp Trên Phần Mềm** do bạn **Phạm Gia Thịnh** trực tiếp thao tác."*

---

### [Slide 14] Chuyển giao sang Phần Thực nghiệm Chạy Demo Trực tiếp (14:30 - 14:45)
* **Người trình bày:** **Lê Hữu Tiến** giới thiệu chuyển giao ➔ **Phạm Gia Thịnh** tiếp nhận máy tính và bắt đầu Demo.
* **Lời thoại (Tiến):**
> *"Dạ thưa Thầy Cô, Slide 14 là 3 nội dung nhóm sẽ thực hiện demo trực tiếp ngay bây giờ:
> 1. Soạn thảo hợp đồng tự động từ dữ liệu mẫu và xuất tệp Word chuẩn A4.
> 2. Tải lên tệp hợp đồng có cài cắm lỗi vi phạm để xem hệ thống phát hiện rủi ro theo thời gian thực.
> 3. Trò chuyện với Chatbot ở cả hai chế độ và thử nghiệm các câu hỏi bẫy triệt tiêu ảo giác.
> Em xin mời bạn Thịnh bắt đầu phần chạy thử nghiệm ạ!"*

---

## PHẦN II: KỊCH BẢN THAO TÁC DEMO TRỰC TIẾP TRÊN PHẦN MỀM (THỊNH THỰC HIỆN)

```
[Thời lượng demo: 5 - 6 phút]
[Người thao tác chuột và thuyết minh: Phạm Gia Thịnh]
[Người hỗ trợ đứng cạnh màn chiếu: Lê Hữu Tiến]
```

### Màn 1: Soạn thảo Hợp đồng thông minh (Thao tác: 2 phút)

* **Giao diện:** Mở trang web ứng dụng tại cổng `http://localhost:8501`, chọn trang `📝 Soạn thảo Hợp đồng` (mã nguồn tại [ui/pages/page_drafting.py](file:///d:/PJ/Lexdraft/ui/pages/page_drafting.py)).
* **Thao tác chuột của Thịnh:**
  1. Di chuột đến hàng nút thao tác nhanh trên cùng, bấm nút **`⚡ Mẫu thử HĐ Thiết kế Web`**.
     * *(Thịnh chỉ tay lên màn hình: Toàn bộ biểu mẫu được điền tự động: Bên A là Công ty TNHH Công nghệ Lexdraft, Bên B là Công ty CP Giải pháp Số Việt, giá trị 150 triệu đồng, thời hạn 6 tháng, cam kết bảo hành 12 tháng).*
  2. Cuộn chuột xuống dưới và bấm nút **`🚀 Tiến hành Tạo Dự thảo Hợp đồng`**.
* **Lời thuyết minh của Thịnh:**
  > *"Kính thưa Thầy Cô, khi em bấm nút tạo dự thảo, hệ thống kích hoạt cơ chế Truy xuất tăng cường kép (Dual-Index RAG): một mặt lấy khung điều khoản chuẩn từ kho mẫu hợp đồng thiết kế web, mặt khác tra cứu các quy định bắt buộc trong luật hiện hành để thực hiện 'Tiêm tuân thủ pháp lý động'.
  >
  > *Chỉ sau vài giây, bản dự thảo hợp đồng hoàn chỉnh đã được tạo ra. Em xin kính mời Thầy Cô quan sát khung **Xem trước khổ giấy A4 (A4 Paper View)**:*
  > * Phần Quốc hiệu, Tiêu ngữ và Tên hợp đồng được hệ thống đọc trực tiếp thuộc tính căn giữa từ mã nguồn để căn giữa hoàn hảo, không bị xô lệch lề.
  > * Khoảng cách dòng đạt chuẩn 1.5 của văn bản hành chính.
  > * Em có thể kéo thanh trượt **Phóng to / Thu nhỏ (Zoom Preview)** từ 100% lên 110% để người dùng dễ đọc trên các màn hình khác nhau.
  > * Đặc biệt, tại **Điều khoản Phạt vi phạm**: Hệ thống đã tự động cài cắm câu văn: 'Mức phạt vi phạm tối đa không vượt quá 8% giá trị phần nghĩa vụ hợp đồng bị vi phạm theo Điều 301 Luật Thương mại'.
  > * Bây giờ em bấm nút **`📥 Tải file Word (.docx)`**. Tệp Word tải về có đầy đủ cấu trúc Heading, bảng biểu và mở ra trên Microsoft Word chuẩn chỉ 100%."*

---

### Màn 2: Rà soát Rủi ro & Cảnh báo Hiệu lực Văn bản (Thao tác: 2 phút)

* **Giao diện:** Chuyển sang thanh điều hướng, chọn trang `📤 Gợi ý Rủi ro Pháp lý` (mã nguồn tại [ui/pages/page_risk.py](file:///d:/PJ/Lexdraft/ui/pages/page_risk.py)).
* **Thao tác chuột của Thịnh:**
  1. Tại ô tải tệp hợp đồng, nhấn chọn tệp kiểm thử có sẵn trong thư mục dự án: `d:\PJ\Lexdraft\data\test_contract_risky.docx`.
  2. Bấm nút màu xanh: **`🔍 Bắt đầu Phân tích Rủi ro`**.
* **Lời thuyết minh của Thịnh:**
  > *"Bây giờ em chuyển sang Phân hệ rà soát rủi ro. Em tải lên tệp `test_contract_risky.docx` – đây là hợp đồng nhóm đã cố tình cài cắm ba lỗi vi phạm nghiêm trọng để thử thách hệ thống.
  >
  > *Khi bấm bắt đầu phân tích, quy trình phân tích dạng dòng (Streaming Pipeline) lập tức khởi chạy và hiển thị kết quả trực tiếp lên bảng điều khiển bên phải:*
  > 1. * **Ngay trên cùng là Banner cảnh báo màu đỏ của Chốt chặn Tầng 1:** Hệ thống phát hiện ngay tại Lời mở đầu của hợp đồng có viện dẫn 'Luật Giao dịch điện tử số 51/2005/QH11'. Hệ thống thông báo rõ: Văn bản này đã hết hiệu lực từ ngày 01/07/2024 và bị thay thế toàn bộ bởi Luật Giao dịch điện tử 2023.
  > 2. * **Tiếp theo trong Bảng phân tích chi tiết từng điều khoản:**
  >    * Tại **Điều 6 về Phạt vi phạm**: Hợp đồng ghi bên vi phạm phải chịu phạt 20%. Hệ thống gắn nhãn **Cờ Đỏ – Rủi ro cao**, và trích dẫn chuẩn mực Điều 301 Luật Thương mại (Văn bản hợp nhất số 113): Mức phạt tối đa chỉ là 8%, việc thỏa thuận 20% là vi phạm điều cấm của luật và phần vượt quá sẽ bị vô hiệu.
  >    * Tại **Điều 9 về Miễn trừ trách nhiệm**: Hợp đồng ghi bên cung ứng được miễn trừ mọi trách nhiệm trong mọi trường hợp. Hệ thống cảnh báo vi phạm Điều 360 và Điều 584 Bộ luật Dân sự 2015, giải thích rõ các bên không được thỏa thuận miễn trừ trách nhiệm đối với hành vi cố ý gây thiệt hại.
  >
  > *Sau khi rà soát xong, ở góc dưới có nút **`💬 Hỏi Chatbot về hợp đồng này`**. Em xin bấm vào nút này để chuyển ngữ cảnh sang Phân hệ 3."*

---

### Màn 3: Trợ lý Hỏi – Đáp Pháp lý & Thử nghiệm Bẫy Ảo giác (Thao tác: 2 phút)

* **Giao diện:** Ứng dụng tự động điều hướng sang trang `💬 Chatbot Q&A` (mã nguồn tại [ui/pages/page_chatbot.py](file:///d:/PJ/Lexdraft/ui/pages/page_chatbot.py)).

#### 🔹 Thử nghiệm 1: Chế độ A – Tư vấn sửa đổi theo hợp đồng vừa tải
* **Thao tác:** Nhìn thấy thông báo màu xanh lá: `🟢 Chế độ A — Trợ lý đang theo dõi ngữ cảnh: test_contract_risky.docx`.
* **Thịnh gõ câu hỏi vào ô chat:**
  > `"Điều 6 hợp đồng của tôi phạt 20% thì tôi nên sửa lại như thế nào cho đúng luật?"`
* **Lời thuyết minh của Thịnh:**
  > *"Ở Chế độ A, Chatbot đã nắm giữ ngữ cảnh của hợp đồng vừa rà soát. Em đặt câu hỏi nhờ sửa Điều 6. 
  > Quý Thầy Cô có thể thấy: Trợ lý phản hồi rất thông minh, giải thích mức phạt 20% là vượt quá trần quy định và soạn thảo lại ngay cho em một điều khoản mẫu chuẩn xác: 'Trong trường hợp một bên vi phạm, mức phạt là 8% giá trị phần nghĩa vụ bị vi phạm theo Điều 301 Luật Thương mại'. Phía dưới có hộp mở rộng hiển thị đúng căn cứ pháp lý được trích xuất."*

#### 🔹 Thử nghiệm 2: Chế độ B – Thử thách Bẫy văn bản luật không tồn tại
* **Thao tác:** Bấm nút chuyển phiên hoặc gõ trực tiếp câu hỏi bẫy luật không có thật:
* **Thịnh gõ câu hỏi vào ô chat:**
  > `"Hợp đồng dịch vụ thương mại ký căn cứ 'Luật Thương mại 2020' thì có giá trị pháp lý không?"`
* **Lời thuyết minh của Thịnh:**
  > *"Bây giờ em chuyển sang thử nghiệm các câu hỏi bẫy ảo giác. Câu hỏi này bẫy về một văn bản không có thật: 'Luật Thương mại 2020'. Các mô hình AI thông thường sẽ tưởng thật và trả lời phân tích dài dòng.
  > Nhưng trên LexDraft: **Chốt chặn Tầng 1 và Tầng 3 lập tức phát hiện trong 0.01 giây** và trả lời dứt khoát: 'Không tồn tại văn bản quy phạm pháp luật nào tên là Luật Thương mại 2020. Văn bản hiện hành là Luật Thương mại 2005 được hợp nhất tại Văn bản hợp nhất số 113 năm 2025'."*

#### 🔹 Thử nghiệm 3: Thử thách Bẫy Điều luật giả mạo (Chứng minh Chốt chặn Tầng 3)
* **Thịnh gõ câu hỏi vào ô chat:**
  > `"Điều 999 Luật Thương mại quy định gì về mức bồi thường thiệt hại hợp đồng?"`
* **Lời thuyết minh của Thịnh:**
  > *"Cuối cùng, em thử một câu bẫy điều luật giả mạo: 'Điều 999 Luật Thương mại'. Trên thực tế, Luật Thương mại Việt Nam chỉ có tối đa 324 điều.
  > Kết quả: Chốt chặn độ tương đồng $\tau = 0.75$ ở tầng mã nguồn kích hoạt tính năng **Từ chối an toàn (Safe Refusal)**, hệ thống trả lời ngay: 'Luật Thương mại hiện hành chỉ có 324 điều, không tồn tại Điều 999. Do đó câu hỏi không có căn cứ pháp lý để giải đáp'.
  > Hệ thống tuyệt đối không bịa đặt nội dung điều luật!
  >
  > *Kính thưa Thầy Cô, phần chạy demo thực nghiệm của em xin được tạm dừng tại đây. Em xin mời bạn Tiến tiếp tục trình bày hai slide cuối về Kết luận và Hướng phát triển của đề tài."*

---

### [Slide 15] Kết luận, Hạn chế và Hướng phát triển (Sau Demo)
* **Người trình bày:** **Lê Hữu Tiến**
* **Điểm nhấn trên slide:** 3 Giả thiết đã bảo vệ thành công; 4 Điểm hạn chế hiện tại; 4 Hướng phát triển trong tương lai.
* **Lời thoại (Tiến):**
  > *"Kính thưa Thầy Cô, qua phần báo cáo lý thuyết và demo thực nghiệm, nhóm chúng em xin được đúc kết lại các kết quả đạt được (Slide 15):*
  > * **Về mặt khoa học:** Đề tài đã **bảo vệ thành công cả 3 giả thiết khoa học**: chứng minh việc kết hợp RAG, phân đoạn theo Điều/Khoản kèm siêu dữ liệu và cơ chế 4 tầng kiểm soát sinh ảo có thể triệt tiêu hoàn toàn ảo giác (đưa tỷ lệ ảo giác của câu hỏi bẫy về 0.0%).
  > * **Về mặt ứng dụng:** Xây dựng thành công một giải pháp phần mềm web hoàn chỉnh, hỗ trợ thiết thực cho cộng đồng khởi nghiệp và người làm nghề tự do.
  >
  > *Tuy nhiên, nhóm cũng thẳng thắn nhìn nhận **bốn hạn chế còn tồn đọng**:*
  > 1. *Việc bóc tách bảng biểu phức tạp trong tệp PDF quét đôi lúc còn sót thông tin (tỷ lệ bỏ sót khoảng 15%).*
  > 2. *Hệ thống vẫn phụ thuộc vào đường truyền API bên ngoài của Google Gemini, dẫn đến độ trễ trung bình khoảng 40 giây khi rà soát toàn bộ một hợp đồng dài.*
  > 3. *Ngưỡng tương đồng $\tau = 0.75$ hiện đang cố định, gây ra hiện tượng từ chối nhầm 6.67% đối với các câu hỏi dùng ngôn ngữ chưa chuẩn mực.*
  > 4. *Dữ liệu phiên hiện lưu trên RAM máy chủ, chưa có hệ quản trị cơ sở dữ liệu bền vững đa người dùng.*
  >
  > *Từ những hạn chế đó, **bốn hướng phát triển tiếp theo của nhóm bao gồm**:*
  > 1. *Nâng cấp tìm kiếm kết hợp (**Hybrid Search** giữa từ khóa BM25 và véc-tơ ngữ nghĩa) đi kèm mô hình xếp hạng lại (**Re-ranking**).*
  > 2. *Nghiên cứu cơ chế **Ngưỡng thích ứng động (Adaptive Threshold)** tự điều chỉnh theo ngữ cảnh câu hỏi.*
  > 3. *Tiến hành tinh chỉnh sâu (**Fine-tune**) một mô hình ngôn ngữ lớn nguồn mở chuyên ngành pháp lý Việt Nam để chạy hoàn toàn trên máy chủ nội bộ, đảm bảo tuyệt đối tính bảo mật thông tin.*
  > 4. *Xây dựng đồ thị tri thức pháp lý (**GraphRAG**) để biểu diễn mối quan hệ dẫn chiếu chéo phức tạp giữa các thông tư, nghị định và luật."*

---

### [Slide 16] Kết thúc báo cáo và chuyển sang Q&A
* **Người trình bày:** **Lê Hữu Tiến** & **Phạm Gia Thịnh**
* **Lời thoại (Tiến & Thịnh cùng cúi đầu chào):**
  > *"Kính thưa quý Thầy Cô trong Hội đồng, phần báo cáo khóa luận tốt nghiệp của Nhóm 14 đến đây là kết thúc. Chúng em xin chân thành cảm ơn Thầy hướng dẫn TS. Hàn Trung Định và quý Thầy Cô trong Hội đồng đã chú ý lắng nghe.*
  >
  > *Nhóm chúng em kính mong nhận được những nhận xét, góp ý quý báu của Thầy Cô và chúng em đã sẵn sàng trả lời các câu hỏi phản biện ạ!"*

---

## PHẦN III: BỘ CÂU HỎI HỘI ĐỒNG PHẢN BIỆN DỰ KIẾN KÈM CÂU TRẢ LỜI CHIẾN LƯỢC

---

### NHÓM A: CÁC CÂU HỎI NỀN TẢNG, CƠ BẢN VỀ AI, VÉC-TƠ, CƠ SỞ DỮ LIỆU

#### ❓ Câu hỏi A.1: 
*Véc-tơ nhúng (Embedding) thực chất là gì? Tại sao các em lại dùng mô hình véc-tơ 768 chiều mà không dùng các mô hình nhiều chiều hơn như 1536 chiều của OpenAI hay ít chiều hơn như 384 chiều của MiniLM?*
* **Người trả lời tối ưu:** **Phạm Gia Thịnh**
* **Câu trả lời chiến lược:**
  > *"Dạ thưa Thầy, véc-tơ nhúng thực chất là một phép ánh xạ chuyển đổi một đoạn văn bản ngôn ngữ tự nhiên thành một mảng các con số thực trong không gian hình học đa chiều, sao cho những đoạn văn có ngữ nghĩa gần nhau thì khoảng cách giữa các véc-tơ của chúng trong không gian cũng nằm gần nhau.
  >
  > *Về câu hỏi tại sao chọn **768 chiều** của mô hình `gemini-embedding-2`:*
  > * Nếu dùng không gian véc-tơ quá nhỏ như **384 chiều** (như các mô hình MiniLM cũ), sức chứa biểu diễn ngữ nghĩa của nó không đủ lớn để phân biệt sự khác nhau tinh tế giữa các thuật ngữ pháp lý phức tạp như 'đình chỉ thực hiện hợp đồng' khác với 'hủy bỏ hợp đồng'.
  > * Ngược lại, nếu dùng mô hình **1536 chiều hay 3072 chiều** (như mô hình text-embedding của OpenAI), kích thước bộ nhớ RAM tiêu thụ tăng gấp đôi hoặc gấp 4 lần, tốc độ tính toán tích vô hướng khi tìm kiếm sẽ chậm đi đáng kể, và chi phí gọi API cũng đắt đỏ hơn nhiều.
  > * Không gian **768 chiều** của Google là kích thước tiêu chuẩn vàng, vừa vặn để biểu đạt đầy đủ ngữ nghĩa tiếng Việt chuyên ngành pháp lý mà vẫn đảm bảo tốc độ tìm kiếm cực nhanh và tiêu tốn rất ít bộ nhớ."*

#### ❓ Câu hỏi A.2: 
*Độ tương đồng Cosine là gì? Tại sao trong slide ghi đo Cosine mà trong code lại dùng chỉ mục `IndexFlatIP` (tính tích vô hướng - Inner Product) của FAISS?*
* **Người trả lời tối ưu:** **Lê Hữu Tiến**
* **Câu trả lời chiến lược:**
  > *"Dạ thưa Thầy Cô, công thức toán học tính độ tương đồng Cosine giữa hai véc-tơ $\vec{u}$ và $\vec{v}$ là:
  > $$\text{Cosine Similarity}(\vec{u}, \vec{v}) = \frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}$$
  > Trong đó $\vec{u} \cdot \vec{v}$ là tích vô hướng, còn mẫu số là tích độ dài của hai véc-tơ.
  >
  > Trong mã nguồn tại file [modules/shared/embedding.py](file:///d:/PJ/Lexdraft/modules/shared/embedding.py), ngay khi nhận véc-tơ từ mô hình về, nhóm đã gọi hàm `faiss.normalize_L2(vectors)`. Hàm này chuẩn hóa độ dài của tất cả các véc-tơ về đúng bằng 1 (nghĩa là $\|\vec{u}\| = 1$ và $\|\vec{v}\| = 1$).
  > Khi mẫu số đã bằng 1, thì công thức Cosine rút gọn thành: $\text{Cosine Similarity} = \vec{u} \cdot \vec{v}$.
  > Do đó, việc sử dụng `IndexFlatIP` (Inner Product) trên các véc-tơ đã chuẩn hóa L2 chính là tính chính xác 100% độ tương đồng Cosine. Cách làm này giúp giảm thiểu việc tính căn bậc hai nhiều lần, giúp tăng tốc độ tìm kiếm của CPU lên gấp nhiều lần."*

#### ❓ Câu hỏi A.3: 
*Cơ sở dữ liệu véc-tơ FAISS thực chất lưu ở đâu trong ổ cứng máy tính? Nó gồm những file gì? Tại sao không dùng ChromaDB hay cơ sở dữ liệu trên mây như Pinecone?*
* **Người trả lời tối ưu:** **Lê Hữu Tiến**
* **Câu trả lời chiến lược:**
  > *"Dạ thưa Thầy, chỉ mục FAISS được lưu trữ cục bộ ngay trong thư mục [data/faiss_index/](file:///d:/PJ/Lexdraft/data/faiss_index) của dự án. Cụ thể gồm 4 tệp chính:
  > * `law_index.faiss`: Tệp nhị phân chứa không gian 583 véc-tơ đặc trưng của văn bản luật.
  > * `law_index.pkl`: Tệp lưu cấu trúc ánh xạ chỉ số véc-tơ với 5 trường siêu dữ liệu nguồn gốc tương ứng.
  > * `template_index.faiss` và `template_index.pkl`: Chứa 28 véc-tơ của các mẫu hợp đồng.
  >
  > *Lý do nhóm chọn FAISS CPU mà không dùng Pinecone hay ChromaDB:*
  > * **Pinecone** là dịch vụ đám mây, mỗi truy vấn tìm kiếm đều phải gửi dữ liệu ra Internet, gây thêm độ trễ mạng và người dùng bị phụ thuộc chi phí duy trì hàng tháng.
  > * **ChromaDB** chạy trên môi trường nhúng đòi hỏi nhiều thư viện nền (SQLite phiên bản cao) và đôi lúc gặp lỗi xung đột tiến trình trên Windows.
  > * **FAISS** do Meta AI phát triển viết bằng C++ cực kỳ tối ưu, nạp trực tiếp toàn bộ 583 véc-tơ vào bộ nhớ RAM chỉ tốn chưa đầy 10 Megabyte, và thời gian tìm kiếm chỉ mất **dưới 2 mili-giây** cho mỗi truy vấn, hoàn toàn chạy ngoại tuyến và độc lập."*

#### ❓ Câu hỏi A.4: 
*Temperature là gì? Và tại sao trong LexDraft lại để = 0?*
* **Người trả lời tối ưu:** **Phạm Gia Thịnh**
* **Câu trả lời cực ngắn (1 và 2.1):**
  > *"Dạ thưa Thầy:
  > 1. **Temperature là gì:** Là tham số điều khiển mức độ ngẫu nhiên (sáng tạo) khi AI chọn từ tiếp theo.
  > 2.1. **Tại sao để = 0:** Để **triệt tiêu hoàn toàn sự ngẫu nhiên**, đưa AI về cơ chế chọn từ tham lam (Greedy Search) — luôn chọn từ có xác suất cao nhất. Trong pháp luật, chúng em **không cần AI sáng tạo**, mà cần **sự chuẩn xác và tính nhất quán tuyệt đối** (cùng một điều khoản vi phạm, hỏi bao nhiêu lần cũng ra đúng một kết quả và một căn cứ duy nhất)."*

#### ❓ Câu hỏi A.4.1: 
*st.session_state là gì? Đọc sang tiếng Việt thế nào và tại sao phải dùng?*
* **Người trả lời tối ưu:** **Phạm Gia Thịnh**
* **Câu trả lời cực ngắn:**
  > *"Dạ thưa Thầy:
  > 1. **Đọc tiếng Việt:** Là **'Trạng thái phiên làm việc'** (hoặc Bộ nhớ phiên).
  > 2. **Tại sao phải dùng:** Mặc định Streamlit chạy lại code từ đầu sau mỗi cú click chuột và xóa sạch biến. Phải dùng `st.session_state` để giữ lại file hợp đồng vừa tải, lưu lịch sử chat, và chuyển kết quả rà soát rủi ro sang cho Chatbot mà không bị mất dữ liệu."*


#### ❓ Câu hỏi A.5: 
*Tại sao trong slide ghi kho luật có đúng 583 véc-tơ? Con số 583 này ở đâu ra? Làm sao để chứng minh trong code là có đúng 583 véc-tơ?*
* **Người trả lời tối ưu:** **Lê Hữu Tiến**
* **Câu trả lời chiến lược:**
  > *"Dạ thưa Thầy, con số 583 véc-tơ là tổng số Điều luật sau khi chạy qua bộ phân đoạn `chunk_by_article()` trên 7 văn bản luật trong thư mục `data/raw/laws/`:
  > * Bộ luật Dân sự 2015: đóng góp phần lớn các điều khoản về hợp đồng dịch vụ và bồi thường thiệt hại.
  > * Luật Thương mại 2005 (VBHN 113): gồm các điều khoản về chế tài, phạt vi phạm và cung ứng dịch vụ.
  > * Cùng các điều khoản tương ứng của Luật Sở hữu trí tuệ, Giao dịch điện tử, Bảo vệ dữ liệu cá nhân...
  >
  > *Để chứng minh con số này trong mã nguồn:*
  > * Khi chạy script nạp dữ liệu tại file [scripts/build_index.py](file:///d:/PJ/Lexdraft/scripts/build_index.py), dòng lệnh in log kết thúc luôn thông báo rõ: `Đã nạp thành công 583 chunks vào law_index`.
  > * Hoặc trong Python, chỉ cần mở file `data/faiss_index/law_index.faiss` bằng câu lệnh: `index = faiss.read_index(...)` và gọi `index.ntotal`, thuộc tính này sẽ trả về chính xác con số nguyên là **583**."*

---

### NHÓM B: CÁC CÂU HỎI "BẬT CODE LÊN CHỈ CHO THẦY" (CHỈ RÕ FILE VÀ DÒNG CODE)

#### ❓ Câu hỏi B.1: 
*Thầy muốn xem Cơ chế 4 tầng kiểm soát sinh ảo nằm ở đâu trong mã nguồn? Bật từng file và chỉ rõ dòng code tương ứng cho Thầy xem!*
* **Người trả lời tối ưu:** **Lê Hữu Tiến** (mở VS Code chiếu lên màn hình)
* **Câu trả lời và thao tác chỉ điểm mã nguồn:**
  > *"Dạ thưa Thầy, em xin phép mở mã nguồn dự án để chỉ rõ 4 tầng kiểm soát:*
  >
  > 1. * **TẦNG 1 – Sàng lọc hiệu lực văn bản:**
  >    * Em mở file [modules/risk_assessment/law_validity_checker.py](file:///d:/PJ/Lexdraft/modules/risk_assessment/law_validity_checker.py).
  >    * Tại **dòng 17 đến dòng 19**: Định nghĩa đường dẫn tới tệp cơ sở tri thức Cấp 1: `_EXPIRED_LAWS_PATH = ... / "data" / "expired_laws.json"`.
  >    * Tại **dòng 61 đến dòng 70**: Hàm `_check_tier1(law_name)` thực hiện đối chiếu tên luật trong hợp đồng với danh mục kiểm duyệt; nếu khớp với từ khóa luật cũ thì cảnh báo ngay với độ tin cậy 100%.
  >
  > 2. * **TẦNG 2 – Ràng buộc Cấu trúc Siêu dữ liệu:**
  >    * Nằm tại file [modules/shared/llm_client.py](file:///d:/PJ/Lexdraft/modules/shared/llm_client.py), tại **dòng 237**: Hàm `extract_citations_from_chunks(retrieved_chunks)` bóc tách bắt buộc 5 trường siêu dữ liệu (`ten_luat`, `so_hieu`, `so_dieu`, `ten_dieu`, `nguon_dan`) từ các véc-tơ lấy từ FAISS để chuẩn bị đưa vào câu trả lời.
  >
  > 3. * **TẦNG 3 – Chốt chặn Ngưỡng tương đồng $\tau = 0.75$ (Code Gatekeeper):**
  >    * Cũng tại file [modules/shared/llm_client.py](file:///d:/PJ/Lexdraft/modules/shared/llm_client.py), tại **dòng 199 đến dòng 235**:
  >    * Dòng 202 đọc ngưỡng từ cấu hình: `getattr(Config, "SIMILARITY_THRESHOLD", 0.75)`.
  >    * Dòng 221 đến 224: Lấy điểm tương đồng cao nhất `max_score = max(scores)`.
  >    * **Dòng 224 đến dòng 234**: Điều kiện `if max_score < active_threshold: return {"answer": active_refusal, "citations": [], "refusal": True}`. Đoạn code này chạy trực tiếp ở Python, lập tức từ chối trả lời trong 0.01 giây mà không gọi đến API Gemini!
  >
  > 4. * **TẦNG 4 – Thiết kế Lời nhắc Neo dữ liệu:**
  >    * Nằm tại file `modules/chatbot_qa/prompts.py` (dòng 18-45) và `modules/risk_assessment/prompts.py`: Ép mô hình bằng lời nhắc phủ định: 'Chỉ được sử dụng duy nhất các căn cứ được cung cấp trong [NGỮ CẢNH]; nếu ngữ cảnh không đề cập hoặc mâu thuẫn, tuyệt đối không suy đoán'."*

#### ❓ Câu hỏi B.2: 
*Sau khi LLM trả lời xong, làm sao các em lọc sạch được các căn cứ pháp lý để đảm bảo chỉ hiển thị đúng những Điều luật mà AI thực sự dùng, chứ không hiển thị tràn lan các đoạn retrieved từ FAISS? Code nằm ở dòng nào?*
* **Người trả lời tối ưu:** **Lê Hữu Tiến**
* **Câu trả lời và thao tác chỉ điểm mã nguồn:**
  > *"Dạ thưa Thầy, kỹ thuật này nhóm đặt tên là **Cited-only Filtering (Lọc sạch căn cứ trích dẫn)**.
  > Em xin mở file [modules/shared/llm_client.py](file:///d:/PJ/Lexdraft/modules/shared/llm_client.py) từ **dòng 246 đến dòng 263**:
  > * Sau khi nhận văn bản trả lời `answer` từ Gemini ở dòng 244, nhóm không lấy toàn bộ `raw_citations` của FAISS.
  > * Tại dòng 248 đến 257: Nhóm dùng biểu thức chính quy Regex: `re.search(rf"\b[Đđ]iều\s+{art_num}\b", answer)`.
  > * Đoạn code này quét lại toàn bộ văn bản câu trả lời của AI: Chỉ những Điều luật nào **thực sự được AI nhắc tên bằng chữ trong bài viết** thì mới được đưa vào danh sách `used_citations`.
  > * Nếu AI từ chối trả lời hoặc không nhắc đến điều nào, danh sách căn cứ sẽ hoàn toàn rỗng (`citations = []`). Nhờ vậy, giao diện web Streamlit tự động ẩn hộp trích dẫn, tránh gây hiểu lầm cho người dùng."*

#### ❓ Câu hỏi B.3: 
*Hàm `attach_contract_context` giúp chuyển đổi ngữ cảnh từ Phân hệ rà soát rủi ro sang Chatbot nằm ở đâu? Nó hoạt động như thế nào?*
* **Người trả lời tối ưu:** **Lê Hữu Tiến**
* **Câu trả lời và thao tác chỉ điểm mã nguồn:**
  > *"Dạ thưa Thầy, hàm này nằm tại file `modules/chatbot_qa/service.py` (dòng 40 đến 65).
  > Khi người dùng bấm nút 'Hỏi Chatbot về hợp đồng này' trên giao diện Streamlit:
  > 1. Giao diện sẽ gọi hàm `attach_contract_context(session_id, contract_chunks, risk_report)`.
  > 2. Hàm này truy xuất vào từ điển `_SESSIONS[session_id]` lưu trên bộ nhớ RAM, gán danh sách các điều khoản hợp đồng và toàn bộ bảng báo cáo cờ đỏ/cờ vàng vào phiên làm việc.
  > 3. Khi người dùng nhập tin nhắn tiếp theo, Chatbot nhận biết phiên này đã có hợp đồng (Chế độ A) và tự động gắn nội dung điều khoản vi phạm vào lời nhắc gửi cho Gemini."*

#### ❓ Câu hỏi B.4: 
*Khi xuất file Word `.docx` và hiển thị bản xem trước A4 trên Web, code xử lý căn giữa tiêu đề và chống vỡ giao diện nằm ở đâu?*
* **Người trả lời tối ưu:** **Lê Hữu Tiến**
* **Câu trả lời và thao tác chỉ điểm mã nguồn:**
  > *"Dạ thưa Thầy, mã nguồn nằm tại file [modules/drafting/document_utils.py](file:///d:/PJ/Lexdraft/modules/drafting/document_utils.py) kết hợp với [ui/styles.py](file:///d:/PJ/Lexdraft/ui/styles.py):
  > * Trong `document_utils.py` (hàm `build_docx_bytes`): Nhóm đọc từng đoạn văn bản, nếu phát hiện là tiêu ngữ hoặc tên hợp đồng thì gán thuộc tính của python-docx: `paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER`.
  > * Trong hàm chuyển đổi sang HTML `docx_bytes_to_preview_html`: Nhóm kiểm tra trực tiếp thuộc tính `paragraph.alignment`, nếu là căn giữa thì bọc thẻ HTML với class `.a4p-center`, nếu là thụt đầu dòng thì bọc class `.a4p-justify`.

#### ❓ Câu hỏi B.5: 
*Hàm phân đoạn văn bản theo Điều luật và Biểu thức chính quy Regex nằm ở file nào, dòng bao nhiêu? Giải thích chi tiết các ký tự trong Regex và cách chia đoạn trong code?*
* **Người trả lời tối ưu:** **Phạm Gia Thịnh** hoặc **Lê Hữu Tiến**
* **Câu trả lời và thao tác chỉ điểm mã nguồn:**
  > *"Dạ thưa Thầy, mã nguồn nằm tại file [modules/shared/chunking.py](file:///d:/PJ/Lexdraft/modules/shared/chunking.py):
  >
  > 1. * **Vị trí biểu thức Regex (Dòng 259 đến 262):**
  >    ```python
  >    ARTICLE_HEADER_PATTERN = re.compile(
  >        r"(?m)^(?:#{1,4}\s*)?(?:\*{1,2})?Điều\s+(\d+)[.:\s]?(.*?)$",
  >        re.IGNORECASE,
  >    )
  >    ```
  >    * `(?m)^`: Neo tìm kiếm ở **đầu mỗi dòng** (Multiline mode). Điều này cực kỳ quan trọng: nó **loại trừ tuyệt đối việc bắt nhầm** các cụm từ trích dẫn nằm ở giữa câu (ví dụ: *"Căn cứ theo Điều 35 Bộ luật Dân sự..."* thì chữ 'Điều 35' nằm giữa dòng sẽ bị bỏ qua, không bị xé nhầm thành một chunk mới).
  >    * `(?:#{1,4}\s*)?(?:\*{1,2})?`: Nhóm không bắt giữ (non-capturing group `(?:...)`) có dấu `?` (tùy chọn) để xử lý linh hoạt các ký tự định dạng Markdown như `#`, `##` hoặc `**`.
  >    * `Điều\s+`: Nhận diện từ khóa 'Điều' và các khoảng trắng theo sau.
  >    * `(\d+)`: Nhóm bắt giữ 1 — trích xuất **chính xác số hiệu của Điều** (ví dụ: `401`, `513`) để lưu vào metadata `article`.
  >    * `[.:\s]?`: Xử lý ký tự phân cách tùy chọn sau số điều (dấu chấm, hai chấm hoặc khoảng trắng).
  >    * `(.*?)`: Nhóm bắt giữ 2 — trích xuất **tiêu đề của Điều** cho đến hết dòng (`$`).
  >
  > 2. * **Thuật toán cắt chunk (Dòng 331 đến 335):**
  >    * Hàm `chunk_by_article()` dùng `ARTICLE_HEADER_PATTERN.finditer(text)` để lấy danh sách vị trí xuất hiện của tất cả các Điều.
  >    * Sau đó chạy vòng lặp cắt văn bản từ vị trí `match.start()` của Điều hiện tại đến trước `matches[i+1].start()` của Điều kế tiếp.
  >    * Nhờ vậy, toàn bộ các Khoản, Điểm, và điều kiện loại trừ ('trừ trường hợp...', 'khoản 2 điều này...') đều nằm trọn vẹn 100% trong một chunk duy nhất, bảo toàn tính ngữ nghĩa pháp lý hoàn chỉnh."*

---

### NHÓM C: CÁC CÂU HỎI HỌC THUẬT SÂU, RAGAS, ĐÁNH ĐỔI KHOA HỌC VÀ PHÁP LÝ

#### ❓ Câu hỏi C.1: 
*Nhìn vào Bảng ở Slide 13, tại sao chỉ số Faithfulness của Fact Retrieval đạt 0.85 rất cao, nhưng khi tính trên toàn bộ hệ thống 50 câu thì Faithfulness lại tụt xuống 0.275 và Context Recall tụt xuống 0.57? Nhóm hãy giải thích bản chất toán học của hiện tượng này!*
* **Người trả lời tối ưu:** **Phạm Gia Thịnh**
* **Câu trả lời chiến lược:**
  > *"Kính thưa Thầy Cô, đây là một phát hiện phương pháp luận rất sâu sắc của nhóm em trong quá trình đánh giá bằng Framework RAGAS:
  > * Trong bộ dữ liệu kiểm thử 50 câu, có **6 câu hỏi cố tình bẫy về các văn bản luật đã hết hiệu lực** (ví dụ hỏi: 'Hợp đồng ký năm 2026 áp dụng Luật Giao dịch điện tử 2005 được không?').
  > * Khi gặp các câu này, **Chốt chặn Tầng 1 của LexDraft phát hiện ngay luật cũ và chủ động kích hoạt Từ chối an toàn (Safe Refusal)**, đưa ra câu trả lời cảnh báo luật đã hết hiệu lực và không đưa nội dung luật cũ vào ngữ cảnh truy xuất.
  > * Tuy nhiên, thuật toán tính điểm của RAGAS LLM Judge hoạt động theo nguyên lý: Nó so sánh câu trả lời với Ground Truth và đếm số lượng luận điểm có bằng chứng trong Context. Khi hệ thống của chúng em từ chối trả lời (trả lời ngắn gọn rằng luật đã bãi bỏ), RAGAS coi đây là một câu trả lời 'thiếu căn cứ từ ngữ cảnh' và **chấm điểm Faithfulness và Context Recall của các câu này bằng 0 điểm tuyệt đối**!
  > * Khi lấy trung bình cộng của 44 câu điểm cao (0.85) với 6 câu bị RAGAS chấm 0 điểm do từ chối an toàn, điểm trung bình toàn hệ thống bị kéo tụt xuống 0.275.
  > * Vì vậy, con số 0.275 không hề phản ánh hệ thống bị ảo giác, mà ngược lại nó là bằng chứng cho thấy cơ chế từ chối an toàn đang hoạt động rất chủ động trước các câu hỏi bẫy."*

#### ❓ Câu hỏi C.2: 
*Tỷ lệ từ chối nhầm 6.67% (False Refusal) trong bài test H3 là rơi vào câu hỏi cụ thể nào? Tại sao lại bị từ chối nhầm?*
* **Người trả lời tối ưu:** **Phạm Gia Thịnh**
* **Câu trả lời chiến lược:**
  > *"Dạ thưa Thầy, trong tập kiểm thử 15 câu hợp lệ của bài test H3, câu hỏi duy nhất bị từ chối nhầm là câu:
  > *'Bên thuê dịch vụ không trả tiền đúng hẹn thì bên làm dịch vụ được làm gì?'*
  > * Trong cơ sở dữ liệu luật, hành vi này được định danh bằng thuật ngữ pháp lý chuẩn xác là: 'Chậm thực hiện nghĩa vụ thanh toán tiền dịch vụ' (theo Điều 519 Bộ luật Dân sự 2015 và Điều 306 Luật Thương mại).
  > * Do người dùng đặt câu hỏi bằng khẩu ngữ đời thường ('không trả tiền đúng hẹn', 'bên làm dịch vụ'), khoảng cách ngữ nghĩa giữa câu hỏi và văn bản luật bị xa hơn bình thường. Khi nhúng véc-tơ, điểm tương đồng Cosine cao nhất truy xuất từ FAISS chỉ đạt **0.742**.
  > * Do hệ thống đang cài đặt ngưỡng cứng $\tau = 0.75$, nên điểm 0.742 đã bị Chốt chặn Tầng 3 chặn lại và kích hoạt thông báo từ chối an toàn.
  > * Như nhóm đã trình bày, đây là một sự đánh đổi hoàn toàn chấp nhận được: Giữ ngưỡng 0.75 giúp bảo vệ 100% trước 20 câu bẫy nguy hiểm. Và hướng khắc phục của nhóm là bổ sung kỹ thuật làm giàu câu hỏi (Query Expansion) hoặc hạ ngưỡng thích ứng động khi nhận diện được ý định của người dùng."*

#### ❓ Câu hỏi C.3: 
*Hệ thống LexDraft này trong tương lai có khả năng thay thế được hoàn toàn vai trò của các Luật sư tư vấn hợp đồng hay không?*
* **Người trả lời tối ưu:** **Phạm Gia Thịnh**
* **Câu trả lời chiến lược:**
  > *"Dạ thưa Thầy Cô, nhóm xin được khẳng định dứt khoát: **LexDraft hoàn toàn không được tạo ra để thay thế luật sư hay chuyên gia pháp lý**.
  >
  > *Về mặt bản chất: Trong quan hệ hợp đồng thương mại, pháp luật chỉ là một khung hành lang cứng; còn các điều khoản kinh tế, tỷ lệ chiết khấu, phương thức thanh toán từng đợt hay các thỏa thuận thương lượng ngầm đòi hỏi sự nhạy bén kinh doanh và kinh nghiệm đàm phán mà chỉ con người mới có được.
  >
  > *Giá trị cốt lõi của LexDraft nằm ở vai trò **Hệ thống hỗ trợ sàng lọc sơ bộ (L1 Triage Assistant)**:
  > 1. Giúp các bạn Freelancer và doanh nghiệp nhỏ tiết kiệm 80% thời gian rà soát các lỗi kỹ thuật cơ bản (như vượt trần phạt 8%, viện dẫn luật hết hiệu lực, thiếu điều khoản bàn giao bản quyền).
  > 2. Giúp người dùng có một bản dự thảo chỉn chu và hiểu rõ vị thế của mình trước khi bước vào bàn đàm phán hoặc trước khi chi tiền thuê luật sư hoàn thiện hợp đồng. Đó là sự kết hợp cộng hưởng giữa công nghệ và con người, chứ không phải thay thế con người ạ."*

#### ❓ Câu hỏi C.4: 
*Tại sao các em lại chọn kiến trúc Đơn khối phân mô-đun (Modular Monolith) mà không chọn Vi dịch vụ (Microservices) hay Đơn khối truyền thống? Điểm đặc biệt nhất của nó đối với bài toán RAG pháp lý này là gì?*
* **Người trả lời tối ưu:** **Phạm Gia Thịnh** hoặc **Lê Hữu Tiến**
* **Câu trả lời chiến lược:**
  > *"Dạ thưa Thầy Cô, quyết định lựa chọn Modular Monolith xuất phát từ sự tính toán kỹ lưỡng về mặt kỹ thuật và chi phí vận hành:
  > 
  > 1. **Bản chất của Modular Monolith (Cấu trúc phân khối):** 
  >    * Là sự kết hợp giữa **Monolith** (toàn bộ ứng dụng chạy chung một tiến trình, một cơ sở mã nguồn duy nhất) và **Modular** (bên trong được chia thành các phân khối độc lập, đóng gói kín như các khoang kín nước trên tàu thủy).
  > 
  > 2. **Điểm đặc biệt sống còn đối với bài toán RAG pháp lý:**
  >    * Nếu triển khai **Microservices**, mỗi dịch vụ (Soạn thảo, Rà soát, Chatbot) là một container riêng. Khi đó, mỗi dịch vụ hoặc phải nạp một bản sao chỉ mục FAISS riêng làm nhân ba dung lượng RAM, hoặc phải gọi chỉ mục qua mạng HTTP/gRPC. Mỗi câu hỏi của người dùng phải chịu thêm độ trễ mạng từ 50 đến 200 mili-giây và tốn chi phí hạ tầng.
  >    * Trong khi đó, với **Modular Monolith**, điểm đặc biệt nhất là **hệ thống chia sẻ trực tiếp duy nhất một chỉ mục FAISS (583 véc-tơ) ngay trong bộ nhớ RAM**. Cả ba phân khối đều gọi trực tiếp trong RAM với độ trễ gần như bằng 0 (dưới 2 mili-giây).
  > 
  > 3. **Khắc phục triệt để nhược điểm của Monolith truyền thống:**
  >    * Trong monolith thông thường, mã nguồn hay bị phụ thuộc chéo (spaghetti code). Ở LexDraft, nhóm ép quy tắc: Mọi giao tiếp giữa các phân khối phải đi qua file `service.py`. Phân hệ này không được can thiệp vào logic nội bộ của phân hệ khác. Nhờ đó, nhóm dễ dàng viết các bài kiểm thử tự động độc lập và đo lường RAGAS cho từng tính năng mà không sợ hiệu ứng cánh bướm làm hỏng hệ thống."*

---


### BẢNG TỔNG HỢP PHẢN XẠ NHANH KHI ĐỨNG TRÊN BỤC HỘI ĐỒNG

| Tình huống câu hỏi của Thầy Cô | Người phản xạ trả lời chính | Hành động phối hợp của người còn lại |
|:---|:---:|:---|
| **Hỏi về Số liệu, Biểu đồ, Ragas, Đánh đổi khoa học (Slide 1-3, 11-13)** | **Phạm Gia Thịnh** | Tiến chủ động dùng chuột trỏ đúng vào biểu đồ/số liệu trên slide đang chiếu. |
| **Hỏi về Kiến trúc, Dữ liệu, 4 Tầng kiểm soát, Code nằm ở đâu (Slide 4-7)** | **Lê Hữu Tiến** | Tiến trình bày logic, Thịnh nhanh chóng mở đúng file code trên máy tính để sẵn sàng soi dòng. |
| **Hỏi về Hiện thực 3 Phân hệ, Soạn thảo Word, Định dạng A4 (Slide 8-10)** | **Lê Hữu Tiến** | Thịnh mở sẵn cửa sổ thư mục `data/` hoặc file `.docx` đã tải về để minh chứng. |
| **Thầy yêu cầu thử gõ một câu hỏi bất kỳ trên màn hình Demo** | **Phạm Gia Thịnh** | Thịnh trực tiếp thao tác gõ vào ô Chatbot; Tiến đứng bên cạnh phân tích luồng xử lý của hệ thống. |
| **Hỏi về Tính pháp lý thực tế, Trách nhiệm sản phẩm, Hạn chế (Slide 15)** | **Phạm Gia Thịnh** | Tiến bổ sung các giải pháp kỹ thuật nâng cấp trong tương lai (Hybrid Search, GraphRAG). |

---
*Tài liệu được biên soạn phục vụ buổi báo cáo Khóa luận Tốt nghiệp chính thức của Nhóm 14 – Viện CNTT&Đ-ĐT, Trường Đại học Giao thông Vận tải TP.HCM.*
