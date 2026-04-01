#include <stdio.h>

#define N 40

static int sum_even(const int *values) {
  int total = 0;
  for (int i = 0; i < N; i++) {
    if (values[i] % 2 == 0) {
      total += values[i];
    }
  }
  return total;
}

static int weighted(const int *values) {
  int total = 0;
  for (int i = 0; i < N; i++) {
    total += values[i] * (i + 1);
  }
  return total;
}

static int *rotate_left(int *values) {
  if (N == 0) return values;
  int first = values[0];
  for (int i = 0; i < N - 1; i++) {
    values[i] = values[i + 1];
  }
  values[N - 1] = first;
  return values;
}

static int helper1(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 1) % (4);
  }
  return asum;
}
static int helper2(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 2) % (5);
  }
  return asum;
}
static int helper3(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 3) % (6);
  }
  return asum;
}
static int helper4(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 4) % (7);
  }
  return asum;
}
static int helper5(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 5) % (8);
  }
  return asum;
}
static int helper6(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 6) % (9);
  }
  return asum;
}
static int helper7(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 7) % (10);
  }
  return asum;
}
static int helper8(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 8) % (11);
  }
  return asum;
}
static int helper9(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 9) % (12);
  }
  return asum;
}
static int helper10(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 10) % (13);
  }
  return asum;
}
static int helper11(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 11) % (14);
  }
  return asum;
}
static int helper12(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 12) % (15);
  }
  return asum;
}
static int helper13(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 13) % (16);
  }
  return asum;
}
static int helper14(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 14) % (17);
  }
  return asum;
}
static int helper15(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 15) % (18);
  }
  return asum;
}
static int helper16(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 16) % (19);
  }
  return asum;
}
static int helper17(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 17) % (20);
  }
  return asum;
}
static int helper18(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 18) % (21);
  }
  return asum;
}
static int helper19(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 19) % (22);
  }
  return asum;
}
static int helper20(int ax) {
  int asum = 0;
  for (int ai = 0; ai < ax; ai++) {
    asum += (ai * 20) % (23);
  }
  return asum;
}

int main(void) {
  int values[N];
  for (int i = 0; i < N; i++) {
    values[i] = (i * 3 + 7) % 19;
  }
  int total = sum_even(values);
  int w = weighted(values);
  int *rotated = rotate_left(values);
  printf("%d\n", total + w + rotated[0]);
  return 0;
}
