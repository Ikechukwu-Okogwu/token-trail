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
    printf("]\n");
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
    printf("Steepest rise at: %d\n", steepestRiseIndex(data, n));
    printf("Positive count: %d\n",   count_positive(data, n));
    return 0;
}
