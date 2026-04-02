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
