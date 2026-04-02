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
