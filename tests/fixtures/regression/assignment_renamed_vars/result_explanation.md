# result_explanation

## Pair Alice.zip,Bob.zip
- Pair: `Alice.zip,Bob.zip`
- Testing: `rename_invariance`
- Why expected label: Bob is a rename-only transformation of Alice, so this pair is intentionally high.
- What engine should do: preserve strong similarity despite identifier-level renaming.

## Pair Alice.zip,Carol.zip
- Pair: `Alice.zip,Carol.zip`
- Testing: `false_positive_control`
- Why expected label: Carol is from a distinct control program and is intentionally unrelated to Alice, so this pair is low.
- What engine should do: avoid false positives from superficial structure overlap.

## Pair Bob.zip,Carol.zip
- Pair: `Bob.zip,Carol.zip`
- Testing: `false_positive_control`
- Why expected label: Bob stays in Alice's renamed family while Carol remains unrelated control logic, so this pair is low.
- What engine should do: keep control comparisons low even when one side is a transformed variant.
