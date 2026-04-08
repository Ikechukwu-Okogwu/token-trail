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
    printf("Sum: %d\n",         computeSum(data, n));
    printf("Average: %.2f\n",   computeAverage(data, n));
    printf("Max: %d\n",         findMax(data, n));
    printf("Min: %d\n",         findMin(data, n));
    return 0;
}
