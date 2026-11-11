"""Đọc và tra cứu Danh mục Phân loại Hợp đồng (Taxonomy) và Vị thế Bảo vệ Pháp lý (Stance)."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_TAXONOMY_PATH = (
    Path(__file__).resolve().parent.parent.parent / "data" / "contract_taxonomy.json"
)
_taxonomy_cache: Optional[Dict[str, Any]] = None

_KEYWORD_CATEGORY_MAP = [
    (
        "software_dev",
        ["phần mềm", "software", "erp", "lập trình", "cntt", "code", "ứng dụng"],
    ),
    (
        "web_design",
        ["website", "trang web", "web", "hosting", "tên miền", "domain", "giao diện"],
    ),
    (
        "digital_marketing",
        ["marketing", "quảng cáo", "tiếp thị", "kol", "truyền thông", "seo", "fanpage"],
    ),
    ("cloud_saas", ["cloud", "đám mây", "saas", "máy chủ", "server", "hạ tầng", "ai"]),
    (
        "consulting_freelance",
        ["tư vấn", "cá nhân", "freelance", "chuyên gia", "thuê ngoài", "đào tạo"],
    ),
]


def load_contract_taxonomy() -> Dict[str, Any]:
    """Đọc và lưu bộ nhớ đệm cấu hình Phân loại Hợp đồng & Vị thế Pháp lý từ JSON."""
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
    categories = load_contract_taxonomy().get("categories", {})
    if not categories:
        return None

    if category_id_or_query in categories:
        return categories[category_id_or_query]

    q_lower = (category_id_or_query or "").lower()
    for cat_id, kws in _KEYWORD_CATEGORY_MAP:
        if cat_id in categories and any(kw in q_lower for kw in kws):
            return categories[cat_id]

    return None


def get_stance_config(stance_id: str) -> Dict[str, Any]:
    """Lấy cấu hình Vị thế Bảo vệ Pháp lý ('protect_party_a', 'protect_party_b', 'balanced')."""
    stances = load_contract_taxonomy().get("stances", {})
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
