class FibWhile {
    public static void main(String[] args) {
        printFibonacci(10);
    }

    public static void printFibonacci(int n) {
        if (n <= 0) return;
        int a = 0, b = 1;
        int i = 0;
        while (i < n) {
            System.out.print(a + " ");
            int next = a + b;
            a = b;
            b = next;
            i++;
        }
        System.out.println();
    }
}
