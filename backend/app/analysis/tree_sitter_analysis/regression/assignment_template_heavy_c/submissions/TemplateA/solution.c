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
    printf("Best window start: %d\n", bestWindowIndex(data, n, k));
    printf("Positive count: %d\n",    count_positive(data, n));
    return 0;
}
