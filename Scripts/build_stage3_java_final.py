"""
Build Stage 3 FINAL Java Test Set for Token Trail.

15 programs total:
  S01, S02       — Pair A (local-var rename detection)
  S03, S04, S05  — Triple B (reorder + local-var rename)
  S06–S10        — False-positive controls
  S11, S12       — Hard Pair C (same logic, moderate structural change)
  S13–S15        — False-positive controls

Output: TestSetJava.zip + MANIFEST.md
"""

import io
import zipfile
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "test_repos" / "final"

# ═══════════════════════════════════════════════════════════════
#  PAIR A — Linked list, local-var renames only
# ═══════════════════════════════════════════════════════════════

JAVA_S01 = """\
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

# ═══════════════════════════════════════════════════════════════
#  TRIPLE B — Matrix ops, reorder + local-var renames
# ═══════════════════════════════════════════════════════════════

JAVA_S03 = """\
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

# ═══════════════════════════════════════════════════════════════
#  FALSE-POSITIVE CONTROLS — S06, S07, S08, S09, S10
# ═══════════════════════════════════════════════════════════════

JAVA_S06 = """\
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

JAVA_S08 = """\
public class StackCalculator {
    private int[] stack;
    private int top;
    private int capacity;

    public StackCalculator(int capacity) {
        this.capacity = capacity;
        this.stack = new int[capacity];
        this.top = -1;
    }

    public void push(int value) {
        if (top >= capacity - 1) {
            throw new RuntimeException("Stack overflow");
        }
        stack[++top] = value;
    }

    public int pop() {
        if (top < 0) {
            throw new RuntimeException("Stack underflow");
        }
        return stack[top--];
    }

    public int peek() {
        if (top < 0) {
            throw new RuntimeException("Stack is empty");
        }
        return stack[top];
    }

    public boolean isEmpty() {
        return top < 0;
    }

    public int size() {
        return top + 1;
    }

    public static int precedence(char op) {
        switch (op) {
            case '+': case '-': return 1;
            case '*': case '/': return 2;
            case '^': return 3;
            default: return 0;
        }
    }

    public static boolean isOperator(char ch) {
        return ch == '+' || ch == '-' || ch == '*' || ch == '/' || ch == '^';
    }

    public static int applyOp(int left, int right, char op) {
        switch (op) {
            case '+': return left + right;
            case '-': return left - right;
            case '*': return left * right;
            case '/':
                if (right == 0) throw new ArithmeticException("Division by zero");
                return left / right;
            case '^': return (int) Math.pow(left, right);
            default: throw new IllegalArgumentException("Unknown operator: " + op);
        }
    }

    public static int evaluatePostfix(String expression) {
        StackCalculator evalStack = new StackCalculator(100);
        String[] tokens = expression.trim().split("\\\\s+");
        for (String token : tokens) {
            if (token.length() == 1 && isOperator(token.charAt(0))) {
                int right = evalStack.pop();
                int left = evalStack.pop();
                int result = applyOp(left, right, token.charAt(0));
                evalStack.push(result);
            } else {
                evalStack.push(Integer.parseInt(token));
            }
        }
        return evalStack.pop();
    }

    public static String infixToPostfix(String expression) {
        StringBuilder output = new StringBuilder();
        StackCalculator opStack = new StackCalculator(100);
        String[] tokens = expression.trim().split("\\\\s+");
        for (String token : tokens) {
            if (token.equals("(")) {
                opStack.push('(');
            } else if (token.equals(")")) {
                while (!opStack.isEmpty() && (char) opStack.peek() != '(') {
                    output.append((char) opStack.pop()).append(' ');
                }
                if (!opStack.isEmpty()) opStack.pop();
            } else if (token.length() == 1 && isOperator(token.charAt(0))) {
                char op = token.charAt(0);
                while (!opStack.isEmpty() && precedence((char) opStack.peek()) >= precedence(op)) {
                    output.append((char) opStack.pop()).append(' ');
                }
                opStack.push(op);
            } else {
                output.append(token).append(' ');
            }
        }
        while (!opStack.isEmpty()) {
            output.append((char) opStack.pop()).append(' ');
        }
        return output.toString().trim();
    }

    public void printStack() {
        System.out.print("Stack [bottom -> top]: ");
        for (int i = 0; i <= top; i++) {
            System.out.print(stack[i] + " ");
        }
        System.out.println();
    }

    public static void main(String[] args) {
        StackCalculator sc = new StackCalculator(20);
        for (int i = 1; i <= 8; i++) {
            sc.push(i * 10);
        }
        sc.printStack();
        System.out.println("Pop: " + sc.pop());
        System.out.println("Peek: " + sc.peek());
        System.out.println("Size: " + sc.size());
        String postfix = "3 4 + 2 * 7 /";
        System.out.println("Postfix '" + postfix + "' = " + evaluatePostfix(postfix));
        String infix = "3 + 4 * 2 / ( 1 - 5 )";
        String converted = infixToPostfix(infix);
        System.out.println("Infix: " + infix);
        System.out.println("Postfix: " + converted);
    }
}
"""

JAVA_S09 = """\
public class StatisticsCalculator {
    private double[] data;
    private int count;
    private int capacity;

    public StatisticsCalculator(int capacity) {
        this.capacity = capacity;
        this.data = new double[capacity];
        this.count = 0;
    }

    public void addValue(double value) {
        if (count >= capacity) {
            int newCap = capacity * 2;
            double[] newData = new double[newCap];
            for (int i = 0; i < count; i++) {
                newData[i] = data[i];
            }
            data = newData;
            capacity = newCap;
        }
        data[count++] = value;
    }

    public double mean() {
        if (count == 0) throw new IllegalStateException("No data");
        double sum = 0;
        for (int i = 0; i < count; i++) {
            sum += data[i];
        }
        return sum / count;
    }

    public double median() {
        if (count == 0) throw new IllegalStateException("No data");
        double[] sorted = getSorted();
        if (count % 2 == 0) {
            return (sorted[count / 2 - 1] + sorted[count / 2]) / 2.0;
        }
        return sorted[count / 2];
    }

    public double variance() {
        if (count < 2) throw new IllegalStateException("Need at least 2 values");
        double avg = mean();
        double sumSqDiff = 0;
        for (int i = 0; i < count; i++) {
            double diff = data[i] - avg;
            sumSqDiff += diff * diff;
        }
        return sumSqDiff / (count - 1);
    }

    public double standardDeviation() {
        return Math.sqrt(variance());
    }

    public double min() {
        if (count == 0) throw new IllegalStateException("No data");
        double minVal = data[0];
        for (int i = 1; i < count; i++) {
            if (data[i] < minVal) minVal = data[i];
        }
        return minVal;
    }

    public double max() {
        if (count == 0) throw new IllegalStateException("No data");
        double maxVal = data[0];
        for (int i = 1; i < count; i++) {
            if (data[i] > maxVal) maxVal = data[i];
        }
        return maxVal;
    }

    public double range() {
        return max() - min();
    }

    public double percentile(double p) {
        if (p < 0 || p > 100) throw new IllegalArgumentException("Percentile must be 0-100");
        if (count == 0) throw new IllegalStateException("No data");
        double[] sorted = getSorted();
        double rank = (p / 100.0) * (count - 1);
        int lower = (int) Math.floor(rank);
        int upper = (int) Math.ceil(rank);
        if (lower == upper) return sorted[lower];
        double fraction = rank - lower;
        return sorted[lower] + fraction * (sorted[upper] - sorted[lower]);
    }

    private double[] getSorted() {
        double[] sorted = new double[count];
        for (int i = 0; i < count; i++) {
            sorted[i] = data[i];
        }
        for (int i = 0; i < count - 1; i++) {
            for (int j = 0; j < count - i - 1; j++) {
                if (sorted[j] > sorted[j + 1]) {
                    double temp = sorted[j];
                    sorted[j] = sorted[j + 1];
                    sorted[j + 1] = temp;
                }
            }
        }
        return sorted;
    }

    public int getCount() {
        return count;
    }

    public void printSummary() {
        System.out.println("=== Statistical Summary ===");
        System.out.println("Count: " + count);
        System.out.printf("Mean: %.4f%n", mean());
        System.out.printf("Median: %.4f%n", median());
        System.out.printf("Std Dev: %.4f%n", standardDeviation());
        System.out.printf("Variance: %.4f%n", variance());
        System.out.printf("Min: %.4f%n", min());
        System.out.printf("Max: %.4f%n", max());
        System.out.printf("Range: %.4f%n", range());
        System.out.printf("25th Percentile: %.4f%n", percentile(25));
        System.out.printf("75th Percentile: %.4f%n", percentile(75));
    }

    public static void main(String[] args) {
        StatisticsCalculator calc = new StatisticsCalculator(10);
        double[] values = {23.5, 45.1, 12.8, 67.3, 34.9, 56.7, 28.4, 41.2, 39.6, 51.0,
                           18.3, 62.1, 44.7, 31.5, 55.8, 20.9, 48.3, 37.6, 59.2, 26.1};
        for (double v : values) {
            calc.addValue(v);
        }
        calc.printSummary();
    }
}
"""

JAVA_S10 = """\
public class GraphTraversal {
    private int vertices;
    private int[][] adjacency;
    private boolean directed;

    public GraphTraversal(int vertices, boolean directed) {
        this.vertices = vertices;
        this.directed = directed;
        this.adjacency = new int[vertices][vertices];
    }

    public void addEdge(int from, int to) {
        if (from < 0 || from >= vertices || to < 0 || to >= vertices) {
            throw new IllegalArgumentException("Invalid vertex");
        }
        adjacency[from][to] = 1;
        if (!directed) {
            adjacency[to][from] = 1;
        }
    }

    public void bfs(int start) {
        if (start < 0 || start >= vertices) {
            throw new IllegalArgumentException("Invalid start vertex");
        }
        boolean[] visited = new boolean[vertices];
        int[] queue = new int[vertices];
        int front = 0, rear = 0;
        visited[start] = true;
        queue[rear++] = start;
        System.out.print("BFS from " + start + ": ");
        while (front < rear) {
            int current = queue[front++];
            System.out.print(current + " ");
            for (int neighbor = 0; neighbor < vertices; neighbor++) {
                if (adjacency[current][neighbor] == 1 && !visited[neighbor]) {
                    visited[neighbor] = true;
                    queue[rear++] = neighbor;
                }
            }
        }
        System.out.println();
    }

    public void dfs(int start) {
        if (start < 0 || start >= vertices) {
            throw new IllegalArgumentException("Invalid start vertex");
        }
        boolean[] visited = new boolean[vertices];
        System.out.print("DFS from " + start + ": ");
        dfsHelper(start, visited);
        System.out.println();
    }

    private void dfsHelper(int vertex, boolean[] visited) {
        visited[vertex] = true;
        System.out.print(vertex + " ");
        for (int neighbor = 0; neighbor < vertices; neighbor++) {
            if (adjacency[vertex][neighbor] == 1 && !visited[neighbor]) {
                dfsHelper(neighbor, visited);
            }
        }
    }

    public boolean hasPath(int from, int to) {
        if (from < 0 || from >= vertices || to < 0 || to >= vertices) {
            return false;
        }
        boolean[] visited = new boolean[vertices];
        return hasPathDFS(from, to, visited);
    }

    private boolean hasPathDFS(int current, int target, boolean[] visited) {
        if (current == target) return true;
        visited[current] = true;
        for (int neighbor = 0; neighbor < vertices; neighbor++) {
            if (adjacency[current][neighbor] == 1 && !visited[neighbor]) {
                if (hasPathDFS(neighbor, target, visited)) {
                    return true;
                }
            }
        }
        return false;
    }

    public int countConnectedComponents() {
        boolean[] visited = new boolean[vertices];
        int components = 0;
        for (int v = 0; v < vertices; v++) {
            if (!visited[v]) {
                dfsMarkComponent(v, visited);
                components++;
            }
        }
        return components;
    }

    private void dfsMarkComponent(int vertex, boolean[] visited) {
        visited[vertex] = true;
        for (int neighbor = 0; neighbor < vertices; neighbor++) {
            if (adjacency[vertex][neighbor] == 1 && !visited[neighbor]) {
                dfsMarkComponent(neighbor, visited);
            }
        }
    }

    public int[] shortestPath(int start) {
        int[] dist = new int[vertices];
        boolean[] visited = new boolean[vertices];
        for (int i = 0; i < vertices; i++) {
            dist[i] = Integer.MAX_VALUE;
        }
        dist[start] = 0;
        int[] queue = new int[vertices];
        int front = 0, rear = 0;
        visited[start] = true;
        queue[rear++] = start;
        while (front < rear) {
            int current = queue[front++];
            for (int neighbor = 0; neighbor < vertices; neighbor++) {
                if (adjacency[current][neighbor] == 1 && !visited[neighbor]) {
                    visited[neighbor] = true;
                    dist[neighbor] = dist[current] + 1;
                    queue[rear++] = neighbor;
                }
            }
        }
        return dist;
    }

    public void printAdjacencyMatrix() {
        System.out.println("Adjacency Matrix:");
        for (int i = 0; i < vertices; i++) {
            for (int j = 0; j < vertices; j++) {
                System.out.print(adjacency[i][j] + " ");
            }
            System.out.println();
        }
    }

    public static void main(String[] args) {
        GraphTraversal graph = new GraphTraversal(8, false);
        graph.addEdge(0, 1);
        graph.addEdge(0, 2);
        graph.addEdge(1, 3);
        graph.addEdge(1, 4);
        graph.addEdge(2, 5);
        graph.addEdge(3, 6);
        graph.addEdge(4, 7);
        graph.printAdjacencyMatrix();
        graph.bfs(0);
        graph.dfs(0);
        System.out.println("Path 0->7: " + graph.hasPath(0, 7));
        System.out.println("Path 5->6: " + graph.hasPath(5, 6));
        System.out.println("Components: " + graph.countConnectedComponents());
        int[] distances = graph.shortestPath(0);
        System.out.print("Distances from 0: ");
        for (int d : distances) {
            System.out.print((d == Integer.MAX_VALUE ? "INF" : d) + " ");
        }
        System.out.println();
    }
}
"""

# ═══════════════════════════════════════════════════════════════
#  HARD PAIR C — Hash table, same class/method names,
#  moderate structural differences (different helper logic)
# ═══════════════════════════════════════════════════════════════

JAVA_S11 = """\
public class HashTable {
    private int[] keys;
    private int[] values;
    private boolean[] occupied;
    private int capacity;
    private int size;

    public HashTable(int capacity) {
        this.capacity = capacity;
        this.keys = new int[capacity];
        this.values = new int[capacity];
        this.occupied = new boolean[capacity];
        this.size = 0;
    }

    private int hash(int key) {
        int h = key % capacity;
        if (h < 0) h += capacity;
        return h;
    }

    public void put(int key, int value) {
        if (size >= capacity * 3 / 4) {
            resize();
        }
        int index = hash(key);
        int startIndex = index;
        while (occupied[index]) {
            if (keys[index] == key) {
                values[index] = value;
                return;
            }
            index = (index + 1) % capacity;
            if (index == startIndex) {
                resize();
                put(key, value);
                return;
            }
        }
        keys[index] = key;
        values[index] = value;
        occupied[index] = true;
        size++;
    }

    public int get(int key) {
        int index = hash(key);
        int startIndex = index;
        while (occupied[index]) {
            if (keys[index] == key) {
                return values[index];
            }
            index = (index + 1) % capacity;
            if (index == startIndex) break;
        }
        throw new RuntimeException("Key not found: " + key);
    }

    public boolean containsKey(int key) {
        int index = hash(key);
        int startIndex = index;
        while (occupied[index]) {
            if (keys[index] == key) {
                return true;
            }
            index = (index + 1) % capacity;
            if (index == startIndex) break;
        }
        return false;
    }

    public boolean remove(int key) {
        int index = hash(key);
        int startIndex = index;
        while (occupied[index]) {
            if (keys[index] == key) {
                occupied[index] = false;
                size--;
                rehashCluster(index);
                return true;
            }
            index = (index + 1) % capacity;
            if (index == startIndex) break;
        }
        return false;
    }

    private void rehashCluster(int removedIndex) {
        int index = (removedIndex + 1) % capacity;
        while (occupied[index]) {
            int k = keys[index];
            int v = values[index];
            occupied[index] = false;
            size--;
            put(k, v);
            index = (index + 1) % capacity;
        }
    }

    private void resize() {
        int oldCap = capacity;
        int[] oldKeys = keys;
        int[] oldValues = values;
        boolean[] oldOccupied = occupied;
        capacity = capacity * 2;
        keys = new int[capacity];
        values = new int[capacity];
        occupied = new boolean[capacity];
        size = 0;
        for (int i = 0; i < oldCap; i++) {
            if (oldOccupied[i]) {
                put(oldKeys[i], oldValues[i]);
            }
        }
    }

    public int getSize() {
        return size;
    }

    public double loadFactor() {
        return (double) size / capacity;
    }

    public void printTable() {
        System.out.println("Hash Table (capacity=" + capacity + ", size=" + size + "):");
        for (int i = 0; i < capacity; i++) {
            if (occupied[i]) {
                System.out.println("  [" + i + "] " + keys[i] + " => " + values[i]);
            }
        }
    }

    public int[] getAllKeys() {
        int[] result = new int[size];
        int idx = 0;
        for (int i = 0; i < capacity; i++) {
            if (occupied[i]) {
                result[idx++] = keys[i];
            }
        }
        return result;
    }

    public static void main(String[] args) {
        HashTable table = new HashTable(16);
        for (int i = 0; i < 20; i++) {
            table.put(i * 7, i * 100);
        }
        table.printTable();
        System.out.println("Size: " + table.getSize());
        System.out.printf("Load factor: %.2f%n", table.loadFactor());
        System.out.println("Get key 14: " + table.get(14));
        System.out.println("Contains 21: " + table.containsKey(21));
        System.out.println("Contains 999: " + table.containsKey(999));
        table.remove(14);
        System.out.println("After removing 14, contains 14: " + table.containsKey(14));
        System.out.println("Size: " + table.getSize());
    }
}
"""

JAVA_S12 = """\
public class HashTable {
    private Entry[] buckets;
    private int capacity;
    private int size;

    private static class Entry {
        int key;
        int value;
        Entry next;
        Entry(int key, int value) {
            this.key = key;
            this.value = value;
            this.next = null;
        }
    }

    public HashTable(int capacity) {
        this.capacity = capacity;
        this.buckets = new Entry[capacity];
        this.size = 0;
    }

    private int hash(int key) {
        int h = key % capacity;
        if (h < 0) h += capacity;
        return h;
    }

    public void put(int key, int value) {
        if (size >= capacity * 3 / 4) {
            resize();
        }
        int index = hash(key);
        Entry current = buckets[index];
        while (current != null) {
            if (current.key == key) {
                current.value = value;
                return;
            }
            current = current.next;
        }
        Entry newEntry = new Entry(key, value);
        newEntry.next = buckets[index];
        buckets[index] = newEntry;
        size++;
    }

    public int get(int key) {
        int index = hash(key);
        Entry current = buckets[index];
        while (current != null) {
            if (current.key == key) {
                return current.value;
            }
            current = current.next;
        }
        throw new RuntimeException("Key not found: " + key);
    }

    public boolean containsKey(int key) {
        int index = hash(key);
        Entry current = buckets[index];
        while (current != null) {
            if (current.key == key) {
                return true;
            }
            current = current.next;
        }
        return false;
    }

    public boolean remove(int key) {
        int index = hash(key);
        Entry prev = null;
        Entry current = buckets[index];
        while (current != null) {
            if (current.key == key) {
                if (prev == null) {
                    buckets[index] = current.next;
                } else {
                    prev.next = current.next;
                }
                size--;
                return true;
            }
            prev = current;
            current = current.next;
        }
        return false;
    }

    private void resize() {
        int oldCap = capacity;
        Entry[] oldBuckets = buckets;
        capacity = capacity * 2;
        buckets = new Entry[capacity];
        size = 0;
        for (int i = 0; i < oldCap; i++) {
            Entry current = oldBuckets[i];
            while (current != null) {
                put(current.key, current.value);
                current = current.next;
            }
        }
    }

    public int getSize() {
        return size;
    }

    public double loadFactor() {
        return (double) size / capacity;
    }

    public void printTable() {
        System.out.println("Hash Table (capacity=" + capacity + ", size=" + size + "):");
        for (int i = 0; i < capacity; i++) {
            if (buckets[i] != null) {
                System.out.print("  [" + i + "] ");
                Entry current = buckets[i];
                while (current != null) {
                    System.out.print(current.key + "=>" + current.value);
                    if (current.next != null) System.out.print(" -> ");
                    current = current.next;
                }
                System.out.println();
            }
        }
    }

    public int[] getAllKeys() {
        int[] result = new int[size];
        int idx = 0;
        for (int i = 0; i < capacity; i++) {
            Entry current = buckets[i];
            while (current != null) {
                result[idx++] = current.key;
                current = current.next;
            }
        }
        return result;
    }

    public static void main(String[] args) {
        HashTable table = new HashTable(16);
        for (int i = 0; i < 20; i++) {
            table.put(i * 7, i * 100);
        }
        table.printTable();
        System.out.println("Size: " + table.getSize());
        System.out.printf("Load factor: %.2f%n", table.loadFactor());
        System.out.println("Get key 14: " + table.get(14));
        System.out.println("Contains 21: " + table.containsKey(21));
        System.out.println("Contains 999: " + table.containsKey(999));
        table.remove(14);
        System.out.println("After removing 14, contains 14: " + table.containsKey(14));
        System.out.println("Size: " + table.getSize());
    }
}
"""

# ═══════════════════════════════════════════════════════════════
#  FALSE-POSITIVE CONTROLS — S13, S14, S15
# ═══════════════════════════════════════════════════════════════

JAVA_S13 = """\
public class StringProcessor {
    private char[] buffer;
    private int length;

    public StringProcessor(String input) {
        this.buffer = input.toCharArray();
        this.length = buffer.length;
    }

    public String reverse() {
        char[] result = new char[length];
        for (int i = 0; i < length; i++) {
            result[i] = buffer[length - 1 - i];
        }
        return new String(result);
    }

    public boolean isPalindrome() {
        int left = 0;
        int right = length - 1;
        while (left < right) {
            char lc = Character.toLowerCase(buffer[left]);
            char rc = Character.toLowerCase(buffer[right]);
            if (!Character.isLetterOrDigit(lc)) { left++; continue; }
            if (!Character.isLetterOrDigit(rc)) { right--; continue; }
            if (lc != rc) return false;
            left++;
            right--;
        }
        return true;
    }

    public int countOccurrences(char target) {
        int count = 0;
        for (int i = 0; i < length; i++) {
            if (buffer[i] == target) count++;
        }
        return count;
    }

    public String compress() {
        if (length == 0) return "";
        StringBuilder sb = new StringBuilder();
        char current = buffer[0];
        int count = 1;
        for (int i = 1; i < length; i++) {
            if (buffer[i] == current) {
                count++;
            } else {
                sb.append(current);
                if (count > 1) sb.append(count);
                current = buffer[i];
                count = 1;
            }
        }
        sb.append(current);
        if (count > 1) sb.append(count);
        String compressed = sb.toString();
        return compressed.length() < length ? compressed : new String(buffer);
    }

    public int indexOf(String pattern) {
        char[] pat = pattern.toCharArray();
        int patLen = pat.length;
        if (patLen > length) return -1;
        for (int i = 0; i <= length - patLen; i++) {
            boolean match = true;
            for (int j = 0; j < patLen; j++) {
                if (buffer[i + j] != pat[j]) {
                    match = false;
                    break;
                }
            }
            if (match) return i;
        }
        return -1;
    }

    public String caesarEncrypt(int shift) {
        char[] result = new char[length];
        for (int i = 0; i < length; i++) {
            char ch = buffer[i];
            if (Character.isUpperCase(ch)) {
                result[i] = (char) ((ch - 'A' + shift) % 26 + 'A');
            } else if (Character.isLowerCase(ch)) {
                result[i] = (char) ((ch - 'a' + shift) % 26 + 'a');
            } else {
                result[i] = ch;
            }
        }
        return new String(result);
    }

    public String caesarDecrypt(int shift) {
        return new StringProcessor(new String(buffer)).caesarEncrypt(26 - (shift % 26));
    }

    public int[] charFrequency() {
        int[] freq = new int[128];
        for (int i = 0; i < length; i++) {
            if (buffer[i] < 128) {
                freq[buffer[i]]++;
            }
        }
        return freq;
    }

    public String toUpperCase() {
        char[] result = new char[length];
        for (int i = 0; i < length; i++) {
            result[i] = Character.toUpperCase(buffer[i]);
        }
        return new String(result);
    }

    public static void main(String[] args) {
        StringProcessor sp = new StringProcessor("Hello, World!");
        System.out.println("Original: Hello, World!");
        System.out.println("Reversed: " + sp.reverse());
        System.out.println("Uppercase: " + sp.toUpperCase());
        System.out.println("Count 'l': " + sp.countOccurrences('l'));
        System.out.println("Index of 'World': " + sp.indexOf("World"));
        System.out.println("Caesar +3: " + sp.caesarEncrypt(3));
        StringProcessor sp2 = new StringProcessor("aabcccccaaa");
        System.out.println("Compressed: " + sp2.compress());
        StringProcessor sp3 = new StringProcessor("A man a plan a canal Panama");
        System.out.println("Palindrome: " + sp3.isPalindrome());
    }
}
"""

JAVA_S14 = """\
public class CircularQueue {
    private int[] data;
    private int front;
    private int rear;
    private int size;
    private int capacity;

    public CircularQueue(int capacity) {
        this.capacity = capacity;
        this.data = new int[capacity];
        this.front = 0;
        this.rear = -1;
        this.size = 0;
    }

    public void enqueue(int value) {
        if (size >= capacity) {
            resize();
        }
        rear = (rear + 1) % capacity;
        data[rear] = value;
        size++;
    }

    public int dequeue() {
        if (size == 0) {
            throw new RuntimeException("Queue is empty");
        }
        int value = data[front];
        front = (front + 1) % capacity;
        size--;
        return value;
    }

    public int peek() {
        if (size == 0) {
            throw new RuntimeException("Queue is empty");
        }
        return data[front];
    }

    public int peekRear() {
        if (size == 0) {
            throw new RuntimeException("Queue is empty");
        }
        return data[rear];
    }

    public boolean isEmpty() {
        return size == 0;
    }

    public boolean isFull() {
        return size == capacity;
    }

    public int getSize() {
        return size;
    }

    private void resize() {
        int newCapacity = capacity * 2;
        int[] newData = new int[newCapacity];
        for (int i = 0; i < size; i++) {
            newData[i] = data[(front + i) % capacity];
        }
        data = newData;
        front = 0;
        rear = size - 1;
        capacity = newCapacity;
    }

    public boolean contains(int value) {
        for (int i = 0; i < size; i++) {
            if (data[(front + i) % capacity] == value) {
                return true;
            }
        }
        return false;
    }

    public int[] toArray() {
        int[] result = new int[size];
        for (int i = 0; i < size; i++) {
            result[i] = data[(front + i) % capacity];
        }
        return result;
    }

    public void clear() {
        front = 0;
        rear = -1;
        size = 0;
    }

    public void printQueue() {
        System.out.print("Queue [front -> rear]: ");
        for (int i = 0; i < size; i++) {
            System.out.print(data[(front + i) % capacity]);
            if (i < size - 1) System.out.print(", ");
        }
        System.out.println();
    }

    public static int[] simulateJosephus(int n, int k) {
        CircularQueue circle = new CircularQueue(n);
        for (int i = 1; i <= n; i++) {
            circle.enqueue(i);
        }
        int[] elimination = new int[n];
        int idx = 0;
        while (!circle.isEmpty()) {
            for (int step = 1; step < k; step++) {
                circle.enqueue(circle.dequeue());
            }
            elimination[idx++] = circle.dequeue();
        }
        return elimination;
    }

    public static void main(String[] args) {
        CircularQueue queue = new CircularQueue(4);
        for (int i = 10; i <= 80; i += 10) {
            queue.enqueue(i);
        }
        queue.printQueue();
        System.out.println("Size: " + queue.getSize());
        System.out.println("Front: " + queue.peek());
        System.out.println("Rear: " + queue.peekRear());
        System.out.println("Dequeue: " + queue.dequeue());
        System.out.println("Dequeue: " + queue.dequeue());
        queue.printQueue();
        System.out.println("Contains 50: " + queue.contains(50));
        System.out.println("Contains 10: " + queue.contains(10));
        System.out.print("Josephus(7,3): ");
        int[] order = simulateJosephus(7, 3);
        for (int v : order) System.out.print(v + " ");
        System.out.println();
    }
}
"""

JAVA_S15 = """\
public class PriorityHeap {
    private int[] heap;
    private int size;
    private int capacity;
    private boolean isMinHeap;

    public PriorityHeap(int capacity, boolean isMinHeap) {
        this.capacity = capacity;
        this.heap = new int[capacity];
        this.size = 0;
        this.isMinHeap = isMinHeap;
    }

    private int parent(int i) { return (i - 1) / 2; }
    private int leftChild(int i) { return 2 * i + 1; }
    private int rightChild(int i) { return 2 * i + 2; }

    private boolean compare(int a, int b) {
        return isMinHeap ? a < b : a > b;
    }

    private void swap(int i, int j) {
        int temp = heap[i];
        heap[i] = heap[j];
        heap[j] = temp;
    }

    public void insert(int value) {
        if (size >= capacity) {
            int newCap = capacity * 2;
            int[] newHeap = new int[newCap];
            for (int i = 0; i < size; i++) {
                newHeap[i] = heap[i];
            }
            heap = newHeap;
            capacity = newCap;
        }
        heap[size] = value;
        siftUp(size);
        size++;
    }

    private void siftUp(int index) {
        while (index > 0 && compare(heap[index], heap[parent(index)])) {
            swap(index, parent(index));
            index = parent(index);
        }
    }

    public int extractTop() {
        if (size == 0) {
            throw new RuntimeException("Heap is empty");
        }
        int top = heap[0];
        heap[0] = heap[size - 1];
        size--;
        if (size > 0) {
            siftDown(0);
        }
        return top;
    }

    private void siftDown(int index) {
        while (true) {
            int best = index;
            int left = leftChild(index);
            int right = rightChild(index);
            if (left < size && compare(heap[left], heap[best])) {
                best = left;
            }
            if (right < size && compare(heap[right], heap[best])) {
                best = right;
            }
            if (best == index) break;
            swap(index, best);
            index = best;
        }
    }

    public int peekTop() {
        if (size == 0) {
            throw new RuntimeException("Heap is empty");
        }
        return heap[0];
    }

    public int getSize() { return size; }
    public boolean isEmpty() { return size == 0; }

    public static int[] heapSort(int[] arr) {
        PriorityHeap minHeap = new PriorityHeap(arr.length, true);
        for (int val : arr) {
            minHeap.insert(val);
        }
        int[] sorted = new int[arr.length];
        for (int i = 0; i < arr.length; i++) {
            sorted[i] = minHeap.extractTop();
        }
        return sorted;
    }

    public static int kthSmallest(int[] arr, int k) {
        PriorityHeap maxHeap = new PriorityHeap(k + 1, false);
        for (int val : arr) {
            maxHeap.insert(val);
            if (maxHeap.getSize() > k) {
                maxHeap.extractTop();
            }
        }
        return maxHeap.peekTop();
    }

    public void printHeap() {
        System.out.print("Heap: [");
        for (int i = 0; i < size; i++) {
            System.out.print(heap[i]);
            if (i < size - 1) System.out.print(", ");
        }
        System.out.println("]");
    }

    public static void main(String[] args) {
        PriorityHeap minHeap = new PriorityHeap(10, true);
        int[] values = {45, 20, 14, 12, 31, 7, 11, 28, 33, 17};
        for (int v : values) {
            minHeap.insert(v);
        }
        minHeap.printHeap();
        System.out.println("Top: " + minHeap.peekTop());
        System.out.println("Extract: " + minHeap.extractTop());
        System.out.println("Extract: " + minHeap.extractTop());
        minHeap.printHeap();
        int[] data = {64, 34, 25, 12, 22, 11, 90, 1};
        int[] sorted = heapSort(data);
        System.out.print("Heap sorted: ");
        for (int v : sorted) System.out.print(v + " ");
        System.out.println();
        System.out.println("3rd smallest: " + kthSmallest(data, 3));
    }
}
"""


# ═══════════════════════════════════════════════════════════════
#  PACKAGING
# ═══════════════════════════════════════════════════════════════

def make_inner_zip(filename, source_code):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(filename, source_code)
    return buf.getvalue()


def make_repo_zip(programs):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as outer:
        for label, (filename, source) in programs.items():
            inner_bytes = make_inner_zip(filename, source)
            outer.writestr(f"{label}.zip", inner_bytes)
    return buf.getvalue()


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    programs = {
        "S01": ("LinkedList.java", JAVA_S01),
        "S02": ("LinkedList.java", JAVA_S02),
        "S03": ("MatrixOps.java", JAVA_S03),
        "S04": ("MatrixOps.java", JAVA_S04),
        "S05": ("MatrixOps.java", JAVA_S05),
        "S06": ("BinarySearchTree.java", JAVA_S06),
        "S07": ("SortBenchmark.java", JAVA_S07),
        "S08": ("StackCalculator.java", JAVA_S08),
        "S09": ("StatisticsCalculator.java", JAVA_S09),
        "S10": ("GraphTraversal.java", JAVA_S10),
        "S11": ("HashTable.java", JAVA_S11),
        "S12": ("HashTable.java", JAVA_S12),
        "S13": ("StringProcessor.java", JAVA_S13),
        "S14": ("CircularQueue.java", JAVA_S14),
        "S15": ("PriorityHeap.java", JAVA_S15),
    }

    print("=== Line counts ===")
    for label, (filename, source) in programs.items():
        lines = len(source.strip().split("\n"))
        print(f"  {label} ({filename}): {lines} lines")

    repo_zip = make_repo_zip(programs)
    (OUTPUT_DIR / "TestSetJava.zip").write_bytes(repo_zip)

    manifest = """\
# Stage 3 Final Java Test Set — Internal Manifest

## Overview
- 15 Java programs in zip-of-zips format (TestSetJava.zip)
- Neutral S01-S15 naming — no hints to evaluator

## Categories

### True-Positive Pair A — Local Variable Rename Detection
| ID  | Description |
|-----|-------------|
| S01 | LinkedList: insert, delete, search, reverse, getAt, insertAt — original |
| S02 | LinkedList: identical structure, local variables renamed (current->ptr, newNode->n, prev->p, i->k) |

**Expected:** >90% similarity. Tests basic local-variable rename detection.

### True-Positive Triple B — Reorder + Local Variable Rename
| ID  | Description |
|-----|-------------|
| S03 | MatrixOps: add, multiply, transpose, trace, scalarMultiply, isSymmetric — original |
| S04 | MatrixOps: functions reordered (transpose first, add/multiply last), locals renamed (i,j->r,c; sum->acc; result->res) |
| S05 | MatrixOps: same function order as S03, different rename scheme (i,j->a,b; sum->val; result->out) |

**Expected:** >70% similarity for all 3 pairs. Tests function reorder + rename robustness.

### True-Positive Hard Pair C — Different Internal Data Structure
| ID  | Description |
|-----|-------------|
| S11 | HashTable with open addressing (linear probing): arrays for keys/values/occupied, rehash on remove |
| S12 | HashTable with separate chaining (linked list buckets): Entry linked list per bucket |

Same public API (put, get, containsKey, remove, getSize, loadFactor, printTable, getAllKeys).
Same class name, same method signatures, same main(). Different internal implementation.

**Expected:** 30-60% similarity. Tests whether engine detects shared API shape despite different internals.

### False-Positive Controls
| ID  | Description |
|-----|-------------|
| S06 | BinarySearchTree: recursive insert/search/delete, traversals, height, count |
| S07 | SortBenchmark: bubble, selection, insertion, merge, quick sort on arrays |
| S08 | StackCalculator: array stack, postfix evaluation, infix-to-postfix conversion |
| S09 | StatisticsCalculator: mean, median, variance, stddev, percentile, dynamic array |
| S10 | GraphTraversal: adjacency matrix, BFS, DFS, path finding, connected components |
| S13 | StringProcessor: reverse, palindrome, compress, indexOf, Caesar cipher, frequency |
| S14 | CircularQueue: circular array queue, resize, Josephus problem simulation |
| S15 | PriorityHeap: binary heap, insert/extract, heap sort, kth smallest |

**Expected:** <30% similarity between any two controls, and <30% against positive pairs.

## Score Targets Summary

| Pair | Expected | Category |
|------|----------|----------|
| S01 vs S02 | >90% | Rename detection |
| S03 vs S04 | >70% | Reorder + rename |
| S03 vs S05 | >70% | Rename variant |
| S04 vs S05 | >70% | Reorder vs rename |
| S11 vs S12 | 30-60% | Structural similarity |
| Any control pair | <30% | False positive rejection |
"""
    (OUTPUT_DIR / "MANIFEST.md").write_text(manifest, encoding="utf-8")

    print(f"\n=== Output ===")
    print(f"  {OUTPUT_DIR / 'TestSetJava.zip'} ({len(repo_zip)} bytes)")
    print(f"  {OUTPUT_DIR / 'MANIFEST.md'}")
    print("\nDone.")


if __name__ == "__main__":
    main()
