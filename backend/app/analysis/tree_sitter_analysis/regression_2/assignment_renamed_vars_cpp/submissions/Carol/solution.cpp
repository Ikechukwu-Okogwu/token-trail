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
        if (c != ' ' && c != '\t' && c != '\n') {
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
