"""Generate C regression fixture datasets for Zhang's mutation operator training.

Run from repo root:
    python tests/analysis/generate_c_fixtures.py

Creates:
    tests/fixtures/regression/assignment_renamed_vars_c/
    tests/fixtures/regression/assignment_reordered_functions_c/
    tests/fixtures/regression/assignment_template_heavy_c/
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

FIXTURES_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "regression"


# ---------------------------------------------------------------------------
# Source code — fixture 1: assignment_renamed_vars_c
# Four integer-array functions; Bob is a local-variable rename of Alice.
# Carol is a completely different string-manipulation control.
# ---------------------------------------------------------------------------

ALICE_C = """\
#include <stdio.h>

/* Sum all elements of an integer array. */
int computeSum(const int *nums, int n) {
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += nums[i];
    }
    return total;
}

/* Arithmetic average; returns 0.0 for empty arrays. */
double computeAverage(const int *nums, int n) {
    if (n == 0) return 0.0;
    return (double)computeSum(nums, n) / n;
}

/* Return the maximum element; -1 if the array is empty. */
int findMax(const int *nums, int n) {
    if (n == 0) return -1;
    int maxVal = nums[0];
    for (int i = 1; i < n; i++) {
        if (nums[i] > maxVal) maxVal = nums[i];
    }
    return maxVal;
}

/* Return the minimum element; -1 if the array is empty. */
int findMin(const int *nums, int n) {
    if (n == 0) return -1;
    int minVal = nums[0];
    for (int i = 1; i < n; i++) {
        if (nums[i] < minVal) minVal = nums[i];
    }
    return minVal;
}

int main(void) {
    int data[] = {5, 3, 8, 1, 9, 2, 7, 4, 6};
    int n = 9;
    printf("Sum: %d\\n",         computeSum(data, n));
    printf("Average: %.2f\\n",   computeAverage(data, n));
    printf("Max: %d\\n",         findMax(data, n));
    printf("Min: %d\\n",         findMin(data, n));
    return 0;
}
"""

# Bob: same algorithm; local variables renamed:
#   total  -> acc
#   i      -> idx
#   maxVal -> peak
#   minVal -> floor_val
BOB_C = """\
#include <stdio.h>

/* Accumulate all elements of an integer array. */
int computeSum(const int *nums, int n) {
    int acc = 0;
    for (int idx = 0; idx < n; idx++) {
        acc += nums[idx];
    }
    return acc;
}

/* Mean of the elements; returns 0.0 for empty arrays. */
double computeAverage(const int *nums, int n) {
    if (n == 0) return 0.0;
    return (double)computeSum(nums, n) / n;
}

/* Largest element; -1 when array is empty. */
int findMax(const int *nums, int n) {
    if (n == 0) return -1;
    int peak = nums[0];
    for (int idx = 1; idx < n; idx++) {
        if (nums[idx] > peak) peak = nums[idx];
    }
    return peak;
}

/* Smallest element; -1 when array is empty. */
int findMin(const int *nums, int n) {
    if (n == 0) return -1;
    int floor_val = nums[0];
    for (int idx = 1; idx < n; idx++) {
        if (nums[idx] < floor_val) floor_val = nums[idx];
    }
    return floor_val;
}

int main(void) {
    int data[] = {5, 3, 8, 1, 9, 2, 7, 4, 6};
    int n = 9;
    printf("Sum: %d\\n",         computeSum(data, n));
    printf("Average: %.2f\\n",   computeAverage(data, n));
    printf("Max: %d\\n",         findMax(data, n));
    printf("Min: %d\\n",         findMin(data, n));
    return 0;
}
"""

# Carol: completely different — C string manipulation (no numeric arrays at all)
CAROL_C = """\
#include <stdio.h>
#include <string.h>

/* Return 1 if s is a palindrome, 0 otherwise. */
int isPalindrome(const char *s) {
    int left = 0;
    int right = (int)strlen(s) - 1;
    while (left < right) {
        if (s[left] != s[right]) return 0;
        left++;
        right--;
    }
    return 1;
}

/* Write the reverse of s into out (caller must supply sufficient space). */
void reverseString(const char *s, char *out) {
    int n = (int)strlen(s);
    for (int i = 0; i < n; i++) {
        out[i] = s[n - 1 - i];
    }
    out[n] = '\\0';
}

/* Count vowels (case-insensitive) in s. */
int countVowels(const char *s) {
    int count = 0;
    for (int i = 0; s[i] != '\\0'; i++) {
        char c = s[i];
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' ||
            c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U') {
            count++;
        }
    }
    return count;
}

/* Count whitespace-delimited words in s. */
int countWords(const char *s) {
    int count = 0;
    int inWord = 0;
    for (int i = 0; s[i] != '\\0'; i++) {
        if (s[i] != ' ' && s[i] != '\\t' && s[i] != '\\n') {
            if (!inWord) { count++; inWord = 1; }
        } else {
            inWord = 0;
        }
    }
    return count;
}

int main(void) {
    const char *text = "racecar";
    printf("Palindrome: %s\\n", isPalindrome(text) ? "yes" : "no");
    char reversed[64];
    reverseString(text, reversed);
    printf("Reversed: %s\\n", reversed);
    const char *sentence = "Hello World";
    printf("Vowels: %d\\n", countVowels(sentence));
    printf("Words: %d\\n",  countWords(sentence));
    return 0;
}
"""

# ---------------------------------------------------------------------------
# Source code — fixture 2: assignment_reordered_functions_c
# Four classic C array utility functions; Dev2 declares them in a different
# order but the function bodies are byte-for-byte identical to Dev1.
# Dev3 is a linked-list control — completely unrelated.
# ---------------------------------------------------------------------------

C_HEADER = "#include <stdio.h>\n#include <stdlib.h>\n\n"

FUNC_A_C = """\
/* Bubble sort arr[0..n-1] in ascending order. */
void bubbleSort(int *arr, int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int tmp  = arr[j];
                arr[j]   = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }
}

"""

FUNC_B_C = """\
/* Linear search; returns index of target or -1 if not found. */
int linearSearch(const int *arr, int n, int target) {
    for (int i = 0; i < n; i++) {
        if (arr[i] == target) return i;
    }
    return -1;
}

"""

FUNC_C_C = """\
/* Count how many times value appears in arr. */
int countOccurrences(const int *arr, int n, int value) {
    int count = 0;
    for (int i = 0; i < n; i++) {
        if (arr[i] == value) count++;
    }
    return count;
}

"""

FUNC_D_C = """\
/* Fill out[0..n-1] with prefix sums of arr. */
void prefixSums(const int *arr, int *out, int n) {
    if (n == 0) return;
    out[0] = arr[0];
    for (int i = 1; i < n; i++) {
        out[i] = out[i - 1] + arr[i];
    }
}

"""

MAIN_REORDER_C = """\
int main(void) {
    int data[] = {4, 2, 7, 1, 9, 3, 6, 8, 5};
    int n = 9;
    bubbleSort(data, n);
    printf("Sorted first: %d\\n",   data[0]);
    printf("Search 7: %d\\n",       linearSearch(data, n, 7));
    printf("Count 3: %d\\n",        countOccurrences(data, n, 3));
    int ps[9];
    prefixSums(data, ps, n);
    printf("Prefix[4]: %d\\n",      ps[4]);
    return 0;
}
"""

# Dev1: A B C D
DEV1_C = C_HEADER + FUNC_A_C + FUNC_B_C + FUNC_C_C + FUNC_D_C + MAIN_REORDER_C

# Dev2: C A D B  (same k-gram set, different declaration order)
DEV2_C = C_HEADER + FUNC_C_C + FUNC_A_C + FUNC_D_C + FUNC_B_C + MAIN_REORDER_C

# Dev3: singly linked list — completely unrelated to array utilities
DEV3_C = """\
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node *next;
} Node;

Node *listInsert(Node *head, int val) {
    Node *node = (Node *)malloc(sizeof(Node));
    node->value = val;
    node->next  = head;
    return node;
}

int listLength(const Node *head) {
    int count = 0;
    while (head != NULL) { count++; head = head->next; }
    return count;
}

int listContains(const Node *head, int val) {
    while (head != NULL) {
        if (head->value == val) return 1;
        head = head->next;
    }
    return 0;
}

Node *listReverse(Node *head) {
    Node *prev = NULL;
    Node *curr = head;
    while (curr != NULL) {
        Node *next = curr->next;
        curr->next = prev;
        prev = curr;
        curr = next;
    }
    return prev;
}

void listFree(Node *head) {
    while (head != NULL) {
        Node *tmp = head;
        head = head->next;
        free(tmp);
    }
}

int main(void) {
    Node *list = NULL;
    int vals[] = {3, 1, 4, 1, 5, 9, 2, 6};
    for (int i = 0; i < 8; i++) list = listInsert(list, vals[i]);
    printf("Length: %d\\n",    listLength(list));
    printf("Contains 5: %d\\n", listContains(list, 5));
    list = listReverse(list);
    printf("After reverse, first: %d\\n", list->value);
    listFree(list);
    return 0;
}
"""

# ---------------------------------------------------------------------------
# Source code — fixture 3: assignment_template_heavy_c
# Shared boilerplate template + distinct unique algorithms.
# Tests template-exclusion behavior for the C engine.
# ---------------------------------------------------------------------------

# Shared template: validation helpers, array utilities (9 functions)
TEMPLATE_C = """\
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* --- shared template helpers --- */

int validate_range(int value, int lo, int hi) {
    return value >= lo && value <= hi;
}

int validate_array(const int *arr, int n) {
    return arr != NULL && n > 0;
}

void clamp_array(int *arr, int n, int lo, int hi) {
    for (int i = 0; i < n; i++) {
        if (arr[i] < lo)      arr[i] = lo;
        else if (arr[i] > hi) arr[i] = hi;
    }
}

void copy_array(const int *src, int *dst, int n) {
    for (int i = 0; i < n; i++) dst[i] = src[i];
}

int array_equals(const int *a, const int *b, int n) {
    for (int i = 0; i < n; i++) {
        if (a[i] != b[i]) return 0;
    }
    return 1;
}

void print_array(const char *label, const int *arr, int n) {
    printf("%s: [", label);
    for (int i = 0; i < n; i++) {
        printf("%d", arr[i]);
        if (i < n - 1) printf(", ");
    }
    printf("]\\n");
}

int find_first(const int *arr, int n, int value) {
    for (int i = 0; i < n; i++) {
        if (arr[i] == value) return i;
    }
    return -1;
}

int sum_range(const int *arr, int lo, int hi) {
    int total = 0;
    for (int i = lo; i <= hi; i++) total += arr[i];
    return total;
}

int count_positive(const int *arr, int n) {
    int cnt = 0;
    for (int i = 0; i < n; i++) {
        if (arr[i] > 0) cnt++;
    }
    return cnt;
}
"""

# TemplateA: template + sliding-window maximum (unique logic)
TEMPLATE_A_C = TEMPLATE_C + """
/* --- unique logic: sliding window maximum --- */

/* Fill out[0..n-k] with the maximum of each window of size k. */
void slidingWindowMax(const int *arr, int n, int k, int *out) {
    for (int i = 0; i <= n - k; i++) {
        int best = arr[i];
        for (int j = i + 1; j < i + k; j++) {
            if (arr[j] > best) best = arr[j];
        }
        out[i] = best;
    }
}

/* Return the index of the window (size k) with the greatest sum. */
int bestWindowIndex(const int *arr, int n, int k) {
    if (n < k) return -1;
    int best_sum = sum_range(arr, 0, k - 1);
    int best_idx = 0;
    for (int i = 1; i <= n - k; i++) {
        int s = sum_range(arr, i, i + k - 1);
        if (s > best_sum) { best_sum = s; best_idx = i; }
    }
    return best_idx;
}

int main(void) {
    int data[] = {2, 1, 5, 3, 6, 4, 8, 7, 9};
    int n = 9;
    int k = 3;
    if (!validate_array(data, n)) return 1;
    clamp_array(data, n, 0, 100);
    print_array("Input", data, n);
    int windows[7];
    slidingWindowMax(data, n, k, windows);
    print_array("Window maxima", windows, n - k + 1);
    printf("Best window start: %d\\n", bestWindowIndex(data, n, k));
    printf("Positive count: %d\\n",    count_positive(data, n));
    return 0;
}
"""

# TemplateB: template + prefix-difference analysis (unique logic)
TEMPLATE_B_C = TEMPLATE_C + """
/* --- unique logic: prefix-difference analysis --- */

/* Fill out[0..n-1] with the prefix sums of arr. */
void buildPrefixSums(const int *arr, int *out, int n) {
    out[0] = arr[0];
    for (int i = 1; i < n; i++) out[i] = out[i - 1] + arr[i];
}

/* Fill diff[0..n-2] with the first-order differences of arr. */
void buildDifferences(const int *arr, int *diff, int n) {
    for (int i = 0; i < n - 1; i++) diff[i] = arr[i + 1] - arr[i];
}

/* Return the index of the largest positive difference (steepest rise). */
int steepestRiseIndex(const int *arr, int n) {
    if (n < 2) return -1;
    int best_diff = arr[1] - arr[0];
    int best_idx  = 0;
    for (int i = 1; i < n - 1; i++) {
        int d = arr[i + 1] - arr[i];
        if (d > best_diff) { best_diff = d; best_idx = i; }
    }
    return best_idx;
}

int main(void) {
    int data[] = {3, 7, 2, 9, 1, 6, 4, 8, 5};
    int n = 9;
    if (!validate_array(data, n)) return 1;
    clamp_array(data, n, 0, 100);
    print_array("Input", data, n);
    int prefix[9];
    buildPrefixSums(data, prefix, n);
    print_array("Prefix sums", prefix, n);
    int diff[8];
    buildDifferences(data, diff, n - 1);
    print_array("Differences", diff, n - 1);
    printf("Steepest rise at: %d\\n", steepestRiseIndex(data, n));
    printf("Positive count: %d\\n",   count_positive(data, n));
    return 0;
}
"""

# TemplateC: entirely different — recursive matrix operations, no shared template
TEMPLATE_C_CTRL = """\
#include <stdio.h>
#include <stdlib.h>

#define SIZE 3

typedef int Matrix[SIZE][SIZE];

void matMul(const Matrix a, const Matrix b, Matrix out) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            out[i][j] = 0;
            for (int k = 0; k < SIZE; k++) {
                out[i][j] += a[i][k] * b[k][j];
            }
        }
    }
}

void matIdentity(Matrix m) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            m[i][j] = (i == j) ? 1 : 0;
        }
    }
}

void matPrint(const char *label, const Matrix m) {
    printf("%s:\\n", label);
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            printf("%4d", m[i][j]);
        }
        printf("\\n");
    }
}

int matTrace(const Matrix m) {
    int tr = 0;
    for (int i = 0; i < SIZE; i++) tr += m[i][i];
    return tr;
}

int matEqual(const Matrix a, const Matrix b) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            if (a[i][j] != b[i][j]) return 0;
        }
    }
    return 1;
}

int main(void) {
    Matrix a = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
    Matrix id;
    matIdentity(id);
    Matrix result;
    matMul(a, id, result);
    matPrint("A", a);
    matPrint("A * I", result);
    printf("Trace: %d\\n",        matTrace(a));
    printf("A * I == A: %d\\n",   matEqual(a, result));
    return 0;
}
"""


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_zip(filename: str, content: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, content)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Write fixture 1: assignment_renamed_vars_c
# ---------------------------------------------------------------------------

f1 = FIXTURES_ROOT / "assignment_renamed_vars_c"
subs1 = f1 / "submissions"
subs1.mkdir(parents=True, exist_ok=True)

(subs1 / "Alice.zip").write_bytes(make_zip("solution.c", ALICE_C))
(subs1 / "Bob.zip").write_bytes(make_zip("solution.c", BOB_C))
(subs1 / "Carol.zip").write_bytes(make_zip("solution.c", CAROL_C))

(f1 / "result.txt").write_text(
    "fixture=assignment_renamed_vars_c\n"
    "language=c\n"
    "homogeneous=true\n"
    "template_exclusion=false\n"
    "engine_mode=direct\n"
    "require_all_pairs=true\n"
    "\n"
    "Alice.zip,Bob.zip,expected=0.5200,range=0.4000-0.7000,label=medium\n"
    "Alice.zip,Carol.zip,expected=0.0500,range=0.0000-0.2500,label=low\n"
    "Bob.zip,Carol.zip,expected=0.0500,range=0.0000-0.2500,label=low\n",
    encoding="utf-8",
)

(f1 / "result_explanation.md").write_text(
    "# result_explanation\n\n"
    "## Pair Alice.zip,Bob.zip\n"
    "- Pair: `Alice.zip,Bob.zip`\n"
    "- Testing: `rename_invariance`\n"
    "- Why expected label: Bob applies the same four numeric-array functions as Alice with only"
    " local variable names changed (`total`->`acc`, `i`->`idx`, `maxVal`->`peak`,"
    " `minVal`->`floor_val`). All function signatures, operators, control-flow keywords, and"
    " constant values are identical, so character k-gram overlap remains high. A future C AST"
    " engine should score this even higher (full rename-robustness).\n"
    "- What engine should do: preserve high similarity despite local-variable-level renaming.\n\n"
    "## Pair Alice.zip,Carol.zip\n"
    "- Pair: `Alice.zip,Carol.zip`\n"
    "- Testing: `false_positive_control`\n"
    "- Why expected label: Carol implements string manipulation (isPalindrome, reverseString,"
    " countVowels, countWords) using `<string.h>` and character arrays — entirely unrelated to"
    " Alice's integer-array statistics.\n"
    "- What engine should do: avoid false positives from shared `#include <stdio.h>` and"
    " generic loop boilerplate.\n\n"
    "## Pair Bob.zip,Carol.zip\n"
    "- Pair: `Bob.zip,Carol.zip`\n"
    "- Testing: `false_positive_control`\n"
    "- Why expected label: Bob is in the numeric-array family; Carol is in the string family."
    " The pair should remain low even though both are valid C programs sharing basic structure.\n"
    "- What engine should do: keep control comparisons low regardless of shared language"
    " scaffolding.\n",
    encoding="utf-8",
)

(f1 / "submission_creation.md").write_text(
    "# submission_creation\n\n"
    "## Alice.zip\n"
    "- File: `solution.c`\n"
    "- Role: `base`\n"
    "- Family: `numeric_array`\n"
    "- Description: four functions over int arrays: computeSum, computeAverage, findMax,"
    " findMin. Uses `total`, `i`, `maxVal`, `minVal` as local variable names.\n\n"
    "## Bob.zip\n"
    "- File: `solution.c`\n"
    "- Role: `variant`\n"
    "- Family: `numeric_array`\n"
    "- Description: same four functions as Alice with local variables renamed:"
    " total->acc, i->idx, maxVal->peak, minVal->floor_val. Logic, signatures, and"
    " control flow are byte-for-byte identical otherwise.\n\n"
    "## Carol.zip\n"
    "- File: `solution.c`\n"
    "- Role: `control`\n"
    "- Family: `string_manipulation`\n"
    "- Description: four unrelated string functions: isPalindrome, reverseString,"
    " countVowels, countWords. Uses `<string.h>` and char arrays; no numeric arrays.\n",
    encoding="utf-8",
)

print("Created fixture 1: assignment_renamed_vars_c")
for p in sorted(f1.rglob("*")):
    print(f"  {p.relative_to(FIXTURES_ROOT)}")


# ---------------------------------------------------------------------------
# Write fixture 2: assignment_reordered_functions_c
# ---------------------------------------------------------------------------

f2 = FIXTURES_ROOT / "assignment_reordered_functions_c"
subs2 = f2 / "submissions"
subs2.mkdir(parents=True, exist_ok=True)

(subs2 / "Dev1.zip").write_bytes(make_zip("solution.c", DEV1_C))
(subs2 / "Dev2.zip").write_bytes(make_zip("solution.c", DEV2_C))
(subs2 / "Dev3.zip").write_bytes(make_zip("solution.c", DEV3_C))

(f2 / "result.txt").write_text(
    "fixture=assignment_reordered_functions_c\n"
    "language=c\n"
    "homogeneous=true\n"
    "template_exclusion=false\n"
    "engine_mode=direct\n"
    "require_all_pairs=true\n"
    "\n"
    "Dev1.zip,Dev2.zip,expected=0.9500,range=0.8000-1.0000,label=high\n"
    "Dev1.zip,Dev3.zip,expected=0.0500,range=0.0000-0.2500,label=low\n"
    "Dev2.zip,Dev3.zip,expected=0.0500,range=0.0000-0.2500,label=low\n",
    encoding="utf-8",
)

(f2 / "result_explanation.md").write_text(
    "# result_explanation\n\n"
    "## Pair Dev1.zip,Dev2.zip\n"
    "- Pair: `Dev1.zip,Dev2.zip`\n"
    "- Testing: `reorder_invariance`\n"
    "- Why expected label: both submissions contain identical function bodies"
    " (bubbleSort, linearSearch, countOccurrences, prefixSums) with only declaration"
    " order permuted (A-B-C-D vs C-A-D-B). Character k-gram winnowing is set-based so"
    " the position of each function does not affect which k-grams are fingerprinted;"
    " overlap stays very high.\n"
    "- What engine should do: keep similarity high when logic is preserved but function"
    " declaration order changes.\n\n"
    "## Pair Dev1.zip,Dev3.zip\n"
    "- Pair: `Dev1.zip,Dev3.zip`\n"
    "- Testing: `false_positive_control`\n"
    "- Why expected label: Dev3 implements a singly linked list (listInsert, listLength,"
    " listContains, listReverse, listFree) using dynamic memory allocation — completely"
    " unrelated to Dev1's static array utilities.\n"
    "- What engine should do: avoid flagging similarity for independent algorithm families.\n\n"
    "## Pair Dev2.zip,Dev3.zip\n"
    "- Pair: `Dev2.zip,Dev3.zip`\n"
    "- Testing: `false_positive_control`\n"
    "- Why expected label: Dev2 is in the array-utilities family; Dev3 is the linked-list"
    " control. Reordering functions on one side does not create artificial overlap with"
    " unrelated code.\n"
    "- What engine should do: keep control comparisons low regardless of function-order"
    " variation within one submission.\n",
    encoding="utf-8",
)

(f2 / "submission_creation.md").write_text(
    "# submission_creation\n\n"
    "## Dev1.zip\n"
    "- File: `solution.c`\n"
    "- Role: `base`\n"
    "- Family: `array_utilities`\n"
    "- Description: four array functions declared in order A-B-C-D: bubbleSort,"
    " linearSearch, countOccurrences, prefixSums.\n\n"
    "## Dev2.zip\n"
    "- File: `solution.c`\n"
    "- Role: `variant`\n"
    "- Family: `array_utilities`\n"
    "- Description: identical function bodies as Dev1, declared in order C-A-D-B:"
    " countOccurrences, bubbleSort, prefixSums, linearSearch. Function text is"
    " byte-for-byte identical to Dev1; only declaration order differs.\n\n"
    "## Dev3.zip\n"
    "- File: `solution.c`\n"
    "- Role: `control`\n"
    "- Family: `linked_list`\n"
    "- Description: singly linked list: listInsert, listLength, listContains,"
    " listReverse, listFree. Uses dynamic malloc/free; completely unrelated to"
    " the array-utilities family.\n",
    encoding="utf-8",
)

print("\nCreated fixture 2: assignment_reordered_functions_c")
for p in sorted(f2.rglob("*")):
    print(f"  {p.relative_to(FIXTURES_ROOT)}")


# ---------------------------------------------------------------------------
# Write fixture 3: assignment_template_heavy_c
# ---------------------------------------------------------------------------

f3 = FIXTURES_ROOT / "assignment_template_heavy_c"
subs3 = f3 / "submissions"
subs3.mkdir(parents=True, exist_ok=True)

(subs3 / "TemplateA.zip").write_bytes(make_zip("solution.c", TEMPLATE_A_C))
(subs3 / "TemplateB.zip").write_bytes(make_zip("solution.c", TEMPLATE_B_C))
(subs3 / "TemplateC.zip").write_bytes(make_zip("solution.c", TEMPLATE_C_CTRL))

# Template ZIP: the shared boilerplate that both A and B include
(f3 / "template.zip").write_bytes(make_zip("template.c", TEMPLATE_C))

(f3 / "result.txt").write_text(
    "fixture=assignment_template_heavy_c\n"
    "language=c\n"
    "homogeneous=true\n"
    "template_exclusion=true\n"
    "engine_mode=direct\n"
    "require_all_pairs=true\n"
    "\n"
    "TemplateA.zip,TemplateB.zip,expected=0.1800,range=0.0000-0.2500,label=low\n"
    "TemplateA.zip,TemplateC.zip,expected=0.0200,range=0.0000-0.2000,label=low\n"
    "TemplateB.zip,TemplateC.zip,expected=0.0200,range=0.0000-0.2000,label=low\n",
    encoding="utf-8",
)

(f3 / "result_explanation.md").write_text(
    "# result_explanation\n\n"
    "## Pair TemplateA.zip,TemplateB.zip\n"
    "- Pair: `TemplateA.zip,TemplateB.zip`\n"
    "- Testing: `template_exclusion`\n"
    "- Why expected label: both submissions embed the same 9-function shared template"
    " (validate_range, validate_array, clamp_array, copy_array, array_equals, print_array,"
    " find_first, sum_range, count_positive). After template k-grams are excluded,"
    " only the unique logic remains: TemplateA has a sliding-window maximum algorithm"
    " (slidingWindowMax, bestWindowIndex) and TemplateB has a prefix-difference analysis"
    " (buildPrefixSums, buildDifferences, steepestRiseIndex). These algorithms are distinct,"
    " so the pair scores low once boilerplate is stripped.\n"
    "- What engine should do: suppress the shared-template contribution and score only the"
    " unique algorithmic portions, yielding a low similarity.\n\n"
    "## Pair TemplateA.zip,TemplateC.zip\n"
    "- Pair: `TemplateA.zip,TemplateC.zip`\n"
    "- Testing: `false_positive_control`\n"
    "- Why expected label: TemplateC implements fixed-size matrix operations (matMul,"
    " matIdentity, matPrint, matTrace, matEqual) with no shared template code. After"
    " template exclusion TemplateA is only its sliding-window logic; overlap with the"
    " matrix code is minimal.\n"
    "- What engine should do: produce a low score; TemplateC shares neither template"
    " boilerplate nor unique algorithm with TemplateA.\n\n"
    "## Pair TemplateB.zip,TemplateC.zip\n"
    "- Pair: `TemplateB.zip,TemplateC.zip`\n"
    "- Testing: `false_positive_control`\n"
    "- Why expected label: TemplateC shares no code with TemplateB's template or its"
    " unique prefix-difference logic. The pair is a clean cross-family control.\n"
    "- What engine should do: produce a low score regardless of shared C idioms"
    " (loops, printf, return 0).\n",
    encoding="utf-8",
)

(f3 / "submission_creation.md").write_text(
    "# submission_creation\n\n"
    "## TemplateA.zip\n"
    "- File: `solution.c`\n"
    "- Role: `template_heavy`\n"
    "- Family: `sliding_window`\n"
    "- Description: shared template (9 helper functions) plus unique sliding-window"
    " maximum logic: slidingWindowMax fills an output array with per-window maxima;"
    " bestWindowIndex returns the start index of the highest-sum window.\n\n"
    "## TemplateB.zip\n"
    "- File: `solution.c`\n"
    "- Role: `template_heavy`\n"
    "- Family: `prefix_difference`\n"
    "- Description: same shared template as TemplateA plus unique prefix-difference"
    " analysis: buildPrefixSums, buildDifferences, steepestRiseIndex. Unique logic"
    " is algorithmically unrelated to TemplateA's sliding window.\n\n"
    "## TemplateC.zip\n"
    "- File: `solution.c`\n"
    "- Role: `control`\n"
    "- Family: `matrix_ops`\n"
    "- Description: 3x3 fixed-size matrix operations — matMul, matIdentity, matPrint,"
    " matTrace, matEqual. No shared template code; completely unrelated to the"
    " template-heavy family.\n\n"
    "## template.zip\n"
    "- File: `template.c`\n"
    "- Role: `template_reference`\n"
    "- Family: `shared_template`\n"
    "- Description: the 9 shared helper functions included verbatim in both TemplateA"
    " and TemplateB: validate_range, validate_array, clamp_array, copy_array,"
    " array_equals, print_array, find_first, sum_range, count_positive.\n",
    encoding="utf-8",
)

print("\nCreated fixture 3: assignment_template_heavy_c")
for p in sorted(f3.rglob("*")):
    print(f"  {p.relative_to(FIXTURES_ROOT)}")

print("\nDone.")
