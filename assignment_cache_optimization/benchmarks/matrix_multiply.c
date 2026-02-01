/*
 * Matrix Multiplication Benchmark for gem5 Cache Analysis
 *
 * This benchmark performs matrix multiplication of two NxN matrices.
 * It is designed to be memory-intensive to stress the cache hierarchy.
 *
 * Team Members: Sumit Kumar(22CS30056) and Aviral Singh(22CS30015)
 * Assignment 1 - Cache Hierarchy Optimization
 */

#include <stdio.h>
#include <stdlib.h>

#define N 64  // Matrix size (64x64 = 4096 elements per matrix)

// Global matrices to avoid stack overflow
int A[N][N];
int B[N][N];
int C[N][N];

/*
 * Matrix multiplication: C = A * B
 * Uses standard triple-nested loop (not optimized)
 * This creates realistic cache access patterns
 */
void matrix_multiply(int A[N][N], int B[N][N], int C[N][N]) {
    int i, j, k;

    // Initialize result matrix to zero
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) {
            C[i][j] = 0;
        }
    }

    // Perform matrix multiplication
    // This loop order causes many cache misses on matrix B
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) {
            for (k = 0; k < N; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

int main() {
    int i, j;

    printf("Matrix Multiplication Benchmark\n");
    printf("Matrix size: %d x %d\n", N, N);
    printf("Total elements per matrix: %d\n", N * N);
    printf("Memory per matrix: %d bytes\n", N * N * sizeof(int));
    printf("Total memory: %d bytes\n", 3 * N * N * sizeof(int));
    printf("========================================\n");

    // Initialize matrix A with sequential values
    printf("Initializing matrices...\n");
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) {
            A[i][j] = i * N + j;
            B[i][j] = (i + j) % 100;  // Some variety in values
        }
    }

    // Perform matrix multiplication
    printf("Starting matrix multiplication...\n");
    matrix_multiply(A, B, C);
    printf("Matrix multiplication complete!\n");

    // Print checksum to verify correctness
    // (prevents compiler from optimizing away the computation)
    long long checksum = 0;
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) {
            checksum += C[i][j];
        }
    }

    printf("========================================\n");
    printf("Checksum: %lld\n", checksum);
    printf("Sample results:\n");
    printf("  C[0][0] = %d\n", C[0][0]);
    printf("  C[%d][%d] = %d\n", N/2, N/2, C[N/2][N/2]);
    printf("  C[%d][%d] = %d\n", N-1, N-1, C[N-1][N-1]);
    printf("========================================\n");
    printf("Benchmark complete!\n");

    return 0;
}
