# Token Trail Analysis Engine — Technical Evaluation

**Date:** 2026-03-26
**Branch evaluated:** `integration/dev-branch`
**Evaluator:** Claude Code (Sonnet 4.6)

---

## Section 1: What the Engine Actually Does

**Pipeline stages (production path):**

1. **Submission upload** → `zip_service` extracts, `merge_service` concatenates source files into one `_merged.txt`
2. **Analysis trigger** → `run_analysis_for_assignment()` in `backend/app/services/analysis_service.py`
3. **For each pair** → `build_similarity_metrics(text_a, text_b, k=5)` calls `compare_texts_with_template()`
4. **Winnowing** (`backend/app/analysis/testWinowingCode/winnowingCopy.py`):
   - `sanitize()` strips all non-word chars (`[^\w]`), lowercases everything. All punctuation, spaces, operators disappear. `int x = 1;` becomes `intx1`
   - 5-character k-grams generated from the sanitized stream
   - Each k-gram hashed via SHA-1 last 8 hex digits (32-bit hash)
   - Sliding window of **hardcoded size 4** → select min hash per window (winnowing)
5. **Jaccard similarity** on fingerprint hash sets (after optional template hash subtraction)
6. **Group matching** (`fingerprint.py`) — `group_match_points(min_group_size=4, delta_tol=5, max_gap=20)` — diagonal segment clustering in (pos_a, pos_b) space
7. **Line number mapping** in `build_similarity_metrics()` → produces `matchingRegions`, `excludedRegions`
8. **Confidence** = `min(1.0, 0.55 * similarity + 0.45 * coverage)` (coverage = avg matched lines / total lines)
9. **Storage** → `similarity_results` MongoDB collection with full pair data

**What is NOT wired to production:**
- `backend/app/analysis/preprocess.py` — never called from `run_analysis_for_assignment`
- `backend/app/analysis/tree_sitter_analysis/pipeline.py` — full AST pipeline exists, never called

---

## Section 2: Evidence from Tests

**Regression fixtures (all 4 pass):**

| Fixture | Key pair | Expected range | What it proves |
|---|---|---|---|
| `renamed_vars` | Alice/Bob | 0.85–1.00 | Variable renaming doesn't break detection |
| `reordered_functions` | Dev1/Dev2 | 0.82–1.00 | Function reordering doesn't break detection |
| `template_heavy` | A/B | 0.00–0.18 | Template exclusion works |
| `stage3_rankset` | S01–S03 cluster | 0.78–1.00 | 10-student class, clusters correctly ranked |

**E2E API contract tests:** 29 tests, all passing.

**Repeatability test:** 50 consecutive runs on `renamed_vars` fixture — stable.

---

## Section 3: Grades

### 1. Algorithmic Correctness — 6 / 10

The Jaccard + winnowing core is correctly implemented. Template exclusion is correct. Line number mapping logic is sound.

**Deductions:**
- `preprocess.py:48` has a **broken `preprocess()` function**: `return winnow(text)` returns a `set[tuple[int, int]]`, not a `str`. The actual normalization logic on line 49 is **dead code** — it will never execute. If this function were ever wired to the pipeline, it would store garbage to MongoDB.
- Window size is hardcoded to 4 in `winnowingCopy.py:93`: `windows = kgrams(hashes, 4)` — not parameterizable alongside `k`.
- `max_gap=20` in `compare_texts_with_template` vs `max_gap=120` in `compare_files` — inconsistency between the two functions, though `compare_files` is not in the production path.
- 32-bit hash (SHA-1 last 8 hex chars): sufficient for files up to ~100K fingerprints before collision risk. A very large merged submission could theoretically generate false positives.

---

### 2. Detection Quality — 5 / 10

**What the engine catches well:**
- **Variable renaming (short identifiers):** Sanitize lowercases and keeps only `\w`, so k-gram patterns from surrounding code (keywords, structure) dominate. A rename of `x → y` changes only a handful of k-grams. Fixture confirms ~0.92 score for renamed submissions. ✓
- **Function reordering:** Since Jaccard operates on a *set* of fingerprints (position-independent), moving functions around doesn't remove any hashes. Fixture confirms ~0.90. ✓
- **Template exclusion:** Hash subtraction works correctly. ✓
- **Whitespace changes:** Free — sanitize strips all spaces. ✓

**What the engine misses or is weak on:**

- **Long identifier renaming:** Renaming `calculateAverageScore → computeMeanValue` changes many character k-grams. The Jaccard score drops noticeably. The engine has no identifier normalization at this level (the AST pipeline that does this — `function_rename_variable_by_defining_order` — is not wired).
- **Comment injection as dilution attack:** Adding 50 lines of English comments to a submission adds unique character k-grams to only one file, growing the union without growing the intersection. Jaccard drops. A student adding a large fake-javadoc block before every method could reduce detected similarity significantly.
- **Loop conversion (for→while or vice versa):** Sanitize removes `{}();` etc., so `for(int i=0; i<n; i++)` → `forinti0in` vs `while(i<n)` → `whilein`. The control-flow tokens differ, the loop body tokens are identical. Score will drop proportionally to how much code is in loop headers vs bodies. Not caught by any fixture.
- **Code insertion (adding dummy methods):** Adding an unrelated helper method adds new k-grams to only one file, diluting Jaccard. Large enough dummy methods can reduce score from 0.9 to below the flagging threshold.
- **Character-level only:** No semantic understanding. Two structurally identical programs with different logic that happen to share identifier name patterns could get a non-trivial score.

**False positive risk:** Low for truly independent implementations. The `renamed_vars` and `reordered_functions` control pairs (Carol, Dev3) correctly score near 0.05–0.08. ✓

---

### 3. Robustness / Edge Cases — 5 / 10

- Empty submission handled (returns 0.0) ✓
- OS errors on file read handled gracefully ✓
- Template not provided → no exclusion applied ✓

**Problems:**
- `max_pos_each=100` in `build_match_points`: for heavily templated code where a common k-gram appears 100+ times in both files, the cross-product is 10,000 match points per hash. For boilerplate-heavy Java this could be slow. There is a `[CUT]` print (not a warning/log) when this threshold is hit — in production this prints to stdout.
- No timeout on analysis computation. A 40-student class (780 pairs) with large submissions has no timeout guard.
- Analysis is triggered manually via API endpoint — there is no automatic trigger after submission processing completes. An instructor who forgets to click "Run Analysis" won't see results.
- `preprocess.py`'s `get_or_create_preprocessed` is never called — the MongoDB `preprocessed_files` collection will never be populated.

---

### 4. Code Quality — 6 / 10

Good: typed dataclasses, separation of concerns, deterministic resultId format, fallback result ID lookup.

**Problems:**
- `preprocess.py:48`: active line returns wrong type; dead code immediately below it — this will confuse any future developer who tries to wire the preprocessing cache.
- Magic numbers throughout (`k=5`, `min_group_size=4`, `delta_tol=5`, `max_gap=20`, `0.55`, `0.45`) — none are named constants or documented.
- `[CUT]` debug print in `fingerprint.py:92` goes to stdout in production.
- `tree_sitter_analysis/` is a complete, apparently tested module that is completely invisible to the analysis pipeline. Its existence suggests either incomplete integration or abandoned work — either way it should be either wired or deleted.
- Commented-out code in multiple files (`winnowingCopy.py`, `testWinowingLib.py`, `pipeline.py`).
- Confidence formula (`0.55 * sim + 0.45 * cov`) is undocumented — there's no comment explaining why these weights were chosen.
- `_load_run_and_verify_owner` and `_get_authorized_run_and_assignment` in `instructor_similarity.py` do the same thing — duplicate code.

---

### 5. Test Coverage — 7 / 10

The regression fixture system is genuinely well-designed: structured `result.txt` format, documentation enforcement, repeatability testing, full matrix validation. This is above average for a student project.

**Gaps:**
- No unit tests for `winnow()`, `sanitize()`, `kgrams()`, `jaccard_similarity()` individually
- No unit tests for `build_similarity_metrics()` — line number mapping, confidence formula, excluded region construction
- No test for the comment-injection evasion scenario
- No test for the loop-conversion scenario
- No test for confidence formula boundary behavior
- No regression fixture for C or C++ (only Java)
- No test for `preprocess.py` — the broken function would have been caught immediately
- No performance/timeout test for large submission sets

---

### 6. API / Integration Quality — 7 / 10

- Deterministic resultId (`runId__leftId__rightId`) ✓
- Fallback lookup for old `-index` format ✓
- Student names included in similarity results ✓
- Proper ownership verification on all routes ✓
- `matchingRegions` and `excludedRegions` stored at analysis time, not recomputed on read ✓

**Gaps:**
- No pagination on similarity results — 40 students = 780 pairs returned in one response
- 400 validation on resultId format uses two independent regex checks (`__` and `-index`) that could accept some malformed IDs
- No rate limiting on the analysis trigger endpoint — double-clicking "Run Analysis" runs two analyses simultaneously
- `leftFilePath` / `rightFilePath` are returned in the comparison response — these are server-side file system paths exposed to the client

---

### 7. Evasion Resistance — 3 / 10

This is the weakest dimension. Character-level Jaccard has well-known weaknesses:

| Evasion technique | Effect on score | Caught? |
|---|---|---|
| Rename short vars | Minimal drop | ✓ Detected |
| Rename long identifiers | Moderate drop | Partially evaded |
| Add blank lines / whitespace | Zero effect | ✓ Detected |
| Add inline comments | Dilutes Jaccard | **Evaded** |
| Add dummy methods | Dilutes Jaccard | **Evaded** |
| Loop for→while conversion | Small drop | **Partially evaded** |
| Add large javadoc blocks | Significant dilution | **Evaded** |
| Reorder statements within a method | Removes k-gram adjacency | **Partially evaded** |
| Extract method (split one method into two) | Changes block structure | **Evaded** |

The AST pipeline in `tree_sitter_analysis/` would have addressed most of these (variable normalization, method-level pairing, structural comparison). It is fully implemented but never called.

---

### 8. Demo Readiness — 7 / 10

- Core flow works end-to-end ✓
- Side-by-side comparison UI with highlighted regions ✓
- Ranked results list with confidence scores ✓
- Student names shown ✓
- All regression tests pass ✓

**Risks:**
- Analysis must be manually triggered — if the demo instructor doesn't explicitly run it, the results page is empty
- If a demo submission is a heavy copy with long renamed identifiers + added comments, the score might be lower than expected (0.7 range instead of 0.9), which could look unconvincing
- The `leftFilePath` / `rightFilePath` server paths visible in the comparison API response is awkward if a professor inspects the network tab

---

## Section 4: Deep Evasion Analysis

### Scenario A: Comment flooding

```java
// Method to add elements to the list of items
// This implementation follows standard Java conventions
// Please see Assignment 1 requirements section 3.2
public void add(int x) { items.add(x); }
```

After sanitize: the comment words become character k-grams that appear ONLY in this file. Jaccard = intersection / union. Union grows, intersection stays the same. A 50-line file + 100 lines of comments could drop the similarity from 0.92 → 0.65, below the "high" threshold.

**Verdict: Effective evasion against this engine.**

### Scenario B: Dummy method injection

```java
public int unusedHelper() {
    Random rand = new Random();
    int alpha = rand.nextInt(100);
    int beta = alpha * 2 + rand.nextInt(50);
    return beta;
}
```

Adds ~30 new unique k-grams to the file. For a 100-line assignment, this shifts Jaccard by roughly 20–30 points. Two collusion students who each add different dummy methods see similarity drop further.

### Scenario C: Method extraction (split one method into two)

```java
// Original: one method
public double average(int[] arr) { ... }

// Evaded: split into two
private int sum(int[] arr) { ... }
public double average(int[] arr) { return sum(arr) / arr.length; }
```

The k-grams from inside `average` are now spread across two methods. The character-level approach still catches most of the inner logic, but the split adds new k-grams that exist in only one file.

---

## Section 5: Weaknesses and Blind Spots

**Critical:**

1. `preprocess.py:48` — broken function with wrong return type. If anyone wires it, it silently stores garbage. Should be fixed now before it causes a production bug.
2. `tree_sitter_analysis/` module — fully implemented AST pipeline that would dramatically improve evasion resistance, but is completely disconnected. This is the biggest missed opportunity in the codebase.
3. No timeout on pairwise analysis — a class of 40 with large submissions could hang the worker.

**Demo risks:**

4. Manual analysis trigger — demo can fail if instructor doesn't click "Run Analysis"
5. Long-identifier renaming produces noticeably lower scores than short-identifier renaming — may surprise the team during a live demo with a carefully crafted example

**Architectural:**

6. Analysis runs on the main worker — no parallelism. With 780 pairs for 40 students, this blocks the worker for the duration.
7. No version pinning on the algorithm — if `k` or `max_gap` changes, all stored similarity results become inconsistent with future runs.

---

## Section 6: Suggested Improvements

### A: Quick wins (< 1 day each)

1. **Fix `preprocess.py:48`** — either restore the real normalization line or delete the file. This is a bug waiting to cause a production incident.

2. **Wire `tree_sitter_analysis/pipeline.py`** to `run_analysis_for_assignment()` for Java submissions. The infrastructure is complete. It uses variable normalization + method-level pairing + k=8 character k-grams — far more evasion-resistant. Add a `try/except ValueError` around it to fall back to character-level comparison when AST parsing fails (multi-class, malformed code).

3. **Replace `print("[CUT]")` in `fingerprint.py:92`** with `import logging; logging.getLogger(__name__).warning(...)`. Debug prints to stdout are silent in Docker logs unless explicitly followed.

4. **Deduplicate `_load_run_and_verify_owner` / `_get_authorized_run_and_assignment`** in `instructor_similarity.py` — they are identical in purpose.

5. **Name the magic constants** in `analysis_service.py`:
   ```python
   _WINNOW_K = 5
   _CONFIDENCE_SIM_WEIGHT = 0.55
   _CONFIDENCE_COV_WEIGHT = 0.45
   ```

### B: Longer-term (1–3 days each)

6. **Add evasion test fixtures** — create fixtures specifically for comment-injection, dummy-method, and loop-conversion evasion scenarios. The current fixtures test the happy path. Grade the engine against adversarial inputs.

7. **Add pagination to the similarity results endpoint** — `?page=1&page_size=50` with total count in response. Required for any class over ~20 students.

8. **Auto-trigger analysis** after all submissions for an assignment reach `processed` status — worker could watch for this condition instead of requiring manual trigger.

9. **Redact file system paths** from the comparison API response — `leftFilePath`/`rightFilePath` expose internal storage structure to the client.

---

## Section 7: Missing Tests

### Proposed test additions (concrete, implementable)

**1. Evasion resistance tests** — add to `tests/analysis/`:

```python
def test_comment_flooding_does_not_evade_detection():
    """Adding 100 lines of comments to one file should not drop score below 0.70."""
    # Build a version of a submission with a 100-line comment block injected
    # Assert similarity(original, flooded) > 0.70

def test_dummy_method_injection_score_still_flags():
    """Adding one dummy method should not drop score below 0.60."""
```

**2. Unit tests for confidence formula:**

```python
def test_confidence_is_capped_at_1():
    assert build_similarity_metrics("abc" * 100, "abc" * 100)["confidence"] == 1.0

def test_confidence_is_zero_for_empty():
    assert build_similarity_metrics("", "")["confidence"] == 0.0

def test_confidence_formula_weights():
    # sim=1.0, coverage=0.0 → confidence = 0.55
    # sim=0.0, coverage=1.0 → confidence = 0.45
```

**3. Unit tests for line number mapping:**

```python
def test_matching_region_line_numbers_are_1indexed():
def test_excluded_regions_cover_all_lines_for_empty_match():
def test_excluded_regions_skip_matched_ranges():
```

**4. Performance regression test:**

```python
@pytest.mark.slow
def test_40_student_analysis_completes_under_30s():
    # Build 40 variants, run run_analysis_for_assignment, assert wall time < 30s
```

**5. C/C++ fixture** — add `assignment_renamed_vars_cpp` with `.c` files to verify the engine works for the other supported languages.

**6. `preprocess.py` unit test** (documents the broken state so it gets fixed):

```python
def test_preprocess_returns_a_string():
    result = preprocess("int x = 1;")
    assert isinstance(result, str), f"Expected str, got {type(result)}"
```

---

## Section 8: Final Verdict

**Plain English summary:**

Token Trail has a working plagiarism detection pipeline. The core algorithm (Jaccard similarity over winnowed character k-grams) is correctly implemented, the API layer is clean, and the regression test infrastructure is better than most student projects. For basic copying with minor cosmetic changes, the engine will flag pairs correctly and rank them appropriately.

The critical problem is **evasion**. Character k-gram Jaccard with k=5 and no identifier normalization is known to be defeatable by comment insertion and code expansion — two techniques any student who Googles "how to avoid plagiarism detection" will find in the first 5 results. The irony is that the team has already built the countermeasure (`tree_sitter_analysis/pipeline.py` with AST-based variable normalization and method-level pairing) — it just isn't wired to anything.

The second critical problem is the **broken `preprocess.py`** — a dormant bug with the wrong return type on the active line and correct logic on the dead line. It hasn't caused a production failure only because nothing calls it.

**Demo readiness: 7/10.** It will work for the prepared demo scenario. It will fail to impress a professor who asks "what happens if a student adds 100 lines of comments?"

---

### Top 5 Next Steps Before Any Professor Review

| Priority | Action | Effort |
|---|---|---|
| 1 | Fix `preprocess.py:48` — swap the two return statements | 1 line |
| 2 | Wire `tree_sitter_analysis/pipeline.py` to Java analysis path with AST→winnowing fallback | 1–2 days |
| 3 | Add comment-flooding evasion fixture to prove/disprove engine handles it | Half day |
| 4 | Replace `print("[CUT]")` with proper logging | 1 line |
| 5 | Add analysis auto-trigger so instructor doesn't have to remember to click "Run Analysis" during demo | Half day |

---

### Grade Summary

| Category | Score |
|---|---|
| Algorithmic Correctness | 6 / 10 |
| Detection Quality | 5 / 10 |
| Robustness / Edge Cases | 5 / 10 |
| Code Quality | 6 / 10 |
| Test Coverage | 7 / 10 |
| API / Integration Quality | 7 / 10 |
| Evasion Resistance | 3 / 10 |
| Demo Readiness | 7 / 10 |
| **Overall** | **5.75 / 10** |
