"""tests/conftest.py

Shared fixtures for Lexdraft unit and integration tests.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from docx import Document as DocxDocument

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_contract_text():
    """Văn bản mẫu hợp đồng dịch vụ chuẩn tiếng Việt với nhiều điều khoản."""
    return """
CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM
Độc lập – Tự do – Hạnh phúc
---o0o---

HỢP ĐỒNG DỊCH VỤ THIẾT KẾ WEBSITE
Số: 01/HĐDV/2026

Căn cứ Bộ luật Dân sự số 91/2015/QH13 ngày 24/11/2015;
Căn cứ Luật Thương mại số 36/2005/QH11 ngày 14/06/2005;

Hôm nay, ngày 17 tháng 09 năm 2026, chúng tôi gồm có:

BÊN A (BÊN THUÊ DỊCH VỤ):
- Tên công ty: Công ty TNHH Lexdraft
- Đại diện: Ông Nguyễn Văn A

BÊN B (BÊN CUNG CẤP DỊCH VỤ):
- Tên công ty: Công ty Cổ phần Giải pháp Số
- Đại diện: Bà Trần Thị B

Hai bên thống nhất ký kết hợp đồng dịch vụ với các điều khoản sau:

ĐIỀU 1. ĐỐI TƯỢNG HỢP ĐỒNG
1.1. Bên B đồng ý cung cấp dịch vụ thiết kế hệ thống website thương mại điện tử cho Bên A.
1.2. Bên B cam kết bàn giao đầy đủ mã nguồn và tài liệu hướng dẫn kỹ thuật.

ĐIỀU 2. GIÁ TRỊ HỢP ĐỒNG VÀ PHƯƠNG THỨC THANH TOÁN
2.1. Tổng giá trị hợp đồng là 150.000.000 VNĐ (Một trăm năm mươi triệu đồng).
2.2. Bên A thanh toán thành 02 đợt qua tài khoản ngân hàng của Bên B.

ĐIỀU 3. PHẠT VI PHẠM VÀ BỒI THƯỜNG THIỆT HẠI
3.1. Nếu Bên B chậm tiến độ quá 15 ngày, Bên B chịu phạt vi phạm 8% giá trị phần nghĩa vụ hợp đồng bị vi phạm.
3.2. Mức phạt vi phạm và bồi thường thiệt hại tuân thủ quy định của Luật Thương mại 2005.

ĐIỀU 4. BẢO MẬT THÔNG TIN
4.1. Hai bên cam kết tuân thủ Luật Bảo vệ dữ liệu cá nhân 91/2025/QH15.
4.2. Nghĩa vụ bảo mật kéo dài 02 năm kể từ ngày hợp đồng chấm dứt.

| ĐẠI DIỆN BÊN A | ĐẠI DIỆN BÊN B |
| :---: | :---: |
| (Ký, đóng dấu) | (Ký, đóng dấu) |
| Nguyễn Văn A | Trần Thị B |
"""


@pytest.fixture
def sample_docx_file(sample_contract_text):
    """Tạo file .docx tạm thời chứa nội dung hợp đồng mẫu."""
    doc = DocxDocument()
    for line in sample_contract_text.split("\n"):
        if line.strip():
            doc.add_paragraph(line.strip())

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        doc.save(tmp.name)
        tmp_path = Path(tmp.name)

    yield tmp_path

    if tmp_path.exists():
        tmp_path.unlink()


@pytest.fixture
def sample_law_chunks():
    """Danh sách các chunk văn bản luật mẫu cho retrieval."""
    return [
        {
            "content": "Điều 513. Hợp đồng dịch vụ là sự thỏa thuận giữa các bên, theo đó bên cung ứng dịch vụ thực hiện công việc cho bên thuê dịch vụ, bên thuê dịch vụ phải trả tiền dịch vụ cho bên cung ứng dịch vụ.",
            "metadata": {
                "law_name": "Bộ luật Dân sự 2015",
                "article": "Điều 513",
                "source": "Bộ luật Dân sự 2015",
            },
            "score": 0.88,
        },
        {
            "content": "Điều 300. Phạt vi phạm là việc bên bị vi phạm yêu cầu bên vi phạm trả một khoản tiền phạt do vi phạm hợp đồng nếu trong hợp đồng có thỏa thuận, trừ các trường hợp miễn trách nhiệm quy định tại Điều 294 của Luật này.",
            "metadata": {
                "law_name": "Luật Thương mại 2005",
                "article": "Điều 300",
                "source": "Luật Thương mại 2005",
            },
            "score": 0.85,
        },
        {
            "content": "Điều 301. Mức phạt vi phạm: Mức phạt đối với vi phạm nghĩa vụ hợp đồng hoặc tổng mức phạt đối với nhiều vi phạm do các bên thoả thuận trong hợp đồng, nhưng không quá 8% giá trị phần nghĩa vụ hợp đồng bị vi phạm, trừ trường hợp quy định tại Điều 266 của Luật này.",
            "metadata": {
                "law_name": "Luật Thương mại 2005",
                "article": "Điều 301",
                "source": "Luật Thương mại 2005",
            },
            "score": 0.92,
        },
    ]


@pytest.fixture
def mock_gemini_client():
    """Mock GeminiClient trả về phản hồi hợp lệ cho các tác vụ LLM."""
    mock_client = MagicMock()
    mock_client.generate_text.return_value = "Phản hồi thử nghiệm từ Mock Gemini."
    mock_client.get_embedding.return_value = [0.1] * 768
    mock_client.get_embeddings_batch.return_value = [[0.1] * 768]
    return mock_client
