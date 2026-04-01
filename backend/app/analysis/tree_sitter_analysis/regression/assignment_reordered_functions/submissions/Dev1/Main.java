public class OrderedA {
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

    public static int helper1(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 1) % (4);
        }
        return vsum;
    }

    public static int helper2(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 2) % (5);
        }
        return vsum;
    }

    public static int helper3(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 3) % (6);
        }
        return vsum;
    }

    public static int helper4(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 4) % (7);
        }
        return vsum;
    }

    public static int helper5(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 5) % (8);
        }
        return vsum;
    }

    public static int helper6(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 6) % (9);
        }
        return vsum;
    }

    public static int helper7(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 7) % (10);
        }
        return vsum;
    }

    public static int helper8(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 8) % (11);
        }
        return vsum;
    }

    public static int helper9(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 9) % (12);
        }
        return vsum;
    }

    public static int helper10(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 10) % (13);
        }
        return vsum;
    }

    public static int helper11(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 11) % (14);
        }
        return vsum;
    }

    public static int helper12(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 12) % (15);
        }
        return vsum;
    }

    public static int helper13(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 13) % (16);
        }
        return vsum;
    }

    public static int helper14(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 14) % (17);
        }
        return vsum;
    }

    public static int helper15(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 15) % (18);
        }
        return vsum;
    }

    public static int helper16(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 16) % (19);
        }
        return vsum;
    }

    public static int helper17(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 17) % (20);
        }
        return vsum;
    }

    public static int helper18(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 18) % (21);
        }
        return vsum;
    }

    public static int helper19(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 19) % (22);
        }
        return vsum;
    }

    public static int helper20(int vx) {
        int vsum = 0;
        for (int vi = 0; vi < vx; vi++) {
            vsum += (vi * 20) % (23);
        }
        return vsum;
    }

}
