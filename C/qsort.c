#include <stdio.h>
#include <stdlib.h>
#include <time.h>

void gennum(long *arr, long *arr2, int length){
	int i;
	for (i = 0; i < length; i++) {
		arr[i] = arr2[i] = ((long)rand() << 16) | rand();
	}
}
void _qsort(long *arr, int left, int right) {
	int sorted = 1, i, j;
	long key;

	//No need to continue sort
	if (left >= right) {
		return;
	}

	//Check if the sequence is sorted
	for (i = left; i < right; i++) {
		if (arr[i] > arr[i+1]) {
			sorted = 0;
			break;
		}
	}
	if (sorted) {
		return;
	}

	//Quick sort current sequence
	i = left; j = right; key = arr[left];	
	while (i < j) {
		while (i < j && key <= arr[j]) {
			j--;
		}
		arr[i] = arr[j];
		while (i < j && key >= arr[j]) {
			i++;
		}
		arr[j] = arr[i];
	}
	arr[i] = key;

	//Sort each subsequences
	_qsort(arr, left, i-1);
	_qsort(arr, i+1, right);
}
void myqsort(long *arr, int length) {
	_qsort(arr, 0, length - 1);
}
void bubblesort(long *arr, int length) {
	int i, j; long temp;
	for (i = length - 1; i >= 1; i--) {
		for (j = 0; j < i - 1; j++) {
			temp = arr[j]; arr[j] = arr[j+1]; arr[j+1] = temp;
		}
	}
}
int verifysort(long *arr, long *arr2, int length) {
	int i, pass = 1;;
	for (i = 0; i < length; i++) {
		printf("%ld\t%ld\n", arr[i], arr2[i]);
		/*
		if (i < length - 1) {
			if (arr[i] > arr[i+1]) {
				printf("Error: %ld, %ld, %d", arr[i], arr[i+1], i);
				return 0;
			}
			if (arr2[i] > arr2[i+1]) {
				puts("Error 2");
				return 0;
			}
		}
		if (arr[i] != arr2[i]) {
			printf("Error 3, %d", i);
			return 0;
		}
		*/
	}
	return 1;
}
#define LENGTH 16
int main(){
	long data[LENGTH], data2[LENGTH];
	int length = LENGTH;
	time_t time_qsort, time_bsort;

	puts("クイックソートや二分探索のデモ");

	srand(time(NULL));
	gennum(data, data2, length);
	verifysort(data, data2, length);
	puts("");

	time_qsort = time(0);
	myqsort(data, length);
	time_qsort = time(0) - time_qsort;

	time_bsort = time(0);
	bubblesort(data2, length);
	time_bsort = time(0) - time_bsort;

	verifysort(data, data2, length);
	printf("クイックソートの実行時間：%lu秒\n", time_qsort);
	printf("バブルソートの実行時間：%lu秒\n", time_bsort);
}

