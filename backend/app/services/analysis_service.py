"""Analysis service: baseline similarity run.

Loads merged submission files for an assignment, computes pairwise similarity,
and stores results in the similarity_results collection (one doc per run).
"""
from __future__ import annotations

from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

from pymongo.database import Database

from app.analysis.config import (
    SUPPORTED_TOKENIZE_LANGUAGES,
    load_tokenize_pipeline_config_from_meta_json,
)
from app.analysis.config.pipeline_config import CONFIG_PACKAGE_DIR
from app.core.deps import to_object_id
from app.analysis.tree_sitter_analysis.tokenize_pipeline import (
    run_tokenize_similarity_pipeline,
)

_BUNDLES_DIR = CONFIG_PACKAGE_DIR / "bundles"

# Production tokenize bundles: folder names under ``bundles/`` (copy new GA outputs here and update).
_PRODUCTION_BUNDLE_JAVA = "java_20260401T014642_g001_i08_F0p824260"
_PRODUCTION_BUNDLE_C = "c_20260401T151536_g001_i00_F1p000000"
_PRODUCTION_BUNDLE_CPP = "cpp_20260401T154450_g017_i00_F0p824255"


def _normalize_assignment_language(raw: object) -> str:
    if not isinstance(raw, str) or not raw.strip():
        return "java"
    lang = raw.strip().lower()
    if lang not in SUPPORTED_TOKENIZE_LANGUAGES:
        return "java"
    return lang


def _bundle_meta_json_for_language(lang: str) -> Path:
    """``bundles/<gene-folder>/meta.json`` for each assignment language."""
    if lang == "c":
        return (_BUNDLES_DIR / _PRODUCTION_BUNDLE_C / "meta.json").resolve()
    if lang == "cpp":
        return (_BUNDLES_DIR / _PRODUCTION_BUNDLE_CPP / "meta.json").resolve()
    return (_BUNDLES_DIR / _PRODUCTION_BUNDLE_JAVA / "meta.json").resolve()


def run_analysis_for_assignment(
    db: Database, assignment_id: str, run_id: str
) -> None:
    """Run the similarity-analysis pipeline for one assignment.

    Writes one document to the similarity_results collection:
    {runId, assignmentId, createdAt, pairs:[{submissionA, submissionB, score, matchingRegions}]}

    Score and ``matchingRegions`` come from ``run_tokenize_similarity_pipeline`` (dye
    coverage + per-kept-group line spans). On pipeline error (empty/unparseable source),
    score is 0.0 and regions are empty.

    Bundle is ``app/analysis/config/bundles/<gene-folder>/meta.json``, chosen by
    assignment ``language`` (``java`` / ``c`` / ``cpp``); see module-level
    ``_PRODUCTION_BUNDLE_*`` constants. Unknown or missing language defaults to the
    Java bundle.

    If the assignment has non-empty ``exclusionCode``, it is passed as ``template`` for
    line-based template token dropping (see ``template_exclusion``).
    """
    assignment = db["assignments"].find_one(
        {"_id": to_object_id(assignment_id)},
        {"exclusionCode": 1, "language": 1},
    )
    _exc = (assignment or {}).get("exclusionCode")
    template = _exc.strip() if isinstance(_exc, str) else ""
    lang = _normalize_assignment_language((assignment or {}).get("language"))

    submissions = list(
        db["submissions"].find(
            {"assignmentId": assignment_id, "status": "processed"},
            {"_id": 1, "mergedStoragePath": 1},
        )
    )

    print(
        "run analysis for assignment",
        assignment_id,
        "language=",
        lang,
        flush=True,
    )

    # Deterministic ordering
    submissions.sort(key=lambda s: str(s.get("_id", "")))

    pipeline_cfg = load_tokenize_pipeline_config_from_meta_json(
        _bundle_meta_json_for_language(lang)
    )

    prepared: list[dict[str, str]] = []
    for s in submissions:
        merged_path = s.get("mergedStoragePath")
        submission_id = str(s.get("_id"))

        text = ""
        if merged_path:
            try:
                text = Path(merged_path).read_text(encoding="utf-8", errors="replace")
            except OSError:
                text = ""

        prepared.append({"submissionId": submission_id, "text": text})

    pairs: list[dict[str, object]] = []
    for a, b in combinations(prepared, 2):
        try:
            result = run_tokenize_similarity_pipeline(
                a["text"],
                b["text"],
                config=pipeline_cfg,
                language=lang,
                template=template,
            )
            score = result.similarity
            regions = result.matching_regions_as_dicts()
        except (ValueError, FileNotFoundError, OSError):
            score = 0.0
            regions = []
        pairs.append(
            {
                "submissionA": a["submissionId"],
                "submissionB": b["submissionId"],
                "score": score,
                "matchingRegions": regions,
            }
        )

    result_doc = {
        "runId": run_id,
        "assignmentId": assignment_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "pairs": pairs,
    }

    # One result document per run.
    db["similarity_results"].update_one(
        {"runId": run_id},
        {"$set": result_doc},
        upsert=True,
    )
