"""
modules/drafting/retrieval.py
Truy vấn danh mục phân loại hợp đồng (Contract Taxonomy) và điều khoản pháp luật tham chiếu
cho phân hệ hỗ trợ soạn thảo hợp đồng.
"""

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

# Cache module-level: cả index và taxonomy đều tĩnh, chỉ cần load 1 lần.
_template_db = None
_law_db = None
_taxonomy_cache: Optional[Dict[str, Any]] = None

_TAXONOMY_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "contract_taxonomy.json"
)


def load_contract_taxonomy() -> Dict[str, Any]:
    """
    Đọc và cache cấu hình Phân loại Hợp đồng Dịch vụ & Vị thế Đàm phán từ contract_taxonomy.json.
    """
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
    """
    Tìm cấu hình phân loại hợp đồng theo ID (vd: 'software_dev') hoặc theo tên/từ khóa.
    """
    taxonomy = load_contract_taxonomy()
    categories = taxonomy.get("categories", {})
    if not categories:
        return None

    # 1. Khớp chính xác theo ID
    if category_id_or_query in categories:
        return categories[category_id_or_query]

    # 2. Khớp mềm theo từ khóa trong tên hợp đồng
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

    # Fallback về loại đầu tiên nếu không khớp từ khóa đặc thù
    return None


def get_stance_config(stance_id: str) -> Dict[str, Any]:
    """
    Lấy cấu hình Vị thế Bảo vệ Pháp lý ('protect_party_a', 'protect_party_b', 'balanced').
    """
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
            raise RuntimeError(
                "modules.shared.embedding.VectorDB chưa sẵn sàng (Phần 4 chưa build)."
            )
        index_dir = Path(getattr(config, "FAISS_INDEX_DIR", "data/faiss_index"))
        _template_db = VectorDB()
        _template_db.load_index(str(index_dir / "template_index"))
    return _template_db


def _get_law_db():
    global _law_db
    if _law_db is None:
        if VectorDB is None:
            raise RuntimeError(
                "modules.shared.embedding.VectorDB chưa sẵn sàng (Phần 4 chưa build)."
            )
        index_dir = Path(getattr(config, "FAISS_INDEX_DIR", "data/faiss_index"))
        _law_db = VectorDB()
        _law_db.load_index(str(index_dir / "law_index"))
    return _law_db


def retrieve_template(
    contract_type_query: str, top_k: int = 1
) -> Optional[Dict[str, Any]]:
    """
    Lấy cấu trúc mẫu hợp đồng chuẩn theo Phân loại (Taxonomy) hoặc fallback về template_index.
    """
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
    """
    Lấy các điều luật liên quan từ law_index để làm căn cứ soạn thảo.
    Hỗ trợ Multi-query RAG theo Phân loại hợp đồng (Taxonomy) để bao phủ toàn diện
    các điều luật về quyền/nghĩa vụ, sở hữu trí tuệ, dữ liệu cá nhân và chế tài phạt 8%.
    """
    limit = top_k or getattr(getattr(config, "Config", config), "RETRIEVAL_TOP_K", 10)
    db = _get_law_db()

    cat_cfg = get_category_config(category_id or query)
    rag_queries = cat_cfg.get("rag_queries", []) if cat_cfg else []

    if not rag_queries:
        return db.hybrid_search(query, top_k=limit)

    merged_hits: List[Dict[str, Any]] = []
    seen_keys = set()

    # 1. Truy xuất theo từng nhóm chủ đề pháp lý trọng tâm của loại hợp đồng đó
    per_query_k = max(2, limit // max(len(rag_queries), 1))
    for sub_q in rag_queries:
        hits = db.hybrid_search(sub_q, top_k=per_query_k)
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

    # 2. Bổ sung truy xuất trực tiếp từ query/yêu cầu riêng của người dùng
    direct_hits = db.hybrid_search(query, top_k=4)
    for h in direct_hits:
        meta = h.get("metadata", {})
        key = (
            meta.get("source", ""),
            meta.get("article", ""),
            h.get("content", "")[:60],
        )
        if key not in seen_keys:
            seen_keys.add(key)
            merged_hits.append(h)

    # Sắp xếp giảm dần theo điểm tương đồng Cosine
    merged_hits.sort(key=lambda x: x.get("score", 0.0), reverse=True)
    return merged_hits[: max(limit, 10)]
