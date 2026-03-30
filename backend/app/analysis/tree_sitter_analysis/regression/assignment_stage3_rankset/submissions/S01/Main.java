public class RankA {
    public static void main(String[] args) {
        int[] values = new int[40];
        for (int i = 0; i < values.length; i++) {
            values[i] = (i * 3 + 7) % 19;
        }
        int total = sumEven(values);
        int w = weighted(values);
        int[] rotated = rotate(values);
        System.out.println(total + w + rotated[0]);
    }

    public static int sumEven(int[] values) {
        int total = 0;
        for (int v : values) {
            if (v % 2 == 0) {
                total += v;
            }
        }
        return total;
    }
    public static int weighted(int[] values) {
        int total = 0;
        for (int i = 0; i < values.length; i++) {
            total += values[i] * (i + 1);
        }
        return total;
    }
    public static int[] rotate(int[] values) {
        if (values.length == 0) return values;
        int first = values[0];
        for (int i = 0; i < values.length - 1; i++) {
            values[i] = values[i + 1];
        }
        values[values.length - 1] = first;
        return values;
    }

    public static int helper1(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 1) % (4);
        }
        return xsum;
    }

    public static int helper2(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 2) % (5);
        }
        return xsum;
    }

    public static int helper3(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 3) % (6);
        }
        return xsum;
    }

    public static int helper4(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 4) % (7);
        }
        return xsum;
    }

    public static int helper5(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 5) % (8);
        }
        return xsum;
    }

    public static int helper6(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 6) % (9);
        }
        return xsum;
    }

    public static int helper7(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 7) % (10);
        }
        return xsum;
    }

    public static int helper8(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 8) % (11);
        }
        return xsum;
    }

    public static int helper9(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 9) % (12);
        }
        return xsum;
    }

    public static int helper10(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 10) % (13);
        }
        return xsum;
    }

    public static int helper11(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 11) % (14);
        }
        return xsum;
    }

    public static int helper12(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 12) % (15);
        }
        return xsum;
    }

    public static int helper13(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 13) % (16);
        }
        return xsum;
    }

    public static int helper14(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 14) % (17);
        }
        return xsum;
    }

    public static int helper15(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 15) % (18);
        }
        return xsum;
    }

    public static int helper16(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 16) % (19);
        }
        return xsum;
    }

    public static int helper17(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 17) % (20);
        }
        return xsum;
    }

    public static int helper18(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 18) % (21);
        }
        return xsum;
    }

    public static int helper19(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 19) % (22);
        }
        return xsum;
    }

    public static int helper20(int xx) {
        int xsum = 0;
        for (int xi = 0; xi < xx; xi++) {
            xsum += (xi * 20) % (23);
        }
        return xsum;
    }

}
