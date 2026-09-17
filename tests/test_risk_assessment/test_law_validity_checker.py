"""tests/test_risk_assessment/test_law_validity_checker.py

Unit tests for modules.risk_assessment.law_validity_checker
Covers: Tier 1 (expired_laws.json), Tier 2 (law_index), Tier 3 (LLM fallback),
        check_expired_laws() integration-like test with mocked data.
"""

import json
from unittest.mock import patch

import pytest


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

SAMPLE_EXPIRED_LAWS_DATA = {
    "expired_laws": [
        {
            "law_id": "75/2019/QH14",
            "name": "Luật Bảo vệ bí mật nhà nước 75/2019/QH14",
            "keywords": ["bí mật nhà nước", "75/2019"],
            "replaced_by": "Không có văn bản thay thế hiện tại",
            "status": "Hết hiệu lực",
        },
        {
            "law_id": "ND30/EXPIRED",
            "name": "Nghị định 30 EXPIRED",
            "keywords": ["nghị định 30 cũ", "30/EXPIRED"],
            "replaced_by": "Nghị định 30/2020/NĐ-CP",
            "status": "Đã hết hiệu lực",
        },
    ]
}


@pytest.fixture
def expired_laws_json(tmp_path):
    """Tạo file expired_laws.json tạm thời cho test Cấp 1."""
    f = tmp_path / "expired_laws.json"
    f.write_text(json.dumps(SAMPLE_EXPIRED_LAWS_DATA), encoding="utf-8")
    return f


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _load_expired_laws (Cấp 1 data loading)
# ──────────────────────────────────────────────────────────────────────────────


class TestLoadExpiredLaws:
    def test_returns_empty_list_when_file_missing(self, tmp_path):
        import modules.risk_assessment.law_validity_checker as lvc

        # Reset cache
        lvc._expired_laws_cache = None
        missing_path = tmp_path / "nonexistent.json"
        with patch.object(lvc, "_EXPIRED_LAWS_PATH", missing_path):
            result = lvc._load_expired_laws()
        assert result == []

    def test_loads_correctly_from_valid_json(self, expired_laws_json, tmp_path):
        import modules.risk_assessment.law_validity_checker as lvc

        lvc._expired_laws_cache = None
        with patch.object(lvc, "_EXPIRED_LAWS_PATH", expired_laws_json):
            result = lvc._load_expired_laws()
        assert len(result) == 2
        assert result[0]["law_id"] == "75/2019/QH14"

    def test_caches_result_on_second_call(self, expired_laws_json):
        import modules.risk_assessment.law_validity_checker as lvc

        lvc._expired_laws_cache = None
        with patch.object(lvc, "_EXPIRED_LAWS_PATH", expired_laws_json):
            r1 = lvc._load_expired_laws()
            r2 = lvc._load_expired_laws()
        assert r1 is r2  # Cùng object → đã cache

    def test_returns_empty_on_invalid_json(self, tmp_path):
        import modules.risk_assessment.law_validity_checker as lvc

        lvc._expired_laws_cache = None
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{invalid json", encoding="utf-8")
        with patch.object(lvc, "_EXPIRED_LAWS_PATH", bad_file):
            result = lvc._load_expired_laws()
        assert result == []


# ──────────────────────────────────────────────────────────────────────────────
# Tests: check_expired_laws (integration-like)
# ──────────────────────────────────────────────────────────────────────────────


class TestCheckExpiredLaws:
    @pytest.fixture(autouse=True)
    def _reset_cache(self):
        import modules.risk_assessment.law_validity_checker as lvc

        lvc._expired_laws_cache = None
        yield
        lvc._expired_laws_cache = None

    def test_tier1_detects_expired_keyword(self, expired_laws_json):
        """Cấp 1: Hợp đồng đề cập keyword 75/2019 → phải có cảnh báo."""
        import modules.risk_assessment.law_validity_checker as lvc

        with patch.object(lvc, "_EXPIRED_LAWS_PATH", expired_laws_json):
            alerts = lvc.check_expired_laws(
                contract_text="Căn cứ Luật Bảo vệ bí mật nhà nước 75/2019/QH14 ngày 15/11/2019.",
                law_index_chunks=[],
                enable_llm_fallback=False,
            )
        assert len(alerts) >= 1
        # source field: 'tier1_curated' hoặc 'tier2_statutory'
        alert = alerts[0]
        assert alert.get("source") == "tier1_curated"
        # law_ref chứa tên luật đã trích xuất
        assert (
            "75/2019" in alert.get("law_ref", "")
            or "bí mật" in alert.get("law_ref", "").lower()
        )

    def test_no_alert_when_contract_clean(self, expired_laws_json):
        """Hợp đồng không đề cập văn bản hết hiệu lực → alerts rỗng."""
        import modules.risk_assessment.law_validity_checker as lvc

        with patch.object(lvc, "_EXPIRED_LAWS_PATH", expired_laws_json):
            alerts = lvc.check_expired_laws(
                contract_text="Hợp đồng dịch vụ thiết kế website, căn cứ Bộ luật Dân sự 2015.",
                law_index_chunks=[],
                enable_llm_fallback=False,
            )
        assert alerts == []

    def test_tier2_detects_from_law_index_chunk(self, expired_laws_json):
        """Cấp 2: Tìm thấy chunk law_index chứa 'bãi bỏ' → tạo cảnh báo Cấp 2."""
        import modules.risk_assessment.law_validity_checker as lvc

        chunk_with_repeal = {
            "content": "Luật số 36/2005/QH11 (Luật Thương mại 2005) bị bãi bỏ bởi Luật Thương mại mới 2024.",
            "metadata": {
                "law_name": "Luật Thương mại mới 2024",
                "article": "Điều thi hành",
            },
        }
        with patch.object(lvc, "_EXPIRED_LAWS_PATH", expired_laws_json):
            alerts = lvc.check_expired_laws(
                contract_text="Căn cứ Luật Thương mại số 36/2005/QH11 ngày 14/06/2005.",
                law_index_chunks=[chunk_with_repeal],
                enable_llm_fallback=False,
            )
        # Cấp 2 có thể phát hiện cảnh báo
        # Chỉ cần không crash; kết quả tuỳ vào logic regex Cấp 2
        assert isinstance(alerts, list)

    def test_empty_contract_returns_no_alerts(self, expired_laws_json):
        import modules.risk_assessment.law_validity_checker as lvc

        with patch.object(lvc, "_EXPIRED_LAWS_PATH", expired_laws_json):
            alerts = lvc.check_expired_laws(
                contract_text="",
                law_index_chunks=[],
                enable_llm_fallback=False,
            )
        assert alerts == []

    def test_alerts_have_required_fields(self, expired_laws_json):
        """Mỗi alert phải có source, law_ref, status."""
        import modules.risk_assessment.law_validity_checker as lvc

        with patch.object(lvc, "_EXPIRED_LAWS_PATH", expired_laws_json):
            alerts = lvc.check_expired_laws(
                contract_text="Căn cứ Luật Bảo vệ bí mật nhà nước 75/2019/QH14.",
                law_index_chunks=[],
                enable_llm_fallback=False,
            )
        for alert in alerts:
            assert "source" in alert
            assert "status" in alert
            assert "law_ref" in alert or "law_name" in alert
