#include <stdio.h>
#include <string.h>

/* Return 1 if s is a palindrome, 0 otherwise. */
int isPalindrome(const char *s) {
    int left = 0;
    int right = (int)strlen(s) - 1;
    while (left < right) {
        if (s[left] != s[right]) return 0;
        left++;
        right--;
    }
    return 1;
}

/* Write the reverse of s into out (caller must supply sufficient space). */
void reverseString(const char *s, char *out) {
    int n = (int)strlen(s);
    for (int i = 0; i < n; i++) {
        out[i] = s[n - 1 - i];
    }
    out[n] = '\0';
}

/* Count vowels (case-insensitive) in s. */
int countVowels(const char *s) {
    int count = 0;
    for (int i = 0; s[i] != '\0'; i++) {
        char c = s[i];
        if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' ||
            c == 'A' || c == 'E' || c == 'I' || c == 'O' || c == 'U') {
            count++;
        }
    }
    return count;
}

/* Count whitespace-delimited words in s. */
int countWords(const char *s) {
    int count = 0;
    int inWord = 0;
    for (int i = 0; s[i] != '\0'; i++) {
        if (s[i] != ' ' && s[i] != '\t' && s[i] != '\n') {
            if (!inWord) { count++; inWord = 1; }
        } else {
            inWord = 0;
        }
    }
    return count;
}

int main(void) {
    const char *text = "racecar";
    printf("Palindrome: %s\n", isPalindrome(text) ? "yes" : "no");
    char reversed[64];
    reverseString(text, reversed);
    printf("Reversed: %s\n", reversed);
    const char *sentence = "Hello World";
    printf("Vowels: %d\n", countVowels(sentence));
    printf("Words: %d\n",  countWords(sentence));
    return 0;
}
