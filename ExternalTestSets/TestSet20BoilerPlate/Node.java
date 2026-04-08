/**
 * Node.java
 * Provided by: Prof. Margaret Collins
 * Course: COSC 2P03 - Data Structures
 * Assignment 2: Linked List Implementation
 *
 * DO NOT MODIFY THIS FILE.
 * This class is provided as boilerplate for your LinkedList implementation.
 */
public class Node {

    public int data;
    public Node next;

    /**
     * Constructs a new Node with the given data.
     * @param data the integer value to store in this node
     */
    public Node(int data) {
        this.data = data;
        this.next = null;
    }
}
