# Evaluating external ZIPs against the analysis engine

External course bundles (for example under `ExternalTestSets/`) can be scored with the **same** code path as committed regression fixtures: safe ZIP extract, source merge, then pairwise similarity.

## Batch report (all bundled `ExternalTestSets/`)

From the repository root, one command for a full summary table (pairwise stats per set):

```bash
python scripts/run_external_testsets_batch.py
```

Save output to a file (e.g. to attach in stand-up or email):

```bash
python scripts/run_external_testsets_batch.py --output external_testsets_report.txt
```

## Quick run (single folder)

From the repository root:

```bash
python -m tests.analysis.external_eval --assignment-dir <PATH> --language java
```

- **Assignment directory**: May contain optional `template.txt` or `template.zip`. Submissions are read from `<assignment-dir>/submissions/*.zip` by default.
- **Flat layout**: If there is no `submissions/` folder but the assignment directory contains at least two `*.zip` files, those zips are used as submissions (template files can still sit beside them).

Options:

| Flag | Meaning |
|------|--------|
| `--submissions-dir DIR` | Override where `*.zip` files are found |
| `--template-exclusion` | Subtract template fingerprints (needs `template.txt` or `template.zip` under assignment-dir) |
| `--csv` | Print `left,right,similarity,label` CSV to stdout |

Use `--csv` output as a **baseline** when authoring `result.txt` ranges for a new fixture.

## Normalizing vendor data

1. One ZIP per student submission (match production uploads).
2. Place them under `submissions/` (or a folder you pass with `--submissions-dir`).
3. If the vendor ships loose source trees, zip each tree into its own file.
4. Boilerplate: merge into `template.zip` (or a single `template.txt`) next to `submissions/`, then use `--template-exclusion`.

Constraints match the fixture runner: homogeneous language per run; do not mix supported extensions (e.g. `.java` and `.cpp`) inside one submission zip.

## Promoting to CI regression

1. Copy the working folder to `tests/fixtures/regression/<fixture_name>/`.
2. Add `result.txt` with `language=`, `homogeneous=true`, and pair lines (`range=`, `label=`, `expected=`).
3. Add **`result_explanation.md`** and **`submission_creation.md`** (required by `regression_runner`).
4. Add a test in `tests/analysis/test_regression_fixtures.py` that calls `validate_fixture_assignment`.

Shared implementation: `compute_pairwise_similarity_scores` in `tests/analysis/regression_runner.py`.
