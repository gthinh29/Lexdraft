"""
modules/chatbot_qa/chat_session.py

Quản lý 1 phiên hội thoại chatbot Q&A.

LƯU Ý QUAN TRỌNG (SRS 6.1 - Tối ưu token/độ trễ):
Lịch sử hội thoại (self._messages) CHỈ lưu role + text ngắn gọn.
KHÔNG được lưu context RAG (các chunk truy xuất được) vào lịch sử - context đó
chỉ đính kèm cho câu hỏi hiện tại tại thời điểm gọi LLM, tránh phình token
qua từng lượt hỏi.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class ChatSession:
    """
    Đại diện cho 1 phiên chat, có thể ở:
      - Chế độ B (has_contract_context=False): tra cứu luật chung, không có hợp đồng.
      - Chế độ A (has_contract_context=True): có ngữ cảnh hợp đồng + báo cáo rủi ro,
        tiếp nối từ Module 1 (Drafting) hoặc Module 2 (Risk Assessment).
    """

    def __init__(
        self,
        session_id: str,
        has_contract_context: bool = False,
        contract_chunks: Optional[List[Dict[str, Any]]] = None,
        risk_report: Optional[List[Dict[str, Any]]] = None,
    ):
        self.session_id = session_id
        self.has_contract_context = has_contract_context

        # Các chunk Điều/Khoản của hợp đồng (dùng để build contract_index ephemeral).
        self.contract_chunks: List[Dict[str, Any]] = contract_chunks or []

        # Báo cáo rủi ro từ Module 2 (Phần 8): [{"dieu_khoan":..., "rui_ro":..., "can_cu":[...]}]
        self.risk_report: Optional[List[Dict[str, Any]]] = risk_report

        # VectorDB ephemeral build từ contract_chunks, cache tại đây để không build lại
        # mỗi lượt hỏi trong cùng 1 phiên (contract_index là "Động - Mỗi phiên" theo SRS 5.1).
        # Được gán/đọc bởi modules/chatbot_qa/retrieval.py.
        self.contract_vector_db: Optional[Any] = None

        self._messages: List[Dict[str, str]] = []

    def add_message(self, role: str, text: str) -> None:
        """
        Thêm 1 lượt tin nhắn vào lịch sử.

        Args:
            role: "user" hoặc "model".
            text: nội dung tin nhắn (không kèm context RAG).
        """
        if role not in ("user", "model"):
            raise ValueError(f"role không hợp lệ: '{role}' (chỉ nhận 'user' hoặc 'model').")

        self._messages.append(
            {
                "role": role,
                "text": text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def get_text_history(self) -> List[Dict[str, str]]:
        """
        Trả về lịch sử hội thoại dạng text ngắn gọn (role + text),
        KHÔNG bao gồm context RAG cũ - đúng theo SRS 6.1.
        """
        return [{"role": m["role"], "text": m["text"]} for m in self._messages]

    def set_contract_context(
        self,
        contract_chunks: List[Dict[str, Any]],
        risk_report: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Nạp/refresh ngữ cảnh hợp đồng cho phiên (chuyển sang Chế độ A).
        Reset contract_vector_db cũ (nếu có) để buộc build lại với dữ liệu mới nhất.
        """
        self.has_contract_context = True
        self.contract_chunks = contract_chunks
        self.risk_report = risk_report
        self.contract_vector_db = None
