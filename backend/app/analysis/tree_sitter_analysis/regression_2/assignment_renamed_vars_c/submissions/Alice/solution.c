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
    printf("Sum: %d\n",         computeSum(data, n));
    printf("Average: %.2f\n",   computeAverage(data, n));
    printf("Max: %d\n",         findMax(data, n));
    printf("Min: %d\n",         findMin(data, n));
    return 0;
}
