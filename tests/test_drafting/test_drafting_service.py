import pytest
from unittest.mock import MagicMock, patch


# ──────────────────────────────────────────────────────────────────────────────
# Tests: generate_contract_draft
# ──────────────────────────────────────────────────────────────────────────────


class TestGenerateContractDraft:
    @pytest.fixture(autouse=True)
    def _patch_deps(self, sample_law_chunks):
        """Patch toàn bộ I/O bên ngoài để test chạy không cần FAISS / Gemini."""
        mock_llm = MagicMock()
        mock_llm.generate_grounded_response.return_value = {
            "answer": "BẢN NHÁP HỢP ĐỒNG THIẾT KẾ WEBSITE\nĐIỀU 1. ĐỐI TƯỢNG\nNội dung điều 1.",
            "citations": [],
            "refusal": False,
        }

        mock_template = {
            "content": "Mẫu hợp đồng dịch vụ số 01.",
            "metadata": {"template_type": "dich_vu"},
        }

        with (
            patch("modules.drafting.service.llm_client", mock_llm),
            patch(
                "modules.drafting.retrieval.retrieve_template",
                return_value=mock_template,
            ),
            patch(
                "modules.drafting.retrieval.retrieve_relevant_law",
                return_value=sample_law_chunks,
            ),
        ):
            yield mock_llm

    def test_happy_path_returns_draft_string(self):
        from modules.drafting.service import generate_contract_draft

        result = generate_contract_draft(
            {
                "contract_type": "hợp đồng thiết kế website",
                "ben_a": "Công ty A",
                "ben_b": "Công ty B",
            }
        )
        assert "draft" in result
        assert isinstance(result["draft"], str)
        assert len(result["draft"]) > 10

    def test_result_contains_required_keys(self):
        from modules.drafting.service import generate_contract_draft

        result = generate_contract_draft({"contract_type": "hợp đồng dịch vụ"})
        assert "draft" in result
        assert "risk_report" in result
        assert "expired_law_alerts" in result

    def test_risk_report_is_empty_list_by_default(self):
        """Theo yêu cầu không tự chạy risk, risk_report phải là []."""
        from modules.drafting.service import generate_contract_draft

        result = generate_contract_draft({"contract_type": "hợp đồng thuê xe"})
        assert result["risk_report"] == []
        assert result["expired_law_alerts"] == []

    def test_missing_contract_type_raises_value_error(self):
        from modules.drafting.service import generate_contract_draft

        with pytest.raises(ValueError, match="contract_type"):
            generate_contract_draft({"ben_a": "Công ty A"})

    def test_llm_client_none_raises_runtime_error(self):
        from modules.drafting import service as svc

        with patch.object(svc, "llm_client", None):
            with pytest.raises(RuntimeError, match="llm_client"):
                svc.generate_contract_draft({"contract_type": "hợp đồng dịch vụ"})

    def test_template_not_found_still_generates(self):
        """Không tìm thấy mẫu → vẫn gọi LLM với template_text rỗng."""
        from modules.drafting.service import generate_contract_draft

        with patch("modules.drafting.retrieval.retrieve_template", return_value=None):
            result = generate_contract_draft({"contract_type": "hợp đồng mới lạ"})
        assert isinstance(result["draft"], str)

    def test_llm_returns_empty_string(self):
        """LLM trả về chuỗi rỗng → draft là chuỗi rỗng, không crash."""
        from modules.drafting.service import generate_contract_draft

        with patch("modules.drafting.retrieval.retrieve_relevant_law", return_value=[]):
            # llm_client đã mock trả về rỗng
            mock_llm = MagicMock()
            mock_llm.generate_grounded_response.return_value = {
                "answer": "",
                "citations": [],
                "refusal": False,
            }
            with patch("modules.drafting.service.llm_client", mock_llm):
                with patch(
                    "modules.drafting.retrieval.retrieve_template", return_value=None
                ):
                    result = generate_contract_draft({"contract_type": "abc"})
        assert result["draft"] == ""

    def test_draft_content_matches_llm_answer(self):
        """draft phải đúng là answer từ LLM, không bị biến đổi."""
        from modules.drafting.service import generate_contract_draft

        result = generate_contract_draft({"contract_type": "hợp đồng mua bán"})
        assert "BẢN NHÁP HỢP ĐỒNG" in result["draft"]


# ──────────────────────────────────────────────────────────────────────────────
# Tests: _run_risk_assessment_safely
# ──────────────────────────────────────────────────────────────────────────────


class TestRunRiskAssessmentSafely:
    def test_returns_none_when_risk_service_unavailable(self):
        from modules.drafting import service as svc

        with patch.object(svc, "risk_assessment_service", None):
            result = svc._run_risk_assessment_safely("text", None)
        assert result is None

    def test_returns_none_on_exception(self):
        from modules.drafting import service as svc

        mock_risk = MagicMock()
        mock_risk.analyze_contract.side_effect = RuntimeError("LLM lỗi")
        with patch.object(svc, "risk_assessment_service", mock_risk):
            result = svc._run_risk_assessment_safely("text", "session_123")
        assert result is None

    def test_Returns_result_on_success(self):
        from modules.drafting import service as svc

        mock_risk = MagicMock()
        mock_risk.analyze_contract.return_value = {
            "expired_law_alerts": [],
            "risk_results": [],
        }
        with patch.object(svc, "risk_assessment_service", mock_risk):
            result = svc._run_risk_assessment_safely("text hợp đồng", "session_123")
        assert result is not None
        assert "risk_results" in result


# ──────────────────────────────────────────────────────────────────────────────
# Tests: Taxonomy & Stance-Based Drafting (Lexdraft v2.0)
# ──────────────────────────────────────────────────────────────────────────────


class TestTaxonomyAndStanceDrafting:
    def test_load_contract_taxonomy_has_5_categories_and_3_stances(self):
        from modules.drafting import retrieval

        tax = retrieval.load_contract_taxonomy()
        assert "categories" in tax
        assert "stances" in tax
        assert len(tax["categories"]) >= 5
        assert set(tax["stances"].keys()) == {
            "protect_party_a",
            "protect_party_b",
            "balanced",
        }

    def test_retrieve_template_returns_clause_playbook_for_known_category(self):
        from modules.drafting import retrieval

        tpl = retrieval.retrieve_template("Hợp đồng Phát triển Phần mềm")
        assert tpl is not None
        assert "CLAUSE PLAYBOOK" in tpl["content"]
        assert tpl["metadata"]["template_type"] == "software_dev"

    def test_build_drafting_prompt_includes_stance_directives_and_specific_fields(
        self, sample_law_chunks
    ):
        from modules.drafting import prompts

        user_input = {
            "contract_type": "Hợp đồng Phát triển Phần mềm",
            "category_id": "software_dev",
            "stance_id": "protect_party_a",
            "stance_label": "Bảo vệ Bên A",
            "ben_a": "Công ty Alpha",
            "ben_b": "Công ty Beta",
            "specific_values": {
                "Thời hạn bảo hành": "12 tháng miễn phí",
            },
        }
        prompt_str = prompts.build_drafting_prompt(
            template="ĐIỀU 1. PHẠM VI",
            law_context=sample_law_chunks,
            user_input=user_input,
        )
        assert "CHIẾN LƯỢC VỊ THẾ BẢO VỆ PHÁP LÝ" in prompt_str
        assert "Bảo vệ Bên A" in prompt_str
        assert "Thời hạn bảo hành: 12 tháng miễn phí" in prompt_str
        assert "QUY TẮC TRÍCH DẪN PHÁP LÝ BẮT BUỘC" in prompt_str
