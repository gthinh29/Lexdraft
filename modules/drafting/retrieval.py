"""Truy vấn danh mục Phân loại Hợp đồng (Contract Taxonomy) và điều khoản pháp luật tham chiếu."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from modules.shared.embedding import VectorDB
except ImportError:
    VectorDB = None

import config

logger = logging.getLogger(__name__)

_template_db = None
_law_db = None
_taxonomy_cache: Optional[Dict[str, Any]] = None

_TAXONOMY_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "contract_taxonomy.json"
)


def load_contract_taxonomy() -> Dict[str, Any]:
    """Đọc và lưu bộ nhớ đệm cấu hình Phân loại Hợp đồng & Vị thế Pháp lý."""
    global _taxonomy_cache
    if _taxonomy_cache is not None:
        return _taxonomy_cache

    if not _TAXONOMY_PATH.exists():
        logger.warning(
            "Không tìm thấy file contract_taxonomy.json tại %s", _TAXONOMY_PATH
        )
        _taxonomy_cache = {"stances": {}, "categories": {}}
        return _taxonomy_cache

    try:
        with open(_TAXONOMY_PATH, encoding="utf-8") as f:
            _taxonomy_cache = json.load(f)
    except Exception as e:
        logger.exception("Lỗi khi đọc contract_taxonomy.json: %s", e)
        _taxonomy_cache = {"stances": {}, "categories": {}}

    return _taxonomy_cache


def get_category_config(category_id_or_query: str) -> Optional[Dict[str, Any]]:
    """Tìm cấu hình phân loại hợp đồng theo ID hoặc theo từ khóa trong tiêu đề."""
    taxonomy = load_contract_taxonomy()
    categories = taxonomy.get("categories", {})
    if not categories:
        return None

    if category_id_or_query in categories:
        return categories[category_id_or_query]

    q_lower = (category_id_or_query or "").lower()
    keyword_map = [
        (
            "software_dev",
            ["phần mềm", "software", "erp", "lập trình", "cntt", "code", "ứng dụng"],
        ),
        (
            "web_design",
            [
                "website",
                "trang web",
                "web",
                "hosting",
                "tên miền",
                "domain",
                "giao diện",
            ],
        ),
        (
            "digital_marketing",
            [
                "marketing",
                "quảng cáo",
                "tiếp thị",
                "kol",
                "truyền thông",
                "seo",
                "fanpage",
            ],
        ),
        (
            "cloud_saas",
            ["cloud", "đám mây", "saas", "máy chủ", "server", "hạ tầng", "ai"],
        ),
        (
            "consulting_freelance",
            ["tư vấn", "cá nhân", "freelance", "chuyên gia", "thuê ngoài", "đào tạo"],
        ),
    ]
    for cat_id, kws in keyword_map:
        if cat_id in categories and any(kw in q_lower for kw in kws):
            return categories[cat_id]

    return None


def get_stance_config(stance_id: str) -> Dict[str, Any]:
    """Lấy cấu hình Vị thế Bảo vệ Pháp lý ('protect_party_a', 'protect_party_b', 'balanced')."""
    taxonomy = load_contract_taxonomy()
    stances = taxonomy.get("stances", {})
    if stance_id in stances:
        return stances[stance_id]
    return stances.get(
        "balanced",
        {
            "label": "⚖️ Cân bằng lợi ích hai bên",
            "short_name": "Cân bằng hai bên",
            "drafting_directives": [],
        },
    )


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


def retrieve_template(
    contract_type_query: str, top_k: int = 1
) -> Optional[Dict[str, Any]]:
    """Lấy khung điều khoản chuẩn theo Phân loại (Taxonomy) hoặc fallback về template_index."""
    cat_cfg = get_category_config(contract_type_query)
    if cat_cfg:
        clauses_str = "\n".join(
            f"- {clause}" for clause in cat_cfg.get("mandatory_clauses", [])
        )
        laws_str = "\n".join(
            f"- Căn cứ {law};" for law in cat_cfg.get("governing_laws", [])
        )
        structured_skeleton = (
            f"TIÊU ĐỀ CHUẨN: {cat_cfg.get('contract_title_upper', 'HỢP ĐỒNG DỊCH VỤ')}\n"
            f"PHÂN LOẠI NGHIỆP VỤ: {cat_cfg.get('name', '')}\n\n"
            f"DANH MỤC CĂN CỨ PHÁP LÝ BẮT BUỘC CHO LOẠI HỢP ĐỒNG NÀY:\n{laws_str}\n\n"
            f"KHUNG CẤU TRÚC ĐIỀU KHOẢN BẮT BUỘC (CLAUSE PLAYBOOK):\n{clauses_str}"
        )
        return {
            "content": structured_skeleton,
            "metadata": {
                "template_type": cat_cfg.get("id", "dich_vu"),
                "category_name": cat_cfg.get("name", ""),
            },
        }

    try:
        db = _get_template_db()
        hits = db.hybrid_search(contract_type_query, top_k=top_k)
        if hits:
            return hits[0]
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

    merged_hits: List[Dict[str, Any]] = []
    seen_keys = set()
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
            q_vecs = db._embed_texts(all_queries, task_type="retrieval_query")
            search_k = min(db.index.ntotal, max(max(top_k_per_q) * 2, 12))
            distances, indices = db.index.search(q_vecs, search_k)
            for row_idx, k_want in enumerate(top_k_per_q):
                added = 0
                for score, chunk_idx in zip(distances[row_idx], indices[row_idx]):
                    if chunk_idx < 0 or chunk_idx >= len(db.chunks):
                        continue
                    chunk = db.chunks[chunk_idx]
                    meta = chunk.get("metadata", {})
                    key = (
                        meta.get("source", ""),
                        meta.get("article", ""),
                        chunk.get("content", "")[:60],
                    )
                    if key not in seen_keys:
                        seen_keys.add(key)
                        merged_hits.append(
                            {
                                "content": chunk.get("content", ""),
                                "metadata": dict(meta),
                                "score": float(score),
                            }
                        )
                    added += 1
                    if added >= k_want:
                        break
            merged_hits.sort(key=lambda x: x.get("score", 0.0), reverse=True)
            return merged_hits[: max(limit, 10)]
        except Exception as e:
            logger.warning(
                "Batch embedding fallback sang hybrid_search từng câu: %s", e
            )

    for sub_q, k_want in zip(all_queries, top_k_per_q):
        hits = db.hybrid_search(sub_q, top_k=k_want)
        for h in hits:
            meta = h.get("metadata", {})
            key = (
                meta.get("source", ""),
                meta.get("article", ""),
                h.get("content", "")[:60],
            )
            if key not in seen_keys:
                seen_keys.add(key)
                merged_hits.append(h)

    merged_hits.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return merged_hits[: max(limit, 10)]
