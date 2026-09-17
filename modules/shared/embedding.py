"""
modules/shared/embedding.py

Module quản lý Vector Database dùng FAISS và Google Gemini Embedding API.
Hỗ trợ:
- Embedding qua Gemini API (models/text-embedding-004) với Batching + Exponential Backoff.
- IndexFlatIP (Cosine Similarity sau khi chuẩn hóa L2).
- Metadata Filtering linh hoạt theo số Điều, văn bản nguồn...
- Lưu/Tải index (.faiss + .pkl).
- Tương thích hoàn toàn interface hybrid_search() và search_with_metadata().

Tuân thủ:
- Implementation Plan Phần 4 (4.1 -> 4.5)
- SRS 5.1, 5.2, 6.2
"""

import logging
import os
import pickle
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import faiss
import numpy as np
from config import Config

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = getattr(
    Config, "EMBEDDING_MODEL_NAME", "models/gemini-embedding-001"
)
EMBEDDING_DIMENSION = 768
BATCH_SIZE = 50
SLEEP_BETWEEN_BATCHES = 2.0


class VectorDB:
    """
    Quản lý Vector Index (FAISS) kết hợp lưu trữ Metadata và tìm kiếm có bộ lọc.
    """

    def __init__(self, model_name: Optional[str] = None):
        self.api_key = getattr(Config, "GEMINI_API_KEY", None) or os.environ.get(
            "GEMINI_API_KEY"
        )
        self.model_name = model_name or DEFAULT_EMBEDDING_MODEL
        self.dimension = EMBEDDING_DIMENSION
        self.index: Optional[faiss.IndexFlatIP] = None
        self.chunks: List[Dict[str, Any]] = []

        self._init_embedder()

    def _init_embedder(self):
        """Khởi tạo client embedding dùng google.genai hoặc google.generativeai."""
        try:
            from google import genai

            if self.api_key:
                self._client = genai.Client(api_key=self.api_key)
            else:
                self._client = None
            self._is_new_sdk = True
        except ImportError:
            import google.generativeai as legacy_genai

            if self.api_key:
                legacy_genai.configure(api_key=self.api_key)
            self._is_new_sdk = False

    def _embed_texts(
        self,
        texts: List[str],
        task_type: Optional[str] = None,
        max_retries: int = 5,
        base_delay: float = 2.0,
    ) -> np.ndarray:
        """
        Gửi batch văn bản lên API để lấy vector embedding.
        Tự động chia batch theo BATCH_SIZE và retry khi gặp 429 / Rate Limit.
        """
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)

        clean_model = (
            self.model_name[len("models/") :]
            if self.model_name.startswith("models/")
            else self.model_name
        )

        all_embeddings: List[List[float]] = []

        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i : i + BATCH_SIZE]
            batch_success = False
            last_err = None

            for attempt in range(max_retries):
                try:
                    if self._is_new_sdk:
                        if not hasattr(self, "_client") or self._client is None:
                            self._init_embedder()
                        from google.genai import types

                        cfg = types.EmbedContentConfig(
                            task_type=task_type.upper() if task_type else None,
                            output_dimensionality=self.dimension,
                        )
                        contents_batch = [
                            types.Content(parts=[types.Part.from_text(text=t)])
                            for t in batch
                        ]
                        response = self._client.models.embed_content(
                            model=clean_model,
                            contents=contents_batch,
                            config=cfg,
                        )
                        for emb in response.embeddings:
                            all_embeddings.append(emb.values)
                    else:
                        import google.generativeai as legacy_genai

                        for text in batch:
                            res = legacy_genai.embed_content(
                                model=self.model_name,
                                content=text,
                                task_type=task_type,
                            )
                            all_embeddings.append(res["embedding"])

                    batch_success = True
                    break
                except Exception as e:
                    last_err = e
                    err_msg = str(e).lower()
                    if (
                        "429" in err_msg
                        or "quota" in err_msg
                        or "resource_exhausted" in err_msg
                    ):
                        # Tìm thời gian retry do Google khuyến cáo trong thông báo lỗi (vd: 'retry in 48s' hoặc 'retrydelay: 48s')
                        delay_match = re.search(
                            r"retry\s*(?:in|delay)?[:\s]+(\d+(?:\.\d+)?)s?", err_msg
                        )
                        if delay_match:
                            wait_sec = float(delay_match.group(1)) + 3.0
                        else:
                            wait_sec = max(base_delay * (2**attempt) + 5.0, 45.0)

                        logger.warning(
                            "Embedding API gặp 429/quota. Đang ngủ %.1fs để hồi phục quota (lần %d/%d)...",
                            wait_sec,
                            attempt + 1,
                            max_retries,
                        )
                        time.sleep(wait_sec)
                    else:
                        logger.error(
                            "Lỗi không thể phục hồi khi gọi embed_content: %s", e
                        )
                        raise e

            if not batch_success:
                raise last_err or RuntimeError(
                    "Không thể embed batch văn bản sau nhiều lần thử lại."
                )

            # Nghỉ ngắn giữa các batch để giữ an toàn cho quota API
            if i + BATCH_SIZE < len(texts):
                time.sleep(SLEEP_BETWEEN_BATCHES)

        embeddings_np = np.array(all_embeddings, dtype=np.float32)
        # Chuẩn hóa L2 để tích vô hướng Inner Product (IP) tương đương Cosine Similarity
        faiss.normalize_L2(embeddings_np)
        return embeddings_np

    def create_index(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Tạo FAISS index từ danh sách chunks.
        Mỗi chunk có format: {"content": str, "metadata": dict}
        """
        if not chunks:
            logger.warning("create_index được gọi với danh sách chunks rỗng.")
            self.index = faiss.IndexFlatIP(self.dimension)
            self.chunks = []
            return

        self.chunks = list(chunks)
        texts = [c.get("content", "") for c in self.chunks]

        vectors = self._embed_texts(texts, task_type="retrieval_document")

        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(vectors)
        logger.info("Đã tạo FAISS index thành công với %d vectors.", self.index.ntotal)

    def add_chunks(self, new_chunks: List[Dict[str, Any]]) -> None:
        """
        Nạp bổ sung danh sách chunks mới vào FAISS index hiện tại.
        """
        if not new_chunks:
            logger.warning("add_chunks được gọi với danh sách chunks rỗng.")
            return

        if self.index is None:
            self.create_index(new_chunks)
            return

        texts = [c.get("content", "") for c in new_chunks]
        vectors = self._embed_texts(texts, task_type="retrieval_document")

        self.index.add(vectors)
        self.chunks.extend(new_chunks)
        logger.info(
            "Đã nạp bổ sung %d vectors thành công. Tổng số vector hiện tại: %d.",
            len(new_chunks),
            self.index.ntotal,
        )

    def save_index(self, path: str) -> None:
        """
        Lưu index và metadata xuống đĩa.
        Tạo ra 2 file: {path}.faiss (vector) và {path}.pkl (metadata & chunks).
        """
        if self.index is None:
            raise RuntimeError("Chưa có index để lưu. Vui lòng gọi create_index trước.")

        dest_path = Path(path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        faiss_file = str(dest_path.with_suffix(".faiss"))
        pkl_file = str(dest_path.with_suffix(".pkl"))

        # Lưu FAISS index
        faiss.write_index(self.index, faiss_file)

        # Lưu Chunks và Metadata
        data_to_save = {
            "chunks": self.chunks,
            "dimension": self.dimension,
            "model_name": self.model_name,
        }
        with open(pkl_file, "wb") as f:
            pickle.dump(data_to_save, f)

        logger.info("Đã lưu VectorDB ra %s và %s", faiss_file, pkl_file)

    def load_index(self, path: str) -> None:
        """
        Load lại index từ đĩa ({path}.faiss và {path}.pkl).
        """
        dest_path = Path(path)
        faiss_file = dest_path.with_suffix(".faiss")
        pkl_file = dest_path.with_suffix(".pkl")

        # Hỗ trợ nếu path truyền vào là thư mục chứa index.faiss hoặc đường dẫn không đuôi
        if not faiss_file.exists() and dest_path.is_dir():
            faiss_file = dest_path / "index.faiss"
            pkl_file = dest_path / "index.pkl"

        if not faiss_file.exists() or not pkl_file.exists():
            raise FileNotFoundError(
                f"Không tìm thấy index tại '{path}'. Cần có cả file .faiss và .pkl."
            )

        self.index = faiss.read_index(str(faiss_file))

        with open(pkl_file, "rb") as f:
            data = pickle.load(f)
            self.chunks = data.get("chunks", [])
            self.dimension = data.get("dimension", EMBEDDING_DIMENSION)
            self.model_name = data.get("model_name", self.model_name)

        logger.info(
            "Đã nạp VectorDB thành công từ '%s' (%d vectors, %d chunks).",
            path,
            self.index.ntotal,
            len(self.chunks),
        )

    def search_with_metadata(
        self,
        query: str,
        metadata_filter: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm semantic kết hợp lọc siêu dữ liệu (Metadata Filtering) theo số Điều/Khoản.
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("VectorDB đang rỗng hoặc chưa nạp index.")
            return []

        # 1. Embed query
        query_vec = self._embed_texts([query], task_type="retrieval_query")

        # 2. Lấy dư ứng viên để khi filter không bị hụt kết quả
        search_k = min(self.index.ntotal, max(top_k * 4, 20))
        distances, indices = self.index.search(query_vec, search_k)

        results = []
        raw_distances = distances[0]
        raw_indices = indices[0]

        for score, idx in zip(raw_distances, raw_indices):
            if idx < 0 or idx >= len(self.chunks):
                continue

            chunk = self.chunks[idx]
            chunk_metadata = chunk.get("metadata", {})

            # Áp dụng Metadata Filtering (nếu có)
            if metadata_filter:
                match = True
                for f_key, f_val in metadata_filter.items():
                    target_val = chunk_metadata.get(f_key)
                    if target_val is None:
                        # Thử lấy từ các alias phổ biến (article vs article_number)
                        if f_key == "article":
                            target_val = chunk_metadata.get("article_number")
                        elif f_key == "article_number":
                            target_val = chunk_metadata.get("article")

                    if (
                        target_val != f_val
                        and str(target_val).lower() != str(f_val).lower()
                    ):
                        match = False
                        break
                if not match:
                    continue

            result_item = {
                "content": chunk.get("content", ""),
                "metadata": dict(chunk_metadata),
                "score": float(score),
            }
            results.append(result_item)

            if len(results) >= top_k:
                break

        return results

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Interface chuẩn tương thích với các module gọi (drafting/retrieval, chatbot_qa/retrieval).
        Thực hiện Semantic Search kết hợp Metadata Filtering theo SRS 5.1 & 6.2.
        """
        return self.search_with_metadata(
            query=query, metadata_filter=metadata_filter, top_k=top_k
        )
