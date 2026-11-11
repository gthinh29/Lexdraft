"""Quản lý trạng thái phiên hội thoại, lịch sử tin nhắn và chỉ mục hợp đồng tạm thời."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class ChatSession:
    """Lưu trữ lịch sử hội thoại và ngữ cảnh hợp đồng của một phiên làm việc."""

    def __init__(
        self,
        session_id: str,
        has_contract_context: bool = False,
        contract_chunks: Optional[List[Dict[str, Any]]] = None,
        risk_report: Optional[List[Dict[str, Any]]] = None,
    ):
        self.session_id = session_id
        self.has_contract_context = has_contract_context
        self.contract_chunks: List[Dict[str, Any]] = contract_chunks or []
        self.risk_report: Optional[List[Dict[str, Any]]] = risk_report
        self.contract_vector_db: Optional[Any] = None
        self._messages: List[Dict[str, str]] = []

    def add_message(self, role: str, text: str) -> None:
        """Thêm một lượt tin nhắn ('user' hoặc 'model') vào lịch sử."""
        if role not in ("user", "model"):
            raise ValueError(
                f"role không hợp lệ: '{role}' (chỉ nhận 'user' hoặc 'model')."
            )

        self._messages.append(
            {
                "role": role,
                "text": text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def get_text_history(self) -> List[Dict[str, str]]:
        """Trả về lịch sử hội thoại rút gọn gồm role và text."""
        return [{"role": m["role"], "text": m["text"]} for m in self._messages]

    def set_contract_context(
        self,
        contract_chunks: List[Dict[str, Any]],
        risk_report: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Cập nhật hoặc xóa ngữ cảnh hợp đồng của phiên."""
        if not contract_chunks and not risk_report:
            self.has_contract_context = False
            self.contract_chunks = []
            self.risk_report = None
            self.contract_vector_db = None
        else:
            self.has_contract_context = True
            if contract_chunks:
                self.contract_chunks = contract_chunks
                self.contract_vector_db = None
            if risk_report is not None:
                self.risk_report = risk_report
