/**
 * LinkedListTest.java
 * Provided by: Prof. Margaret Collins
 * Course: COSC 2P03 - Data Structures
 * Assignment 2: Linked List Implementation
 *
 * DO NOT MODIFY THIS FILE.
 * This test class will be used for grading. Your LinkedList.java must
 * pass all tests below without altering this file.
 */
public class LinkedListTest {

    public static void main(String[] args) {
        System.out.println("=== Running LinkedList Tests ===\n");

        LinkedList list = new LinkedList();

        // Test insert
        list.insert(10);
        list.insert(20);
        list.insert(30);
        list.insert(40);
        System.out.print("After inserting 10, 20, 30, 40: ");
        list.display();

        // Test size
        System.out.println("Size: " + list.size());

        // Test contains
        System.out.println("Contains 20: " + list.contains(20));
        System.out.println("Contains 99: " + list.contains(99));

        // Test delete
        list.delete(20);
        System.out.print("After deleting 20: ");
        list.display();

        // Test reverse
        list.reverse();
        System.out.print("After reverse: ");
        list.display();

        // Test size after operations
        System.out.println("Final size: " + list.size());

        System.out.println("\n=== Tests Complete ===");
    }
}
