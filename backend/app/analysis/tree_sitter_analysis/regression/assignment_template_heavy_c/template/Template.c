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
