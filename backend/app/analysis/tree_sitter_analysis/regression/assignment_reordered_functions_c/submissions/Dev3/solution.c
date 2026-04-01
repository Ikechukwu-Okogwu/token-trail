#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node *next;
} Node;

Node *listInsert(Node *head, int val) {
    Node *node = (Node *)malloc(sizeof(Node));
    node->value = val;
    node->next  = head;
    return node;
}

int listLength(const Node *head) {
    int count = 0;
    while (head != NULL) { count++; head = head->next; }
    return count;
}

int listContains(const Node *head, int val) {
    while (head != NULL) {
        if (head->value == val) return 1;
        head = head->next;
    }
    return 0;
}

Node *listReverse(Node *head) {
    Node *prev = NULL;
    Node *curr = head;
    while (curr != NULL) {
        Node *next = curr->next;
        curr->next = prev;
        prev = curr;
        curr = next;
    }
    return prev;
}

void listFree(Node *head) {
    while (head != NULL) {
        Node *tmp = head;
        head = head->next;
        free(tmp);
    }
}

int main(void) {
    Node *list = NULL;
    int vals[] = {3, 1, 4, 1, 5, 9, 2, 6};
    for (int i = 0; i < 8; i++) list = listInsert(list, vals[i]);
    printf("Length: %d\n",    listLength(list));
    printf("Contains 5: %d\n", listContains(list, 5));
    list = listReverse(list);
    printf("After reverse, first: %d\n", list->value);
    listFree(list);
    return 0;
}
