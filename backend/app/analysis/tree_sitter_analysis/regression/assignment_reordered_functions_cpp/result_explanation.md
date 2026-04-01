# result_explanation

## Pair Dev1.zip,Dev2.zip
- Pair: `Dev1.zip,Dev2.zip`
- Testing: `reorder_invariance`
- Why expected label: both submissions contain identical function bodies (bubbleSort, linearSearch, countOccurrences, prefixSums) with only declaration order permuted (A-B-C-D vs C-A-D-B). Character k-gram winnowing is set-based so order does not affect score.
- What engine should do: keep similarity high when logic is preserved but function order changes.

## Pair Dev1.zip,Dev3.zip
- Pair: `Dev1.zip,Dev3.zip`
- Testing: `false_positive_control`
- Why expected label: Dev3 implements a binary search tree (insert, search, treeHeight, countNodes) completely unrelated to Dev1's vector utilities.
- What engine should do: avoid flagging high similarity for independent implementations.

## Pair Dev2.zip,Dev3.zip
- Pair: `Dev2.zip,Dev3.zip`
- Testing: `false_positive_control`
- Why expected label: Dev2 is in the vector-utilities family; Dev3 is the BST control. Reordering functions on one side does not create artificial overlap with unrelated code.
- What engine should do: keep control comparisons low regardless of function-order variation.
