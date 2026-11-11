"""Quản lý FAISS Vector Database và tạo vector embedding qua Google Gemini API."""

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
    Config, "EMBEDDING_MODEL_NAME", "models/gemini-embedding-002"
)
EMBEDDING_DIMENSION = 768
BATCH_SIZE = 15
SLEEP_BETWEEN_BATCHES = 1.0


def _matches_metadata_filter(
    chunk_metadata: Dict[str, Any], metadata_filter: Dict[str, Any]
) -> bool:
    """Kiểm tra metadata của một chunk có khớp với bộ lọc đầu vào hay không."""
    for f_key, f_val in metadata_filter.items():
        target_val = chunk_metadata.get(f_key)
        if target_val is None:
            if f_key == "article":
                target_val = chunk_metadata.get("article_number")
            elif f_key == "article_number":
                target_val = chunk_metadata.get("article")

        if target_val != f_val and str(target_val).lower() != str(f_val).lower():
            return False
    return True


class VectorDB:
    """Quản lý chỉ mục FAISS kết hợp lưu trữ Metadata và tìm kiếm ngữ nghĩa."""

    def __init__(self, model_name: Optional[str] = None):
        self.api_key = getattr(Config, "GEMINI_API_KEY", None) or os.environ.get(
            "GEMINI_API_KEY"
        )
        self.model_name = model_name or DEFAULT_EMBEDDING_MODEL
        self.dimension = EMBEDDING_DIMENSION
        self.index: Optional[faiss.IndexFlatIP] = None
        self.chunks: List[Dict[str, Any]] = []
        self._init_embedder()

    def _init_embedder(self) -> None:
        try:
            from google import genai

            self._client = genai.Client(api_key=self.api_key) if self.api_key else None
            self._is_new_sdk = True
        except ImportError:
            import google.generativeai as legacy_genai  # type: ignore

            if self.api_key:
                legacy_genai.configure(api_key=self.api_key)
            self._is_new_sdk = False

    def _call_embed_batch(
        self, batch: List[str], clean_model: str, task_type: Optional[str]
    ) -> List[List[float]]:
        """Gọi API embedding cho một lô văn bản."""
        if self._is_new_sdk:
            if not hasattr(self, "_client") or self._client is None:
                self._init_embedder()
            from google.genai import types

            cfg = types.EmbedContentConfig(
                task_type=task_type.upper() if task_type else None,
                output_dimensionality=self.dimension,
            )
            contents_batch = [
                types.Content(parts=[types.Part.from_text(text=t)]) for t in batch
            ]
            response = self._client.models.embed_content(
                model=clean_model,
                contents=contents_batch,
                config=cfg,
            )
            return [emb.values for emb in response.embeddings]

        import google.generativeai as legacy_genai  # type: ignore

        return [
            legacy_genai.embed_content(
                model=self.model_name, content=text, task_type=task_type
            )["embedding"]
            for text in batch
        ]

    def _embed_texts(
        self,
        texts: List[str],
        task_type: Optional[str] = None,
        max_retries: int = 5,
        base_delay: float = 2.0,
    ) -> np.ndarray:
        """Tạo vector embedding chuẩn hóa L2 cho danh sách văn bản kèm cơ chế retry khi gặp 429."""
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
                    all_embeddings.extend(
                        self._call_embed_batch(batch, clean_model, task_type)
                    )
                    batch_success = True
                    break
                except Exception as e:
                    last_err = e
                    err_msg = str(e).lower()
                    if any(
                        k in err_msg for k in ("429", "quota", "resource_exhausted")
                    ):
                        delay_match = re.search(
                            r"retry\s*(?:in|delay)?[:\s]+(\d+(?:\.\d+)?)s?", err_msg
                        )
                        wait_sec = (
                            float(delay_match.group(1)) + 3.0
                            if delay_match
                            else max(base_delay * (2**attempt) + 5.0, 45.0)
                        )
                        logger.warning(
                            "Embedding API rate limit. Chờ %.1fs (lần %d/%d)...",
                            wait_sec,
                            attempt + 1,
                            max_retries,
                        )
                        time.sleep(wait_sec)
                    else:
                        logger.error("Lỗi khi gọi embed_content: %s", e)
                        raise

            if not batch_success:
                raise last_err or RuntimeError(
                    "Không thể embed batch văn bản sau nhiều lần thử lại."
                )

            if i + BATCH_SIZE < len(texts):
                time.sleep(SLEEP_BETWEEN_BATCHES)

        embeddings_np = np.array(all_embeddings, dtype=np.float32)
        faiss.normalize_L2(embeddings_np)
        return embeddings_np

    def create_index(self, chunks: List[Dict[str, Any]]) -> None:
        """Xây dựng mới FAISS index từ danh sách chunks."""
        if not chunks:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.chunks = []
            return

        self.chunks = list(chunks)
        texts = [c.get("content", "") for c in self.chunks]
        vectors = self._embed_texts(texts, task_type="retrieval_document")

        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(vectors)

    def add_chunks(self, new_chunks: List[Dict[str, Any]]) -> None:
        """Nạp bổ sung danh sách chunks mới vào FAISS index hiện có."""
        if not new_chunks:
            return
        if self.index is None:
            self.create_index(new_chunks)
            return

        texts = [c.get("content", "") for c in new_chunks]
        vectors = self._embed_texts(texts, task_type="retrieval_document")
        self.index.add(vectors)
        self.chunks.extend(new_chunks)

    def save_index(self, path: str) -> None:
        """Lưu FAISS index (.faiss) và metadata chunks (.pkl) ra đĩa."""
        if self.index is None:
            raise RuntimeError("Chưa có index để lưu. Vui lòng gọi create_index trước.")

        dest_path = Path(path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(dest_path.with_suffix(".faiss")))

        with open(dest_path.with_suffix(".pkl"), "wb") as f:
            pickle.dump(
                {
                    "chunks": self.chunks,
                    "dimension": self.dimension,
                    "model_name": self.model_name,
                },
                f,
            )

    def load_index(self, path: str) -> None:
        """Nạp lại FAISS index và metadata từ đĩa."""
        dest_path = Path(path)
        faiss_file = dest_path.with_suffix(".faiss")
        pkl_file = dest_path.with_suffix(".pkl")

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

    def search_with_metadata(
        self,
        query: str,
        metadata_filter: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """Tìm kiếm tương đồng ngữ nghĩa kết hợp lọc siêu dữ liệu."""
        if self.index is None or self.index.ntotal == 0:
            return []

        query_vec = self._embed_texts([query], task_type="retrieval_query")
        search_k = min(self.index.ntotal, max(top_k * 4, 20))
        distances, indices = self.index.search(query_vec, search_k)

        results = []
        for score, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.chunks):
                continue

            chunk = self.chunks[idx]
            chunk_metadata = chunk.get("metadata", {})
            if metadata_filter and not _matches_metadata_filter(
                chunk_metadata, metadata_filter
            ):
                continue

            results.append(
                {
                    "content": chunk.get("content", ""),
                    "metadata": dict(chunk_metadata),
                    "score": float(score),
                }
            )
            if len(results) >= top_k:
                break

        return results

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Thực hiện tìm kiếm vector kết hợp lọc metadata."""
        return self.search_with_metadata(
            query=query, metadata_filter=metadata_filter, top_k=top_k
        )
