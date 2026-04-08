#include <iostream>
#include <vector>

// Count occurrences of a value
int countOccurrences(const std::vector<int>& arr, int value) {
    int count = 0;
    for (int i = 0; i < (int)arr.size(); i++) {
        if (arr[i] == value) count++;
    }
    return count;
}

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

// Linear search; returns index or -1 if not found
int linearSearch(const std::vector<int>& arr, int target) {
    for (int i = 0; i < (int)arr.size(); i++) {
        if (arr[i] == target) return i;
    }
    return -1;
}

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
