# result_explanation

## Pair Alice.zip,Bob.zip
- Pair: `Alice.zip,Bob.zip`
- Testing: `rename_gap` (character engine baseline + AST engine target)
- Why expected label: Bob applies the same algorithm as Alice with local variable names changed
  (`total`->`acc`, `i`->`idx`, `maxVal`->`best`, `minVal`->`least`). The current character
  k-gram engine scores this ~0.46 (medium) because renamed identifiers change k-grams.
  **This is the known gap Zhang's C++ AST engine must close.**
- Current character-engine score: ~0.4583 (label=medium) — used as the regression baseline.
- C++ AST engine target: >= 0.85 (label=high) — same rename-robustness standard as Java fixtures.
- What engine should do: score this pair >= 0.85 once the C++ tokenize pipeline is built.

## Pair Alice.zip,Carol.zip
- Pair: `Alice.zip,Carol.zip`
- Testing: `false_positive_control`
- Why expected label: Carol implements string manipulation (palindrome, reverse, vowel count) entirely unrelated to Alice's numeric vector analysis.
- What engine should do: avoid false positives from shared `#include` and loop boilerplate.

## Pair Bob.zip,Carol.zip
- Pair: `Bob.zip,Carol.zip`
- Testing: `false_positive_control`
- Why expected label: Bob is in the numeric-analysis family while Carol is in the string family; the pair should stay low despite both being valid C++ programs.
- What engine should do: keep control comparisons low regardless of shared language scaffolding.
