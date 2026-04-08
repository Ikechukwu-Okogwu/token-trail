# Regression Test ZIPs

This document defines the offline regression fixture ZIPs used to evaluate the similarity engine directly (no frontend/API flow required).

## Scope And Rules

- Assignment fixtures are **homogeneous**: one fixture contains exactly one language (`java`, `c`, or `cpp`).
- Current committed regression assets include Java, C, and C++ fixture sets.
- Expected scores are normalized decimals in `0..1`.
- Expected values are **aspirational, human-curated targets** (not generated from the current engine).
- Pair keys are order-independent (`A.zip,B.zip` is equivalent to `B.zip,A.zip`).
- Template-heavy fixtures use the regression runner's real scoring order:
  Java prefers `compute_javacode_similarity()` when available, then falls back to `compare_texts_with_template()`;
  non-Java fixtures use `compare_texts_with_template()`.

## Why Aspirational Values Are Valid

Expected values are tied to **known fixture construction intent**:

- We intentionally create transformed versions of the same underlying program (rename-only, reorder-only), so those pairs are expected to be flagged high.
- We intentionally create control/unrelated programs, so those pairs are expected to stay low.
- We intentionally create template-heavy submissions and provide `template.zip`, so post-exclusion similarity is expected to stay low.

Because the transformations are controlled and known in advance, `result.txt` encodes ground-truth targets we can compare the engine against.

## Processing Parity With Production

The regression runner mirrors backend ingestion behavior:

- safe extraction for ZIP entries
- language extension filtering
- binary-file skipping
- deterministic relative-path sorting
- merged source text generation before similarity scoring

Scoring-path parity is narrower:

- Java fixtures prefer `app.analysis.analysis.compute_javacode_similarity()`, which loads the active tokenize config and passes `template` through to the tokenize pipeline.
- C and C++ fixtures use character winnowing only in `tests/analysis/regression_runner.py`.
- Production worker behavior in `backend/app/services/analysis_service.py` is tokenize-first for `java`, `c`, and `cpp`.

So these fixtures preserve ingestion parity across languages, but do **not** currently provide full production-engine parity for C/C++.

## Fixture Location

- `tests/fixtures/regression/assignment_renamed_vars`
- `tests/fixtures/regression/assignment_reordered_functions`
- `tests/fixtures/regression/assignment_template_heavy`
- `tests/fixtures/regression/assignment_stage3_rankset`

Each assignment folder contains:

- `submissions/*.zip` (student submissions)
- `result.txt` (expected score + range + label per pair)
- `result_explanation.md` (human rationale for every pair listed in `result.txt`)
- `submission_creation.md` (how each submission ZIP was constructed and why it exists)
- `template.zip` only when template exclusion is enabled

## What Each Fixture Tests

### `assignment_renamed_vars`

- **Purpose:** detects similarity when student code is renamed/refactored at identifier level.
- **How it was built:** `Bob.zip` is a rename-focused variant of `Alice.zip`; `Carol.zip` is a separate control program.
- **Expected behavior:** the rename pair should still be flagged strongly; control pairs should remain low.
- **Representative expectations (`result.txt`):**
  - `Alice.zip,Bob.zip`: expected `~0.92`, label `high`
  - `Alice.zip,Carol.zip`: expected `~0.08`, label `low`

### `assignment_reordered_functions`

- **Purpose:** verifies structural detection when function order changes but logic remains similar.
- **How it was built:** `Dev1.zip` and `Dev2.zip` contain the same core logic with method-order permutations; `Dev3.zip` is a control program.
- **Expected behavior:** reordered pair remains high; control pairs remain low.
- **Representative expectations (`result.txt`):**
  - `Dev1.zip,Dev2.zip`: expected `~0.90`, label `high`
  - `Dev1.zip,Dev3.zip`: low similarity

### `assignment_template_heavy`

- **Purpose:** validates boilerplate exclusion using a shared template.
- **How it was built:** `TemplateA.zip` and `TemplateB.zip` both include heavy starter/template structure plus different unique logic; `TemplateC.zip` is control.
- **Expected behavior:** after template exclusion, all pairs should be low (including `TemplateA/TemplateB`).
- **Representative expectations (`result.txt`):**
  - `TemplateA.zip,TemplateB.zip`: expected `~0.08`, label `low` (after template exclusion)
  - other pairs: low

### `assignment_stage3_rankset`

- **Purpose:** Stage 3 style robustness set with 10 submissions (ranked pair matrix).
- **Includes:**
  - at least one strong pair (`S04.zip,S05.zip`)
  - at least one triple cluster (`S01.zip,S02.zip,S03.zip`)
  - template-heavy pair (`S06.zip,S07.zip`) expected low after exclusion
- **How it was built:** groups are intentionally constructed (high-sim pair, high-sim triple, template-heavy low-sim pair, and controls), so expected ranges/labels are known before scoring.
- **Representative expectations (`result.txt`):**
  - `S04.zip,S05.zip`: expected `~0.97`, label `high`
  - `S01.zip,S02.zip`: expected `~0.90`, label `high`
  - `S06.zip,S07.zip`: expected `~0.08`, label `low`

## `result.txt` Contract

Example:

```txt
fixture=assignment_renamed_vars
language=java
homogeneous=true
template_exclusion=false
engine_mode=direct
require_all_pairs=true

Alice.zip,Bob.zip,expected=0.9200,range=0.8500-1.0000,label=high
Alice.zip,Carol.zip,expected=0.0800,range=0.0000-0.2000,label=low
```

Required metadata:

- `language`
- `homogeneous` (must be `true`)
- `template_exclusion` (`true`/`false`)

Pair requirements:

- `expected=<0..1>`
- `range=<min>-<max>` with `0 <= min <= max <= 1`
- `label=high|medium|low`

## Required Markdown Documentation

Every assignment fixture directory must include both files below.

### `result_explanation.md`

Purpose:
- Explain **every** similarity pair declared in `result.txt`.

Required coverage:
- Every canonical pair key from `result.txt` must appear in this file using exact key text (for example, `Alice.zip,Bob.zip`).

Required per-pair format:

```md
# result_explanation

## Pair Alice.zip,Bob.zip
- Pair: `Alice.zip,Bob.zip`
- Testing: `rename_invariance`
- Why expected label: Bob is a rename-only variant of Alice's base logic, so this pair remains high by fixture intent.
- What engine should do: stay robust to identifier renaming and retain strong similarity.

## Pair Alice.zip,Carol.zip
- Pair: `Alice.zip,Carol.zip`
- Testing: `false_positive_control`
- Why expected label: Carol is intentionally unrelated to Alice for control coverage, so this pair is low.
- What engine should do: avoid inflating similarity from superficial scaffolding overlap.
```

Accepted `Testing` labels (use one short value per pair):
- `rename_invariance`
- `reorder_invariance`
- `template_exclusion`
- `false_positive_control`
- `family_separation`
- `cluster_consistency`
- `pair_anchor_high`
- `template_vs_non_template_control`

Worked example for frequent confusion:

```md
## Pair S09.zip,S10.zip
- Pair: `S09.zip,S10.zip`
- Testing: `false_positive_control`
- Why expected label: both are in the distinct-control family and are intentionally treated as unrelated for fixture policy.
- What engine should do: avoid flagging similarity from shared scaffold/shape alone.
```

### `submission_creation.md`

Purpose:
- Document how each submission ZIP was generated so future contributors do not need to reverse engineer fixtures.

Required coverage:
- Every `submissions/*.zip` filename must appear in this file (for example, `Alice.zip`).

Required per-submission format:

```md
# submission_creation

## Alice.zip
- Generator: `_long_java_program("RenamedBase", "a")`
- Role: `base`
- Family: `rename_cluster`

## Bob.zip
- Generator: `_light_rename_variant(_long_java_program("RenamedBase", "a"))`
- Role: `variant`
- Family: `rename_cluster`
```

## How To Run

Run only regression fixtures:

```bash
pytest tests/analysis -v
```

Run full test suite:

```bash
pytest -v
```

## Notes For Adding New Fixtures

- Keep one language per assignment fixture.
- Ensure each submission ZIP has at least one valid source file for that assignment language.
- Prefer score ranges over exact equality to absorb minor score drift while still catching regressions.
- Do not auto-generate expectations from engine output; update ranges/labels by review and intended detection quality.
- When changing fixture construction, update expected values to match the new known transformation intent.
- Always include `result_explanation.md` and `submission_creation.md` with full pair/submission coverage.
