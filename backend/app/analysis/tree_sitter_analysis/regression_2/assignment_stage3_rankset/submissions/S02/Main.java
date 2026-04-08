public class RankB {
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

    public static int weighted(int[] values) {
        int total = 0;
        for (int i = 0; i < values.length; i++) {
            total += values[i] * (i + 1);
        }
        return total;
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
    public static int[] rotate(int[] values) {
        if (values.length == 0) return values;
        int first = values[0];
        for (int i = 0; i < values.length - 1; i++) {
            values[i] = values[i + 1];
        }
        values[values.length - 1] = first;
        return values;
    }

    public static int helper1(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 1) % (4);
        }
        return ysum;
    }

    public static int helper2(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 2) % (5);
        }
        return ysum;
    }

    public static int helper3(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 3) % (6);
        }
        return ysum;
    }

    public static int helper4(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 4) % (7);
        }
        return ysum;
    }

    public static int helper5(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 5) % (8);
        }
        return ysum;
    }

    public static int helper6(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 6) % (9);
        }
        return ysum;
    }

    public static int helper7(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 7) % (10);
        }
        return ysum;
    }

    public static int helper8(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 8) % (11);
        }
        return ysum;
    }

    public static int helper9(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 9) % (12);
        }
        return ysum;
    }

    public static int helper10(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 10) % (13);
        }
        return ysum;
    }

    public static int helper11(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 11) % (14);
        }
        return ysum;
    }

    public static int helper12(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 12) % (15);
        }
        return ysum;
    }

    public static int helper13(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 13) % (16);
        }
        return ysum;
    }

    public static int helper14(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 14) % (17);
        }
        return ysum;
    }

    public static int helper15(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 15) % (18);
        }
        return ysum;
    }

    public static int helper16(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 16) % (19);
        }
        return ysum;
    }

    public static int helper17(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 17) % (20);
        }
        return ysum;
    }

    public static int helper18(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 18) % (21);
        }
        return ysum;
    }

    public static int helper19(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 19) % (22);
        }
        return ysum;
    }

    public static int helper20(int yx) {
        int ysum = 0;
        for (int yi = 0; yi < yx; yi++) {
            ysum += (yi * 20) % (23);
        }
        return ysum;
    }

}
