"""eval/schema.py

Pydantic schemas cho bộ dữ liệu đánh giá (Golden Dataset) và kết quả Ragas.
Đảm bảo tính hợp lệ, đầy đủ của dữ liệu trước khi đưa vào pipeline đánh giá.
"""

from typing import Any, List, Optional
from pydantic import BaseModel, Field


class GoldenSample(BaseModel):
    """Một mẫu dữ liệu chuẩn (Ground Truth) dùng để kiểm thử RAG."""

    id: str = Field(..., description="Mã định danh duy nhất (ví dụ: TC_01, TC_02)")
    category: str = Field(
        default="Fact Retrieval",
        description="Phân loại: 'Fact Retrieval', 'Conditional / Multi-hop', 'Negative / Law Validity'",
    )
    question: str = Field(..., description="Câu hỏi của người dùng")
    ground_truth: str = Field(
        ..., description="Câu trả lời chuẩn mực từ chuyên gia pháp lý"
    )
    expected_laws: List[str] = Field(
        default_factory=list,
        description="Danh sách Điều luật bắt buộc phải viện dẫn (ví dụ: ['Điều 301 Luật Thương mại 2005'])",
    )
    source_chunk_ids: Optional[List[str]] = Field(
        default=None,
        description="ID của chunk tài liệu chứa thông tin này trong Vector DB",
    )


class EvalSampleResult(BaseModel):
    """Kết quả thu được sau khi chạy một câu hỏi qua hệ thống Lexdraft."""

    id: str
    question: str
    ground_truth: str
    system_answer: str
    retrieved_contexts: List[str]
    citations: List[Any] = Field(default_factory=list)
    similarity_score_max: float = 0.0
