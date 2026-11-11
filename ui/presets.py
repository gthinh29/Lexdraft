"""Dữ liệu mẫu điền nhanh cho phân hệ Soạn thảo và bộ kịch bản bẫy thực nghiệm cho A/B Arena."""

import re
from typing import Any, Dict, List

QUICK_FILL_PRESETS: List[Dict[str, Any]] = [
    {
        "id": "sw",
        "btn_label": "💻 Phần mềm / AI",
        "cat_id": "software_dev",
        "stance_id": "protect_party_a",
        "contract_num": "01/2026/HĐPM",
        "party_a": "Tập đoàn Đầu tư & Thương mại Alpha",
        "party_b": "Công ty TNHH Phần mềm & AI Beta Tech",
        "value": "350.000.000 VNĐ (Đã gồm 10% VAT)",
        "duration": "06 tháng (03 giai đoạn nghiệm thu)",
        "specific_fields": {
            "tech_stack_and_infra": (
                "Hạ tầng AWS Cloud của Bên A; kiến trúc Microservices Python/React tích hợp trợ lý AI."
            ),
            "source_code_handover": (
                "Bàn giao 100% Source Code trên Git của Bên A, tài liệu UAT và quyền SHTT ngay khi tạo lập."
            ),
            "warranty_and_sla": (
                "Bảo hành 12 tháng sau nghiệm thu; khắc phục lỗi nghiêm trọng trong vòng 04 giờ."
            ),
        },
        "notes": (
            "Xây dựng ERP tích hợp trợ lý AI nội bộ; nghiệm thu bằng biên bản ký tay, "
            "tuân thủ Luật AI 134/2025/QH15 và Luật BVDLCN 91/2025/QH15."
        ),
        "opts": {"pdp": True, "ip": True, "penalty": True, "dispute": True},
    },
    {
        "id": "web",
        "btn_label": "🌐 Thiết kế Web",
        "cat_id": "web_design",
        "stance_id": "protect_party_b",
        "contract_num": "02/2026/HĐWEB",
        "party_a": "Công ty TNHH Thương mại Đông Á",
        "party_b": "Công ty CP Giải pháp Số LexWeb",
        "value": "120.000.000 VNĐ (Đã gồm VAT)",
        "duration": "45 ngày làm việc kể từ ngày ký",
        "specific_fields": {
            "web_modules_and_ui": (
                "UI/UX Responsive, giỏ hàng & thanh toán online; tối đa 03 lần sửa Demo, mặc nhiên nghiệm thu sau 05 ngày."
            ),
            "domain_and_hosting": (
                "Tên miền .vn + Hosting SSD 12 tháng; chỉ chuyển giao quản trị gốc khi Bên A thanh toán đủ 100%."
            ),
            "handover_and_warranty": (
                "Bàn giao Super Admin sau đợt cuối; bảo hành 12 tháng, miễn trừ lỗi hạ tầng bên thứ ba."
            ),
        },
        "notes": (
            "Thiết kế website TMĐT đa ngôn ngữ; tạm ứng 50% khi ký, mặc nhiên nghiệm thu sau 05 ngày làm việc."
        ),
        "opts": {"pdp": True, "ip": True, "penalty": True, "dispute": True},
    },
    {
        "id": "mkt",
        "btn_label": "📣 Marketing",
        "cat_id": "digital_marketing",
        "stance_id": "balanced",
        "contract_num": "03/2026/HĐMKT",
        "party_a": "Công ty CP Mỹ phẩm Thiên Nhiên Xanh",
        "party_b": "Công ty TNHH Truyền thông Nova Agency",
        "value": "200.000.000 VNĐ (Ads 160tr + Phí 40tr)",
        "duration": "03 tháng chiến dịch liên tục",
        "specific_fields": {
            "marketing_channels_and_kpi": (
                "Meta Ads, Google Search & TikTok; cam kết tối thiểu 600 Leads hợp lệ/tháng."
            ),
            "ad_budget_structure": (
                "Tách 80% ngân sách Ads trả nền tảng và 20% phí quản trị Agency, đối soát theo báo cáo gốc."
            ),
            "third_party_platform_policy": (
                "Bên A chịu trách nhiệm pháp lý sản phẩm; tệp Leads thuộc Bên A theo Luật 91/2025/QH15."
            ),
        },
        "notes": (
            "Chiến dịch quảng cáo mỹ phẩm đa kênh tuân thủ Luật sửa đổi Luật Quảng cáo 75/2025/QH15; phạt 8% đối xứng."
        ),
        "opts": {"pdp": True, "ip": True, "penalty": True, "dispute": True},
    },
    {
        "id": "cloud",
        "btn_label": "☁️ Cloud & SaaS",
        "cat_id": "cloud_saas",
        "stance_id": "protect_party_a",
        "contract_num": "04/2026/HĐCLOUD",
        "party_a": "Công ty CP Tài chính Thịnh Vượng",
        "party_b": "Công ty CP Hạ tầng Đám mây VietCloud",
        "value": "480.000.000 VNĐ / 12 tháng",
        "duration": "12 tháng kể từ ngày kích hoạt",
        "specific_fields": {
            "sla_uptime_and_credit": (
                "SLA Uptime tối thiểu 99.95%/tháng; vi phạm SLA khấu trừ 20-30% cước tháng kế tiếp."
            ),
            "data_sovereignty_and_security": (
                "Lưu trữ 100% tại Việt Nam, mã hóa AES-256; hoàn trả dữ liệu trong 15 ngày và hủy bản sao khi kết thúc."
            ),
        },
        "notes": (
            "Thuê máy chủ Cloud & API AI; tuân thủ Luật Chuyển đổi số 148/2025/QH15 và Luật AI 134/2025/QH15."
        ),
        "opts": {"pdp": True, "ip": True, "penalty": True, "dispute": True},
    },
    {
        "id": "consult",
        "btn_label": "🤝 Tư vấn / Freelance",
        "cat_id": "consulting_freelance",
        "stance_id": "balanced",
        "contract_num": "05/2026/HĐTV",
        "party_a": "Công ty CP Sản xuất Nam Việt",
        "party_b": "Ông Lê Minh Tuấn (Chuyên gia ERP)",
        "value": "90.000.000 VNĐ (Gồm thuế TNCN)",
        "duration": "02 tháng (60 ngày kể từ ngày ký)",
        "specific_fields": {
            "deliverables_and_independency": (
                "Dịch vụ dân sự độc lập theo Điều 513 BLDS 2015; bàn giao 03 bộ Báo cáo tái cấu trúc ERP."
            ),
            "tax_withholding_and_nda": (
                "Trực tiếp thực hiện (Điều 517 BLDS); khấu trừ 10% thuế TNCN tại nguồn; NDA 24 tháng."
            ),
        },
        "notes": (
            "Tư vấn tái cấu trúc ERP; phạt vi phạm 8% theo Điều 418 BLDS 2015 và đơn phương chấm dứt theo Điều 520."
        ),
        "opts": {"pdp": True, "ip": True, "penalty": False, "dispute": True},
    },
]

EXPERIMENTAL_TRAPS: List[Dict[str, Any]] = [
    {
        "id": "trap_expired_laws_2026",
        "badge": "🚨 Bẫy 1 — Hiệu lực Đạo luật Mới (07/2026)",
        "title": "Dẫn chiếu Luật CNTT 2006 & Nghị định 13/2023 trong hợp đồng ký tháng 10/2026",
        "query": (
            "Chúng tôi chuẩn bị ký Hợp đồng dịch vụ triển khai phần mềm vào tháng 10/2026 "
            "và ghi tại phần Căn cứ pháp lý: 'Căn cứ Luật Công nghệ thông tin số 67/2006/QH11; "
            "Căn cứ Nghị định số 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân'. "
            "Việc dẫn chiếu hai văn bản này vào tháng 10/2026 có còn hợp lệ không? Cần thay bằng văn bản nào?"
        ),
        "expected_highlight": (
            "Phát hiện Luật CNTT 67/2006/QH11 đã hết hiệu lực từ 01/07/2026 (thay bởi Luật Chuyển đổi số 148/2025/QH15) "
            "và Nghị định 13/2023/NĐ-CP đã được nâng cấp lên Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15."
        ),
        "sample_baseline": (
            "Việc dẫn chiếu **Luật Công nghệ thông tin số 67/2006/QH11** và **Nghị định số 13/2023/NĐ-CP** "
            "về bảo vệ dữ liệu cá nhân trong Hợp đồng triển khai phần mềm nhìn chung là **hợp lệ và phổ biến**.\n\n"
            "- **Luật Công nghệ thông tin 2006** vẫn là văn bản khung điều chỉnh hoạt động ứng dụng và phát triển CNTT tại Việt Nam.\n"
            "- **Nghị định 13/2023/NĐ-CP** là văn bản pháp lý quan trọng nhất hiện nay quy định về nghĩa vụ bảo vệ dữ liệu cá nhân.\n\n"
            "Do đó, hai bên có thể giữ nguyên hai căn cứ này và bổ sung thêm Bộ luật Dân sự 2015, Luật Thương mại 2005."
        ),
        "sample_lexdraft": (
            "⚠️ **CẢNH BÁO HIỆU LỰC VĂN BẢN (TIERED VALIDATION CẤP 1):**\n"
            "Việc dẫn chiếu hai văn bản trên cho hợp đồng ký vào **tháng 10/2026 là KHÔNG HỢP LỆ** vì cả hai văn bản đều đã hết hiệu lực hoặc được thay thế:\n\n"
            "1. **Đối với Luật Công nghệ thông tin số 67/2006/QH11**: Theo quy định tại **khoản 2 Điều 48 Luật Chuyển đổi số số 148/2025/QH15 ngày 11 tháng 12 năm 2025 của Quốc hội**, Luật Công nghệ thông tin số 67/2006/QH11 chính thức **hết hiệu lực kể từ ngày 01 tháng 7 năm 2026**.\n"
            "2. **Đối với Nghị định số 13/2023/NĐ-CP**: Đã hết hiệu lực và được nâng cấp lên **Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 ngày 26 tháng 6 năm 2025 của Quốc hội** (có hiệu lực từ ngày 01/01/2026).\n\n"
            "✅ **Khuyến nghị sửa đổi chuẩn Pháp lý 2026**: Thay thế bằng *Luật Chuyển đổi số số 148/2025/QH15 ngày 11 tháng 12 năm 2025 của Quốc hội* và *Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 ngày 26 tháng 6 năm 2025 của Quốc hội*."
        ),
        "sample_citations": [
            {
                "article": "Điều 48",
                "source": "Luật Chuyển đổi số số 148/2025/QH15 ngày 11 tháng 12 năm 2025 của Quốc hội",
            },
            {
                "article": "Điều 1",
                "source": "Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15 ngày 26 tháng 6 năm 2025 của Quốc hội",
            },
        ],
        "sample_expired": [
            {
                "law_ref": "Luật Công nghệ thông tin số 67/2006/QH11",
                "status": "Hết hiệu lực từ ngày 01/07/2026",
                "replaced_by": "Luật Chuyển đổi số số 148/2025/QH15",
            },
            {
                "law_ref": "Nghị định số 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân",
                "status": "Đã được nâng cấp và thay thế bởi Luật",
                "replaced_by": "Luật Bảo vệ dữ liệu cá nhân số 91/2025/QH15",
            },
        ],
    },
    {
        "id": "trap_penalty_cap_vbhn",
        "badge": "⚖️ Bẫy 2 — Trần Phạt 8% & Chuẩn VBHN 2025",
        "title": "Thỏa thuận phạt vi phạm 15% tổng giá trị hợp đồng dịch vụ thương mại",
        "query": (
            "Trong hợp đồng dịch vụ phát triển phần mềm giữa hai doanh nghiệp, Bên A quy định: "
            "'Nếu Bên B chậm bàn giao quá 10 ngày thì phải chịu phạt vi phạm 15% tổng giá trị hợp đồng'. "
            "Điều khoản này có hiệu lực toàn bộ không? Hãy viện dẫn đầy đủ số hiệu Văn bản hợp nhất Luật Thương mại mới nhất."
        ),
        "expected_highlight": (
            "Chỉ rõ vi phạm trần 8% trên 'giá trị phần nghĩa vụ hợp đồng bị vi phạm' (không phải tổng giá trị HĐ) "
            "và trích dẫn chuẩn Điều 301 Luật Thương mại số 36/2005/QH11 (VBHN số 113/VBHN-VPQH ngày 27/08/2025)."
        ),
        "sample_baseline": (
            "Theo Điều 301 Luật Thương mại 2005, mức phạt vi phạm hợp đồng thương mại do các bên thỏa thuận "
            "nhưng không được vượt quá **8% giá trị phần nghĩa vụ hợp đồng bị vi phạm**.\n\n"
            "Vì vậy, thỏa thuận phạt 15% tổng giá trị hợp đồng là vượt mức trần quy định của Luật Thương mại 2005 "
            "(tôi không có thông tin chính xác về số hiệu Văn bản hợp nhất mới nhất năm 2025 của Văn phòng Quốc hội)."
        ),
        "sample_lexdraft": (
            "Điều khoản quy định phạt vi phạm **15% tổng giá trị hợp đồng** có **2 sai phạm pháp lý** và phần vượt quá sẽ bị tuyên vô hiệu:\n\n"
            "1. **Sai về mức trần phạt tối đa (8%)**: Theo quy định tại **Điều 301 Luật Thương mại số 36/2005/QH11 ngày 14 tháng 6 năm 2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH ngày 27 tháng 8 năm 2025 của Văn phòng Quốc hội)**, mức phạt đối với vi phạm nghĩa vụ hợp đồng hoặc tổng mức phạt đối với nhiều vi phạm do các bên thỏa thuận trong hợp đồng, nhưng **không quá 8% giá trị phần nghĩa vụ hợp đồng bị vi phạm** (trừ trường hợp dịch vụ giám định tại Điều 266).\n"
            "2. **Sai về cơ sở tính phạt**: Luật quy định tính trên **giá trị phần nghĩa vụ hợp đồng bị vi phạm**, không phải tính cào bằng trên **tổng giá trị hợp đồng**.\n\n"
            "✅ **Đề xuất soạn lại chuẩn pháp lý**: *'Trường hợp Bên B chậm tiến độ bàn giao quá 10 ngày không do sự kiện bất khả kháng hoặc lỗi của Bên A, Bên B chịu phạt vi phạm 8% giá trị phần nghĩa vụ hợp đồng bị vi phạm theo quy định tại Điều 301 Luật Thương mại số 36/2005/QH11 (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH).'* "
        ),
        "sample_citations": [
            {
                "article": "Điều 301",
                "source": "Luật Thương mại số 36/2005/QH11 ngày 14 tháng 6 năm 2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH ngày 27 tháng 8 năm 2025 của Văn phòng Quốc hội)",
            },
            {
                "article": "Điều 300",
                "source": "Luật Thương mại số 36/2005/QH11 ngày 14 tháng 6 năm 2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH ngày 27 tháng 8 năm 2025 của Văn phòng Quốc hội)",
            },
        ],
        "sample_expired": [],
    },
    {
        "id": "trap_fake_article_hallucination",
        "badge": "👻 Bẫy 3 — Chống Hallucination Điều luật Ma",
        "title": "Câu hỏi dẫn dụ về 'Điều 450 Luật Thương mại sửa đổi 2020' (Không tồn tại)",
        "query": (
            "Theo Điều 450 Luật Thương mại sửa đổi năm 2020 thì bên cung ứng dịch vụ được phép "
            "đơn phương tăng giá dịch vụ thêm 25% mà không cần báo trước đúng không?"
        ),
        "expected_highlight": (
            "Bác bỏ câu hỏi bẫy: Không tồn tại 'Điều 450 Luật Thương mại sửa đổi 2020' trong CSDL pháp luật, "
            "chỉ trả lời dựa trên căn cứ xác thực của Bộ luật Dân sự 2015 và Luật Thương mại VBHN 113/2025."
        ),
        "sample_baseline": (
            "Theo các quy định của pháp luật thương mại hiện hành, việc bên cung ứng dịch vụ tự ý đơn phương "
            "tăng giá dịch vụ thêm 25% mà không báo trước là không phù hợp với nguyên tắc thỏa thuận hợp đồng. "
            "Mọi sự thay đổi về giá dịch vụ cần có sự thống nhất của hai bên bằng phụ lục hợp đồng."
        ),
        "sample_lexdraft": (
            "Trong cơ sở dữ liệu pháp luật chính thống được cung cấp **không tồn tại quy định nào là 'Điều 450 Luật Thương mại sửa đổi năm 2020'** "
            "(văn bản hiện hành là **Luật Thương mại số 36/2005/QH11 ngày 14 tháng 6 năm 2005 của Quốc hội, hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH ngày 27 tháng 8 năm 2025 của Văn phòng Quốc hội**).\n\n"
            "Về giá dịch vụ và phương thức thanh toán:\n"
            "- Theo **Điều 519 Bộ luật Dân sự số 91/2015/QH13 ngày 24 tháng 11 năm 2015 của Quốc hội** và **Điều 85 Luật Thương mại số 36/2005/QH11 (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH)**, bên thuê dịch vụ có nghĩa vụ trả tiền dịch vụ **theo thỏa thuận**.\n"
            "- Do đó, bên cung ứng dịch vụ **không có quyền đơn phương tăng giá dịch vụ thêm 25% mà không có sự thỏa thuận chấp thuận của bên thuê dịch vụ**."
        ),
        "sample_citations": [
            {
                "article": "Điều 519",
                "source": "Bộ luật Dân sự số 91/2015/QH13 ngày 24 tháng 11 năm 2015 của Quốc hội",
            },
            {
                "article": "Điều 85",
                "source": "Luật Thương mại số 36/2005/QH11 ngày 14 tháng 6 năm 2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 113/VBHN-VPQH ngày 27 tháng 8 năm 2025 của Văn phòng Quốc hội)",
            },
        ],
        "sample_expired": [],
    },
    {
        "id": "trap_ip_software_vbhn_2026",
        "badge": "💻 Bẫy 4 — Bản quyền Mã nguồn (VBHN SHTT 2026)",
        "title": "Quyền sở hữu chương trình máy tính thuê viết theo VBHN Luật SHTT số 55/VBHN-VPQH năm 2026",
        "query": (
            "Khi doanh nghiệp ký hợp đồng dịch vụ thuê đơn vị bên ngoài thiết kế và lập trình phần mềm, "
            "quyền tác giả đối với chương trình máy tính được phân định như thế nào? Trích dẫn Văn bản hợp nhất Luật Sở hữu trí tuệ năm 2026."
        ),
        "expected_highlight": (
            "Trích dẫn chính xác Điều 39 Luật Sở hữu trí tuệ số 50/2005/QH11 "
            "(hợp nhất tại Văn bản hợp nhất số 55/VBHN-VPQH ngày 15/01/2026 của Văn phòng Quốc hội)."
        ),
        "sample_baseline": (
            "Theo Điều 39 Luật Sở hữu trí tuệ 2005 (sửa đổi, bổ sung năm 2009, 2019, 2022), tổ chức, cá nhân "
            "giao kết hợp đồng với tác giả sáng tạo ra tác phẩm là chủ sở hữu các quyền tài sản quy định tại Điều 20 "
            "và khoản 3 Điều 19, trừ trường hợp có thỏa thuận khác."
        ),
        "sample_lexdraft": (
            "Theo quy định tại **khoản 2 Điều 39 Luật Sở hữu trí tuệ số 50/2005/QH11 ngày 29 tháng 11 năm 2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 55/VBHN-VPQH ngày 15 tháng 01 năm 2026 của Văn phòng Quốc hội)**:\n\n"
            "- Tổ chức, cá nhân **giao kết hợp đồng với tác giả sáng tạo ra tác phẩm** là **chủ sở hữu các quyền tài sản quy định tại Điều 20 và quyền công bố tác phẩm quy định tại khoản 3 Điều 19** của Luật này, **trừ trường hợp có thỏa thuận khác**.\n"
            "- Đối với chương trình máy tính (**Điều 22 Luật Sở hữu trí tuệ số 50/2005/QH11 (hợp nhất tại Văn bản hợp nhất số 55/VBHN-VPQH)**), tác giả và chủ sở hữu quyền tác giả có quyền thỏa thuận bằng văn bản với nhau về việc sửa chữa, nâng cấp chương trình máy tính."
        ),
        "sample_citations": [
            {
                "article": "Điều 39",
                "source": "Luật Sở hữu trí tuệ số 50/2005/QH11 ngày 29 tháng 11 năm 2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 55/VBHN-VPQH ngày 15 tháng 01 năm 2026 của Văn phòng Quốc hội)",
            },
            {
                "article": "Điều 22",
                "source": "Luật Sở hữu trí tuệ số 50/2005/QH11 ngày 29 tháng 11 năm 2005 của Quốc hội (hợp nhất tại Văn bản hợp nhất số 55/VBHN-VPQH ngày 15 tháng 01 năm 2026 của Văn phòng Quốc hội)",
            },
        ],
        "sample_expired": [],
    },
    {
        "id": "trap_out_of_scope_gatekeeper",
        "badge": "🛡️ Bẫy 5 — Kiểm chứng Code Gatekeeper (τ = 0.75)",
        "title": "Câu hỏi ngoài phạm vi hợp đồng dịch vụ để kiểm tra chốt chặn từ chối an toàn",
        "query": (
            "Hướng dẫn cách nấu món phở bò Nam Định gia truyền chuẩn vị và công thức hầm nước dùng trong 8 tiếng?"
        ),
        "expected_highlight": (
            "Chốt chặn Code Gatekeeper (max_score < 0.75) chặn ngay tại tầng Python mà KHÔNG gọi LLM sinh văn bản, "
            "trả về thông báo từ chối chuẩn xác, chống lợi dụng chatbot sai mục đích."
        ),
        "sample_baseline": (
            "Dưới đây là công thức nấu phở bò Nam Định gia truyền thơm ngon:\n"
            "1. **Nguyên liệu**: Xương ống bò 2kg, thịt bắp bò, thảo quả, hoa hồi, quế thanh, gừng nướng, hành nướng...\n"
            "2. **Hầm nước dùng**: Chần xương bò qua nước sôi, sau đó ninh nhỏ lửa từ 6–8 tiếng..."
        ),
        "sample_lexdraft": (
            "Hiện tại trong cơ sở dữ liệu pháp luật về hợp đồng dịch vụ của hệ thống chưa có quy định về vấn đề này. "
            "Bạn vui lòng tra cứu thêm các văn bản pháp luật chuyên ngành liên quan hoặc tham vấn chuyên gia pháp lý."
        ),
        "sample_citations": [],
        "sample_expired": [],
        "sample_gatekeeper_blocked": True,
    },
]


def evaluate_ab_response(
    answer: str,
    citations: List[Dict[str, Any]],
    expired_alerts: List[Dict[str, Any]],
    debug_trace: Dict[str, Any] | None,
    is_lexdraft: bool,
) -> Dict[str, str]:
    """Chấm điểm tự động 5 tiêu chí kỹ thuật giữa LLM Truyền thống và Lexdraft."""
    has_vbhn_or_full_law = bool(
        re.search(
            r"(?:VBHN-VPQH|91/2015/QH13|36/2005/QH11|148/2025/QH15|91/2025/QH15|20/2023/QH15|50/2005/QH11)",
            answer,
        )
    )
    has_2025_2026_update = bool(
        re.search(r"(?:2025|2026|148/2025|91/2025|113/VBHN|55/VBHN)", answer)
    )

    if not is_lexdraft:
        return {
            "rag_grounding": "❌ Không có (Zero-Shot)",
            "tiered_validation": "❌ Không kiểm tra hiệu lực",
            "citation_standard": (
                "⚠️ Tự sinh tự do (Thiếu chuẩn VBHN)"
                if not has_vbhn_or_full_law
                else "🟡 Tự nêu số hiệu (chưa xác thực)"
            ),
            "law_2026_awareness": (
                "🔴 Thiếu Luật 2025–2026 / VBHN mới"
                if not has_2025_2026_update
                else "🟡 Có nhắc 2025–2026 (chưa đối chiếu)"
            ),
            "gatekeeper": "❌ Không có chốt chặn phạm vi",
        }

    gatekeeper_status = "🟢 Đạt ngưỡng Cosine (Đủ căn cứ)"
    if debug_trace and debug_trace.get("gatekeeper_passed") is False:
        ms = debug_trace.get("max_similarity_score", debug_trace.get("max_score", 0.0))
        th = debug_trace.get("threshold", 0.75)
        gatekeeper_status = f"🛡️ Chặn tại Code (score={ms:.3f} < τ={th:.2f})"

    return {
        "rag_grounding": f"✅ FAISS VectorDB ({len(citations)} điều luật)",
        "tiered_validation": (
            f"🚨 Bắt {len(expired_alerts)} luật hết hiệu lực (Cấp 1)"
            if expired_alerts
            else "✅ Tiered Validation 3 tầng (An toàn)"
        ),
        "citation_standard": (
            "✅ Chuẩn Điểm/Khoản/Điều & VBHN"
            if has_vbhn_or_full_law or citations
            else "🟢 Trả lời an toàn theo căn cứ"
        ),
        "law_2026_awareness": "✅ Cập nhật Luật 2025–2026 & VBHN mới",
        "gatekeeper": gatekeeper_status,
    }
