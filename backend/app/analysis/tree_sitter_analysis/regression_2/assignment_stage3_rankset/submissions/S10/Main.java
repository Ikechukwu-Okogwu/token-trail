public class UniqueThree {
    public static int gcd(int a, int b) {
        while (b != 0) {
            int t = b;
            b = a % b;
            a = t;
        }
        return a;
    }

    public static int lcm(int a, int b) {
        return (a / gcd(a, b)) * b;
    }

    public static boolean isPrime(int n) {
        if (n < 2) return false;
        for (int i = 2; i * i <= n; i++) {
            if (n % i == 0) return false;
        }
        return true;
    }

    public static int sequence1(int x) {
        int value = x;
        for (int i = 0; i < 6; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence2(int x) {
        int value = x;
        for (int i = 0; i < 7; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence3(int x) {
        int value = x;
        for (int i = 0; i < 8; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence4(int x) {
        int value = x;
        for (int i = 0; i < 9; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence5(int x) {
        int value = x;
        for (int i = 0; i < 10; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence6(int x) {
        int value = x;
        for (int i = 0; i < 11; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence7(int x) {
        int value = x;
        for (int i = 0; i < 12; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence8(int x) {
        int value = x;
        for (int i = 0; i < 13; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence9(int x) {
        int value = x;
        for (int i = 0; i < 14; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence10(int x) {
        int value = x;
        for (int i = 0; i < 15; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence11(int x) {
        int value = x;
        for (int i = 0; i < 16; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence12(int x) {
        int value = x;
        for (int i = 0; i < 17; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence13(int x) {
        int value = x;
        for (int i = 0; i < 18; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence14(int x) {
        int value = x;
        for (int i = 0; i < 19; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence15(int x) {
        int value = x;
        for (int i = 0; i < 20; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence16(int x) {
        int value = x;
        for (int i = 0; i < 21; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence17(int x) {
        int value = x;
        for (int i = 0; i < 22; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence18(int x) {
        int value = x;
        for (int i = 0; i < 23; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence19(int x) {
        int value = x;
        for (int i = 0; i < 24; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence20(int x) {
        int value = x;
        for (int i = 0; i < 25; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence21(int x) {
        int value = x;
        for (int i = 0; i < 26; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence22(int x) {
        int value = x;
        for (int i = 0; i < 27; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence23(int x) {
        int value = x;
        for (int i = 0; i < 28; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence24(int x) {
        int value = x;
        for (int i = 0; i < 29; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence25(int x) {
        int value = x;
        for (int i = 0; i < 30; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence26(int x) {
        int value = x;
        for (int i = 0; i < 31; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence27(int x) {
        int value = x;
        for (int i = 0; i < 32; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence28(int x) {
        int value = x;
        for (int i = 0; i < 33; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence29(int x) {
        int value = x;
        for (int i = 0; i < 34; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence30(int x) {
        int value = x;
        for (int i = 0; i < 35; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence31(int x) {
        int value = x;
        for (int i = 0; i < 36; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence32(int x) {
        int value = x;
        for (int i = 0; i < 37; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence33(int x) {
        int value = x;
        for (int i = 0; i < 38; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence34(int x) {
        int value = x;
        for (int i = 0; i < 39; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence35(int x) {
        int value = x;
        for (int i = 0; i < 40; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence36(int x) {
        int value = x;
        for (int i = 0; i < 41; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence37(int x) {
        int value = x;
        for (int i = 0; i < 42; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence38(int x) {
        int value = x;
        for (int i = 0; i < 43; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence39(int x) {
        int value = x;
        for (int i = 0; i < 44; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence40(int x) {
        int value = x;
        for (int i = 0; i < 45; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence41(int x) {
        int value = x;
        for (int i = 0; i < 46; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence42(int x) {
        int value = x;
        for (int i = 0; i < 47; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence43(int x) {
        int value = x;
        for (int i = 0; i < 48; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static int sequence44(int x) {
        int value = x;
        for (int i = 0; i < 49; i++) {
            value = (value * 40 + i + 6) % 915;
        }
        return value;
    }

    public static void main(String[] args) {
        int output = 0;
        for (int i = 1; i < 50; i++) {
            output += sequence1(i) + sequence2(i);
        }
        System.out.println(output + lcm(91, 36));
    }
}
