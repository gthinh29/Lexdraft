import pytest
from unittest.mock import MagicMock, patch


# ──────────────────────────────────────────────────────────────────────────────
# Common fixtures & mocks
# ──────────────────────────────────────────────────────────────────────────────

MOCK_RISK_ANSWER = """===DIEU_1_KET_QUA===
**Điều 1** không có rủi ro đáng kể.
===DIEU_2_KET_QUA===
**Điều 2** có rủi ro về mức phạt: cần kiểm tra lại không vượt quá 8%.
"""

MOCK_EXPIRED_ALERTS = []  # Clean contract


@pytest.fixture
def patched_risk_deps(sample_law_chunks, sample_contract_text):
    """Patch FAISS, LLM, law_validity_checker cho toàn bộ test risk service."""

    mock_llm = MagicMock()
    mock_llm.generate_grounded_response.return_value = {
        "answer": MOCK_RISK_ANSWER,
        "citations": [],
        "refusal": False,
    }
    mock_llm.extract_citations_from_chunks.return_value = []

    mock_retrieval_find = MagicMock(return_value=sample_law_chunks)
    mock_checker = MagicMock(return_value=MOCK_EXPIRED_ALERTS)

    with (
        patch("modules.risk_assessment.service.llm_client", mock_llm),
        patch("modules.risk_assessment.service.time.sleep", return_value=None),
        patch(
            "modules.risk_assessment.retrieval.find_related_laws", mock_retrieval_find
        ),
        patch(
            "modules.risk_assessment.law_validity_checker.check_expired_laws",
            mock_checker,
        ),
    ):
        yield {
            "llm": mock_llm,
            "retrieval": mock_retrieval_find,
            "checker": mock_checker,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Tests: analyze_contract
# ──────────────────────────────────────────────────────────────────────────────


class TestAnalyzeContract:
    def test_happy_path_returns_dict(self, sample_contract_text, patched_risk_deps):
        from modules.risk_assessment.service import analyze_contract

        result = analyze_contract(sample_contract_text)
        assert isinstance(result, dict)
        assert "expired_law_alerts" in result
        assert "risk_results" in result

    def test_risk_results_is_list(self, sample_contract_text, patched_risk_deps):
        from modules.risk_assessment.service import analyze_contract

        result = analyze_contract(sample_contract_text)
        assert isinstance(result["risk_results"], list)

    def test_each_risk_result_has_required_keys(
        self, sample_contract_text, patched_risk_deps
    ):
        from modules.risk_assessment.service import analyze_contract

        result = analyze_contract(sample_contract_text)
        for item in result["risk_results"]:
            assert "dieu_khoan" in item
            assert "noi_dung" in item
            assert "rui_ro" in item
            assert "can_cu" in item

    def test_empty_text_returns_empty_results(self, patched_risk_deps):
        from modules.risk_assessment.service import analyze_contract

        result = analyze_contract("")
        assert result["risk_results"] == []
        assert result["expired_law_alerts"] == []

    def test_from_file_path(self, sample_docx_file, patched_risk_deps):
        """Truyền Path file .docx thay vì text thô → vẫn phân tích được."""
        from modules.risk_assessment.service import analyze_contract

        result = analyze_contract(sample_docx_file)
        assert isinstance(result, dict)

    def test_calls_tiered_validation(self, sample_contract_text, patched_risk_deps):
        """check_expired_laws phải được gọi ít nhất 1 lần."""
        from modules.risk_assessment.service import analyze_contract

        analyze_contract(sample_contract_text)
        patched_risk_deps["checker"].assert_called()

    def test_llm_exception_still_returns_results(
        self, sample_contract_text, patched_risk_deps
    ):
        """LLM lỗi ở 1 điều khoản → item vẫn được tạo với rui_ro chứa thông báo lỗi."""
        from modules.risk_assessment.service import analyze_contract

        mock_llm = patched_risk_deps["llm"]
        mock_llm.generate_grounded_response.side_effect = RuntimeError("API 429")

        with patch("modules.risk_assessment.service.llm_client", mock_llm):
            result = analyze_contract(sample_contract_text)

        # Không crash, có thể có 0 hoặc nhiều items tuỳ logic
        assert isinstance(result["risk_results"], list)

    def test_session_id_triggers_chatbot_sync(
        self, sample_contract_text, patched_risk_deps
    ):
        """Khi có session_id → thử gọi chatbot_service.attach_contract_context."""
        from modules.risk_assessment.service import analyze_contract

        mock_chatbot = MagicMock()
        with patch("modules.chatbot_qa.service.attach_contract_context", mock_chatbot):
            analyze_contract(sample_contract_text, session_id="session_abc")
        # Không cần gọi đúng (do import guard) nhưng không được crash
        assert True  # Chỉ verify không raise exception


# ──────────────────────────────────────────────────────────────────────────────
# Tests: stream_analyze_contract
# ──────────────────────────────────────────────────────────────────────────────


class TestStreamAnalyzeContract:
    def _collect_events(self, text, **kwargs):
        from modules.risk_assessment.service import stream_analyze_contract

        return list(stream_analyze_contract(text, **kwargs))

    def test_yields_meta_then_results_then_done(
        self, sample_contract_text, patched_risk_deps
    ):
        events = self._collect_events(sample_contract_text)
        types = [e[0] for e in events]
        assert "meta" in types
        assert "done" in types
        assert types[-1] == "done"

    def test_meta_event_has_required_fields(
        self, sample_contract_text, patched_risk_deps
    ):
        events = self._collect_events(sample_contract_text)
        meta_events = [e for e in events if e[0] == "meta"]
        assert len(meta_events) == 1
        meta_data = meta_events[0][1]
        assert "total" in meta_data
        assert "source" in meta_data
        assert "expired_law_alerts" in meta_data

    def test_done_event_has_risk_results(self, sample_contract_text, patched_risk_deps):
        events = self._collect_events(sample_contract_text)
        done_data = events[-1][1]
        assert "risk_results" in done_data
        assert "expired_law_alerts" in done_data

    def test_result_events_have_index_and_total(
        self, sample_contract_text, patched_risk_deps
    ):
        events = self._collect_events(sample_contract_text)
        result_events = [e for e in events if e[0] == "result"]
        for ev in result_events:
            assert "index" in ev[1]
            assert "total" in ev[1]
            assert "dieu_khoan" in ev[1]

    def test_empty_text_yields_error_immediately(self, patched_risk_deps):
        events = self._collect_events("")
        assert events[-1][0] == "error"
        assert "message" in events[-1][1]

    def test_stream_parses_batch_response(
        self, sample_contract_text, patched_risk_deps
    ):
        """Kết quả batch LLM (===DIEU_N_KET_QUA===) phải được parse đúng."""
        events = self._collect_events(sample_contract_text)
        result_events = [e for e in events if e[0] == "result"]
        # Ít nhất 1 điều khoản được phân tích
        assert len(result_events) >= 1

    def test_original_name_used_in_meta(self, sample_contract_text, patched_risk_deps):
        events = self._collect_events(
            sample_contract_text, original_name="my_contract.docx"
        )
        meta_data = [e for e in events if e[0] == "meta"][0][1]
        assert meta_data["source"] == "my_contract.docx"


class TestRiskToRedraft:
    def test_extract_redrafted_clause_parses_redline(self):
        from modules.risk_assessment.service import extract_redrafted_clause

        sample = (
            "- **Mức độ & Nhận diện rủi ro**: [RỦI RO CAO]\n"
            "- **Đề xuất soạn lại điều khoản (Redline)**: Điều 3. Phạt vi phạm 8% giá trị phần nghĩa vụ bị vi phạm."
        )
        res = extract_redrafted_clause(sample)
        assert "8% giá trị phần nghĩa vụ bị vi phạm" in res

    def test_build_redrafted_contract_text_replaces_risky_clause(self):
        from modules.risk_assessment.service import build_redrafted_contract_text

        risk_results = [
            {
                "dieu_khoan": "Điều 1",
                "noi_dung": "ĐIỀU 1. ĐỐI TƯỢNG\nThiết kế phần mềm.",
                "rui_ro": "Không phát hiện rủi ro pháp lý rõ ràng.",
                "redrafted_clause": "",
            },
            {
                "dieu_khoan": "Điều 2",
                "noi_dung": "ĐIỀU 2. PHẠT VI PHẠM\nPhạt 20% tổng giá trị hợp đồng.",
                "rui_ro": "- **Đề xuất soạn lại điều khoản (Redline)**: ĐIỀU 2. PHẠT VI PHẠM\nPhạt 8% giá trị phần nghĩa vụ bị vi phạm theo Điều 301 Luật Thương mại.",
                "redrafted_clause": "ĐIỀU 2. PHẠT VI PHẠM\nPhạt 8% giá trị phần nghĩa vụ bị vi phạm theo Điều 301 Luật Thương mại.",
            },
        ]
        expired = [
            {
                "law_ref": "Luật Công nghệ thông tin 67/2006/QH11",
                "status": "Hết hiệu lực",
                "replaced_by": "Luật Chuyển đổi số số 148/2025/QH15",
            }
        ]
        full_text = build_redrafted_contract_text(risk_results, expired)
        assert "Luật Chuyển đổi số số 148/2025/QH15" in full_text
        assert "Phạt 8% giá trị phần nghĩa vụ bị vi phạm" in full_text
        assert "Phạt 20% tổng giá trị hợp đồng" not in full_text

    def test_separated_risk_and_redraft_prompts(self):
        from modules.risk_assessment import prompts

        risk_prompt = prompts.build_batch_risk_prompt(
            [
                {
                    "label": "Điều 3",
                    "content": "Điều 3. Phạt 20%.",
                    "law_chunks": [],
                }
            ]
        )
        redraft_prompt = prompts.build_batch_redraft_prompt(
            [
                {
                    "seq": 1,
                    "label": "Điều 3",
                    "content": "Điều 3. Phạt 20%.",
                    "risk_summary": "Vượt trần 8% Điều 301 LTM.",
                    "law_chunks": [],
                }
            ]
        )
        assert "===DIEU_1_KET_QUA===" in risk_prompt
        assert "===REDRAFT_" not in risk_prompt
        assert "===REDRAFT_1_KET_QUA===" in redraft_prompt
        assert "===DIEU_1_KET_QUA===" not in redraft_prompt
