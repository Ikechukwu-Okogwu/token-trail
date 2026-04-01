public class PairHighA {
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

    public static int helper1(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 1) % (4);
        }
        return hsum;
    }

    public static int helper2(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 2) % (5);
        }
        return hsum;
    }

    public static int helper3(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 3) % (6);
        }
        return hsum;
    }

    public static int helper4(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 4) % (7);
        }
        return hsum;
    }

    public static int helper5(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 5) % (8);
        }
        return hsum;
    }

    public static int helper6(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 6) % (9);
        }
        return hsum;
    }

    public static int helper7(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 7) % (10);
        }
        return hsum;
    }

    public static int helper8(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 8) % (11);
        }
        return hsum;
    }

    public static int helper9(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 9) % (12);
        }
        return hsum;
    }

    public static int helper10(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 10) % (13);
        }
        return hsum;
    }

    public static int helper11(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 11) % (14);
        }
        return hsum;
    }

    public static int helper12(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 12) % (15);
        }
        return hsum;
    }

    public static int helper13(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 13) % (16);
        }
        return hsum;
    }

    public static int helper14(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 14) % (17);
        }
        return hsum;
    }

    public static int helper15(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 15) % (18);
        }
        return hsum;
    }

    public static int helper16(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 16) % (19);
        }
        return hsum;
    }

    public static int helper17(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 17) % (20);
        }
        return hsum;
    }

    public static int helper18(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 18) % (21);
        }
        return hsum;
    }

    public static int helper19(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 19) % (22);
        }
        return hsum;
    }

    public static int helper20(int hx) {
        int hsum = 0;
        for (int hi = 0; hi < hx; hi++) {
            hsum += (hi * 20) % (23);
        }
        return hsum;
    }

}
