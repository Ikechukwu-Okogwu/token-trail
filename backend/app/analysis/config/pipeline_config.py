"""
Tokenize similarity pipeline configuration: meta.json → in-memory ``TokenizePipelineConfig``.

Runtime config holds loaded objects only (no file paths). Per-language default bundles
are listed in ``default_metas.json`` next to this package. The active bundle for Java-only
helpers is still selected via ``currently_using_meta``.
"""

from __future__ import annotations

import csv
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.analysis.tree_sitter_analysis.tokenize_workflow.group_analysis import (
    GroupFilterConfig,
    load_group_filter_config,
    load_type_mapping_csv,
)
from app.analysis.tree_sitter_analysis.tokenize_workflow.json_kgram_strategy import (
    JsonLeafKgramStrategy,
)

CONFIG_PACKAGE_DIR = Path(__file__).resolve().parent
BUNDLES_DIR = CONFIG_PACKAGE_DIR / "bundles"
CURRENTLY_USING_META_FILENAME = "currently_using_meta"
DEFAULT_METAS_FILENAME = "default_metas.json"

STRATEGY_JSON_LEAF = "json_leaf"

# Tokenizer languages; default bundle folder per language comes from ``default_metas.json``.
SUPPORTED_TOKENIZE_LANGUAGES: frozenset[str] = frozenset({"java", "c", "cpp"})


@dataclass(frozen=True)
class TokenizePipelineConfig:
    """Fully-resolved settings for :func:`run_tokenize_similarity_pipeline`."""

    type_mapping: Mapping[str, frozenset[str]]
    group_filter_config: GroupFilterConfig
    strategy: str
    k: int
    winnow_window: int
    max_pos_each: int
    min_group_size: int
    delta_tol: int
    max_gap: int
    default_categories: tuple[str, ...]


def _currently_using_meta_file() -> Path:
    return CONFIG_PACKAGE_DIR / CURRENTLY_USING_META_FILENAME


def _default_metas_file() -> Path:
    return CONFIG_PACKAGE_DIR / DEFAULT_METAS_FILENAME


def _bundle_folder_from_default_metas(language: str) -> str:
    """Resolve training bundle folder name under ``bundles/`` from ``default_metas.json``."""
    lang = (language or "").strip().lower()
    if lang not in SUPPORTED_TOKENIZE_LANGUAGES:
        raise ValueError(
            f"unsupported tokenize language {language!r}; "
            f"expected one of {sorted(SUPPORTED_TOKENIZE_LANGUAGES)}"
        )
    meta_file = _default_metas_file()
    if not meta_file.is_file():
        raise FileNotFoundError(
            f"missing {DEFAULT_METAS_FILENAME} (expected paths to default bundles under {CONFIG_PACKAGE_DIR})"
        )
    raw: Any = json.loads(meta_file.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{DEFAULT_METAS_FILENAME} must be a JSON object")
    entry = raw.get(lang)
    if not isinstance(entry, str) or not entry.strip():
        raise ValueError(
            f"{DEFAULT_METAS_FILENAME} must set a non-empty string for language {lang!r}"
        )
    return entry.strip()


def default_bundle_meta_path_for_language(language: str) -> Path:
    """
    Return ``bundles/<folder>/meta.json`` where ``folder`` is read from ``default_metas.json``.

    Raises:
        ValueError: if ``language`` is not a supported tokenize language or JSON entry is invalid.
        FileNotFoundError: if ``default_metas.json`` or the resolved ``meta.json`` is missing.
    """
    lang = (language or "").strip().lower()
    folder = _bundle_folder_from_default_metas(language)
    p = (BUNDLES_DIR / folder / "meta.json").resolve()
    if not p.is_file():
        raise FileNotFoundError(
            f"bundle meta.json not found for language={lang!r} (folder={folder!r}): {p}"
        )
    return p


def load_tokenize_pipeline_config_for_language(language: str) -> TokenizePipelineConfig:
    """Load :class:`TokenizePipelineConfig` from :func:`default_bundle_meta_path_for_language`."""
    return load_tokenize_pipeline_config_from_meta_json(
        default_bundle_meta_path_for_language(language)
    )


def resolve_active_meta_json_path() -> Path:
    """
    Read ``app/analysis/config/currently_using_meta``: first non-empty, non-comment line
    is a path to ``meta.json``, relative to ``app/analysis/config/`` if not absolute.
    """
    raw = _currently_using_meta_file().read_text(encoding="utf-8")
    lines = [
        ln.strip()
        for ln in raw.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    if not lines:
        raise ValueError(
            f"{CURRENTLY_USING_META_FILENAME} has no pointer line "
            f"(expected path to meta.json under {CONFIG_PACKAGE_DIR})"
        )
    rel = lines[0]
    p = Path(rel)
    if not p.is_absolute():
        p = CONFIG_PACKAGE_DIR / p
    p = p.resolve()
    if not p.is_file():
        raise FileNotFoundError(f"meta.json not found: {p}")
    return p


def load_tokenize_pipeline_config_from_meta_json(meta_json: Path) -> TokenizePipelineConfig:
    """Load bundle ``meta.json`` and referenced CSV/JSON paths (relative to ``meta.json`` parent)."""
    bundle_root = meta_json.parent
    data: dict[str, Any] = json.loads(meta_json.read_text(encoding="utf-8"))

    strategy = data.get("strategy")
    if strategy is None:
        raise ValueError("meta.json must include non-null 'strategy'")
    strategy = str(strategy)
    if strategy != STRATEGY_JSON_LEAF:
        raise ValueError(
            f"unsupported strategy {strategy!r}; only {STRATEGY_JSON_LEAF!r} is implemented"
        )
    k = int(data["k"])
    winnow_window = int(data.get("winnow_window", 4))
    max_pos_each = int(data.get("max_pos_each", 100))
    min_group_size = int(data.get("min_group_size", 4))
    delta_tol = int(data.get("delta_tol", 5))
    max_gap = int(data.get("max_gap", 120))

    dc = data.get("default_categories")
    if dc is None:
        default_categories: tuple[str, ...] = ("unmapped",)
    elif isinstance(dc, str):
        default_categories = (dc,)
    else:
        default_categories = tuple(str(x) for x in dc)

    tm_name = data.get("type_mapping_file")
    gf_name = data.get("group_filter_config_file")
    if not tm_name or not gf_name:
        raise ValueError(
            "meta.json must set 'type_mapping_file' and 'group_filter_config_file' "
            "(paths relative to the directory containing meta.json)"
        )
    tm_path = (bundle_root / str(tm_name)).resolve()
    gf_path = (bundle_root / str(gf_name)).resolve()
    if not tm_path.is_file():
        raise FileNotFoundError(f"type mapping not found: {tm_path}")
    if not gf_path.is_file():
        raise FileNotFoundError(f"group filter config not found: {gf_path}")

    type_mapping = load_type_mapping_csv(tm_path)
    group_filter_config = load_group_filter_config(gf_path)

    return TokenizePipelineConfig(
        type_mapping=type_mapping,
        group_filter_config=group_filter_config,
        strategy=strategy,
        k=k,
        winnow_window=winnow_window,
        max_pos_each=max_pos_each,
        min_group_size=min_group_size,
        delta_tol=delta_tol,
        max_gap=max_gap,
        default_categories=default_categories,
    )


def write_type_mapping_csv(
    path: str | Path, type_mapping: Mapping[str, frozenset[str]]
) -> None:
    """
    Write ``raw_type,mapped_type`` rows (one row per mapped label; multi-label raw
    types produce multiple rows). Compatible with :func:`load_type_mapping_csv`.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["raw_type", "mapped_type"])
        w.writeheader()
        for raw in sorted(type_mapping.keys()):
            for dst in sorted(type_mapping[raw]):
                w.writerow({"raw_type": raw, "mapped_type": dst})


def write_group_filter_config_json(path: str | Path, config: GroupFilterConfig) -> None:
    """
    Serialize ``group_filtering_config.json`` compatible with
    :func:`load_group_filter_config`.
    """
    for feat in config.features:
        if feat.weight <= 0:
            raise ValueError(f"feature {feat.name!r}: weight must be > 0")
        for key, (lo, hi) in feat.intervals.items():
            if lo > hi:
                raise ValueError(f"feature {feat.name!r}: {key!r} has lo > hi")

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    features_out: list[dict[str, Any]] = []
    for feat in config.features:
        intervals: dict[str, list[float]] = {
            k: [float(lo), float(hi)]
            for k, (lo, hi) in sorted(feat.intervals.items())
        }
        features_out.append(
            {
                "name": feat.name,
                "role": feat.role,
                "intervals": intervals,
                "contribution": feat.contribution,
                "weight": feat.weight,
            }
        )
    data = {
        "keep_threshold": config.keep_threshold,
        "default_similarity_no_match": config.default_similarity_no_match,
        "features": features_out,
    }
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def save_tokenize_pipeline_bundle(
    config: TokenizePipelineConfig,
    bundle_dir: str | Path,
    *,
    type_mapping_filename: str = "type_mapping.csv",
    group_filter_filename: str = "group_filtering_config.json",
    meta_filename: str = "meta.json",
) -> Path:
    """
    Write ``meta.json`` plus referenced type-mapping CSV and group filter JSON
    under ``bundle_dir`` (directory is created if missing).

    Returns:
        Path to the written ``meta.json``.

    Round-trip: :func:`load_tokenize_pipeline_config_from_meta_json` on that path
    should reload an equivalent config (ordering of CSV rows may differ).
    """
    root = Path(bundle_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    tm_path = root / type_mapping_filename
    gf_path = root / group_filter_filename
    write_type_mapping_csv(tm_path, config.type_mapping)
    write_group_filter_config_json(gf_path, config.group_filter_config)

    meta_data: dict[str, Any] = {
        "strategy": config.strategy,
        "k": config.k,
        "winnow_window": config.winnow_window,
        "max_pos_each": config.max_pos_each,
        "min_group_size": config.min_group_size,
        "delta_tol": config.delta_tol,
        "max_gap": config.max_gap,
        "default_categories": list(config.default_categories),
        "type_mapping_file": type_mapping_filename,
        "group_filter_config_file": group_filter_filename,
    }
    meta_path = root / meta_filename
    meta_path.write_text(json.dumps(meta_data, indent=2) + "\n", encoding="utf-8")
    return meta_path


def load_active_tokenize_pipeline_config() -> TokenizePipelineConfig:
    """Resolve ``currently_using_meta`` → ``meta.json`` → :class:`TokenizePipelineConfig`."""
    return load_tokenize_pipeline_config_from_meta_json(resolve_active_meta_json_path())


def build_kgram_strategy(config: TokenizePipelineConfig) -> JsonLeafKgramStrategy:
    if config.strategy == STRATEGY_JSON_LEAF:
        return JsonLeafKgramStrategy(k=config.k)
    raise ValueError(f"unsupported strategy {config.strategy!r}")
