#include <stdio.h>
#include <stdlib.h>

#define SIZE 3

typedef int Matrix[SIZE][SIZE];

void matMul(const Matrix a, const Matrix b, Matrix out) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            out[i][j] = 0;
            for (int k = 0; k < SIZE; k++) {
                out[i][j] += a[i][k] * b[k][j];
            }
        }
    }
}

void matIdentity(Matrix m) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            m[i][j] = (i == j) ? 1 : 0;
        }
    }
}

void matPrint(const char *label, const Matrix m) {
    printf("%s:\n", label);
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            printf("%4d", m[i][j]);
        }
        printf("\n");
    }
}

int matTrace(const Matrix m) {
    int tr = 0;
    for (int i = 0; i < SIZE; i++) tr += m[i][i];
    return tr;
}

int matEqual(const Matrix a, const Matrix b) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            if (a[i][j] != b[i][j]) return 0;
        }
    }
    return 1;
}

int main(void) {
    Matrix a = {{1, 2, 3}, {4, 5, 6}, {7, 8, 9}};
    Matrix id;
    matIdentity(id);
    Matrix result;
    matMul(a, id, result);
    matPrint("A", a);
    matPrint("A * I", result);
    printf("Trace: %d\n",        matTrace(a));
    printf("A * I == A: %d\n",   matEqual(a, result));
    return 0;
}
