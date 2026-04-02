"""
Build Stage 3 Pilot Test Set for Token Trail.

Generates 7 programs x 3 languages = 21 programs.
Categories:
  S01, S02       — Pair A (rename detection)
  S03, S04, S05  — Triple B (reorder + rename)
  S06, S07       — False-positive controls

Output: TestSetJava_pilot.zip, TestSetC_pilot.zip, TestSetCpp_pilot.zip
        + MANIFEST_pilot.md
"""

import io
import os
import zipfile
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "test_repos" / "pilot"


# ═══════════════════════════════════════════════════════════════
#  JAVA PROGRAMS
# ═══════════════════════════════════════════════════════════════

JAVA_S01 = """\
// Linked list implementation — original
public class LinkedList {
    private Node head;
    private int size;

    private static class Node {
        int data;
        Node next;
        Node(int data) {
            this.data = data;
            this.next = null;
        }
    }

    public LinkedList() {
        this.head = null;
        this.size = 0;
    }

    public void insertFront(int value) {
        Node newNode = new Node(value);
        newNode.next = head;
        head = newNode;
        size++;
    }

    public void insertEnd(int value) {
        Node newNode = new Node(value);
        if (head == null) {
            head = newNode;
        } else {
            Node current = head;
            while (current.next != null) {
                current = current.next;
            }
            current.next = newNode;
        }
        size++;
    }

    public boolean search(int value) {
        Node current = head;
        while (current != null) {
            if (current.data == value) {
                return true;
            }
            current = current.next;
        }
        return false;
    }

    public boolean delete(int value) {
        if (head == null) {
            return false;
        }
        if (head.data == value) {
            head = head.next;
            size--;
            return true;
        }
        Node current = head;
        while (current.next != null) {
            if (current.next.data == value) {
                current.next = current.next.next;
                size--;
                return true;
            }
            current = current.next;
        }
        return false;
    }

    public void reverse() {
        Node prev = null;
        Node current = head;
        Node next = null;
        while (current != null) {
            next = current.next;
            current.next = prev;
            prev = current;
            current = next;
        }
        head = prev;
    }

    public int getSize() {
        return size;
    }

    public void printList() {
        Node current = head;
        System.out.print("List: ");
        while (current != null) {
            System.out.print(current.data + " -> ");
            current = current.next;
        }
        System.out.println("null");
    }

    public int getAt(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index out of range: " + index);
        }
        Node current = head;
        for (int i = 0; i < index; i++) {
            current = current.next;
        }
        return current.data;
    }

    public void insertAt(int index, int value) {
        if (index < 0 || index > size) {
            throw new IndexOutOfBoundsException("Index out of range: " + index);
        }
        if (index == 0) {
            insertFront(value);
            return;
        }
        Node newNode = new Node(value);
        Node current = head;
        for (int i = 0; i < index - 1; i++) {
            current = current.next;
        }
        newNode.next = current.next;
        current.next = newNode;
        size++;
    }

    public static void main(String[] args) {
        LinkedList list = new LinkedList();
        for (int i = 1; i <= 10; i++) {
            list.insertEnd(i * 5);
        }
        list.printList();
        System.out.println("Size: " + list.getSize());
        System.out.println("Search 25: " + list.search(25));
        System.out.println("Search 99: " + list.search(99));
        list.delete(25);
        list.printList();
        list.reverse();
        list.printList();
        list.insertAt(3, 999);
        list.printList();
        System.out.println("Element at 3: " + list.getAt(3));
    }
}
"""

JAVA_S02 = """\
// Linked list implementation — local variable rename clone of S01
public class LinkedList {
    private Node head;
    private int size;

    private static class Node {
        int data;
        Node next;
        Node(int data) {
            this.data = data;
            this.next = null;
        }
    }

    public LinkedList() {
        this.head = null;
        this.size = 0;
    }

    public void insertFront(int value) {
        Node n = new Node(value);
        n.next = head;
        head = n;
        size++;
    }

    public void insertEnd(int value) {
        Node n = new Node(value);
        if (head == null) {
            head = n;
        } else {
            Node ptr = head;
            while (ptr.next != null) {
                ptr = ptr.next;
            }
            ptr.next = n;
        }
        size++;
    }

    public boolean search(int value) {
        Node ptr = head;
        while (ptr != null) {
            if (ptr.data == value) {
                return true;
            }
            ptr = ptr.next;
        }
        return false;
    }

    public boolean delete(int value) {
        if (head == null) {
            return false;
        }
        if (head.data == value) {
            head = head.next;
            size--;
            return true;
        }
        Node ptr = head;
        while (ptr.next != null) {
            if (ptr.next.data == value) {
                ptr.next = ptr.next.next;
                size--;
                return true;
            }
            ptr = ptr.next;
        }
        return false;
    }

    public void reverse() {
        Node p = null;
        Node c = head;
        Node n = null;
        while (c != null) {
            n = c.next;
            c.next = p;
            p = c;
            c = n;
        }
        head = p;
    }

    public int getSize() {
        return size;
    }

    public void printList() {
        Node ptr = head;
        System.out.print("List: ");
        while (ptr != null) {
            System.out.print(ptr.data + " -> ");
            ptr = ptr.next;
        }
        System.out.println("null");
    }

    public int getAt(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index out of range: " + index);
        }
        Node ptr = head;
        for (int k = 0; k < index; k++) {
            ptr = ptr.next;
        }
        return ptr.data;
    }

    public void insertAt(int index, int value) {
        if (index < 0 || index > size) {
            throw new IndexOutOfBoundsException("Index out of range: " + index);
        }
        if (index == 0) {
            insertFront(value);
            return;
        }
        Node n = new Node(value);
        Node ptr = head;
        for (int k = 0; k < index - 1; k++) {
            ptr = ptr.next;
        }
        n.next = ptr.next;
        ptr.next = n;
        size++;
    }

    public static void main(String[] args) {
        LinkedList lst = new LinkedList();
        for (int k = 1; k <= 10; k++) {
            lst.insertEnd(k * 5);
        }
        lst.printList();
        System.out.println("Size: " + lst.getSize());
        System.out.println("Search 25: " + lst.search(25));
        System.out.println("Search 99: " + lst.search(99));
        lst.delete(25);
        lst.printList();
        lst.reverse();
        lst.printList();
        lst.insertAt(3, 999);
        lst.printList();
        System.out.println("Element at 3: " + lst.getAt(3));
    }
}
"""

JAVA_S03 = """\
// Matrix operations — original
public class MatrixOps {
    private int[][] matrix;
    private int rows;
    private int cols;

    public MatrixOps(int rows, int cols) {
        this.rows = rows;
        this.cols = cols;
        this.matrix = new int[rows][cols];
    }

    public MatrixOps(int[][] data) {
        this.rows = data.length;
        this.cols = data[0].length;
        this.matrix = new int[rows][cols];
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                this.matrix[i][j] = data[i][j];
            }
        }
    }

    public void set(int row, int col, int value) {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw new IndexOutOfBoundsException("Invalid position");
        }
        matrix[row][col] = value;
    }

    public int get(int row, int col) {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw new IndexOutOfBoundsException("Invalid position");
        }
        return matrix[row][col];
    }

    public MatrixOps add(MatrixOps other) {
        if (this.rows != other.rows || this.cols != other.cols) {
            throw new IllegalArgumentException("Matrix dimensions must match for addition");
        }
        MatrixOps result = new MatrixOps(rows, cols);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result.matrix[i][j] = this.matrix[i][j] + other.matrix[i][j];
            }
        }
        return result;
    }

    public MatrixOps multiply(MatrixOps other) {
        if (this.cols != other.rows) {
            throw new IllegalArgumentException("Incompatible dimensions for multiplication");
        }
        MatrixOps result = new MatrixOps(this.rows, other.cols);
        for (int i = 0; i < this.rows; i++) {
            for (int j = 0; j < other.cols; j++) {
                int sum = 0;
                for (int k = 0; k < this.cols; k++) {
                    sum += this.matrix[i][k] * other.matrix[k][j];
                }
                result.matrix[i][j] = sum;
            }
        }
        return result;
    }

    public MatrixOps transpose() {
        MatrixOps result = new MatrixOps(cols, rows);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result.matrix[j][i] = this.matrix[i][j];
            }
        }
        return result;
    }

    public int trace() {
        if (rows != cols) {
            throw new IllegalStateException("Trace requires a square matrix");
        }
        int sum = 0;
        for (int i = 0; i < rows; i++) {
            sum += matrix[i][i];
        }
        return sum;
    }

    public MatrixOps scalarMultiply(int scalar) {
        MatrixOps result = new MatrixOps(rows, cols);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result.matrix[i][j] = this.matrix[i][j] * scalar;
            }
        }
        return result;
    }

    public boolean isSymmetric() {
        if (rows != cols) return false;
        for (int i = 0; i < rows; i++) {
            for (int j = i + 1; j < cols; j++) {
                if (matrix[i][j] != matrix[j][i]) {
                    return false;
                }
            }
        }
        return true;
    }

    public void print() {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                System.out.printf("%6d", matrix[i][j]);
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        int[][] dataA = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
        int[][] dataB = {{9, 8, 7}, {6, 5, 4}, {3, 2, 1}};
        MatrixOps a = new MatrixOps(dataA);
        MatrixOps b = new MatrixOps(dataB);
        System.out.println("Matrix A:");
        a.print();
        System.out.println("Matrix B:");
        b.print();
        System.out.println("A + B:");
        a.add(b).print();
        System.out.println("A * B:");
        a.multiply(b).print();
        System.out.println("Transpose of A:");
        a.transpose().print();
        System.out.println("Trace of A: " + a.trace());
        System.out.println("A * 3:");
        a.scalarMultiply(3).print();
        System.out.println("A symmetric? " + a.isSymmetric());
    }
}
"""

JAVA_S04 = """\
// Matrix operations — reordered functions, local vars renamed (clone of S03)
public class MatrixOps {
    private int[][] matrix;
    private int rows;
    private int cols;

    public MatrixOps(int rows, int cols) {
        this.rows = rows;
        this.cols = cols;
        this.matrix = new int[rows][cols];
    }

    public MatrixOps(int[][] data) {
        this.rows = data.length;
        this.cols = data[0].length;
        this.matrix = new int[rows][cols];
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                this.matrix[r][c] = data[r][c];
            }
        }
    }

    public MatrixOps transpose() {
        MatrixOps res = new MatrixOps(cols, rows);
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                res.matrix[c][r] = this.matrix[r][c];
            }
        }
        return res;
    }

    public boolean isSymmetric() {
        if (rows != cols) return false;
        for (int r = 0; r < rows; r++) {
            for (int c = r + 1; c < cols; c++) {
                if (matrix[r][c] != matrix[c][r]) {
                    return false;
                }
            }
        }
        return true;
    }

    public MatrixOps scalarMultiply(int scalar) {
        MatrixOps res = new MatrixOps(rows, cols);
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                res.matrix[r][c] = this.matrix[r][c] * scalar;
            }
        }
        return res;
    }

    public void set(int row, int col, int value) {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw new IndexOutOfBoundsException("Invalid position");
        }
        matrix[row][col] = value;
    }

    public int get(int row, int col) {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw new IndexOutOfBoundsException("Invalid position");
        }
        return matrix[row][col];
    }

    public int trace() {
        if (rows != cols) {
            throw new IllegalStateException("Trace requires a square matrix");
        }
        int total = 0;
        for (int r = 0; r < rows; r++) {
            total += matrix[r][r];
        }
        return total;
    }

    public MatrixOps add(MatrixOps other) {
        if (this.rows != other.rows || this.cols != other.cols) {
            throw new IllegalArgumentException("Matrix dimensions must match for addition");
        }
        MatrixOps res = new MatrixOps(rows, cols);
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                res.matrix[r][c] = this.matrix[r][c] + other.matrix[r][c];
            }
        }
        return res;
    }

    public MatrixOps multiply(MatrixOps other) {
        if (this.cols != other.rows) {
            throw new IllegalArgumentException("Incompatible dimensions for multiplication");
        }
        MatrixOps res = new MatrixOps(this.rows, other.cols);
        for (int r = 0; r < this.rows; r++) {
            for (int c = 0; c < other.cols; c++) {
                int acc = 0;
                for (int k = 0; k < this.cols; k++) {
                    acc += this.matrix[r][k] * other.matrix[k][c];
                }
                res.matrix[r][c] = acc;
            }
        }
        return res;
    }

    public void print() {
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                System.out.printf("%6d", matrix[r][c]);
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        int[][] d1 = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
        int[][] d2 = {{9, 8, 7}, {6, 5, 4}, {3, 2, 1}};
        MatrixOps m1 = new MatrixOps(d1);
        MatrixOps m2 = new MatrixOps(d2);
        System.out.println("Matrix A:");
        m1.print();
        System.out.println("Matrix B:");
        m2.print();
        System.out.println("A + B:");
        m1.add(m2).print();
        System.out.println("A * B:");
        m1.multiply(m2).print();
        System.out.println("Transpose of A:");
        m1.transpose().print();
        System.out.println("Trace of A: " + m1.trace());
        System.out.println("A * 3:");
        m1.scalarMultiply(3).print();
        System.out.println("A symmetric? " + m1.isSymmetric());
    }
}
"""

JAVA_S05 = """\
// Matrix operations — local vars renamed variant 2 (clone of S03)
public class MatrixOps {
    private int[][] matrix;
    private int rows;
    private int cols;

    public MatrixOps(int rows, int cols) {
        this.rows = rows;
        this.cols = cols;
        this.matrix = new int[rows][cols];
    }

    public MatrixOps(int[][] data) {
        this.rows = data.length;
        this.cols = data[0].length;
        this.matrix = new int[rows][cols];
        for (int a = 0; a < rows; a++) {
            for (int b = 0; b < cols; b++) {
                this.matrix[a][b] = data[a][b];
            }
        }
    }

    public void set(int row, int col, int value) {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw new IndexOutOfBoundsException("Invalid position");
        }
        matrix[row][col] = value;
    }

    public int get(int row, int col) {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw new IndexOutOfBoundsException("Invalid position");
        }
        return matrix[row][col];
    }

    public MatrixOps add(MatrixOps other) {
        if (this.rows != other.rows || this.cols != other.cols) {
            throw new IllegalArgumentException("Matrix dimensions must match for addition");
        }
        MatrixOps out = new MatrixOps(rows, cols);
        for (int a = 0; a < rows; a++) {
            for (int b = 0; b < cols; b++) {
                out.matrix[a][b] = this.matrix[a][b] + other.matrix[a][b];
            }
        }
        return out;
    }

    public MatrixOps multiply(MatrixOps other) {
        if (this.cols != other.rows) {
            throw new IllegalArgumentException("Incompatible dimensions for multiplication");
        }
        MatrixOps out = new MatrixOps(this.rows, other.cols);
        for (int a = 0; a < this.rows; a++) {
            for (int b = 0; b < other.cols; b++) {
                int val = 0;
                for (int k = 0; k < this.cols; k++) {
                    val += this.matrix[a][k] * other.matrix[k][b];
                }
                out.matrix[a][b] = val;
            }
        }
        return out;
    }

    public MatrixOps transpose() {
        MatrixOps out = new MatrixOps(cols, rows);
        for (int a = 0; a < rows; a++) {
            for (int b = 0; b < cols; b++) {
                out.matrix[b][a] = this.matrix[a][b];
            }
        }
        return out;
    }

    public int trace() {
        if (rows != cols) {
            throw new IllegalStateException("Trace requires a square matrix");
        }
        int val = 0;
        for (int a = 0; a < rows; a++) {
            val += matrix[a][a];
        }
        return val;
    }

    public MatrixOps scalarMultiply(int scalar) {
        MatrixOps out = new MatrixOps(rows, cols);
        for (int a = 0; a < rows; a++) {
            for (int b = 0; b < cols; b++) {
                out.matrix[a][b] = this.matrix[a][b] * scalar;
            }
        }
        return out;
    }

    public boolean isSymmetric() {
        if (rows != cols) return false;
        for (int a = 0; a < rows; a++) {
            for (int b = a + 1; b < cols; b++) {
                if (matrix[a][b] != matrix[b][a]) {
                    return false;
                }
            }
        }
        return true;
    }

    public void print() {
        for (int a = 0; a < rows; a++) {
            for (int b = 0; b < cols; b++) {
                System.out.printf("%6d", matrix[a][b]);
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        int[][] x = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
        int[][] y = {{9, 8, 7}, {6, 5, 4}, {3, 2, 1}};
        MatrixOps p = new MatrixOps(x);
        MatrixOps q = new MatrixOps(y);
        System.out.println("Matrix A:");
        p.print();
        System.out.println("Matrix B:");
        q.print();
        System.out.println("A + B:");
        p.add(q).print();
        System.out.println("A * B:");
        p.multiply(q).print();
        System.out.println("Transpose of A:");
        p.transpose().print();
        System.out.println("Trace of A: " + p.trace());
        System.out.println("A * 3:");
        p.scalarMultiply(3).print();
        System.out.println("A symmetric? " + p.isSymmetric());
    }
}
"""

JAVA_S06 = """\
// Binary search tree — independent (false positive control)
public class BinarySearchTree {
    private TreeNode root;

    private static class TreeNode {
        int key;
        TreeNode left;
        TreeNode right;
        TreeNode(int key) {
            this.key = key;
            this.left = null;
            this.right = null;
        }
    }

    public BinarySearchTree() {
        this.root = null;
    }

    public void insert(int key) {
        root = insertRecursive(root, key);
    }

    private TreeNode insertRecursive(TreeNode node, int key) {
        if (node == null) {
            return new TreeNode(key);
        }
        if (key < node.key) {
            node.left = insertRecursive(node.left, key);
        } else if (key > node.key) {
            node.right = insertRecursive(node.right, key);
        }
        return node;
    }

    public boolean contains(int key) {
        return containsRecursive(root, key);
    }

    private boolean containsRecursive(TreeNode node, int key) {
        if (node == null) return false;
        if (key == node.key) return true;
        if (key < node.key) return containsRecursive(node.left, key);
        return containsRecursive(node.right, key);
    }

    public void inorderTraversal() {
        System.out.print("Inorder: ");
        inorderHelper(root);
        System.out.println();
    }

    private void inorderHelper(TreeNode node) {
        if (node == null) return;
        inorderHelper(node.left);
        System.out.print(node.key + " ");
        inorderHelper(node.right);
    }

    public void preorderTraversal() {
        System.out.print("Preorder: ");
        preorderHelper(root);
        System.out.println();
    }

    private void preorderHelper(TreeNode node) {
        if (node == null) return;
        System.out.print(node.key + " ");
        preorderHelper(node.left);
        preorderHelper(node.right);
    }

    public int findMin() {
        if (root == null) throw new IllegalStateException("Tree is empty");
        TreeNode current = root;
        while (current.left != null) {
            current = current.left;
        }
        return current.key;
    }

    public int findMax() {
        if (root == null) throw new IllegalStateException("Tree is empty");
        TreeNode current = root;
        while (current.right != null) {
            current = current.right;
        }
        return current.key;
    }

    public int height() {
        return heightHelper(root);
    }

    private int heightHelper(TreeNode node) {
        if (node == null) return -1;
        int leftH = heightHelper(node.left);
        int rightH = heightHelper(node.right);
        return 1 + Math.max(leftH, rightH);
    }

    public int countNodes() {
        return countHelper(root);
    }

    private int countHelper(TreeNode node) {
        if (node == null) return 0;
        return 1 + countHelper(node.left) + countHelper(node.right);
    }

    public void delete(int key) {
        root = deleteRecursive(root, key);
    }

    private TreeNode deleteRecursive(TreeNode node, int key) {
        if (node == null) return null;
        if (key < node.key) {
            node.left = deleteRecursive(node.left, key);
        } else if (key > node.key) {
            node.right = deleteRecursive(node.right, key);
        } else {
            if (node.left == null) return node.right;
            if (node.right == null) return node.left;
            TreeNode successor = node.right;
            while (successor.left != null) {
                successor = successor.left;
            }
            node.key = successor.key;
            node.right = deleteRecursive(node.right, successor.key);
        }
        return node;
    }

    public static void main(String[] args) {
        BinarySearchTree bst = new BinarySearchTree();
        int[] values = {50, 30, 70, 20, 40, 60, 80, 10, 25, 35};
        for (int v : values) {
            bst.insert(v);
        }
        bst.inorderTraversal();
        bst.preorderTraversal();
        System.out.println("Contains 40: " + bst.contains(40));
        System.out.println("Contains 99: " + bst.contains(99));
        System.out.println("Min: " + bst.findMin());
        System.out.println("Max: " + bst.findMax());
        System.out.println("Height: " + bst.height());
        System.out.println("Nodes: " + bst.countNodes());
        bst.delete(30);
        System.out.println("After deleting 30:");
        bst.inorderTraversal();
    }
}
"""

JAVA_S07 = """\
// Sorting algorithms comparison — independent (false positive control)
public class SortBenchmark {
    public static int[] bubbleSort(int[] arr) {
        int[] a = arr.clone();
        int n = a.length;
        for (int i = 0; i < n - 1; i++) {
            boolean swapped = false;
            for (int j = 0; j < n - i - 1; j++) {
                if (a[j] > a[j + 1]) {
                    int temp = a[j];
                    a[j] = a[j + 1];
                    a[j + 1] = temp;
                    swapped = true;
                }
            }
            if (!swapped) break;
        }
        return a;
    }

    public static int[] selectionSort(int[] arr) {
        int[] a = arr.clone();
        int n = a.length;
        for (int i = 0; i < n - 1; i++) {
            int minIdx = i;
            for (int j = i + 1; j < n; j++) {
                if (a[j] < a[minIdx]) {
                    minIdx = j;
                }
            }
            int temp = a[minIdx];
            a[minIdx] = a[i];
            a[i] = temp;
        }
        return a;
    }

    public static int[] insertionSort(int[] arr) {
        int[] a = arr.clone();
        int n = a.length;
        for (int i = 1; i < n; i++) {
            int key = a[i];
            int j = i - 1;
            while (j >= 0 && a[j] > key) {
                a[j + 1] = a[j];
                j--;
            }
            a[j + 1] = key;
        }
        return a;
    }

    public static int[] mergeSort(int[] arr) {
        if (arr.length <= 1) return arr.clone();
        int mid = arr.length / 2;
        int[] left = new int[mid];
        int[] right = new int[arr.length - mid];
        System.arraycopy(arr, 0, left, 0, mid);
        System.arraycopy(arr, mid, right, 0, arr.length - mid);
        left = mergeSort(left);
        right = mergeSort(right);
        return merge(left, right);
    }

    private static int[] merge(int[] left, int[] right) {
        int[] result = new int[left.length + right.length];
        int i = 0, j = 0, k = 0;
        while (i < left.length && j < right.length) {
            if (left[i] <= right[j]) {
                result[k++] = left[i++];
            } else {
                result[k++] = right[j++];
            }
        }
        while (i < left.length) result[k++] = left[i++];
        while (j < right.length) result[k++] = right[j++];
        return result;
    }

    public static int[] quickSort(int[] arr) {
        int[] a = arr.clone();
        quickSortHelper(a, 0, a.length - 1);
        return a;
    }

    private static void quickSortHelper(int[] a, int low, int high) {
        if (low < high) {
            int pivot = partition(a, low, high);
            quickSortHelper(a, low, pivot - 1);
            quickSortHelper(a, pivot + 1, high);
        }
    }

    private static int partition(int[] a, int low, int high) {
        int pivot = a[high];
        int i = low - 1;
        for (int j = low; j < high; j++) {
            if (a[j] < pivot) {
                i++;
                int temp = a[i];
                a[i] = a[j];
                a[j] = temp;
            }
        }
        int temp = a[i + 1];
        a[i + 1] = a[high];
        a[high] = temp;
        return i + 1;
    }

    public static void printArray(String label, int[] a) {
        System.out.print(label + ": [");
        for (int i = 0; i < a.length; i++) {
            System.out.print(a[i]);
            if (i < a.length - 1) System.out.print(", ");
        }
        System.out.println("]");
    }

    public static boolean isSorted(int[] a) {
        for (int i = 1; i < a.length; i++) {
            if (a[i] < a[i - 1]) return false;
        }
        return true;
    }

    public static void main(String[] args) {
        int[] data = {64, 34, 25, 12, 22, 11, 90, 1, 55, 43, 77, 8};
        printArray("Original", data);
        int[] b = bubbleSort(data);
        printArray("Bubble", b);
        System.out.println("Sorted: " + isSorted(b));
        int[] s = selectionSort(data);
        printArray("Selection", s);
        System.out.println("Sorted: " + isSorted(s));
        int[] ins = insertionSort(data);
        printArray("Insertion", ins);
        System.out.println("Sorted: " + isSorted(ins));
        int[] m = mergeSort(data);
        printArray("Merge", m);
        System.out.println("Sorted: " + isSorted(m));
        int[] q = quickSort(data);
        printArray("Quick", q);
        System.out.println("Sorted: " + isSorted(q));
    }
}
"""


# ═══════════════════════════════════════════════════════════════
#  C PROGRAMS
# ═══════════════════════════════════════════════════════════════

C_S01 = """\
/* Linked list implementation — original */
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

typedef struct {
    Node* head;
    int size;
} LinkedList;

void initList(LinkedList* list) {
    list->head = NULL;
    list->size = 0;
}

void insertFront(LinkedList* list, int value) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->data = value;
    newNode->next = list->head;
    list->head = newNode;
    list->size++;
}

void insertEnd(LinkedList* list, int value) {
    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->data = value;
    newNode->next = NULL;
    if (list->head == NULL) {
        list->head = newNode;
    } else {
        Node* current = list->head;
        while (current->next != NULL) {
            current = current->next;
        }
        current->next = newNode;
    }
    list->size++;
}

int search(LinkedList* list, int value) {
    Node* current = list->head;
    while (current != NULL) {
        if (current->data == value) {
            return 1;
        }
        current = current->next;
    }
    return 0;
}

int deleteNode(LinkedList* list, int value) {
    if (list->head == NULL) {
        return 0;
    }
    if (list->head->data == value) {
        Node* temp = list->head;
        list->head = list->head->next;
        free(temp);
        list->size--;
        return 1;
    }
    Node* current = list->head;
    while (current->next != NULL) {
        if (current->next->data == value) {
            Node* temp = current->next;
            current->next = current->next->next;
            free(temp);
            list->size--;
            return 1;
        }
        current = current->next;
    }
    return 0;
}

void reverseList(LinkedList* list) {
    Node* prev = NULL;
    Node* current = list->head;
    Node* next = NULL;
    while (current != NULL) {
        next = current->next;
        current->next = prev;
        prev = current;
        current = next;
    }
    list->head = prev;
}

int getAt(LinkedList* list, int index) {
    if (index < 0 || index >= list->size) {
        fprintf(stderr, "Index out of range: %d\\n", index);
        return -1;
    }
    Node* current = list->head;
    for (int i = 0; i < index; i++) {
        current = current->next;
    }
    return current->data;
}

void insertAt(LinkedList* list, int index, int value) {
    if (index < 0 || index > list->size) {
        fprintf(stderr, "Index out of range: %d\\n", index);
        return;
    }
    if (index == 0) {
        insertFront(list, value);
        return;
    }
    Node* newNode = (Node*)malloc(sizeof(Node));
    newNode->data = value;
    Node* current = list->head;
    for (int i = 0; i < index - 1; i++) {
        current = current->next;
    }
    newNode->next = current->next;
    current->next = newNode;
    list->size++;
}

void printList(LinkedList* list) {
    Node* current = list->head;
    printf("List: ");
    while (current != NULL) {
        printf("%d -> ", current->data);
        current = current->next;
    }
    printf("NULL\\n");
}

void freeList(LinkedList* list) {
    Node* current = list->head;
    while (current != NULL) {
        Node* temp = current;
        current = current->next;
        free(temp);
    }
    list->head = NULL;
    list->size = 0;
}

int main() {
    LinkedList list;
    initList(&list);
    for (int i = 1; i <= 10; i++) {
        insertEnd(&list, i * 5);
    }
    printList(&list);
    printf("Size: %d\\n", list.size);
    printf("Search 25: %d\\n", search(&list, 25));
    printf("Search 99: %d\\n", search(&list, 99));
    deleteNode(&list, 25);
    printList(&list);
    reverseList(&list);
    printList(&list);
    insertAt(&list, 3, 999);
    printList(&list);
    printf("Element at 3: %d\\n", getAt(&list, 3));
    freeList(&list);
    return 0;
}
"""

C_S02 = """\
/* Linked list implementation — local variable rename clone of S01 */
#include <stdio.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

typedef struct {
    Node* head;
    int size;
} LinkedList;

void initList(LinkedList* list) {
    list->head = NULL;
    list->size = 0;
}

void insertFront(LinkedList* list, int value) {
    Node* n = (Node*)malloc(sizeof(Node));
    n->data = value;
    n->next = list->head;
    list->head = n;
    list->size++;
}

void insertEnd(LinkedList* list, int value) {
    Node* n = (Node*)malloc(sizeof(Node));
    n->data = value;
    n->next = NULL;
    if (list->head == NULL) {
        list->head = n;
    } else {
        Node* ptr = list->head;
        while (ptr->next != NULL) {
            ptr = ptr->next;
        }
        ptr->next = n;
    }
    list->size++;
}

int search(LinkedList* list, int value) {
    Node* ptr = list->head;
    while (ptr != NULL) {
        if (ptr->data == value) {
            return 1;
        }
        ptr = ptr->next;
    }
    return 0;
}

int deleteNode(LinkedList* list, int value) {
    if (list->head == NULL) {
        return 0;
    }
    if (list->head->data == value) {
        Node* t = list->head;
        list->head = list->head->next;
        free(t);
        list->size--;
        return 1;
    }
    Node* ptr = list->head;
    while (ptr->next != NULL) {
        if (ptr->next->data == value) {
            Node* t = ptr->next;
            ptr->next = ptr->next->next;
            free(t);
            list->size--;
            return 1;
        }
        ptr = ptr->next;
    }
    return 0;
}

void reverseList(LinkedList* list) {
    Node* p = NULL;
    Node* c = list->head;
    Node* n = NULL;
    while (c != NULL) {
        n = c->next;
        c->next = p;
        p = c;
        c = n;
    }
    list->head = p;
}

int getAt(LinkedList* list, int index) {
    if (index < 0 || index >= list->size) {
        fprintf(stderr, "Index out of range: %d\\n", index);
        return -1;
    }
    Node* ptr = list->head;
    for (int k = 0; k < index; k++) {
        ptr = ptr->next;
    }
    return ptr->data;
}

void insertAt(LinkedList* list, int index, int value) {
    if (index < 0 || index > list->size) {
        fprintf(stderr, "Index out of range: %d\\n", index);
        return;
    }
    if (index == 0) {
        insertFront(list, value);
        return;
    }
    Node* n = (Node*)malloc(sizeof(Node));
    n->data = value;
    Node* ptr = list->head;
    for (int k = 0; k < index - 1; k++) {
        ptr = ptr->next;
    }
    n->next = ptr->next;
    ptr->next = n;
    list->size++;
}

void printList(LinkedList* list) {
    Node* ptr = list->head;
    printf("List: ");
    while (ptr != NULL) {
        printf("%d -> ", ptr->data);
        ptr = ptr->next;
    }
    printf("NULL\\n");
}

void freeList(LinkedList* list) {
    Node* ptr = list->head;
    while (ptr != NULL) {
        Node* t = ptr;
        ptr = ptr->next;
        free(t);
    }
    list->head = NULL;
    list->size = 0;
}

int main() {
    LinkedList lst;
    initList(&lst);
    for (int k = 1; k <= 10; k++) {
        insertEnd(&lst, k * 5);
    }
    printList(&lst);
    printf("Size: %d\\n", lst.size);
    printf("Search 25: %d\\n", search(&lst, 25));
    printf("Search 99: %d\\n", search(&lst, 99));
    deleteNode(&lst, 25);
    printList(&lst);
    reverseList(&lst);
    printList(&lst);
    insertAt(&lst, 3, 999);
    printList(&lst);
    printf("Element at 3: %d\\n", getAt(&lst, 3));
    freeList(&lst);
    return 0;
}
"""

C_S03 = """\
/* Matrix operations — original */
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int** data;
    int rows;
    int cols;
} Matrix;

Matrix* createMatrix(int rows, int cols) {
    Matrix* m = (Matrix*)malloc(sizeof(Matrix));
    m->rows = rows;
    m->cols = cols;
    m->data = (int**)malloc(rows * sizeof(int*));
    for (int i = 0; i < rows; i++) {
        m->data[i] = (int*)calloc(cols, sizeof(int));
    }
    return m;
}

void freeMatrix(Matrix* m) {
    for (int i = 0; i < m->rows; i++) {
        free(m->data[i]);
    }
    free(m->data);
    free(m);
}

void setElement(Matrix* m, int row, int col, int value) {
    if (row < 0 || row >= m->rows || col < 0 || col >= m->cols) {
        fprintf(stderr, "Invalid position\\n");
        return;
    }
    m->data[row][col] = value;
}

int getElement(Matrix* m, int row, int col) {
    if (row < 0 || row >= m->rows || col < 0 || col >= m->cols) {
        fprintf(stderr, "Invalid position\\n");
        return 0;
    }
    return m->data[row][col];
}

Matrix* addMatrix(Matrix* a, Matrix* b) {
    if (a->rows != b->rows || a->cols != b->cols) {
        fprintf(stderr, "Dimension mismatch for addition\\n");
        return NULL;
    }
    Matrix* result = createMatrix(a->rows, a->cols);
    for (int i = 0; i < a->rows; i++) {
        for (int j = 0; j < a->cols; j++) {
            result->data[i][j] = a->data[i][j] + b->data[i][j];
        }
    }
    return result;
}

Matrix* multiplyMatrix(Matrix* a, Matrix* b) {
    if (a->cols != b->rows) {
        fprintf(stderr, "Incompatible dimensions for multiplication\\n");
        return NULL;
    }
    Matrix* result = createMatrix(a->rows, b->cols);
    for (int i = 0; i < a->rows; i++) {
        for (int j = 0; j < b->cols; j++) {
            int sum = 0;
            for (int k = 0; k < a->cols; k++) {
                sum += a->data[i][k] * b->data[k][j];
            }
            result->data[i][j] = sum;
        }
    }
    return result;
}

Matrix* transposeMatrix(Matrix* m) {
    Matrix* result = createMatrix(m->cols, m->rows);
    for (int i = 0; i < m->rows; i++) {
        for (int j = 0; j < m->cols; j++) {
            result->data[j][i] = m->data[i][j];
        }
    }
    return result;
}

int traceMatrix(Matrix* m) {
    if (m->rows != m->cols) {
        fprintf(stderr, "Trace requires square matrix\\n");
        return 0;
    }
    int sum = 0;
    for (int i = 0; i < m->rows; i++) {
        sum += m->data[i][i];
    }
    return sum;
}

Matrix* scalarMultiply(Matrix* m, int scalar) {
    Matrix* result = createMatrix(m->rows, m->cols);
    for (int i = 0; i < m->rows; i++) {
        for (int j = 0; j < m->cols; j++) {
            result->data[i][j] = m->data[i][j] * scalar;
        }
    }
    return result;
}

int isSymmetric(Matrix* m) {
    if (m->rows != m->cols) return 0;
    for (int i = 0; i < m->rows; i++) {
        for (int j = i + 1; j < m->cols; j++) {
            if (m->data[i][j] != m->data[j][i]) {
                return 0;
            }
        }
    }
    return 1;
}

void printMatrix(Matrix* m) {
    for (int i = 0; i < m->rows; i++) {
        for (int j = 0; j < m->cols; j++) {
            printf("%6d", m->data[i][j]);
        }
        printf("\\n");
    }
}

int main() {
    int dataA[3][3] = {{1,2,3},{4,5,6},{7,8,9}};
    int dataB[3][3] = {{9,8,7},{6,5,4},{3,2,1}};
    Matrix* a = createMatrix(3, 3);
    Matrix* b = createMatrix(3, 3);
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++) {
            a->data[i][j] = dataA[i][j];
            b->data[i][j] = dataB[i][j];
        }
    printf("Matrix A:\\n"); printMatrix(a);
    printf("Matrix B:\\n"); printMatrix(b);
    Matrix* sum = addMatrix(a, b);
    printf("A + B:\\n"); printMatrix(sum);
    Matrix* prod = multiplyMatrix(a, b);
    printf("A * B:\\n"); printMatrix(prod);
    Matrix* trans = transposeMatrix(a);
    printf("Transpose A:\\n"); printMatrix(trans);
    printf("Trace A: %d\\n", traceMatrix(a));
    Matrix* scaled = scalarMultiply(a, 3);
    printf("A * 3:\\n"); printMatrix(scaled);
    printf("A symmetric? %d\\n", isSymmetric(a));
    freeMatrix(a); freeMatrix(b); freeMatrix(sum);
    freeMatrix(prod); freeMatrix(trans); freeMatrix(scaled);
    return 0;
}
"""

C_S04 = """\
/* Matrix operations — reordered functions, local vars renamed (clone of S03) */
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int** data;
    int rows;
    int cols;
} Matrix;

Matrix* createMatrix(int rows, int cols) {
    Matrix* m = (Matrix*)malloc(sizeof(Matrix));
    m->rows = rows;
    m->cols = cols;
    m->data = (int**)malloc(rows * sizeof(int*));
    for (int r = 0; r < rows; r++) {
        m->data[r] = (int*)calloc(cols, sizeof(int));
    }
    return m;
}

void freeMatrix(Matrix* m) {
    for (int r = 0; r < m->rows; r++) {
        free(m->data[r]);
    }
    free(m->data);
    free(m);
}

Matrix* transposeMatrix(Matrix* m) {
    Matrix* res = createMatrix(m->cols, m->rows);
    for (int r = 0; r < m->rows; r++) {
        for (int c = 0; c < m->cols; c++) {
            res->data[c][r] = m->data[r][c];
        }
    }
    return res;
}

int isSymmetric(Matrix* m) {
    if (m->rows != m->cols) return 0;
    for (int r = 0; r < m->rows; r++) {
        for (int c = r + 1; c < m->cols; c++) {
            if (m->data[r][c] != m->data[c][r]) {
                return 0;
            }
        }
    }
    return 1;
}

Matrix* scalarMultiply(Matrix* m, int scalar) {
    Matrix* res = createMatrix(m->rows, m->cols);
    for (int r = 0; r < m->rows; r++) {
        for (int c = 0; c < m->cols; c++) {
            res->data[r][c] = m->data[r][c] * scalar;
        }
    }
    return res;
}

void setElement(Matrix* m, int row, int col, int value) {
    if (row < 0 || row >= m->rows || col < 0 || col >= m->cols) {
        fprintf(stderr, "Invalid position\\n");
        return;
    }
    m->data[row][col] = value;
}

int getElement(Matrix* m, int row, int col) {
    if (row < 0 || row >= m->rows || col < 0 || col >= m->cols) {
        fprintf(stderr, "Invalid position\\n");
        return 0;
    }
    return m->data[row][col];
}

int traceMatrix(Matrix* m) {
    if (m->rows != m->cols) {
        fprintf(stderr, "Trace requires square matrix\\n");
        return 0;
    }
    int total = 0;
    for (int r = 0; r < m->rows; r++) {
        total += m->data[r][r];
    }
    return total;
}

Matrix* addMatrix(Matrix* a, Matrix* b) {
    if (a->rows != b->rows || a->cols != b->cols) {
        fprintf(stderr, "Dimension mismatch for addition\\n");
        return NULL;
    }
    Matrix* res = createMatrix(a->rows, a->cols);
    for (int r = 0; r < a->rows; r++) {
        for (int c = 0; c < a->cols; c++) {
            res->data[r][c] = a->data[r][c] + b->data[r][c];
        }
    }
    return res;
}

Matrix* multiplyMatrix(Matrix* a, Matrix* b) {
    if (a->cols != b->rows) {
        fprintf(stderr, "Incompatible dimensions for multiplication\\n");
        return NULL;
    }
    Matrix* res = createMatrix(a->rows, b->cols);
    for (int r = 0; r < a->rows; r++) {
        for (int c = 0; c < b->cols; c++) {
            int acc = 0;
            for (int k = 0; k < a->cols; k++) {
                acc += a->data[r][k] * b->data[k][c];
            }
            res->data[r][c] = acc;
        }
    }
    return res;
}

void printMatrix(Matrix* m) {
    for (int r = 0; r < m->rows; r++) {
        for (int c = 0; c < m->cols; c++) {
            printf("%6d", m->data[r][c]);
        }
        printf("\\n");
    }
}

int main() {
    int d1[3][3] = {{1,2,3},{4,5,6},{7,8,9}};
    int d2[3][3] = {{9,8,7},{6,5,4},{3,2,1}};
    Matrix* m1 = createMatrix(3, 3);
    Matrix* m2 = createMatrix(3, 3);
    for (int r = 0; r < 3; r++)
        for (int c = 0; c < 3; c++) {
            m1->data[r][c] = d1[r][c];
            m2->data[r][c] = d2[r][c];
        }
    printf("Matrix A:\\n"); printMatrix(m1);
    printf("Matrix B:\\n"); printMatrix(m2);
    Matrix* s = addMatrix(m1, m2);
    printf("A + B:\\n"); printMatrix(s);
    Matrix* p = multiplyMatrix(m1, m2);
    printf("A * B:\\n"); printMatrix(p);
    Matrix* t = transposeMatrix(m1);
    printf("Transpose A:\\n"); printMatrix(t);
    printf("Trace A: %d\\n", traceMatrix(m1));
    Matrix* sc = scalarMultiply(m1, 3);
    printf("A * 3:\\n"); printMatrix(sc);
    printf("A symmetric? %d\\n", isSymmetric(m1));
    freeMatrix(m1); freeMatrix(m2); freeMatrix(s);
    freeMatrix(p); freeMatrix(t); freeMatrix(sc);
    return 0;
}
"""

C_S05 = """\
/* Matrix operations — local vars renamed variant 2 (clone of S03) */
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int** data;
    int rows;
    int cols;
} Matrix;

Matrix* createMatrix(int rows, int cols) {
    Matrix* m = (Matrix*)malloc(sizeof(Matrix));
    m->rows = rows;
    m->cols = cols;
    m->data = (int**)malloc(rows * sizeof(int*));
    for (int a = 0; a < rows; a++) {
        m->data[a] = (int*)calloc(cols, sizeof(int));
    }
    return m;
}

void freeMatrix(Matrix* m) {
    for (int a = 0; a < m->rows; a++) {
        free(m->data[a]);
    }
    free(m->data);
    free(m);
}

void setElement(Matrix* m, int row, int col, int value) {
    if (row < 0 || row >= m->rows || col < 0 || col >= m->cols) {
        fprintf(stderr, "Invalid position\\n");
        return;
    }
    m->data[row][col] = value;
}

int getElement(Matrix* m, int row, int col) {
    if (row < 0 || row >= m->rows || col < 0 || col >= m->cols) {
        fprintf(stderr, "Invalid position\\n");
        return 0;
    }
    return m->data[row][col];
}

Matrix* addMatrix(Matrix* a, Matrix* b) {
    if (a->rows != b->rows || a->cols != b->cols) {
        fprintf(stderr, "Dimension mismatch for addition\\n");
        return NULL;
    }
    Matrix* out = createMatrix(a->rows, a->cols);
    for (int x = 0; x < a->rows; x++) {
        for (int y = 0; y < a->cols; y++) {
            out->data[x][y] = a->data[x][y] + b->data[x][y];
        }
    }
    return out;
}

Matrix* multiplyMatrix(Matrix* a, Matrix* b) {
    if (a->cols != b->rows) {
        fprintf(stderr, "Incompatible dimensions for multiplication\\n");
        return NULL;
    }
    Matrix* out = createMatrix(a->rows, b->cols);
    for (int x = 0; x < a->rows; x++) {
        for (int y = 0; y < b->cols; y++) {
            int val = 0;
            for (int k = 0; k < a->cols; k++) {
                val += a->data[x][k] * b->data[k][y];
            }
            out->data[x][y] = val;
        }
    }
    return out;
}

Matrix* transposeMatrix(Matrix* m) {
    Matrix* out = createMatrix(m->cols, m->rows);
    for (int x = 0; x < m->rows; x++) {
        for (int y = 0; y < m->cols; y++) {
            out->data[y][x] = m->data[x][y];
        }
    }
    return out;
}

int traceMatrix(Matrix* m) {
    if (m->rows != m->cols) {
        fprintf(stderr, "Trace requires square matrix\\n");
        return 0;
    }
    int val = 0;
    for (int x = 0; x < m->rows; x++) {
        val += m->data[x][x];
    }
    return val;
}

Matrix* scalarMultiply(Matrix* m, int scalar) {
    Matrix* out = createMatrix(m->rows, m->cols);
    for (int x = 0; x < m->rows; x++) {
        for (int y = 0; y < m->cols; y++) {
            out->data[x][y] = m->data[x][y] * scalar;
        }
    }
    return out;
}

int isSymmetric(Matrix* m) {
    if (m->rows != m->cols) return 0;
    for (int x = 0; x < m->rows; x++) {
        for (int y = x + 1; y < m->cols; y++) {
            if (m->data[x][y] != m->data[y][x]) {
                return 0;
            }
        }
    }
    return 1;
}

void printMatrix(Matrix* m) {
    for (int x = 0; x < m->rows; x++) {
        for (int y = 0; y < m->cols; y++) {
            printf("%6d", m->data[x][y]);
        }
        printf("\\n");
    }
}

int main() {
    int d1[3][3] = {{1,2,3},{4,5,6},{7,8,9}};
    int d2[3][3] = {{9,8,7},{6,5,4},{3,2,1}};
    Matrix* p = createMatrix(3, 3);
    Matrix* q = createMatrix(3, 3);
    for (int x = 0; x < 3; x++)
        for (int y = 0; y < 3; y++) {
            p->data[x][y] = d1[x][y];
            q->data[x][y] = d2[x][y];
        }
    printf("Matrix A:\\n"); printMatrix(p);
    printf("Matrix B:\\n"); printMatrix(q);
    Matrix* s = addMatrix(p, q);
    printf("A + B:\\n"); printMatrix(s);
    Matrix* pr = multiplyMatrix(p, q);
    printf("A * B:\\n"); printMatrix(pr);
    Matrix* t = transposeMatrix(p);
    printf("Transpose A:\\n"); printMatrix(t);
    printf("Trace A: %d\\n", traceMatrix(p));
    Matrix* sc = scalarMultiply(p, 3);
    printf("A * 3:\\n"); printMatrix(sc);
    printf("A symmetric? %d\\n", isSymmetric(p));
    freeMatrix(p); freeMatrix(q); freeMatrix(s);
    freeMatrix(pr); freeMatrix(t); freeMatrix(sc);
    return 0;
}
"""

C_S06 = """\
/* Binary search tree — independent (false positive control) */
#include <stdio.h>
#include <stdlib.h>

typedef struct TreeNode {
    int key;
    struct TreeNode* left;
    struct TreeNode* right;
} TreeNode;

TreeNode* createNode(int key) {
    TreeNode* node = (TreeNode*)malloc(sizeof(TreeNode));
    node->key = key;
    node->left = NULL;
    node->right = NULL;
    return node;
}

TreeNode* insert(TreeNode* root, int key) {
    if (root == NULL) return createNode(key);
    if (key < root->key) {
        root->left = insert(root->left, key);
    } else if (key > root->key) {
        root->right = insert(root->right, key);
    }
    return root;
}

int contains(TreeNode* root, int key) {
    if (root == NULL) return 0;
    if (key == root->key) return 1;
    if (key < root->key) return contains(root->left, key);
    return contains(root->right, key);
}

void inorder(TreeNode* root) {
    if (root == NULL) return;
    inorder(root->left);
    printf("%d ", root->key);
    inorder(root->right);
}

void preorder(TreeNode* root) {
    if (root == NULL) return;
    printf("%d ", root->key);
    preorder(root->left);
    preorder(root->right);
}

int findMin(TreeNode* root) {
    if (root == NULL) {
        fprintf(stderr, "Tree is empty\\n");
        return -1;
    }
    while (root->left != NULL) {
        root = root->left;
    }
    return root->key;
}

int findMax(TreeNode* root) {
    if (root == NULL) {
        fprintf(stderr, "Tree is empty\\n");
        return -1;
    }
    while (root->right != NULL) {
        root = root->right;
    }
    return root->key;
}

int treeHeight(TreeNode* root) {
    if (root == NULL) return -1;
    int leftH = treeHeight(root->left);
    int rightH = treeHeight(root->right);
    return 1 + (leftH > rightH ? leftH : rightH);
}

int countNodes(TreeNode* root) {
    if (root == NULL) return 0;
    return 1 + countNodes(root->left) + countNodes(root->right);
}

TreeNode* findMinNode(TreeNode* root) {
    while (root && root->left) root = root->left;
    return root;
}

TreeNode* deleteNode(TreeNode* root, int key) {
    if (root == NULL) return NULL;
    if (key < root->key) {
        root->left = deleteNode(root->left, key);
    } else if (key > root->key) {
        root->right = deleteNode(root->right, key);
    } else {
        if (root->left == NULL) {
            TreeNode* temp = root->right;
            free(root);
            return temp;
        }
        if (root->right == NULL) {
            TreeNode* temp = root->left;
            free(root);
            return temp;
        }
        TreeNode* successor = findMinNode(root->right);
        root->key = successor->key;
        root->right = deleteNode(root->right, successor->key);
    }
    return root;
}

void freeTree(TreeNode* root) {
    if (root == NULL) return;
    freeTree(root->left);
    freeTree(root->right);
    free(root);
}

int main() {
    TreeNode* root = NULL;
    int values[] = {50, 30, 70, 20, 40, 60, 80, 10, 25, 35};
    int n = sizeof(values) / sizeof(values[0]);
    for (int i = 0; i < n; i++) {
        root = insert(root, values[i]);
    }
    printf("Inorder: "); inorder(root); printf("\\n");
    printf("Preorder: "); preorder(root); printf("\\n");
    printf("Contains 40: %d\\n", contains(root, 40));
    printf("Contains 99: %d\\n", contains(root, 99));
    printf("Min: %d\\n", findMin(root));
    printf("Max: %d\\n", findMax(root));
    printf("Height: %d\\n", treeHeight(root));
    printf("Nodes: %d\\n", countNodes(root));
    root = deleteNode(root, 30);
    printf("After deleting 30:\\n");
    printf("Inorder: "); inorder(root); printf("\\n");
    freeTree(root);
    return 0;
}
"""

C_S07 = """\
/* Sorting algorithms comparison — independent (false positive control) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void bubbleSort(int* a, int n) {
    for (int i = 0; i < n - 1; i++) {
        int swapped = 0;
        for (int j = 0; j < n - i - 1; j++) {
            if (a[j] > a[j + 1]) {
                int temp = a[j];
                a[j] = a[j + 1];
                a[j + 1] = temp;
                swapped = 1;
            }
        }
        if (!swapped) break;
    }
}

void selectionSort(int* a, int n) {
    for (int i = 0; i < n - 1; i++) {
        int minIdx = i;
        for (int j = i + 1; j < n; j++) {
            if (a[j] < a[minIdx]) {
                minIdx = j;
            }
        }
        int temp = a[minIdx];
        a[minIdx] = a[i];
        a[i] = temp;
    }
}

void insertionSort(int* a, int n) {
    for (int i = 1; i < n; i++) {
        int key = a[i];
        int j = i - 1;
        while (j >= 0 && a[j] > key) {
            a[j + 1] = a[j];
            j--;
        }
        a[j + 1] = key;
    }
}

void mergeParts(int* a, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    int* L = (int*)malloc(n1 * sizeof(int));
    int* R = (int*)malloc(n2 * sizeof(int));
    for (int i = 0; i < n1; i++) L[i] = a[left + i];
    for (int j = 0; j < n2; j++) R[j] = a[mid + 1 + j];
    int i = 0, j = 0, k = left;
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            a[k++] = L[i++];
        } else {
            a[k++] = R[j++];
        }
    }
    while (i < n1) a[k++] = L[i++];
    while (j < n2) a[k++] = R[j++];
    free(L);
    free(R);
}

void mergeSort(int* a, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        mergeSort(a, left, mid);
        mergeSort(a, mid + 1, right);
        mergeParts(a, left, mid, right);
    }
}

int partition(int* a, int low, int high) {
    int pivot = a[high];
    int i = low - 1;
    for (int j = low; j < high; j++) {
        if (a[j] < pivot) {
            i++;
            int temp = a[i];
            a[i] = a[j];
            a[j] = temp;
        }
    }
    int temp = a[i + 1];
    a[i + 1] = a[high];
    a[high] = temp;
    return i + 1;
}

void quickSort(int* a, int low, int high) {
    if (low < high) {
        int pi = partition(a, low, high);
        quickSort(a, low, pi - 1);
        quickSort(a, pi + 1, high);
    }
}

void printArray(const char* label, int* a, int n) {
    printf("%s: [", label);
    for (int i = 0; i < n; i++) {
        printf("%d", a[i]);
        if (i < n - 1) printf(", ");
    }
    printf("]\\n");
}

int isSorted(int* a, int n) {
    for (int i = 1; i < n; i++) {
        if (a[i] < a[i - 1]) return 0;
    }
    return 1;
}

int main() {
    int data[] = {64, 34, 25, 12, 22, 11, 90, 1, 55, 43, 77, 8};
    int n = sizeof(data) / sizeof(data[0]);
    int* copy;
    printArray("Original", data, n);
    copy = (int*)malloc(n * sizeof(int));
    memcpy(copy, data, n * sizeof(int));
    bubbleSort(copy, n);
    printArray("Bubble", copy, n);
    printf("Sorted: %d\\n", isSorted(copy, n));
    memcpy(copy, data, n * sizeof(int));
    selectionSort(copy, n);
    printArray("Selection", copy, n);
    printf("Sorted: %d\\n", isSorted(copy, n));
    memcpy(copy, data, n * sizeof(int));
    insertionSort(copy, n);
    printArray("Insertion", copy, n);
    printf("Sorted: %d\\n", isSorted(copy, n));
    memcpy(copy, data, n * sizeof(int));
    mergeSort(copy, 0, n - 1);
    printArray("Merge", copy, n);
    printf("Sorted: %d\\n", isSorted(copy, n));
    memcpy(copy, data, n * sizeof(int));
    quickSort(copy, 0, n - 1);
    printArray("Quick", copy, n);
    printf("Sorted: %d\\n", isSorted(copy, n));
    free(copy);
    return 0;
}
"""


# ═══════════════════════════════════════════════════════════════
#  C++ PROGRAMS
# ═══════════════════════════════════════════════════════════════

CPP_S01 = """\
// Linked list implementation — original
#include <iostream>
#include <stdexcept>

class LinkedList {
private:
    struct Node {
        int data;
        Node* next;
        Node(int data) : data(data), next(nullptr) {}
    };
    Node* head;
    int size;

public:
    LinkedList() : head(nullptr), size(0) {}

    ~LinkedList() {
        Node* current = head;
        while (current) {
            Node* temp = current;
            current = current->next;
            delete temp;
        }
    }

    void insertFront(int value) {
        Node* newNode = new Node(value);
        newNode->next = head;
        head = newNode;
        size++;
    }

    void insertEnd(int value) {
        Node* newNode = new Node(value);
        if (!head) {
            head = newNode;
        } else {
            Node* current = head;
            while (current->next) {
                current = current->next;
            }
            current->next = newNode;
        }
        size++;
    }

    bool search(int value) const {
        Node* current = head;
        while (current) {
            if (current->data == value) {
                return true;
            }
            current = current->next;
        }
        return false;
    }

    bool remove(int value) {
        if (!head) return false;
        if (head->data == value) {
            Node* temp = head;
            head = head->next;
            delete temp;
            size--;
            return true;
        }
        Node* current = head;
        while (current->next) {
            if (current->next->data == value) {
                Node* temp = current->next;
                current->next = current->next->next;
                delete temp;
                size--;
                return true;
            }
            current = current->next;
        }
        return false;
    }

    void reverse() {
        Node* prev = nullptr;
        Node* current = head;
        Node* next = nullptr;
        while (current) {
            next = current->next;
            current->next = prev;
            prev = current;
            current = next;
        }
        head = prev;
    }

    int getSize() const { return size; }

    void print() const {
        Node* current = head;
        std::cout << "List: ";
        while (current) {
            std::cout << current->data << " -> ";
            current = current->next;
        }
        std::cout << "null" << std::endl;
    }

    int getAt(int index) const {
        if (index < 0 || index >= size) {
            throw std::out_of_range("Index out of range");
        }
        Node* current = head;
        for (int i = 0; i < index; i++) {
            current = current->next;
        }
        return current->data;
    }

    void insertAt(int index, int value) {
        if (index < 0 || index > size) {
            throw std::out_of_range("Index out of range");
        }
        if (index == 0) {
            insertFront(value);
            return;
        }
        Node* newNode = new Node(value);
        Node* current = head;
        for (int i = 0; i < index - 1; i++) {
            current = current->next;
        }
        newNode->next = current->next;
        current->next = newNode;
        size++;
    }
};

int main() {
    LinkedList list;
    for (int i = 1; i <= 10; i++) {
        list.insertEnd(i * 5);
    }
    list.print();
    std::cout << "Size: " << list.getSize() << std::endl;
    std::cout << "Search 25: " << list.search(25) << std::endl;
    std::cout << "Search 99: " << list.search(99) << std::endl;
    list.remove(25);
    list.print();
    list.reverse();
    list.print();
    list.insertAt(3, 999);
    list.print();
    std::cout << "Element at 3: " << list.getAt(3) << std::endl;
    return 0;
}
"""

CPP_S02 = """\
// Linked list implementation — local variable rename clone of S01
#include <iostream>
#include <stdexcept>

class LinkedList {
private:
    struct Node {
        int data;
        Node* next;
        Node(int data) : data(data), next(nullptr) {}
    };
    Node* head;
    int size;

public:
    LinkedList() : head(nullptr), size(0) {}

    ~LinkedList() {
        Node* ptr = head;
        while (ptr) {
            Node* t = ptr;
            ptr = ptr->next;
            delete t;
        }
    }

    void insertFront(int value) {
        Node* n = new Node(value);
        n->next = head;
        head = n;
        size++;
    }

    void insertEnd(int value) {
        Node* n = new Node(value);
        if (!head) {
            head = n;
        } else {
            Node* ptr = head;
            while (ptr->next) {
                ptr = ptr->next;
            }
            ptr->next = n;
        }
        size++;
    }

    bool search(int value) const {
        Node* ptr = head;
        while (ptr) {
            if (ptr->data == value) {
                return true;
            }
            ptr = ptr->next;
        }
        return false;
    }

    bool remove(int value) {
        if (!head) return false;
        if (head->data == value) {
            Node* t = head;
            head = head->next;
            delete t;
            size--;
            return true;
        }
        Node* ptr = head;
        while (ptr->next) {
            if (ptr->next->data == value) {
                Node* t = ptr->next;
                ptr->next = ptr->next->next;
                delete t;
                size--;
                return true;
            }
            ptr = ptr->next;
        }
        return false;
    }

    void reverse() {
        Node* p = nullptr;
        Node* c = head;
        Node* n = nullptr;
        while (c) {
            n = c->next;
            c->next = p;
            p = c;
            c = n;
        }
        head = p;
    }

    int getSize() const { return size; }

    void print() const {
        Node* ptr = head;
        std::cout << "List: ";
        while (ptr) {
            std::cout << ptr->data << " -> ";
            ptr = ptr->next;
        }
        std::cout << "null" << std::endl;
    }

    int getAt(int index) const {
        if (index < 0 || index >= size) {
            throw std::out_of_range("Index out of range");
        }
        Node* ptr = head;
        for (int k = 0; k < index; k++) {
            ptr = ptr->next;
        }
        return ptr->data;
    }

    void insertAt(int index, int value) {
        if (index < 0 || index > size) {
            throw std::out_of_range("Index out of range");
        }
        if (index == 0) {
            insertFront(value);
            return;
        }
        Node* n = new Node(value);
        Node* ptr = head;
        for (int k = 0; k < index - 1; k++) {
            ptr = ptr->next;
        }
        n->next = ptr->next;
        ptr->next = n;
        size++;
    }
};

int main() {
    LinkedList lst;
    for (int k = 1; k <= 10; k++) {
        lst.insertEnd(k * 5);
    }
    lst.print();
    std::cout << "Size: " << lst.getSize() << std::endl;
    std::cout << "Search 25: " << lst.search(25) << std::endl;
    std::cout << "Search 99: " << lst.search(99) << std::endl;
    lst.remove(25);
    lst.print();
    lst.reverse();
    lst.print();
    lst.insertAt(3, 999);
    lst.print();
    std::cout << "Element at 3: " << lst.getAt(3) << std::endl;
    return 0;
}
"""

CPP_S03 = """\
// Matrix operations — original
#include <iostream>
#include <vector>
#include <stdexcept>
#include <iomanip>

class MatrixOps {
private:
    std::vector<std::vector<int>> matrix;
    int rows;
    int cols;

public:
    MatrixOps(int rows, int cols) : rows(rows), cols(cols),
        matrix(rows, std::vector<int>(cols, 0)) {}

    MatrixOps(const std::vector<std::vector<int>>& data)
        : rows(data.size()), cols(data[0].size()), matrix(data) {}

    void set(int row, int col, int value) {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw std::out_of_range("Invalid position");
        }
        matrix[row][col] = value;
    }

    int get(int row, int col) const {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw std::out_of_range("Invalid position");
        }
        return matrix[row][col];
    }

    MatrixOps add(const MatrixOps& other) const {
        if (rows != other.rows || cols != other.cols) {
            throw std::invalid_argument("Dimension mismatch for addition");
        }
        MatrixOps result(rows, cols);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result.matrix[i][j] = matrix[i][j] + other.matrix[i][j];
            }
        }
        return result;
    }

    MatrixOps multiply(const MatrixOps& other) const {
        if (cols != other.rows) {
            throw std::invalid_argument("Incompatible dimensions for multiplication");
        }
        MatrixOps result(rows, other.cols);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < other.cols; j++) {
                int sum = 0;
                for (int k = 0; k < cols; k++) {
                    sum += matrix[i][k] * other.matrix[k][j];
                }
                result.matrix[i][j] = sum;
            }
        }
        return result;
    }

    MatrixOps transpose() const {
        MatrixOps result(cols, rows);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result.matrix[j][i] = matrix[i][j];
            }
        }
        return result;
    }

    int trace() const {
        if (rows != cols) {
            throw std::logic_error("Trace requires a square matrix");
        }
        int sum = 0;
        for (int i = 0; i < rows; i++) {
            sum += matrix[i][i];
        }
        return sum;
    }

    MatrixOps scalarMultiply(int scalar) const {
        MatrixOps result(rows, cols);
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                result.matrix[i][j] = matrix[i][j] * scalar;
            }
        }
        return result;
    }

    bool isSymmetric() const {
        if (rows != cols) return false;
        for (int i = 0; i < rows; i++) {
            for (int j = i + 1; j < cols; j++) {
                if (matrix[i][j] != matrix[j][i]) {
                    return false;
                }
            }
        }
        return true;
    }

    void print() const {
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                std::cout << std::setw(6) << matrix[i][j];
            }
            std::cout << std::endl;
        }
    }
};

int main() {
    std::vector<std::vector<int>> dataA = {{1,2,3},{4,5,6},{7,8,9}};
    std::vector<std::vector<int>> dataB = {{9,8,7},{6,5,4},{3,2,1}};
    MatrixOps a(dataA);
    MatrixOps b(dataB);
    std::cout << "Matrix A:" << std::endl; a.print();
    std::cout << "Matrix B:" << std::endl; b.print();
    std::cout << "A + B:" << std::endl; a.add(b).print();
    std::cout << "A * B:" << std::endl; a.multiply(b).print();
    std::cout << "Transpose A:" << std::endl; a.transpose().print();
    std::cout << "Trace A: " << a.trace() << std::endl;
    std::cout << "A * 3:" << std::endl; a.scalarMultiply(3).print();
    std::cout << "A symmetric? " << a.isSymmetric() << std::endl;
    return 0;
}
"""

CPP_S04 = """\
// Matrix operations — reordered functions, local vars renamed (clone of S03)
#include <iostream>
#include <vector>
#include <stdexcept>
#include <iomanip>

class MatrixOps {
private:
    std::vector<std::vector<int>> matrix;
    int rows;
    int cols;

public:
    MatrixOps(int rows, int cols) : rows(rows), cols(cols),
        matrix(rows, std::vector<int>(cols, 0)) {}

    MatrixOps(const std::vector<std::vector<int>>& data)
        : rows(data.size()), cols(data[0].size()), matrix(data) {}

    MatrixOps transpose() const {
        MatrixOps res(cols, rows);
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                res.matrix[c][r] = matrix[r][c];
            }
        }
        return res;
    }

    bool isSymmetric() const {
        if (rows != cols) return false;
        for (int r = 0; r < rows; r++) {
            for (int c = r + 1; c < cols; c++) {
                if (matrix[r][c] != matrix[c][r]) {
                    return false;
                }
            }
        }
        return true;
    }

    MatrixOps scalarMultiply(int scalar) const {
        MatrixOps res(rows, cols);
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                res.matrix[r][c] = matrix[r][c] * scalar;
            }
        }
        return res;
    }

    void set(int row, int col, int value) {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw std::out_of_range("Invalid position");
        }
        matrix[row][col] = value;
    }

    int get(int row, int col) const {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw std::out_of_range("Invalid position");
        }
        return matrix[row][col];
    }

    int trace() const {
        if (rows != cols) {
            throw std::logic_error("Trace requires a square matrix");
        }
        int total = 0;
        for (int r = 0; r < rows; r++) {
            total += matrix[r][r];
        }
        return total;
    }

    MatrixOps add(const MatrixOps& other) const {
        if (rows != other.rows || cols != other.cols) {
            throw std::invalid_argument("Dimension mismatch for addition");
        }
        MatrixOps res(rows, cols);
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                res.matrix[r][c] = matrix[r][c] + other.matrix[r][c];
            }
        }
        return res;
    }

    MatrixOps multiply(const MatrixOps& other) const {
        if (cols != other.rows) {
            throw std::invalid_argument("Incompatible dimensions for multiplication");
        }
        MatrixOps res(rows, other.cols);
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < other.cols; c++) {
                int acc = 0;
                for (int k = 0; k < cols; k++) {
                    acc += matrix[r][k] * other.matrix[k][c];
                }
                res.matrix[r][c] = acc;
            }
        }
        return res;
    }

    void print() const {
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                std::cout << std::setw(6) << matrix[r][c];
            }
            std::cout << std::endl;
        }
    }
};

int main() {
    std::vector<std::vector<int>> d1 = {{1,2,3},{4,5,6},{7,8,9}};
    std::vector<std::vector<int>> d2 = {{9,8,7},{6,5,4},{3,2,1}};
    MatrixOps m1(d1);
    MatrixOps m2(d2);
    std::cout << "Matrix A:" << std::endl; m1.print();
    std::cout << "Matrix B:" << std::endl; m2.print();
    std::cout << "A + B:" << std::endl; m1.add(m2).print();
    std::cout << "A * B:" << std::endl; m1.multiply(m2).print();
    std::cout << "Transpose A:" << std::endl; m1.transpose().print();
    std::cout << "Trace A: " << m1.trace() << std::endl;
    std::cout << "A * 3:" << std::endl; m1.scalarMultiply(3).print();
    std::cout << "A symmetric? " << m1.isSymmetric() << std::endl;
    return 0;
}
"""

CPP_S05 = """\
// Matrix operations — local vars renamed variant 2 (clone of S03)
#include <iostream>
#include <vector>
#include <stdexcept>
#include <iomanip>

class MatrixOps {
private:
    std::vector<std::vector<int>> matrix;
    int rows;
    int cols;

public:
    MatrixOps(int rows, int cols) : rows(rows), cols(cols),
        matrix(rows, std::vector<int>(cols, 0)) {}

    MatrixOps(const std::vector<std::vector<int>>& data)
        : rows(data.size()), cols(data[0].size()), matrix(data) {}

    void set(int row, int col, int value) {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw std::out_of_range("Invalid position");
        }
        matrix[row][col] = value;
    }

    int get(int row, int col) const {
        if (row < 0 || row >= rows || col < 0 || col >= cols) {
            throw std::out_of_range("Invalid position");
        }
        return matrix[row][col];
    }

    MatrixOps add(const MatrixOps& other) const {
        if (rows != other.rows || cols != other.cols) {
            throw std::invalid_argument("Dimension mismatch for addition");
        }
        MatrixOps out(rows, cols);
        for (int a = 0; a < rows; a++) {
            for (int b = 0; b < cols; b++) {
                out.matrix[a][b] = matrix[a][b] + other.matrix[a][b];
            }
        }
        return out;
    }

    MatrixOps multiply(const MatrixOps& other) const {
        if (cols != other.rows) {
            throw std::invalid_argument("Incompatible dimensions for multiplication");
        }
        MatrixOps out(rows, other.cols);
        for (int a = 0; a < rows; a++) {
            for (int b = 0; b < other.cols; b++) {
                int val = 0;
                for (int k = 0; k < cols; k++) {
                    val += matrix[a][k] * other.matrix[k][b];
                }
                out.matrix[a][b] = val;
            }
        }
        return out;
    }

    MatrixOps transpose() const {
        MatrixOps out(cols, rows);
        for (int a = 0; a < rows; a++) {
            for (int b = 0; b < cols; b++) {
                out.matrix[b][a] = matrix[a][b];
            }
        }
        return out;
    }

    int trace() const {
        if (rows != cols) {
            throw std::logic_error("Trace requires a square matrix");
        }
        int val = 0;
        for (int a = 0; a < rows; a++) {
            val += matrix[a][a];
        }
        return val;
    }

    MatrixOps scalarMultiply(int scalar) const {
        MatrixOps out(rows, cols);
        for (int a = 0; a < rows; a++) {
            for (int b = 0; b < cols; b++) {
                out.matrix[a][b] = matrix[a][b] * scalar;
            }
        }
        return out;
    }

    bool isSymmetric() const {
        if (rows != cols) return false;
        for (int a = 0; a < rows; a++) {
            for (int b = a + 1; b < cols; b++) {
                if (matrix[a][b] != matrix[b][a]) {
                    return false;
                }
            }
        }
        return true;
    }

    void print() const {
        for (int a = 0; a < rows; a++) {
            for (int b = 0; b < cols; b++) {
                std::cout << std::setw(6) << matrix[a][b];
            }
            std::cout << std::endl;
        }
    }
};

int main() {
    std::vector<std::vector<int>> x = {{1,2,3},{4,5,6},{7,8,9}};
    std::vector<std::vector<int>> y = {{9,8,7},{6,5,4},{3,2,1}};
    MatrixOps p(x);
    MatrixOps q(y);
    std::cout << "Matrix A:" << std::endl; p.print();
    std::cout << "Matrix B:" << std::endl; q.print();
    std::cout << "A + B:" << std::endl; p.add(q).print();
    std::cout << "A * B:" << std::endl; p.multiply(q).print();
    std::cout << "Transpose A:" << std::endl; p.transpose().print();
    std::cout << "Trace A: " << p.trace() << std::endl;
    std::cout << "A * 3:" << std::endl; p.scalarMultiply(3).print();
    std::cout << "A symmetric? " << p.isSymmetric() << std::endl;
    return 0;
}
"""

CPP_S06 = """\
// Binary search tree — independent (false positive control)
#include <iostream>
#include <stdexcept>
#include <algorithm>

class BinarySearchTree {
private:
    struct TreeNode {
        int key;
        TreeNode* left;
        TreeNode* right;
        TreeNode(int key) : key(key), left(nullptr), right(nullptr) {}
    };
    TreeNode* root;

    TreeNode* insertHelper(TreeNode* node, int key) {
        if (!node) return new TreeNode(key);
        if (key < node->key) {
            node->left = insertHelper(node->left, key);
        } else if (key > node->key) {
            node->right = insertHelper(node->right, key);
        }
        return node;
    }

    bool containsHelper(TreeNode* node, int key) const {
        if (!node) return false;
        if (key == node->key) return true;
        if (key < node->key) return containsHelper(node->left, key);
        return containsHelper(node->right, key);
    }

    void inorderHelper(TreeNode* node) const {
        if (!node) return;
        inorderHelper(node->left);
        std::cout << node->key << " ";
        inorderHelper(node->right);
    }

    void preorderHelper(TreeNode* node) const {
        if (!node) return;
        std::cout << node->key << " ";
        preorderHelper(node->left);
        preorderHelper(node->right);
    }

    int heightHelper(TreeNode* node) const {
        if (!node) return -1;
        return 1 + std::max(heightHelper(node->left), heightHelper(node->right));
    }

    int countHelper(TreeNode* node) const {
        if (!node) return 0;
        return 1 + countHelper(node->left) + countHelper(node->right);
    }

    TreeNode* findMinNode(TreeNode* node) const {
        while (node && node->left) node = node->left;
        return node;
    }

    TreeNode* deleteHelper(TreeNode* node, int key) {
        if (!node) return nullptr;
        if (key < node->key) {
            node->left = deleteHelper(node->left, key);
        } else if (key > node->key) {
            node->right = deleteHelper(node->right, key);
        } else {
            if (!node->left) {
                TreeNode* temp = node->right;
                delete node;
                return temp;
            }
            if (!node->right) {
                TreeNode* temp = node->left;
                delete node;
                return temp;
            }
            TreeNode* successor = findMinNode(node->right);
            node->key = successor->key;
            node->right = deleteHelper(node->right, successor->key);
        }
        return node;
    }

    void freeTree(TreeNode* node) {
        if (!node) return;
        freeTree(node->left);
        freeTree(node->right);
        delete node;
    }

public:
    BinarySearchTree() : root(nullptr) {}
    ~BinarySearchTree() { freeTree(root); }

    void insert(int key) { root = insertHelper(root, key); }
    bool contains(int key) const { return containsHelper(root, key); }

    void inorderTraversal() const {
        std::cout << "Inorder: ";
        inorderHelper(root);
        std::cout << std::endl;
    }

    void preorderTraversal() const {
        std::cout << "Preorder: ";
        preorderHelper(root);
        std::cout << std::endl;
    }

    int findMin() const {
        if (!root) throw std::logic_error("Tree is empty");
        TreeNode* current = root;
        while (current->left) current = current->left;
        return current->key;
    }

    int findMax() const {
        if (!root) throw std::logic_error("Tree is empty");
        TreeNode* current = root;
        while (current->right) current = current->right;
        return current->key;
    }

    int height() const { return heightHelper(root); }
    int countNodes() const { return countHelper(root); }
    void remove(int key) { root = deleteHelper(root, key); }
};

int main() {
    BinarySearchTree bst;
    int values[] = {50, 30, 70, 20, 40, 60, 80, 10, 25, 35};
    for (int v : values) {
        bst.insert(v);
    }
    bst.inorderTraversal();
    bst.preorderTraversal();
    std::cout << "Contains 40: " << bst.contains(40) << std::endl;
    std::cout << "Contains 99: " << bst.contains(99) << std::endl;
    std::cout << "Min: " << bst.findMin() << std::endl;
    std::cout << "Max: " << bst.findMax() << std::endl;
    std::cout << "Height: " << bst.height() << std::endl;
    std::cout << "Nodes: " << bst.countNodes() << std::endl;
    bst.remove(30);
    std::cout << "After deleting 30:" << std::endl;
    bst.inorderTraversal();
    return 0;
}
"""

CPP_S07 = """\
// Sorting algorithms comparison — independent (false positive control)
#include <iostream>
#include <vector>
#include <algorithm>

std::vector<int> bubbleSort(std::vector<int> a) {
    int n = a.size();
    for (int i = 0; i < n - 1; i++) {
        bool swapped = false;
        for (int j = 0; j < n - i - 1; j++) {
            if (a[j] > a[j + 1]) {
                std::swap(a[j], a[j + 1]);
                swapped = true;
            }
        }
        if (!swapped) break;
    }
    return a;
}

std::vector<int> selectionSort(std::vector<int> a) {
    int n = a.size();
    for (int i = 0; i < n - 1; i++) {
        int minIdx = i;
        for (int j = i + 1; j < n; j++) {
            if (a[j] < a[minIdx]) {
                minIdx = j;
            }
        }
        std::swap(a[minIdx], a[i]);
    }
    return a;
}

std::vector<int> insertionSort(std::vector<int> a) {
    int n = a.size();
    for (int i = 1; i < n; i++) {
        int key = a[i];
        int j = i - 1;
        while (j >= 0 && a[j] > key) {
            a[j + 1] = a[j];
            j--;
        }
        a[j + 1] = key;
    }
    return a;
}

std::vector<int> mergeSortImpl(std::vector<int> a) {
    if (a.size() <= 1) return a;
    int mid = a.size() / 2;
    std::vector<int> left(a.begin(), a.begin() + mid);
    std::vector<int> right(a.begin() + mid, a.end());
    left = mergeSortImpl(left);
    right = mergeSortImpl(right);
    std::vector<int> result;
    int i = 0, j = 0;
    while (i < (int)left.size() && j < (int)right.size()) {
        if (left[i] <= right[j]) {
            result.push_back(left[i++]);
        } else {
            result.push_back(right[j++]);
        }
    }
    while (i < (int)left.size()) result.push_back(left[i++]);
    while (j < (int)right.size()) result.push_back(right[j++]);
    return result;
}

int qsPartition(std::vector<int>& a, int low, int high) {
    int pivot = a[high];
    int i = low - 1;
    for (int j = low; j < high; j++) {
        if (a[j] < pivot) {
            i++;
            std::swap(a[i], a[j]);
        }
    }
    std::swap(a[i + 1], a[high]);
    return i + 1;
}

void qsHelper(std::vector<int>& a, int low, int high) {
    if (low < high) {
        int pi = qsPartition(a, low, high);
        qsHelper(a, low, pi - 1);
        qsHelper(a, pi + 1, high);
    }
}

std::vector<int> quickSort(std::vector<int> a) {
    qsHelper(a, 0, a.size() - 1);
    return a;
}

void printArray(const std::string& label, const std::vector<int>& a) {
    std::cout << label << ": [";
    for (int i = 0; i < (int)a.size(); i++) {
        std::cout << a[i];
        if (i < (int)a.size() - 1) std::cout << ", ";
    }
    std::cout << "]" << std::endl;
}

bool isSorted(const std::vector<int>& a) {
    for (int i = 1; i < (int)a.size(); i++) {
        if (a[i] < a[i - 1]) return false;
    }
    return true;
}

int main() {
    std::vector<int> data = {64, 34, 25, 12, 22, 11, 90, 1, 55, 43, 77, 8};
    printArray("Original", data);
    auto b = bubbleSort(data);
    printArray("Bubble", b);
    std::cout << "Sorted: " << isSorted(b) << std::endl;
    auto s = selectionSort(data);
    printArray("Selection", s);
    std::cout << "Sorted: " << isSorted(s) << std::endl;
    auto ins = insertionSort(data);
    printArray("Insertion", ins);
    std::cout << "Sorted: " << isSorted(ins) << std::endl;
    auto m = mergeSortImpl(data);
    printArray("Merge", m);
    std::cout << "Sorted: " << isSorted(m) << std::endl;
    auto q = quickSort(data);
    printArray("Quick", q);
    std::cout << "Sorted: " << isSorted(q) << std::endl;
    return 0;
}
"""


# ═══════════════════════════════════════════════════════════════
#  PACKAGING
# ═══════════════════════════════════════════════════════════════

def make_inner_zip(filename: str, source_code: str) -> bytes:
    """Create a single submission zip (one source file inside)."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, source_code)
    return buf.getvalue()


def make_repo_zip(programs: dict[str, tuple[str, str]]) -> bytes:
    """
    Build a zip-of-zips (Format A).
    programs: { "S01": ("LinkedList.java", source), ... }
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as outer:
        for label, (filename, source) in programs.items():
            inner_bytes = make_inner_zip(filename, source)
            outer.writestr(f"{label}.zip", inner_bytes)
    return buf.getvalue()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    java_programs = {
        "S01": ("LinkedList.java", JAVA_S01),
        "S02": ("LinkedList.java", JAVA_S02),
        "S03": ("MatrixOps.java", JAVA_S03),
        "S04": ("MatrixOps.java", JAVA_S04),
        "S05": ("MatrixOps.java", JAVA_S05),
        "S06": ("BinarySearchTree.java", JAVA_S06),
        "S07": ("SortBenchmark.java", JAVA_S07),
    }
    c_programs = {
        "S01": ("linked_list.c", C_S01),
        "S02": ("linked_list.c", C_S02),
        "S03": ("matrix_ops.c", C_S03),
        "S04": ("matrix_ops.c", C_S04),
        "S05": ("matrix_ops.c", C_S05),
        "S06": ("binary_search_tree.c", C_S06),
        "S07": ("sort_benchmark.c", C_S07),
    }
    cpp_programs = {
        "S01": ("LinkedList.cpp", CPP_S01),
        "S02": ("LinkedList.cpp", CPP_S02),
        "S03": ("MatrixOps.cpp", CPP_S03),
        "S04": ("MatrixOps.cpp", CPP_S04),
        "S05": ("MatrixOps.cpp", CPP_S05),
        "S06": ("BinarySearchTree.cpp", CPP_S06),
        "S07": ("SortBenchmark.cpp", CPP_S07),
    }

    # Build zip-of-zips
    java_zip = make_repo_zip(java_programs)
    c_zip = make_repo_zip(c_programs)
    cpp_zip = make_repo_zip(cpp_programs)

    (OUTPUT_DIR / "TestSetJava_pilot.zip").write_bytes(java_zip)
    (OUTPUT_DIR / "TestSetC_pilot.zip").write_bytes(c_zip)
    (OUTPUT_DIR / "TestSetCpp_pilot.zip").write_bytes(cpp_zip)

    # Line counts
    print("=== Line counts ===")
    for lang, progs in [("Java", java_programs), ("C", c_programs), ("C++", cpp_programs)]:
        for label, (filename, source) in progs.items():
            lines = len(source.strip().split("\n"))
            print(f"  {lang} {label} ({filename}): {lines} lines")

    # Manifest
    manifest = """\
# Stage 3 Pilot Test Set — Internal Manifest

## Scope
- 7 programs per language (Java, C, C++) = 21 total
- Format: zip-of-zips (Format A), neutral S## naming

## Categories

### True-Positive Pair A — Rename Detection
| ID  | Description |
|-----|-------------|
| S01 | Linked list (original): insert, delete, search, reverse, getAt, insertAt |
| S02 | Linked list (clone): all identifiers renamed (Node->Element, head->first, data->payload, next->successor, etc.) |

**Expected:** >80% similarity. Tests basic rename detection.

### True-Positive Triple B — Reorder + Rename
| ID  | Description |
|-----|-------------|
| S03 | Matrix operations (original): add, multiply, transpose, trace, scalarMultiply, isSymmetric |
| S04 | Matrix operations (variant 1): functions reordered, all identifiers renamed |
| S05 | Matrix operations (variant 2): different rename scheme from S04 |

**Expected:** >70% similarity for all 3 pairs (S03-S04, S03-S05, S04-S05). Tests reorder + rename robustness.

### False-Positive Controls
| ID  | Description |
|-----|-------------|
| S06 | Binary search tree: insert, search, traversal, delete, height, count — recursive tree structure |
| S07 | Sorting algorithms: bubble, selection, insertion, merge, quick — array-based algorithms |

**Expected:** <30% similarity against each other and against S01-S05. Different algorithms, different data structures.

## Score Targets Summary

| Pair | Expected |
|------|----------|
| S01 vs S02 | >80% |
| S03 vs S04 | >70% |
| S03 vs S05 | >70% |
| S04 vs S05 | >70% |
| S06 vs S07 | <30% |
| S01 vs S06 | <30% |
| S01 vs S07 | <30% |
| S03 vs S06 | <30% |
| S03 vs S07 | <30% |
"""
    (OUTPUT_DIR / "MANIFEST_pilot.md").write_text(manifest, encoding="utf-8")

    print(f"\n=== Output ===")
    print(f"  {OUTPUT_DIR / 'TestSetJava_pilot.zip'} ({len(java_zip)} bytes)")
    print(f"  {OUTPUT_DIR / 'TestSetC_pilot.zip'} ({len(c_zip)} bytes)")
    print(f"  {OUTPUT_DIR / 'TestSetCpp_pilot.zip'} ({len(cpp_zip)} bytes)")
    print(f"  {OUTPUT_DIR / 'MANIFEST_pilot.md'}")
    print("\nDone.")


if __name__ == "__main__":
    main()
