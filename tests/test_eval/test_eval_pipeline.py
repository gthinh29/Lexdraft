"""tests/test_eval/test_eval_pipeline.py

Unit tests for eval package (schema, dataset_manager, eval_runner).
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from eval.dataset_manager import DatasetManager
from eval.eval_runner import EvaluationRunner
from eval.schema import GoldenSample


@pytest.fixture
def sample_golden_data():
    return [
        GoldenSample(
            id="TC_TEST_01",
            category="Fact Retrieval",
            question="Mức phạt vi phạm hợp đồng tối đa trong thương mại là bao nhiêu?",
            ground_truth="Mức phạt tối đa là 8% theo Điều 301 Luật Thương mại 2005.",
            expected_laws=["Điều 301", "Luật Thương mại 2005"],
        ),
        GoldenSample(
            id="TC_TEST_02",
            category="Negative / Law Validity",
            question="Quy định về đấu thầu theo Luật Đấu thầu 2013?",
            ground_truth="Luật Đấu thầu 2013 đã hết hiệu lực từ ngày 01/01/2024.",
            expected_laws=["Luật Đấu thầu 2023"],
        ),
    ]


class TestDatasetManager:
    """Test suite cho DatasetManager."""

    def test_save_and_load_dataset(self, sample_golden_data):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test_golden.json"
            dm = DatasetManager(file_path=file_path)

            dm.save_dataset(sample_golden_data)
            assert file_path.exists()

            loaded = dm.load_dataset()
            assert len(loaded) == 2
            assert loaded[0].id == "TC_TEST_01"
            assert loaded[1].id == "TC_TEST_02"

    def test_load_non_existent_file_returns_empty(self):
        dm = DatasetManager(file_path=Path("non_existent_path.json"))
        assert dm.load_dataset() == []

    def test_validate_quality_detects_duplicate_id(self, sample_golden_data):
        dm = DatasetManager()
        duplicate_samples = [
            sample_golden_data[0],
            GoldenSample(
                id="TC_TEST_01",  # Trùng ID
                question="Câu hỏi khác nhưng trùng ID với câu 1?",
                ground_truth="Ground truth hợp lệ với độ dài đầy đủ quy định.",
                expected_laws=["Điều 1"],
            ),
        ]
        is_valid, issues = dm.validate_quality(duplicate_samples)
        assert is_valid is False
        assert any("trùng lặp" in i for i in issues)

    def test_validate_quality_detects_short_question(self):
        dm = DatasetManager()
        invalid_sample = [
            GoldenSample(
                id="TC_01",
                question="Ngắn",
                ground_truth="Ground truth hợp lệ với độ dài đầy đủ quy định.",
                expected_laws=["Điều 1"],
            )
        ]
        is_valid, issues = dm.validate_quality(invalid_sample)
        assert is_valid is False
        assert any("Câu hỏi quá ngắn" in i for i in issues)


class TestEvaluationRunner:
    """Test suite cho EvaluationRunner."""

    def test_run_inference_and_metrics(self, sample_golden_data):
        runner = EvaluationRunner()

        mock_chat_response = {
            "answer": "Theo Điều 301 Luật Thương mại 2005 mức phạt là 8%.",
            "citations": ["Điều 301 Luật Thương mại 2005"],
            "context_chunks": [
                {"content": "Điều 301 Luật Thương mại...", "score": 0.92}
            ],
        }

        mock_chunks = [{"content": "Điều 301 Luật Thương mại...", "score": 0.92}]

        with patch(
            "eval.eval_runner.handle_chat", return_value=mock_chat_response
        ), patch("eval.eval_runner.retrieval.search_context", return_value=mock_chunks):
            results = runner.run_inference(sample_golden_data[:1])

            assert len(results) == 1
            assert results[0].id == "TC_TEST_01"
            assert "8%" in results[0].system_answer
            assert len(results[0].retrieved_contexts) == 1

            metrics = runner.compute_rule_metrics(sample_golden_data[:1], results)
            assert metrics["total_samples"] == 1
            assert metrics["retrieval_success_rate"] == 1.0
            assert metrics["fact_citation_match_rate"] == 1.0
            assert metrics["overall_compliance_rate"] == 1.0
