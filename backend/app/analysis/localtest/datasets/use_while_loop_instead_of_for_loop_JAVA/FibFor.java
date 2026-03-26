class FibFor {
    public static void main(String[] args) {
        printFibonacci(10);
    }

    public static void printFibonacci(int n) {
        if (n <= 0) return;
        int a = 0, b = 1;
        for (int i = 0; i < n; i++) {
            System.out.print(a + " ");
            int next = a + b;
            a = b;
            b = next;
        }
        System.out.println();
    }
}
