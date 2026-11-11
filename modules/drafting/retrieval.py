"""Truy xuất khung hợp đồng chuẩn (template_index) và điều luật liên quan (law_index) từ FAISS."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import config
from modules.drafting.taxonomy import (
    get_category_config,
    get_stance_config,
    load_contract_taxonomy,
)

try:
    from modules.shared.embedding import VectorDB
except ImportError:
    VectorDB = None

logger = logging.getLogger(__name__)

_template_db = None
_law_db = None

__all__ = [
    "retrieve_template",
    "retrieve_relevant_law",
    "load_contract_taxonomy",
    "get_category_config",
    "get_stance_config",
]


def _get_template_db():
    global _template_db
    if _template_db is None:
        if VectorDB is None:
            raise RuntimeError("modules.shared.embedding.VectorDB chưa sẵn sàng.")
        index_dir = Path(getattr(config, "FAISS_INDEX_DIR", "data/faiss_index"))
        _template_db = VectorDB()
        _template_db.load_index(str(index_dir / "template_index"))
    return _template_db


def _get_law_db():
    global _law_db
    if _law_db is None:
        if VectorDB is None:
            raise RuntimeError("modules.shared.embedding.VectorDB chưa sẵn sàng.")
        index_dir = Path(getattr(config, "FAISS_INDEX_DIR", "data/faiss_index"))
        _law_db = VectorDB()
        _law_db.load_index(str(index_dir / "law_index"))
    return _law_db


def _chunk_dedup_key(chunk: Dict[str, Any]) -> tuple:
    meta = chunk.get("metadata", {})
    return (
        meta.get("source", ""),
        meta.get("article", ""),
        chunk.get("content", "")[:60],
    )


def _batch_search_laws(
    db: Any, all_queries: List[str], top_k_per_q: List[int]
) -> List[Dict[str, Any]]:
    """Thực hiện tìm kiếm vector cho nhiều truy vấn trong một lần gọi batch embedding."""
    q_vecs = db._embed_texts(all_queries, task_type="retrieval_query")
    search_k = min(db.index.ntotal, max(max(top_k_per_q) * 2, 12))
    distances, indices = db.index.search(q_vecs, search_k)

    merged_hits: List[Dict[str, Any]] = []
    seen_keys = set()
    for row_idx, k_want in enumerate(top_k_per_q):
        added = 0
        for score, chunk_idx in zip(distances[row_idx], indices[row_idx]):
            if chunk_idx < 0 or chunk_idx >= len(db.chunks):
                continue
            chunk = db.chunks[chunk_idx]
            key = _chunk_dedup_key(chunk)
            if key not in seen_keys:
                seen_keys.add(key)
                merged_hits.append(
                    {
                        "content": chunk.get("content", ""),
                        "metadata": dict(chunk.get("metadata", {})),
                        "score": float(score),
                    }
                )
            added += 1
            if added >= k_want:
                break
    return merged_hits


def retrieve_template(
    contract_type_query: str, top_k: int = 1
) -> Optional[Dict[str, Any]]:
    """Lấy khung điều khoản chuẩn theo Taxonomy hoặc fallback về FAISS template_index."""
    cat_cfg = get_category_config(contract_type_query)
    if cat_cfg:
        clauses_str = "\n".join(
            f"- {clause}" for clause in cat_cfg.get("mandatory_clauses", [])
        )
        laws_str = "\n".join(
            f"- Căn cứ {law};" for law in cat_cfg.get("governing_laws", [])
        )
        skeleton = (
            f"TIÊU ĐỀ CHUẨN: {cat_cfg.get('contract_title_upper', 'HỢP ĐỒNG DỊCH VỤ')}\n"
            f"PHÂN LOẠI NGHIỆP VỤ: {cat_cfg.get('name', '')}\n\n"
            f"DANH MỤC CĂN CỨ PHÁP LÝ BẮT BUỘC CHO LOẠI HỢP ĐỒNG NÀY:\n{laws_str}\n\n"
            f"KHUNG CẤU TRÚC ĐIỀU KHOẢN BẮT BUỘC (CLAUSE PLAYBOOK):\n{clauses_str}"
        )
        return {
            "content": skeleton,
            "metadata": {
                "template_type": cat_cfg.get("id", "dich_vu"),
                "category_name": cat_cfg.get("name", ""),
            },
        }

    try:
        hits = _get_template_db().hybrid_search(contract_type_query, top_k=top_k)
        return hits[0] if hits else None
    except Exception:
        logger.warning(
            "Không thể truy xuất từ template_index cho query: '%s'", contract_type_query
        )
    return None


def retrieve_relevant_law(
    query: str,
    top_k: Optional[int] = None,
    category_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Truy xuất đa truy vấn (Multi-query RAG) các điều luật liên quan từ law_index."""
    limit = top_k or getattr(getattr(config, "Config", config), "RETRIEVAL_TOP_K", 10)
    db = _get_law_db()

    cat_cfg = get_category_config(category_id or query)
    rag_queries = cat_cfg.get("rag_queries", []) if cat_cfg else []
    if not rag_queries:
        return db.hybrid_search(query, top_k=limit)

    per_query_k = max(2, limit // max(len(rag_queries), 1))
    all_queries = list(rag_queries) + [query]
    top_k_per_q = [per_query_k] * len(rag_queries) + [4]

    can_batch = (
        getattr(db, "index", None) is not None
        and getattr(db, "chunks", None)
        and callable(getattr(db, "_embed_texts", None))
        and type(db).__name__ == "VectorDB"
    )
    if can_batch:
        try:
            hits = _batch_search_laws(db, all_queries, top_k_per_q)
            hits.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            return hits[: max(limit, 10)]
        except Exception as e:
            logger.warning("Batch embedding fallback sang tìm kiếm tuần tự: %s", e)

    merged_hits: List[Dict[str, Any]] = []
    seen_keys = set()
    for sub_q, k_want in zip(all_queries, top_k_per_q):
        for h in db.hybrid_search(sub_q, top_k=k_want):
            key = _chunk_dedup_key(h)
            if key not in seen_keys:
                seen_keys.add(key)
                merged_hits.append(h)

    merged_hits.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return merged_hits[: max(limit, 10)]
