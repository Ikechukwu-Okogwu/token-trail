#include <stdio.h>
#include <stdlib.h>

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

/* Linear search; returns index of target or -1 if not found. */
int linearSearch(const int *arr, int n, int target) {
    for (int i = 0; i < n; i++) {
        if (arr[i] == target) return i;
    }
    return -1;
}

/* Count how many times value appears in arr. */
int countOccurrences(const int *arr, int n, int value) {
    int count = 0;
    for (int i = 0; i < n; i++) {
        if (arr[i] == value) count++;
    }
    return count;
}

/* Fill out[0..n-1] with prefix sums of arr. */
void prefixSums(const int *arr, int *out, int n) {
    if (n == 0) return;
    out[0] = arr[0];
    for (int i = 1; i < n; i++) {
        out[i] = out[i - 1] + arr[i];
    }
}

int main(void) {
    int data[] = {4, 2, 7, 1, 9, 3, 6, 8, 5};
    int n = 9;
    bubbleSort(data, n);
    printf("Sorted first: %d\n",   data[0]);
    printf("Search 7: %d\n",       linearSearch(data, n, 7));
    printf("Count 3: %d\n",        countOccurrences(data, n, 3));
    int ps[9];
    prefixSums(data, ps, n);
    printf("Prefix[4]: %d\n",      ps[4]);
    return 0;
}
