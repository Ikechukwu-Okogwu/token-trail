# Java similarity pipeline (high level)

## Entry point

`app/analysis/analysis.py` → **`compute_javacode_similarity`**

- Ensures the backend root is on `sys.path`, then calls  
  **`app.analysis.tree_sitter_analysis.compute_similarity_javacode`** (`pipeline.py`) with `(text_a, text_b, template)`.

---

## File-level aggregation

**`compute_similarity_javacode`** (`pipeline.py`)

1. **`class_pairing`** — For each class name that appears in `template` and in **both** sources, treat it as shared starter code and drop it from comparison. Pair remaining class names with **`match_labels`** (greedy 1:1 by name similarity). Raises **`ValueError`** if nothing remains or pairing is invalid.
2. For each class pair, slice sources with **`get_class_source`** (`refactor_tools.py`).
3. **`compute_similarity_java_class`** on each slice, then **arithmetic mean** across class pairs.

---

## Class-level aggregation

**`compute_similarity_java_class`** (`pipeline.py`)

1. **`function_pairing_for_single_class`** — Expects exactly one class per snippet; pairs methods with **`match_labels`**. Raises **`ValueError`** if a snippet has zero or multiple classes.
2. For each method pair, **`compute_similarity_java_function`**.
3. **Arithmetic mean** over method pairs; **0.0** if there are no pairs.

---

## Refactor step (per method pair)

**`compute_similarity_java_function`** (`pipeline.py`)

1. **`function_rename_variable_by_defining_order`** (`function_refactor_tools.py`) — Renames local variables in definition order to `VAR_1`, `VAR_2`, … on each method body.
2. Pass normalized strings to Winnowing (below). Pipeline passes an empty function-level template here.

---

## Winnowing

**`compare_texts_with_template`** (`app/analysis/testWinowingCode/testWinowingLib.py`)

- Single entry from this pipeline for fingerprinting and similarity on the two normalized method strings (fixed `k` in pipeline call). Internal steps (k-grams, hashing, winnowing window, Jaccard, optional template hashes) are not expanded here.

---

## Flow sketch

```
compute_javacode_similarity
  → compute_similarity_javacode
       → class_pairing  →  [per class pair] get_class_source
       → compute_similarity_java_class
            → function_pairing_for_single_class
            → [per method pair] compute_similarity_java_function
                 → function_rename_variable_by_defining_order
                 → compare_texts_with_template   (Winnowing)
            → mean over methods
       → mean over classes
```
