"""tests/test_shared/test_chunking.py

Unit tests for modules.shared.chunking.
"""

from modules.shared.chunking import (
    chunk_by_article,
    chunk_contract_by_articles,
    extract_law_header,
)


class TestChunking:
    """Test suite for chunking module."""

    def test_chunk_by_article_standard(self, sample_contract_text):
        """Kiểm tra cắt chunk đúng theo từng Điều."""
        chunks = chunk_by_article(
            sample_contract_text, {"source": "sample_contract.docx"}
        )
        assert len(chunks) >= 4

        articles = [c["metadata"].get("article") for c in chunks]
        assert "Điều 1" in articles
        assert "Điều 2" in articles
        assert "Điều 3" in articles
        assert "Điều 4" in articles
        assert "Lời mở đầu" in articles

        # Kiểm tra metadata được gán đúng
        for c in chunks:
            assert c["metadata"]["source"] == "sample_contract.docx"
            assert len(c["content"]) > 0

    def test_chunk_by_article_empty(self):
        """Kiểm tra văn bản rỗng trả về danh sách rỗng."""
        assert chunk_by_article("") == []
        assert chunk_by_article("   \n\t  ") == []

    def test_chunk_by_article_no_structure_fallback(self):
        """Kiểm tra fallback khi văn bản không có từ khóa 'Điều'."""
        text = "Đây là văn bản tự do không phân chia điều khoản.\nĐoạn thứ hai."
        chunks = chunk_by_article(text, {"source": "free_text.txt"})
        assert len(chunks) == 1
        assert chunks[0]["metadata"]["article"] == "Quy định chung"
        assert chunks[0]["content"] == text.strip()

    def test_chunk_contract_by_articles_alias(self, sample_contract_text):
        """Kiểm tra hàm alias hoạt động giống hệt chunk_by_article."""
        chunks = chunk_contract_by_articles(sample_contract_text)
        assert len(chunks) > 0
        assert any(c["metadata"].get("article") == "Điều 1" for c in chunks)

    def test_extract_law_header_normal_law(self):
        """Kiểm tra trích xuất metadata từ văn bản luật thông thường."""
        text = """
QUỐC HỘI
Luật số: 91/2015/QH13
Hà Nội, ngày 24 tháng 11 năm 2015

BỘ LUẬT DÂN SỰ
Căn cứ Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam;
Quốc hội ban hành Bộ luật Dân sự.
        """
        header = extract_law_header(text, "LuatDanSu2015.md")
        assert header["law_number"] == "91/2015/QH13"
        assert header["issued_date"] == "24/11/2015"
        assert header["status"] == "Còn hiệu lực"

    def test_extract_law_header_vbhn(self):
        """Kiểm tra nhận diện và trích xuất VBHN."""
        text = """
VĂN PHÒNG QUỐC HỘI
Số: 113/VBHN-VPQH
HÀ NỘI, ngày 27 tháng 08 năm 2025

LUẬT THƯƠNG MẠI
Luật Thương mại số 36/2005/QH11 ngày 14 tháng 06 năm 2005 của Quốc hội, có hiệu lực kể từ ngày 01 tháng 01 năm 2006
        """
        header = extract_law_header(text, "VBHN_LuatThuongMai2025.md")
        assert header["is_consolidated"] is True
        assert header["law_number"] == "36/2005/QH11"
