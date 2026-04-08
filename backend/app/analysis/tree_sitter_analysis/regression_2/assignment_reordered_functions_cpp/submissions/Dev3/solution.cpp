#include <iostream>

struct Node {
    int value;
    Node* left;
    Node* right;
    Node(int v) : value(v), left(nullptr), right(nullptr) {}
};

Node* insert(Node* root, int val) {
    if (root == nullptr) return new Node(val);
    if (val < root->value) {
        root->left = insert(root->left, val);
    } else if (val > root->value) {
        root->right = insert(root->right, val);
    }
    return root;
}

bool search(Node* root, int val) {
    if (root == nullptr) return false;
    if (val == root->value) return true;
    if (val < root->value) return search(root->left, val);
    return search(root->right, val);
}

int treeHeight(Node* root) {
    if (root == nullptr) return 0;
    int leftH  = treeHeight(root->left);
    int rightH = treeHeight(root->right);
    return 1 + (leftH > rightH ? leftH : rightH);
}

int countNodes(Node* root) {
    if (root == nullptr) return 0;
    return 1 + countNodes(root->left) + countNodes(root->right);
}

int main() {
    Node* root = nullptr;
    int values[] = {5, 3, 8, 1, 4, 7, 9};
    for (int v : values) root = insert(root, v);
    std::cout << "Search 4: " << (search(root, 4) ? "found" : "not found") << std::endl;
    std::cout << "Height: "   << treeHeight(root) << std::endl;
    std::cout << "Nodes: "    << countNodes(root) << std::endl;
    return 0;
}
