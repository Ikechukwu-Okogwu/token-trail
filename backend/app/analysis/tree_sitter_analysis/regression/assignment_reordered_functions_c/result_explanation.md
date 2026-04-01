# result_explanation

## Pair Dev1.zip,Dev2.zip
- Pair: `Dev1.zip,Dev2.zip`
- Testing: `reorder_invariance`
- Why expected label: both submissions contain identical function bodies (bubbleSort, linearSearch, countOccurrences, prefixSums) with only declaration order permuted (A-B-C-D vs C-A-D-B). Character k-gram winnowing is set-based so the position of each function does not affect which k-grams are fingerprinted; overlap stays very high.
- What engine should do: keep similarity high when logic is preserved but function declaration order changes.

## Pair Dev1.zip,Dev3.zip
- Pair: `Dev1.zip,Dev3.zip`
- Testing: `false_positive_control`
- Why expected label: Dev3 implements a singly linked list (listInsert, listLength, listContains, listReverse, listFree) using dynamic memory allocation — completely unrelated to Dev1's static array utilities.
- What engine should do: avoid flagging similarity for independent algorithm families.

## Pair Dev2.zip,Dev3.zip
- Pair: `Dev2.zip,Dev3.zip`
- Testing: `false_positive_control`
- Why expected label: Dev2 is in the array-utilities family; Dev3 is the linked-list control. Reordering functions on one side does not create artificial overlap with unrelated code.
- What engine should do: keep control comparisons low regardless of function-order variation within one submission.
