#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

#define FILENAME "random_numbers.bin"
#define CHUNK_SIZE (2 * 1024 * 1024)
#define STREAM_SIZE (1 * 1024 * 1024)
#define NUM_CHUNKS 5

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

void mergeSort(int arr[], int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        
        merge(arr, left, mid, right);
    }
}

typedef struct {
    int *buffer;
    int bufferSize;
    int bufferIndex;
    int remainingInts;
    FILE *file;
    int currentValue;
    int exhausted;
} Stream;

void refillStream(Stream *stream) {
    if (stream->remainingInts > 0) {
        int toRead = (stream->remainingInts < (STREAM_SIZE / sizeof(int))) ? 
                     stream->remainingInts : (STREAM_SIZE / sizeof(int));
        stream->bufferSize = fread(stream->buffer, sizeof(int), toRead, stream->file);
        stream->remainingInts -= stream->bufferSize;
        stream->bufferIndex = 0;
        
        if (stream->bufferSize > 0) {
            stream->currentValue = stream->buffer[stream->bufferIndex];
            stream->exhausted = 0;
        } else {
            stream->exhausted = 1;
            stream->currentValue = INT_MAX;
        }
    } else {
        stream->exhausted = 1;
        stream->currentValue = INT_MAX;
    }
}

void advanceStream(Stream *stream) {
    stream->bufferIndex++;
    
    if (stream->bufferIndex >= stream->bufferSize) {
        refillStream(stream);
    } else {
        stream->currentValue = stream->buffer[stream->bufferIndex];
    }
}

void initStream(Stream *stream, FILE *file, int totalInts) {
    stream->buffer = (int *)malloc(STREAM_SIZE);
    stream->bufferSize = 0;
    stream->bufferIndex = 0;
    stream->remainingInts = totalInts;
    stream->file = file;
    stream->exhausted = 0;
    stream->currentValue = INT_MAX;
    refillStream(stream);
}

void cleanupStream(Stream *stream) {
    free(stream->buffer);
}

int main() {
    FILE *file;
    long fileSize;
    int *chunk;
    int totalInts;
    int intsPerChunk = CHUNK_SIZE / sizeof(int);
    int intsPerStream = STREAM_SIZE / sizeof(int);
    
    printf("Chunked Merge Sort - Starting\n");
    
    file = fopen(FILENAME, "rb");
    if (file == NULL) {
        printf("Error: Cannot open file\n");
        return 1;
    }
    
    fseek(file, 0, SEEK_END);
    fileSize = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    totalInts = fileSize / sizeof(int);
    
    printf("File size: %ld bytes\n", fileSize);
    printf("Total integers: %d\n", totalInts);
    printf("Chunk size: %d bytes (%d integers)\n", CHUNK_SIZE, intsPerChunk);
    printf("Number of chunks: %d\n", NUM_CHUNKS);
    printf("Stream size: %d bytes (%d integers)\n", STREAM_SIZE, intsPerStream);
    
    chunk = (int *)malloc(CHUNK_SIZE);
    if (chunk == NULL) {
        printf("Error: Memory allocation failed\n");
        fclose(file);
        return 1;
    }
    
    FILE *tempFiles[NUM_CHUNKS];
    int chunkSizes[NUM_CHUNKS];
    
    printf("\nPhase 1: Sorting 2MB chunks\n");
    
    for (int i = 0; i < NUM_CHUNKS; i++) {
        int intsToRead = intsPerChunk;
        if (i == NUM_CHUNKS - 1) {
            intsToRead = totalInts - (i * intsPerChunk);
        }
        
        size_t readCount = fread(chunk, sizeof(int), intsToRead, file);
        if (readCount != (size_t)intsToRead) {
            printf("Error reading chunk\n");
            break;
        }
        
        printf("Chunk %d: Read %d integers\n", i, intsToRead);
        printf("  Before: %d %d %d\n", chunk[0], chunk[1], chunk[2]);
        
        mergeSort(chunk, 0, intsToRead - 1);
        
        printf("  After: %d %d %d\n", chunk[0], chunk[1], chunk[2]);
        
        char tempFilename[50];
        sprintf(tempFilename, "/tmp/chunk_%d.tmp", i);
        tempFiles[i] = fopen(tempFilename, "w+b");
        if (tempFiles[i] == NULL) {
            printf("Error creating temp file\n");
            return 1;
        }
        
        fwrite(chunk, sizeof(int), intsToRead, tempFiles[i]);
        fseek(tempFiles[i], 0, SEEK_SET);
        chunkSizes[i] = intsToRead;
        
        printf("  Chunk %d sorted and saved\n", i);
    }
    fclose(file);
    free(chunk);
    
    printf("\nPhase 2: 5-way parallel merge with 1MB streams\n");
    
    Stream streams[NUM_CHUNKS];
    for (int i = 0; i < NUM_CHUNKS; i++) {
        initStream(&streams[i], tempFiles[i], chunkSizes[i]);
        printf("Stream %d initialized: first value = %d\n", i, streams[i].currentValue);
    }
    
    int *finalData = (int *)malloc(totalInts * sizeof(int));
    if (finalData == NULL) {
        printf("Error: Cannot allocate final data array\n");
        return 1;
    }
    
    printf("Starting 5-way merge...\n");
    int outputIndex = 0;
    int mergeCount = 0;
    
    while (outputIndex < totalInts) {
        int minValue = INT_MAX;
        int minStreamIdx = -1;
        
        for (int i = 0; i < NUM_CHUNKS; i++) {
            if (!streams[i].exhausted && streams[i].currentValue < minValue) {
                minValue = streams[i].currentValue;
                minStreamIdx = i;
            }
        }
        
        if (minStreamIdx == -1) {
            printf("Error: All streams exhausted\n");
            break;
        }
        
        finalData[outputIndex++] = minValue;
        advanceStream(&streams[minStreamIdx]);
        
        mergeCount++;
        if (mergeCount % 500000 == 0) {
            printf("  Merged %d integers...\n", mergeCount);
        }
    }
    
    printf("5-way merge completed: %d integers merged\n", outputIndex);
    
    printf("\nVerification:\n");
    printf("First 10 values: ");
    for (int i = 0; i < 10; i++) {
        printf("%d ", finalData[i]);
    }
    printf("\n");
    
    printf("Last 10 values: ");
    for (int i = totalInts - 10; i < totalInts; i++) {
        printf("%d ", finalData[i]);
    }
    printf("\n");
    
    int sorted = 1;
    for (int i = 1; i < totalInts; i++) {
        if (finalData[i] < finalData[i-1]) {
            sorted = 0;
            printf("ERROR: Not sorted at position %d\n", i);
            break;
        }
    }
    if (sorted) {
        printf("SUCCESS: Array is properly sorted!\n");
    }
    
    for (int i = 0; i < NUM_CHUNKS; i++) {
        cleanupStream(&streams[i]);
        fclose(tempFiles[i]);
        char tempFilename[50];
        sprintf(tempFilename, "/tmp/chunk_%d.tmp", i);
        remove(tempFilename);
    }
    
    free(finalData);
    
    printf("\nChunked Merge Sort - Completed\n");
    
    return 0;
}
