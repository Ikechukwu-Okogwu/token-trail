public class RenamedBase {
    public static void main(String[] args) {
        int[] dataset = new int[40];
        for (int i = 0; i < dataset.length; i++) {
            dataset[i] = (i * 3 + 7) % 19;
        }
        int accumulator = sumEvenTerms(dataset);
        int w = weightedScore(dataset);
        int[] shiftLeftd = shiftLeft(dataset);
        System.out.println(accumulator + w + shiftLeftd[0]);
    }

    public static int sumEvenTerms(int[] dataset) {
        int accumulator = 0;
        for (int v : dataset) {
            if (v % 2 == 0) {
                accumulator += v;
            }
        }
        return accumulator;
    }
    public static int weightedScore(int[] dataset) {
        int accumulator = 0;
        for (int i = 0; i < dataset.length; i++) {
            accumulator += dataset[i] * (i + 1);
        }
        return accumulator;
    }
    public static int[] shiftLeft(int[] dataset) {
        if (dataset.length == 0) return dataset;
        int first = dataset[0];
        for (int i = 0; i < dataset.length - 1; i++) {
            dataset[i] = dataset[i + 1];
        }
        dataset[dataset.length - 1] = first;
        return dataset;
    }

    public static int helper1(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 1) % (4);
        }
        return asum;
    }

    public static int helper2(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 2) % (5);
        }
        return asum;
    }

    public static int helper3(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 3) % (6);
        }
        return asum;
    }

    public static int helper4(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 4) % (7);
        }
        return asum;
    }

    public static int helper5(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 5) % (8);
        }
        return asum;
    }

    public static int helper6(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 6) % (9);
        }
        return asum;
    }

    public static int helper7(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 7) % (10);
        }
        return asum;
    }

    public static int helper8(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 8) % (11);
        }
        return asum;
    }

    public static int helper9(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 9) % (12);
        }
        return asum;
    }

    public static int helper10(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 10) % (13);
        }
        return asum;
    }

    public static int helper11(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 11) % (14);
        }
        return asum;
    }

    public static int helper12(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 12) % (15);
        }
        return asum;
    }

    public static int helper13(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 13) % (16);
        }
        return asum;
    }

    public static int helper14(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 14) % (17);
        }
        return asum;
    }

    public static int helper15(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 15) % (18);
        }
        return asum;
    }

    public static int helper16(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 16) % (19);
        }
        return asum;
    }

    public static int helper17(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 17) % (20);
        }
        return asum;
    }

    public static int helper18(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 18) % (21);
        }
        return asum;
    }

    public static int helper19(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 19) % (22);
        }
        return asum;
    }

    public static int helper20(int ax) {
        int asum = 0;
        for (int ai = 0; ai < ax; ai++) {
            asum += (ai * 20) % (23);
        }
        return asum;
    }

}
