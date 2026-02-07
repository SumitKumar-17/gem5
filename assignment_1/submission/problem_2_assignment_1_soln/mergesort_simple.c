#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define FILENAME "random_numbers.bin"

// Merge function for merge sort
void merge(int arr[], int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    
    int *L = (int *)malloc(n1 * sizeof(int));
    int *R = (int *)malloc(n2 * sizeof(int));
    
    for (int i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];
    
    int i = 0, j = 0, k = left;
    
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }
    
    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }
    
    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
    
    free(L);
    free(R);
}

// Merge sort function
void mergeSort(int arr[], int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        
        merge(arr, left, mid, right);
    }
}

int main() {
    FILE *file;
    long fileSize;
    int *data;
    int count;
    
    printf("Simple Merge Sort - Starting\n");
    
    // Open binary file
    file = fopen(FILENAME, "rb");
    if (file == NULL) {
        printf("Error: Cannot open file %s\n", FILENAME);
        return 1;
    }
    
    // Get file size
    fseek(file, 0, SEEK_END);
    fileSize = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    count = fileSize / sizeof(int);
    printf("File size: %ld bytes\n", fileSize);
    printf("Number of integers: %d\n", count);
    
    // Allocate memory for all data
    data = (int *)malloc(fileSize);
    if (data == NULL) {
        printf("Error: Memory allocation failed\n");
        fclose(file);
        return 1;
    }
    
    // Read entire file into memory
    size_t readCount = fread(data, sizeof(int), count, file);
    if (readCount != count) {
        printf("Error: Failed to read all data\n");
        free(data);
        fclose(file);
        return 1;
    }
    fclose(file);
    
    printf("Data loaded into memory\n");
    printf("First 5 values before sort: %d %d %d %d %d\n", 
           data[0], data[1], data[2], data[3], data[4]);
    
    // Perform merge sort on entire array
    printf("Starting merge sort...\n");
    mergeSort(data, 0, count - 1);
    printf("Merge sort completed\n");
    
    printf("First 5 values after sort: %d %d %d %d %d\n", 
           data[0], data[1], data[2], data[3], data[4]);
    
    // Cleanup
    free(data);
    printf("Simple Merge Sort - Completed\n");
    
    return 0;
}
