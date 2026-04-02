# submission_creation

## TemplateA.zip
- File: `solution.c`
- Role: `template_heavy`
- Family: `sliding_window`
- Description: shared template (9 helper functions) plus unique sliding-window maximum logic: slidingWindowMax fills an output array with per-window maxima; bestWindowIndex returns the start index of the highest-sum window.

## TemplateB.zip
- File: `solution.c`
- Role: `template_heavy`
- Family: `prefix_difference`
- Description: same shared template as TemplateA plus unique prefix-difference analysis: buildPrefixSums, buildDifferences, steepestRiseIndex. Unique logic is algorithmically unrelated to TemplateA's sliding window.

## TemplateC.zip
- File: `solution.c`
- Role: `control`
- Family: `matrix_ops`
- Description: 3x3 fixed-size matrix operations — matMul, matIdentity, matPrint, matTrace, matEqual. No shared template code; completely unrelated to the template-heavy family.

## template.zip
- File: `template.c`
- Role: `template_reference`
- Family: `shared_template`
- Description: the 9 shared helper functions included verbatim in both TemplateA and TemplateB: validate_range, validate_array, clamp_array, copy_array, array_equals, print_array, find_first, sum_range, count_positive.
