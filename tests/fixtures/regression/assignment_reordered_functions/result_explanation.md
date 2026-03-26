# result_explanation

## Pair Dev1.zip,Dev2.zip
- Pair: `Dev1.zip,Dev2.zip`
- Testing: `reorder_invariance`
- Why expected label: both submissions share the same base logic with only method-order permutation, so this pair is high.
- What engine should do: keep similarity strong when logic is preserved but function order changes.

## Pair Dev1.zip,Dev3.zip
- Pair: `Dev1.zip,Dev3.zip`
- Testing: `false_positive_control`
- Why expected label: Dev3 is intentionally unrelated control code, so this pair is low.
- What engine should do: avoid flagging high similarity for independent implementations.

## Pair Dev2.zip,Dev3.zip
- Pair: `Dev2.zip,Dev3.zip`
- Testing: `false_positive_control`
- Why expected label: Dev2 remains in the reordered family while Dev3 is unrelated control logic, so this pair is low.
- What engine should do: keep control comparisons low regardless of method-order variation on the other side.
