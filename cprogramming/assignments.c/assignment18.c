#include <stdio.h>

// Find length
int stringLength(char str[]) {
    int i = 0;
    while (str[i] != '\0') {
        i++;
    }
    return i;
}

// Reverse string
void reverseString(char str[], char rev[]) {
    int i, len = stringLength(str);

    for (i = 0; i < len; i++) {
        rev[i] = str[len - i - 1];
    }
    rev[i] = '\0';
}

// Compare strings
int compareStrings(char str1[], char str2[]) {
    int i = 0;

    while (str1[i] != '\0' && str2[i] != '\0') {
        if (str1[i] != str2[i])
            return 0; // not equal
        i++;
    }

    if (str1[i] == '\0' && str2[i] == '\0')
        return 1; // equal
    else
        return 0;
}

// Substring check
int isSubstring(char str[], char sub[]) {
    int i, j;

    for (i = 0; str[i] != '\0'; i++) {
        j = 0;
        while (sub[j] != '\0' && str[i + j] == sub[j]) {
            j++;
        }
        if (sub[j] == '\0')
            return 1; // found
    }
    return 0; // not found
}

int main() {
    char str1[100], str2[100], rev[100];
    int i = 0;

    // Input string manually
    printf("Enter a string: ");
    gets(str1);   // (used for simplicity in exams)

    // i) Length
    int len = stringLength(str1);
    printf("\nLength = %d\n", len);

    // ii) Reverse
    reverseString(str1, rev);
    printf("Reversed string = %s\n", rev);

    // iii) Equality check
    printf("\nEnter another string: ");
    gets(str2);

    if (compareStrings(str1, str2))
        printf("Strings are equal\n");
    else
        printf("Strings are NOT equal\n");

    // iv) Palindrome check
    if (compareStrings(str1, rev))
        printf("String is Palindrome\n");
    else
        printf("String is NOT Palindrome\n");

    // v) Substring check
    printf("\nEnter substring: ");
    gets(str2);

    if (isSubstring(str1, str2))
        printf("Substring found\n");
    else
        printf("Substring NOT found\n");

    return 0;
}