"""Generate C++ regression fixture datasets.

Run from repo root:
    python tests/analysis/generate_cpp_fixtures.py

Creates:
    tests/fixtures/regression/assignment_renamed_vars_cpp/
    tests/fixtures/regression/assignment_reordered_functions_cpp/
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

FIXTURES_ROOT = Path(__file__).resolve().parents[1] / "fixtures" / "regression"

# ---------------------------------------------------------------------------
# Source code — fixture 1: renamed vars
# ---------------------------------------------------------------------------

ALICE_CPP = """\
#include <iostream>
#include <vector>

// Compute the sum of all elements in a vector
int computeSum(const std::vector<int>& nums) {
    int total = 0;
    for (int i = 0; i < (int)nums.size(); i++) {
        total += nums[i];
    }
    return total;
}

// Compute the arithmetic average
double computeAverage(const std::vector<int>& nums) {
    if (nums.empty()) return 0.0;
    return static_cast<double>(computeSum(nums)) / nums.size();
}

// Return the maximum value; -1 if empty
int findMax(const std::vector<int>& nums) {
    if (nums.empty()) return -1;
    int maxVal = nums[0];
    for (int i = 1; i < (int)nums.size(); i++) {
        if (nums[i] > maxVal) maxVal = nums[i];
    }
    return maxVal;
}

// Return the minimum value; -1 if empty
int findMin(const std::vector<int>& nums) {
    if (nums.empty()) return -1;
    int minVal = nums[0];
    for (int i = 1; i < (int)nums.size(); i++) {
        if (nums[i] < minVal) minVal = nums[i];
    }
    return minVal;
}

int main() {
    std::vector<int> data = {5, 3, 8, 1, 9, 2, 7, 4, 6};
    std::cout << "Sum: "     << computeSum(data)     << std::endl;
    std::cout << "Average: " << computeAverage(data) << std::endl;
    std::cout << "Max: "     << findMax(data)         << std::endl;
    std::cout << "Min: "     << findMin(data)         << std::endl;
    return 0;
}
"""

# Bob: same logic, local variable names changed
# total -> acc, i -> idx, maxVal -> best, minVal -> least
BOB_CPP = """\
#include <iostream>
#include <vector>

// Accumulate all elements
int computeSum(const std::vector<int>& nums) {
    int acc = 0;
    for (int idx = 0; idx < (int)nums.size(); idx++) {
        acc += nums[idx];
    }
    return acc;
}

// Mean of the elements
double computeAverage(const std::vector<int>& nums) {
    if (nums.empty()) return 0.0;
    return static_cast<double>(computeSum(nums)) / nums.size();
}

// Largest element; -1 when empty
int findMax(const std::vector<int>& nums) {
    if (nums.empty()) return -1;
    int best = nums[0];
    for (int idx = 1; idx < (int)nums.size(); idx++) {
        if (nums[idx] > best) best = nums[idx];
    }
    return best;
}

// Smallest element; -1 when empty
int findMin(const std::vector<int>& nums) {
    if (nums.empty()) return -1;
    int least = nums[0];
    for (int idx = 1; idx < (int)nums.size(); idx++) {
        if (nums[idx] < least) least = nums[idx];
    }
    return least;
}

int main() {
    std::vector<int> data = {5, 3, 8, 1, 9, 2, 7, 4, 6};
    std::cout << "Sum: "     << computeSum(data)     << std::endl;
    std::cout << "Average: " << computeAverage(data) << std::endl;
    std::cout << "Max: "     << findMax(data)         << std::endl;
    std::cout << "Min: "     << findMin(data)         << std::endl;
    return 0;
}
"""

# Carol: completely different — string manipulation
CAROL_CPP = """\
#include <iostream>
#include <string>
#include <algorithm>

bool isPalindrome(const std::string& s) {
    int left = 0;
    int right = (int)s.size() - 1;
    while (left < right) {
        if (s[left] != s[right]) return false;
        left++;
        right--;
    }
    return true;
}

std::string reverseString(const std::string& s) {
    std::string result = s;
    std::reverse(result.begin(), result.end());
    return result;
}

int countVowels(const std::string& s) {
    int count = 0;
    for (char c : s) {
        char lc = (char)tolower((unsigned char)c);
        if (lc == 'a' || lc == 'e' || lc == 'i' || lc == 'o' || lc == 'u') {
            count++;
        }
    }
    return count;
}

int countWords(const std::string& s) {
    int count = 0;
    bool inWord = false;
    for (char c : s) {
        if (c != ' ' && c != '\\t' && c != '\\n') {
            if (!inWord) { count++; inWord = true; }
        } else {
            inWord = false;
        }
    }
    return count;
}

int main() {
    std::string text = "racecar";
    std::cout << "Palindrome: " << (isPalindrome(text) ? "yes" : "no") << std::endl;
    std::cout << "Reversed: "   << reverseString(text) << std::endl;
    std::string sentence = "Hello World";
    std::cout << "Vowels: " << countVowels(sentence) << std::endl;
    std::cout << "Words: "  << countWords(sentence)  << std::endl;
    return 0;
}
"""

# ---------------------------------------------------------------------------
# Source code — fixture 2: reordered functions
# ---------------------------------------------------------------------------

HEADER = """\
#include <iostream>
#include <vector>

"""

FUNC_A = """\
// Bubble sort in ascending order
void bubbleSort(std::vector<int>& arr) {
    int n = (int)arr.size();
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int tmp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = tmp;
            }
        }
    }
}

"""

FUNC_B = """\
// Linear search; returns index or -1 if not found
int linearSearch(const std::vector<int>& arr, int target) {
    for (int i = 0; i < (int)arr.size(); i++) {
        if (arr[i] == target) return i;
    }
    return -1;
}

"""

FUNC_C = """\
// Count occurrences of a value
int countOccurrences(const std::vector<int>& arr, int value) {
    int count = 0;
    for (int i = 0; i < (int)arr.size(); i++) {
        if (arr[i] == value) count++;
    }
    return count;
}

"""

FUNC_D = """\
// Compute prefix sum array
std::vector<int> prefixSums(const std::vector<int>& arr) {
    std::vector<int> result(arr.size(), 0);
    if (arr.empty()) return result;
    result[0] = arr[0];
    for (int i = 1; i < (int)arr.size(); i++) {
        result[i] = result[i - 1] + arr[i];
    }
    return result;
}

"""

MAIN_REORDER = """\
int main() {
    std::vector<int> data = {4, 2, 7, 1, 9, 3, 6, 8, 5};
    bubbleSort(data);
    std::cout << "Sorted first: " << data[0] << std::endl;
    std::cout << "Search 7: "     << linearSearch(data, 7) << std::endl;
    std::cout << "Count 3: "      << countOccurrences(data, 3) << std::endl;
    auto ps = prefixSums(data);
    std::cout << "Prefix[4]: "    << ps[4] << std::endl;
    return 0;
}
"""

# Dev1: A B C D
DEV1_CPP = HEADER + FUNC_A + FUNC_B + FUNC_C + FUNC_D + MAIN_REORDER

# Dev2: C A D B  (same k-gram set, different positions)
DEV2_CPP = HEADER + FUNC_C + FUNC_A + FUNC_D + FUNC_B + MAIN_REORDER

# Dev3: binary search tree — completely different
DEV3_CPP = """\
#include <iostream>

struct Node {
    int value;
    Node* left;
    Node* right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* insert(Node* root, int val) {
    if (root == nullptr) return new Node(val);
    if (val < root->value) {
        root->left = insert(root->left, val);
    } else if (val > root->value) {
        root->right = insert(root->right, val);
    }
    return root;
}

bool search(Node* root, int val) {
    if (root == nullptr) return false;
    if (val == root->value) return true;
    if (val < root->value) return search(root->left, val);
    return search(root->right, val);
}

int treeHeight(Node* root) {
    if (root == nullptr) return 0;
    int leftH  = treeHeight(root->left);
    int rightH = treeHeight(root->right);
    return 1 + (leftH > rightH ? leftH : rightH);
}

int countNodes(Node* root) {
    if (root == nullptr) return 0;
    return 1 + countNodes(root->left) + countNodes(root->right);
}

int main() {
    Node* root = nullptr;
    int values[] = {5, 3, 8, 1, 4, 7, 9};
    for (int v : values) root = insert(root, v);
    std::cout << "Search 4: " << (search(root, 4) ? "found" : "not found") << std::endl;
    std::cout << "Height: "   << treeHeight(root) << std::endl;
    std::cout << "Nodes: "    << countNodes(root) << std::endl;
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
# Write fixture 1: assignment_renamed_vars_cpp
# ---------------------------------------------------------------------------

f1 = FIXTURES_ROOT / "assignment_renamed_vars_cpp"
subs1 = f1 / "submissions"
subs1.mkdir(parents=True, exist_ok=True)

(subs1 / "Alice.zip").write_bytes(make_zip("solution.cpp", ALICE_CPP))
(subs1 / "Bob.zip").write_bytes(make_zip("solution.cpp", BOB_CPP))
(subs1 / "Carol.zip").write_bytes(make_zip("solution.cpp", CAROL_CPP))

(f1 / "result.txt").write_text(
    "fixture=assignment_renamed_vars_cpp\n"
    "language=cpp\n"
    "homogeneous=true\n"
    "template_exclusion=false\n"
    "engine_mode=direct\n"
    "require_all_pairs=true\n"
    "\n"
    "Alice.zip,Bob.zip,expected=0.8500,range=0.7000-1.0000,label=high\n"
    "Alice.zip,Carol.zip,expected=0.0500,range=0.0000-0.2500,label=low\n"
    "Bob.zip,Carol.zip,expected=0.0500,range=0.0000-0.2500,label=low\n",
    encoding="utf-8",
)

(f1 / "result_explanation.md").write_text(
    "# result_explanation\n\n"
    "## Pair Alice.zip,Bob.zip\n"
    "- Pair: `Alice.zip,Bob.zip`\n"
    "- Testing: `edit_invariance` (near-rename)\n"
    "- Why expected label: Bob applies the same algorithm as Alice with local variable names changed "
    "(`total`->`acc`, `i`->`idx`, `maxVal`->`best`, `minVal`->`least`). "
    "Structural keywords, operators, and function signatures are identical, so character k-gram "
    "overlap remains high. A future C++ AST engine should score this even higher (full rename-robustness).\n"
    "- What engine should do: preserve high similarity despite minor identifier-level edits.\n\n"
    "## Pair Alice.zip,Carol.zip\n"
    "- Pair: `Alice.zip,Carol.zip`\n"
    "- Testing: `false_positive_control`\n"
    "- Why expected label: Carol implements string manipulation (palindrome, reverse, vowel count) "
    "entirely unrelated to Alice's numeric vector analysis.\n"
    "- What engine should do: avoid false positives from shared `#include` and loop boilerplate.\n\n"
    "## Pair Bob.zip,Carol.zip\n"
    "- Pair: `Bob.zip,Carol.zip`\n"
    "- Testing: `false_positive_control`\n"
    "- Why expected label: Bob is in the numeric-analysis family while Carol is in the string family; "
    "the pair should stay low despite both being valid C++ programs.\n"
    "- What engine should do: keep control comparisons low regardless of shared language scaffolding.\n",
    encoding="utf-8",
)

(f1 / "submission_creation.md").write_text(
    "# submission_creation\n\n"
    "## Alice.zip\n"
    "- File: `solution.cpp`\n"
    "- Role: `base`\n"
    "- Family: `numeric_analysis`\n"
    "- Description: four functions over std::vector<int>: computeSum, computeAverage, findMax, findMin.\n\n"
    "## Bob.zip\n"
    "- File: `solution.cpp`\n"
    "- Role: `variant`\n"
    "- Family: `numeric_analysis`\n"
    "- Description: same four functions as Alice; local variables renamed "
    "(total->acc, i->idx, maxVal->best, minVal->least). Logic unchanged.\n\n"
    "## Carol.zip\n"
    "- File: `solution.cpp`\n"
    "- Role: `control`\n"
    "- Family: `string_manipulation`\n"
    "- Description: four unrelated string functions: isPalindrome, reverseString, countVowels, countWords.\n",
    encoding="utf-8",
)

print("Created fixture 1: assignment_renamed_vars_cpp")
for p in sorted(f1.rglob("*")):
    print(f"  {p.relative_to(FIXTURES_ROOT)}")


# ---------------------------------------------------------------------------
# Write fixture 2: assignment_reordered_functions_cpp
# ---------------------------------------------------------------------------

f2 = FIXTURES_ROOT / "assignment_reordered_functions_cpp"
subs2 = f2 / "submissions"
subs2.mkdir(parents=True, exist_ok=True)

(subs2 / "Dev1.zip").write_bytes(make_zip("solution.cpp", DEV1_CPP))
(subs2 / "Dev2.zip").write_bytes(make_zip("solution.cpp", DEV2_CPP))
(subs2 / "Dev3.zip").write_bytes(make_zip("solution.cpp", DEV3_CPP))

(f2 / "result.txt").write_text(
    "fixture=assignment_reordered_functions_cpp\n"
    "language=cpp\n"
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
    "- Why expected label: both submissions contain identical function bodies "
    "(bubbleSort, linearSearch, countOccurrences, prefixSums) with only declaration order permuted "
    "(A-B-C-D vs C-A-D-B). Character k-gram winnowing is set-based so order does not affect score.\n"
    "- What engine should do: keep similarity high when logic is preserved but function order changes.\n\n"
    "## Pair Dev1.zip,Dev3.zip\n"
    "- Pair: `Dev1.zip,Dev3.zip`\n"
    "- Testing: `false_positive_control`\n"
    "- Why expected label: Dev3 implements a binary search tree (insert, search, treeHeight, countNodes) "
    "completely unrelated to Dev1's vector utilities.\n"
    "- What engine should do: avoid flagging high similarity for independent implementations.\n\n"
    "## Pair Dev2.zip,Dev3.zip\n"
    "- Pair: `Dev2.zip,Dev3.zip`\n"
    "- Testing: `false_positive_control`\n"
    "- Why expected label: Dev2 is in the vector-utilities family; Dev3 is the BST control. "
    "Reordering functions on one side does not create artificial overlap with unrelated code.\n"
    "- What engine should do: keep control comparisons low regardless of function-order variation.\n",
    encoding="utf-8",
)

(f2 / "submission_creation.md").write_text(
    "# submission_creation\n\n"
    "## Dev1.zip\n"
    "- File: `solution.cpp`\n"
    "- Role: `base`\n"
    "- Family: `vector_utilities`\n"
    "- Description: four vector functions in order A-B-C-D: "
    "bubbleSort, linearSearch, countOccurrences, prefixSums.\n\n"
    "## Dev2.zip\n"
    "- File: `solution.cpp`\n"
    "- Role: `variant`\n"
    "- Family: `vector_utilities`\n"
    "- Description: identical function bodies as Dev1, declared in order C-A-D-B: "
    "countOccurrences, bubbleSort, prefixSums, linearSearch. "
    "Function text is byte-for-byte identical; only declaration order differs.\n\n"
    "## Dev3.zip\n"
    "- File: `solution.cpp`\n"
    "- Role: `control`\n"
    "- Family: `binary_search_tree`\n"
    "- Description: BST implementation: insert, search, treeHeight, countNodes. "
    "Completely unrelated to the vector-utilities family.\n",
    encoding="utf-8",
)

print("\nCreated fixture 2: assignment_reordered_functions_cpp")
for p in sorted(f2.rglob("*")):
    print(f"  {p.relative_to(FIXTURES_ROOT)}")

print("\nDone.")
