#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <malloc.h>

typedef long num_t;

void _qsort(num_t arr[], int left, int right) {
	int sorted = 1, i, j;
	num_t key;

	/* No need to continue sort */
	if (left >= right) {
		return;
	}

	/*Check if the sequence is sorted */
	for (i = left; i <= right; i++) {
		if (arr[i] > arr[i+1]) {
			sorted = 0;
			break;
		}
	}
	if (sorted) {
		return;
	}

	/* Quick sort current sequence */
	i = left; j = right; key = arr[left];	
	while (i < j) {
		while (i < j && key <= arr[j]) {
			j--;
		}
		arr[i] = arr[j];
		while (i < j && key >= arr[i]) {
			i++;
		}
		arr[j] = arr[i];
	}
	arr[i] = key;

	/* Sort each subsequences */
	_qsort(arr, left, i-1);
	_qsort(arr, i+1, right);
}
void myqsort(num_t arr[], int length) {
	_qsort(arr, 0, length - 1);
}
void bubblesort(num_t arr[], int length) {
	int i, j; num_t temp;
	for (i = length - 1; i >= 1; i--) {
		for (j = 0; j < i; j++) {
			if (arr[j] > arr[j+1]) {
				temp = arr[j]; arr[j] = arr[j+1]; arr[j+1] = temp;
			}
		}
	}
}
int mybsearch(num_t arr[], int length, num_t target) {
	int low = 0, high = length - 1;
	unsigned int mid;
	while (low <= high) {
		/* mid = low + (high - low) / 2; */
		mid = low + ((high - low) >> 1);
		if (arr[mid] == target) {
			return mid;
		} else if (arr[mid] < target) {
			low = mid + 1;
		} else {
			high = mid - 1;
		}
	}
	return -1;
}
int normalsearch(num_t arr[], int length, num_t target) {
	int i;
	for (i = 0; i < length; i++) {
		if (target == arr[i]) {
			return i;
		}
	}
	return -1;
}

void gennum(num_t arr[], num_t arr2[], int length){
	int i;
	for (i = 0; i < length; i++) {
		arr[i] = arr2[i] = (rand() << 16) | rand();
	}
}
void reversenum(num_t arr[], num_t arr2[], int length) {
	num_t temp;
	int i, j, times = 2;

	for (i = 0; i < length / 2; i++) {
		j = length - 1 - i;
		temp = arr[i]; arr[i] = arr[j]; arr[j] = temp;
		temp = arr2[i]; arr2[i] = arr2[j]; arr2[j] = temp;
	}

	while (times--) {
		i = j = 0;
		while (i == j) {
			i = rand() % (length - 1);
			j = rand() % (length - 1);
		}
		temp = arr[i]; arr[i] = arr[j]; arr[j] = temp;
		temp = arr2[i]; arr2[i] = arr2[j]; arr2[j] = temp;
	}
}
int verifysort(num_t *arr, num_t *arr2, int length) {
	int i;
	for (i = 0; i < length - 1; i++) {
		if (arr[i] > arr[i+1]) {
			printf("配列1のソートに失敗しました。\n");
			return 0;
		} else if (arr2[i] > arr2[i+1]) {
			printf("配列2のソートに失敗しました。\n");
			return 0;
		}
	}
	for (i = 0; i < length; i++) {
		if (arr[i] != arr2[i]) {
			printf("配列1と配列2の数が不一致です。\n");
			return 0;
		}
	}
	return 1;
}

#define LENGTH 6666
int main(){
	num_t *data, *data2, search_num;
	int length = LENGTH, i;
	int search_failed = 0, search_result;
	time_t timestamp;

	/* Allocate memory needed */
	data = malloc(length * sizeof(num_t));
	data2 = malloc(length * sizeof(num_t));
	if (NULL == data) {
		puts("dataのmalloc()に失敗しました。");
		return 1;
	}
	if (NULL == data2) {
		puts("data2のmalloc()に失敗しました。");
		return 1;
	}

	puts("*** クイックソートや二分探索のデモ ***\n");
	srand(time(NULL));
	gennum(data, data2, length);

	/* Quicksort demo */
	printf("クイックソートの実行時間：");
	timestamp = time(0);
	myqsort(data, length);
	printf("%lu秒\n", time(0) - timestamp);

	printf("バブルソートの実行時間：");
	timestamp = time(0);
	bubblesort(data2, length);
	printf("%lu秒\n", time(0) - timestamp);

	puts("");
	if (!verifysort(data, data2, length)) {
		goto error;
	}

	/* Binary Search demo */
	printf("二分探索の実行時間：");
	timestamp = time(0);
	for (i = 0; i < length; i++) {
		search_result = mybsearch(data, length, data2[i]);
		if (i != search_result) {
			search_failed = 1;
			printf("二分探索に失敗しました。\n");
		}
	}
	printf("%lu秒\n", time(0) - timestamp);

	printf("通常の検索方法の実行時間：");
	timestamp = time(0);
	for (i = 0; i < length; i++) {
		search_result = normalsearch(data, length, data2[i]);
		if (i != search_result) {
			search_failed = 1;
			printf("通常の検索方法に失敗しました。\n");
		}
	}
	printf("%lu秒\n", time(0) - timestamp);

	puts("");

	/* Quicksort demo with worst case */
	/*
	reversenum(data, data2, length);

	printf("バブルソートの最悪実行時間：");
	timestamp = time(0);
	bubblesort(data2, length);
	printf("%lu秒\n", time(0) - timestamp);

	printf("クイックソートの最悪実行時間：");
	timestamp = time(0);
	myqsort(data, length);
	printf("%lu秒\n", time(0) - timestamp);

	puts("");
	if (!verifysort(data, data2, length)) {
		goto error;
	}
	*/

	/* Free memory needed */
	free(data);
	free(data2);
	return 0;

error:
	free(data);
	free(data2);
	return 1;
}

