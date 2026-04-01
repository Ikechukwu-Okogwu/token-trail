# result_explanation

## Pair TemplateA.zip,TemplateB.zip
- Pair: `TemplateA.zip,TemplateB.zip`
- Testing: `template_exclusion`
- Why expected label: both submissions embed the same 9-function shared template (validate_range, validate_array, clamp_array, copy_array, array_equals, print_array, find_first, sum_range, count_positive). After template k-grams are excluded, only the unique logic remains: TemplateA has a sliding-window maximum algorithm (slidingWindowMax, bestWindowIndex) and TemplateB has a prefix-difference analysis (buildPrefixSums, buildDifferences, steepestRiseIndex). These algorithms are distinct, so the pair scores low once boilerplate is stripped.
- What engine should do: suppress the shared-template contribution and score only the unique algorithmic portions, yielding a low similarity.

## Pair TemplateA.zip,TemplateC.zip
- Pair: `TemplateA.zip,TemplateC.zip`
- Testing: `false_positive_control`
- Why expected label: TemplateC implements fixed-size matrix operations (matMul, matIdentity, matPrint, matTrace, matEqual) with no shared template code. After template exclusion TemplateA is only its sliding-window logic; overlap with the matrix code is minimal.
- What engine should do: produce a low score; TemplateC shares neither template boilerplate nor unique algorithm with TemplateA.

## Pair TemplateB.zip,TemplateC.zip
- Pair: `TemplateB.zip,TemplateC.zip`
- Testing: `false_positive_control`
- Why expected label: TemplateC shares no code with TemplateB's template or its unique prefix-difference logic. The pair is a clean cross-family control.
- What engine should do: produce a low score regardless of shared C idioms (loops, printf, return 0).
