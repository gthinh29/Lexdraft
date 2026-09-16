"""tests/test_chatbot_qa/test_chat_session.py

Unit tests for modules.chatbot_qa.chat_session.ChatSession
Covers: Mode A/B switching, history management, contract context lifecycle.
"""

import pytest

from modules.chatbot_qa.chat_session import ChatSession


# ──────────────────────────────────────────────────────────────────────────────
# Tests: initial state
# ──────────────────────────────────────────────────────────────────────────────


class TestChatSessionInit:
    def test_default_mode_is_b(self):
        session = ChatSession("s1")
        assert session.has_contract_context is False

    def test_default_contract_chunks_empty(self):
        session = ChatSession("s1")
        assert session.contract_chunks == []

    def test_default_risk_report_none(self):
        session = ChatSession("s1")
        assert session.risk_report is None

    def test_default_vector_db_none(self):
        session = ChatSession("s1")
        assert session.contract_vector_db is None

    def test_session_id_stored(self):
        session = ChatSession("my_session")
        assert session.session_id == "my_session"

    def test_init_with_contract_context(self, sample_law_chunks):
        session = ChatSession(
            "s2", has_contract_context=True, contract_chunks=sample_law_chunks
        )
        assert session.has_contract_context is True
        assert len(session.contract_chunks) == 3


# ──────────────────────────────────────────────────────────────────────────────
# Tests: add_message / get_text_history
# ──────────────────────────────────────────────────────────────────────────────


class TestChatSessionHistory:
    def test_add_user_message(self):
        session = ChatSession("s1")
        session.add_message("user", "Câu hỏi của tôi?")
        history = session.get_text_history()
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["text"] == "Câu hỏi của tôi?"

    def test_add_model_message(self):
        session = ChatSession("s1")
        session.add_message("model", "Phản hồi của AI.")
        history = session.get_text_history()
        assert history[0]["role"] == "model"

    def test_multiple_messages_ordered(self):
        session = ChatSession("s1")
        session.add_message("user", "Q1")
        session.add_message("model", "A1")
        session.add_message("user", "Q2")
        history = session.get_text_history()
        assert len(history) == 3
        assert history[0]["text"] == "Q1"
        assert history[2]["text"] == "Q2"

    def test_invalid_role_raises_value_error(self):
        session = ChatSession("s1")
        with pytest.raises(ValueError, match="role"):
            session.add_message("admin", "Tin nhắn lạ")

    def test_get_text_history_excludes_timestamp(self):
        """get_text_history() chỉ trả về role + text, không có timestamp."""
        session = ChatSession("s1")
        session.add_message("user", "Hello")
        history = session.get_text_history()
        assert "timestamp" not in history[0]

    def test_empty_history_is_list(self):
        session = ChatSession("s1")
        assert session.get_text_history() == []


# ──────────────────────────────────────────────────────────────────────────────
# Tests: set_contract_context (Chế độ A / B switching)
# ──────────────────────────────────────────────────────────────────────────────


class TestSetContractContext:
    def test_set_context_activates_mode_a(self, sample_law_chunks):
        session = ChatSession("s1")
        session.set_contract_context(sample_law_chunks)
        assert session.has_contract_context is True

    def test_contract_chunks_stored(self, sample_law_chunks):
        session = ChatSession("s1")
        session.set_contract_context(sample_law_chunks)
        assert session.contract_chunks == sample_law_chunks

    def test_risk_report_stored_when_provided(self, sample_law_chunks):
        session = ChatSession("s1")
        risk = [{"dieu_khoan": "Điều 1", "rui_ro": "Không có"}]
        session.set_contract_context(sample_law_chunks, risk_report=risk)
        assert session.risk_report == risk

    def test_vector_db_reset_on_new_context(self, sample_law_chunks):
        session = ChatSession("s1")
        session.contract_vector_db = "old_db"
        session.set_contract_context(sample_law_chunks)
        assert session.contract_vector_db is None

    def test_empty_context_reverts_to_mode_b(self, sample_law_chunks):
        session = ChatSession("s1")
        session.set_contract_context(sample_law_chunks)
        assert session.has_contract_context is True
        # Clear context → quay về Chế độ B
        session.set_contract_context([], risk_report=None)
        assert session.has_contract_context is False
        assert session.contract_chunks == []
        assert session.risk_report is None

    def test_none_chunks_with_risk_still_activates(self):
        """Nếu có risk_report nhưng chunks rỗng → vẫn Mode A."""
        session = ChatSession("s1")
        risk = [{"dieu_khoan": "Điều 1", "rui_ro": "Ok"}]
        # Truyền chunks rỗng nhưng có risk_report → mode vẫn A (có context)
        # Theo code: if not contract_chunks and not risk_report → Mode B
        # Nếu có risk_report → Mode A
        session.set_contract_context([], risk_report=risk)
        assert session.has_contract_context is True


# ──────────────────────────────────────────────────────────────────────────────
# Tests: chatbot_qa/service.py - attach_contract_context & handle_chat
# ──────────────────────────────────────────────────────────────────────────────


class TestChatbotService:
    def test_attach_context_creates_session(self, sample_law_chunks):
        """attach_contract_context tạo mới session nếu chưa có."""
        import modules.chatbot_qa.service as svc

        # Xoá cache session cũ
        svc._SESSIONS.pop("test_attach_01", None)
        svc.attach_contract_context("test_attach_01", sample_law_chunks)
        assert "test_attach_01" in svc._SESSIONS
        assert svc._SESSIONS["test_attach_01"].has_contract_context is True

    def test_attach_context_updates_existing_session(self, sample_law_chunks):
        """attach_contract_context refresh session đã tồn tại."""
        import modules.chatbot_qa.service as svc

        svc._SESSIONS.pop("test_attach_02", None)
        svc.attach_contract_context("test_attach_02", [])  # Mode B
        svc.attach_contract_context("test_attach_02", sample_law_chunks)  # Mode A
        assert svc._SESSIONS["test_attach_02"].has_contract_context is True

    def test_handle_chat_raises_if_no_llm(self, sample_law_chunks):
        """handle_chat raise RuntimeError nếu llm_client là None."""
        import modules.chatbot_qa.service as svc
        from unittest.mock import patch

        svc._SESSIONS.pop("test_no_llm", None)
        with patch.object(svc, "llm_client", None):
            with pytest.raises(RuntimeError, match="llm_client"):
                svc.handle_chat("Hỏi gì đó", "test_no_llm")

    def test_handle_chat_returns_answer_and_citations(self, sample_law_chunks):
        """handle_chat trả về dict với answer và citations."""
        import modules.chatbot_qa.service as svc
        from unittest.mock import MagicMock, patch

        svc._SESSIONS.pop("test_handle_01", None)

        mock_llm = MagicMock()
        mock_llm.generate_grounded_response.return_value = {
            "answer": "Đây là câu trả lời.",
            "citations": [{"article": "Điều 513"}],
        }
        mock_retrieval = MagicMock(return_value=[])
        mock_prompt = MagicMock(return_value="prompt text")

        with (
            patch.object(svc, "llm_client", mock_llm),
            patch("modules.chatbot_qa.retrieval.search_context", mock_retrieval),
            patch("modules.chatbot_qa.prompts.build_chat_prompt", mock_prompt),
        ):
            result = svc.handle_chat("Câu hỏi pháp lý?", "test_handle_01")

        assert result["answer"] == "Đây là câu trả lời."
        assert isinstance(result["citations"], list)

    def test_handle_chat_records_history(self, sample_law_chunks):
        """Sau khi handle_chat, history phải có cả user + model message."""
        import modules.chatbot_qa.service as svc
        from unittest.mock import MagicMock, patch

        svc._SESSIONS.pop("test_history_01", None)

        mock_llm = MagicMock()
        mock_llm.generate_grounded_response.return_value = {
            "answer": "AI trả lời.",
            "citations": [],
        }

        with (
            patch.object(svc, "llm_client", mock_llm),
            patch(
                "modules.chatbot_qa.retrieval.search_context",
                MagicMock(return_value=[]),
            ),
            patch(
                "modules.chatbot_qa.prompts.build_chat_prompt",
                MagicMock(return_value="p"),
            ),
        ):
            svc.handle_chat("User hỏi.", "test_history_01")

        session = svc._SESSIONS["test_history_01"]
        history = session.get_text_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "model"

    def test_mode_switch_a_to_b_clears_context(self, sample_law_chunks):
        """Gọi attach với chunks rỗng + risk None → session về Mode B."""
        import modules.chatbot_qa.service as svc

        svc._SESSIONS.pop("test_mode_switch", None)
        svc.attach_contract_context("test_mode_switch", sample_law_chunks)
        assert svc._SESSIONS["test_mode_switch"].has_contract_context is True
        svc.attach_contract_context("test_mode_switch", [], None)
        assert svc._SESSIONS["test_mode_switch"].has_contract_context is False
