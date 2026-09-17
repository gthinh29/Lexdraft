"""tests/test_shared/test_vector_db.py

Unit tests for modules.shared.embedding.VectorDB.
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# Mock faiss before importing embedding module to avoid ModuleNotFoundError
if "faiss" not in sys.modules:
    import types as _types

    _faiss = _types.ModuleType("faiss")

    class _FaissIndex:
        def __init__(self, dim, count=0):
            self.d = dim
            self._vecs = [0] * count

        @property
        def ntotal(self):
            return len(self._vecs)

        def add(self, vecs):
            self._vecs.extend(vecs.tolist())

        def search(self, query, k):
            n = min(k, len(self._vecs))
            indices = list(range(n))
            distances = [0.9] * n
            import numpy as np  # noqa: PLC0415

            return np.array([distances], dtype=np.float32), np.array(
                [indices], dtype=np.int64
            )

    def _write_index(index, path):
        Path(path).write_bytes(b"mock_faiss_data")

    _faiss.IndexFlatL2 = _FaissIndex
    _faiss.IndexFlatIP = _FaissIndex  # embedding.py dùng IndexFlatIP
    _faiss.normalize_L2 = MagicMock()
    _faiss.write_index = _write_index
    _faiss.read_index = lambda path: _FaissIndex(768, count=3)
    sys.modules["faiss"] = _faiss

from modules.shared.embedding import VectorDB  # noqa: E402


class TestVectorDB:
    """Test suite for VectorDB and FAISS indexing."""

    @pytest.fixture
    def mock_embeddings(self):
        """Tạo vector giả lập 768 chiều được chuẩn hóa L2."""

        def _make_vecs(texts, **kwargs):
            n = len(texts)
            vecs = np.random.randn(n, 768).astype(np.float32)
            # Normalize L2
            norms = np.linalg.norm(vecs, axis=1, keepdims=True)
            return vecs / np.maximum(norms, 1e-12)

        return _make_vecs

    def test_init_vector_db(self):
        """Kiểm tra khởi tạo VectorDB."""
        db = VectorDB()
        assert db.dimension == 768
        assert db.index is None
        assert db.chunks == []

    def test_create_and_search_index(self, sample_law_chunks, mock_embeddings):
        """Kiểm tra tạo index và tìm kiếm vector với mock embedding."""
        db = VectorDB()

        with patch.object(db, "_embed_texts", side_effect=mock_embeddings):
            db.create_index(sample_law_chunks)

            assert db.index is not None
            assert db.index.ntotal == len(sample_law_chunks)

            # Tìm kiếm không filter
            results = db.search_with_metadata("hợp đồng dịch vụ", top_k=2)
            assert len(results) <= 2
            assert "score" in results[0]
            assert "content" in results[0]

            # Tìm kiếm có filter metadata
            filtered = db.search_with_metadata(
                "phạt vi phạm",
                metadata_filter={"law_name": "Bộ luật Dân sự 2015"},
                top_k=2,
            )
            for item in filtered:
                assert item.get("metadata", {}).get("law_name") == "Bộ luật Dân sự 2015"

    def test_save_and_load_index(self, sample_law_chunks, mock_embeddings):
        """Kiểm tra lưu và nạp lại FAISS index cùng metadata từ đĩa."""
        db = VectorDB()
        with patch.object(db, "_embed_texts", side_effect=mock_embeddings):
            db.create_index(sample_law_chunks)

            with tempfile.TemporaryDirectory() as tmpdir:
                save_path = Path(tmpdir) / "test_db"
                db.save_index(str(save_path))

                assert (Path(tmpdir) / "test_db.faiss").exists()
                assert (Path(tmpdir) / "test_db.pkl").exists()

                # Nạp vào DB mới
                db_loaded = VectorDB()
                db_loaded.load_index(str(save_path))

                assert db_loaded.index.ntotal == len(sample_law_chunks)
                assert len(db_loaded.chunks) == len(sample_law_chunks)

    def test_load_non_existent_index(self):
        """Kiểm tra ném lỗi FileNotFoundError khi file index không tồn tại."""
        db = VectorDB()
        with pytest.raises(FileNotFoundError, match="Không tìm thấy index tại"):
            db.load_index("non_existent_faiss_db_path")

    def test_search_empty_db(self):
        """Kiểm tra tìm kiếm trên DB rỗng trả về list rỗng."""
        db = VectorDB()
        results = db.search_with_metadata("câu hỏi bất kỳ")
        assert results == []
