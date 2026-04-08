public class RankC {
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

    public static int[] rotate(int[] values) {
        if (values.length == 0) return values;
        int first = values[0];
        for (int i = 0; i < values.length - 1; i++) {
            values[i] = values[i + 1];
        }
        values[values.length - 1] = first;
        return values;
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

    public static int helper1(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 1) % (4);
        }
        return zsum;
    }

    public static int helper2(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 2) % (5);
        }
        return zsum;
    }

    public static int helper3(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 3) % (6);
        }
        return zsum;
    }

    public static int helper4(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 4) % (7);
        }
        return zsum;
    }

    public static int helper5(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 5) % (8);
        }
        return zsum;
    }

    public static int helper6(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 6) % (9);
        }
        return zsum;
    }

    public static int helper7(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 7) % (10);
        }
        return zsum;
    }

    public static int helper8(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 8) % (11);
        }
        return zsum;
    }

    public static int helper9(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 9) % (12);
        }
        return zsum;
    }

    public static int helper10(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 10) % (13);
        }
        return zsum;
    }

    public static int helper11(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 11) % (14);
        }
        return zsum;
    }

    public static int helper12(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 12) % (15);
        }
        return zsum;
    }

    public static int helper13(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 13) % (16);
        }
        return zsum;
    }

    public static int helper14(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 14) % (17);
        }
        return zsum;
    }

    public static int helper15(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 15) % (18);
        }
        return zsum;
    }

    public static int helper16(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 16) % (19);
        }
        return zsum;
    }

    public static int helper17(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 17) % (20);
        }
        return zsum;
    }

    public static int helper18(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 18) % (21);
        }
        return zsum;
    }

    public static int helper19(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 19) % (22);
        }
        return zsum;
    }

    public static int helper20(int zx) {
        int zsum = 0;
        for (int zi = 0; zi < zx; zi++) {
            zsum += (zi * 20) % (23);
        }
        return zsum;
    }

}
