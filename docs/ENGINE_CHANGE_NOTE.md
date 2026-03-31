# Engine Change Note — Hybrid AST/Token Integration

**Branch:** `main` (Phase B–D)
**Author:** Charlotte / Ikechukwu
**Date:** 2026-03-31

---

## 1. Previous Behavior

All languages (Java, C, C++) ran through the character k-gram winnowing engine (`compare_texts_with_template` in `testWinowingLib.py`). For Java, a scalar score override was applied using `run_tokenize_similarity_pipeline` — but only when no `exclusionCode` was set. If a template was present, the tokenize override was silently skipped, leaving Java on the character path.

The guard condition was:

```python
if language == "java" and _JAVA_TOKENIZE_AVAILABLE and text_a.strip() and text_b.strip() and not template_text.strip():
    similarity = float(_compute_java(text_a, text_b, template_text))
```

This replaced only the `similarity` scalar — all region/block/snippet fields still came from the character path regardless of language.

---

## 2. Problem with the Old Integration

Two issues:

**Template exclusion was bypassed for Java.** `compute_javacode_similarity` in `analysis.py` explicitly discards its `template` argument (`_ = (template, ...)`). The tokenize pipeline had no template parameter. The workaround was to skip the tokenize path entirely when a template was present, which meant Java with `exclusionCode` always got character-winnowing scores — not rename-robust scores.

**Missing runtime dependencies.** `group_analysis.py` imports `pandas` at module level, but `pandas` and `numpy` were never added to `requirements.txt`. This caused `_JAVA_TOKENIZE_AVAILABLE = False` in the Docker container, silently routing all Java through character winnowing even when no template was set.

---

## 3. Why the Hybrid Approach Was Chosen

A direct swap of `analysis_service.py` with the PR #35 version would:
- Route C and C++ through the Java tree-sitter pipeline → `ValueError` → silent `score = 0.0`
- Drop 5 output fields (`confidence`, `excludedRegions`, `snippets`, `largestBlockSize`, `summary`) that the Pydantic schema requires and the TA will inspect
- Break 36 unit tests and 29 e2e contract tests immediately

The hybrid keeps the existing service contract intact:
- Java → AST/token path (rename-robust, AST template exclusion)
- C/C++ → character winnowing (unchanged)
- Java parse failure → character winnowing fallback
- All 7 output fields preserved on both paths

A named `_character_winnowing_metrics` helper isolates the C/C++ path so a future C/C++ AST engine can slot in without touching Java logic.

---

## 4. Files Changed

| File | What changed |
|------|-------------|
| `backend/app/analysis/tree_sitter_analysis/template_exclusion.py` | **New.** AST-based template class stripper. Parses Java with tree-sitter, finds top-level class names in the template, removes matching byte spans from both submissions before tokenization. |
| `backend/app/analysis/tree_sitter_analysis/tokenize_pipeline.py` | Added `template: str = ""` parameter to `run_tokenize_similarity_pipeline`. Calls `strip_template_classes` on both sides before tokenizing when template is non-blank. |
| `backend/app/services/analysis_service.py` | Full rewrite of dispatch logic. Added `_tokenize_result_to_metrics` adapter (converts `TokenizePipelineResult` → 7-field metrics dict). Added `_character_winnowing_metrics` named helper for C/C++. `build_similarity_metrics` now dispatches cleanly by language. |
| `backend/requirements.txt` | Added `pandas>=2.0.0` and `numpy>=1.24.0` — required by `group_analysis.py` at import time. |
| `tests/analysis/test_analysis_service_unit.py` | Added 4 new tests: `test_java_with_template_uses_ast_exclusion`, `test_java_tokenize_adapter_all_fields_present`, `test_requirements_include_tokenize_runtime_dependencies`, `test_c_cpp_dispatch_uses_winnowing_path`. |

---

## 5. What Stayed Unchanged

- All routers (`instructor_similarity.py`, `instructor_admin.py`, `public.py`, `auth.py`)
- All Pydantic schemas (`schemas/similarity.py`, `schemas/assignment.py`, etc.)
- All frontend files
- `compare_texts_with_template` in `testWinowingLib.py`
- The 7-field output contract of `build_similarity_metrics`
- Assignment language enforcement: `java`, `c`, `cpp` only (`instructor.py:127`)

---

## 6. Verification Results

**Unit + regression tests:** 50 passed, 1 xfail (known false-positive control, `strict=True`)
**E2E API contract tests:** 29 passed

**Live rehearsal (Phase D):**

| Check | Result |
|-------|--------|
| Java no-template score (rename-robust pair) | 0.8636 |
| Java with-template score (same pair, template stripped) | 0.0000 — correct, only shared class was template |
| `evidenceType` in comparison response | `"tokenize_group"` — confirms AST path active |
| All 7 comparison fields present | Yes |
| C/C++ `evidenceType` | `"winnowing_group"` — character path unchanged |
| Frontend routes | 200 OK |

---

## 7. Future C/C++ AST Integration Path

When you build a C/C++ AST engine, the integration point is `_character_winnowing_metrics` in `analysis_service.py`. The dispatch in `build_similarity_metrics` already separates Java from everything else:

```python
if language == "java" and _JAVA_TOKENIZE_AVAILABLE and ...:
    # Java AST path
    ...

# C, C++, and Java fallback
return _character_winnowing_metrics(...)
```

To add C/C++ AST support:

1. Build your C/C++ tokenize pipeline (separate from the Java one — different grammar, different token types).
2. Add a `_CPP_TOKENIZE_AVAILABLE` flag with the same try/except import guard pattern.
3. Add a `_cpp_tokenize_result_to_metrics` adapter that produces the same 7-field dict.
4. Extend the dispatch:

```python
if language == "java" and _JAVA_TOKENIZE_AVAILABLE and ...:
    # Java AST path

if language in ("c", "cpp") and _CPP_TOKENIZE_AVAILABLE and ...:
    # C/C++ AST path (future)

# Fallback
return _character_winnowing_metrics(...)
```

No router, schema, or frontend changes needed. The service contract is stable.

The `template_exclusion.py` module is Java-specific (tree-sitter Java grammar). A C/C++ template exclusion module would follow the same pattern but use a C/C++ parser.
