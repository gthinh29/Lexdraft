"""eval/synthetic_gen.py

Công cụ tự động sinh câu hỏi & Ground Truth dựa trên chính các Điều luật thực tế trong VectorDB.
Giúp xây dựng Golden Dataset có căn cứ 100%, không bị ảo giác và tiết kiệm thời gian.
"""

import json
import logging
from typing import List, Optional

from eval.schema import GoldenSample
from modules.shared.llm_client import GeminiClient

logger = logging.getLogger(__name__)

GEN_PROMPT_TEMPLATE = """Bạn là chuyên gia pháp lý và kiểm thử hệ thống RAG pháp luật Việt Nam.
Hãy đọc kỹ đoạn Điều luật sau đây và sinh ra đúng 1 câu hỏi kiểm thử chất lượng cao cùng câu trả lời chuẩn (Ground Truth).

NỘI DUNG ĐIỀU LUẬT:
---
{chunk_content}
---

YÊU CẦU:
1. Câu hỏi phải thực tế, mang tính nghiệp vụ rà soát hợp đồng hoặc xử lý tranh chấp.
2. Câu trả lời (Ground Truth) phải dựa 100% vào điều luật trên, có nêu rõ số hiệu Điều luật, tên văn bản và phân tích ngắn gọn.
3. Phân loại thuộc 1 trong 3 nhóm: "Fact Retrieval", "Conditional / Multi-hop", hoặc "Negative / Law Validity".

Trả về ĐÚNG định dạng JSON sau (không kèm markdown thừa):
{{
  "category": "Fact Retrieval",
  "question": "Nội dung câu hỏi...",
  "ground_truth": "Nội dung câu trả lời chuẩn xác...",
  "expected_laws": ["Tên Điều và Luật cụ thể"]
}}
"""


class SyntheticDatasetGenerator:
    """Tạo bộ mẫu kiểm thử nhân tạo từ các chunk văn bản luật có thật."""

    def __init__(self, llm_client: Optional[GeminiClient] = None):
        self.llm = llm_client or GeminiClient(temperature=0.2)

    def generate_from_chunk(
        self, chunk_id: str, chunk_content: str
    ) -> Optional[GoldenSample]:
        """Sinh 1 mẫu GoldenSample từ 1 chunk văn bản luật."""
        prompt = GEN_PROMPT_TEMPLATE.format(chunk_content=chunk_content)
        try:
            response_text = self.llm.generate(prompt)
            # Làm sạch phản hồi JSON nếu có bọc trong markdown codeblock
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            data = json.loads(cleaned_text.strip())
            return GoldenSample(
                id=chunk_id,
                category=data.get("category", "Fact Retrieval"),
                question=data.get("question", ""),
                ground_truth=data.get("ground_truth", ""),
                expected_laws=data.get("expected_laws", []),
                source_chunk_ids=[chunk_id],
            )
        except Exception as e:
            logger.warning(f"Không thể sinh test sample từ chunk {chunk_id}: {e}")
            return None

    def generate_batch_from_chunks(self, chunks: List[dict]) -> List[GoldenSample]:
        """Sinh danh sách mẫu test từ danh sách các chunk luật."""
        results = []
        for idx, c in enumerate(chunks, start=1):
            content = c.get("content", "")
            if len(content.strip()) < 50:
                continue
            chunk_id = f"GEN_{idx:03d}"
            sample = self.generate_from_chunk(chunk_id, content)
            if sample:
                results.append(sample)
        return results
