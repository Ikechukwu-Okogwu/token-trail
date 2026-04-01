# result_explanation

## Pair Alice.zip,Bob.zip
- Pair: `Alice.zip,Bob.zip`
- Testing: `rename_sensitivity`
- Why expected label: Bob applies the same four numeric-array functions as Alice with only local variable names changed (`total`->`acc`, `i`->`idx`, `maxVal`->`peak`, `minVal`->`floor_val`). The character k-gram engine (k=40) is sensitive to these renames because each changed identifier alters a proportionally large fraction of the 40-char windows in these short C functions. The resulting score (~0.52) is medium, not high. This is ground truth for the C character path: it is NOT rename-invariant. A future C AST engine should score this pair high (>= 0.80) and will be distinguished from the character engine precisely by this fixture.
- What engine should do: score medium (~0.50) on the character path; a C AST engine upgrade should raise this to high.

## Pair Alice.zip,Carol.zip
- Pair: `Alice.zip,Carol.zip`
- Testing: `false_positive_control`
- Why expected label: Carol implements string manipulation (isPalindrome, reverseString, countVowels, countWords) using `<string.h>` and character arrays — entirely unrelated to Alice's integer-array statistics.
- What engine should do: avoid false positives from shared `#include <stdio.h>` and generic loop boilerplate.

## Pair Bob.zip,Carol.zip
- Pair: `Bob.zip,Carol.zip`
- Testing: `false_positive_control`
- Why expected label: Bob is in the numeric-array family; Carol is in the string family. The pair should remain low even though both are valid C programs sharing basic structure.
- What engine should do: keep control comparisons low regardless of shared language scaffolding.
