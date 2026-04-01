# submission_creation

## Alice.zip
- File: `solution.c`
- Role: `base`
- Family: `numeric_array`
- Description: four functions over int arrays: computeSum, computeAverage, findMax, findMin. Uses `total`, `i`, `maxVal`, `minVal` as local variable names.

## Bob.zip
- File: `solution.c`
- Role: `variant`
- Family: `numeric_array`
- Description: same four functions as Alice with local variables renamed: total->acc, i->idx, maxVal->peak, minVal->floor_val. Logic, signatures, and control flow are byte-for-byte identical otherwise.

## Carol.zip
- File: `solution.c`
- Role: `control`
- Family: `string_manipulation`
- Description: four unrelated string functions: isPalindrome, reverseString, countVowels, countWords. Uses `<string.h>` and char arrays; no numeric arrays.
