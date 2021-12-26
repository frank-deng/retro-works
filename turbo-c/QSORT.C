#include <stdio.h>
#include <malloc.h>
#include <string.h>

typedef struct{
	size_t length;
	size_t size;
	size_t itemSize;
	void *data;
}arr_t;
int arr_init(arr_t *arr, size_t itemSize, size_t size){
	arr->length=0;
	arr->size=size;
	arr->itemSize=itemSize;
	arr->data=(void*)malloc(itemSize*size);
	return arr->data ? 1 : 0;
}
void arr_close(arr_t *arr){
	if (arr->data != NULL) {
		free(arr->data);
		arr->data=NULL;
	}
	arr->length=arr->size=arr->itemSize=0;
}
int arr_expand(arr_t *arr){
	size_t sizeNew;
	void* dataNew;
	if(arr->length < arr->size){
		return 1;
	}
	sizeNew=arr->size+((arr->size)>>1);
	dataNew=(void*)realloc(arr->data,(arr->itemSize)*sizeNew);
	if(!dataNew){
		return 0;
	}
	arr->data=dataNew;
	arr->size=sizeNew;
	return 2;
}

typedef long item_t;
int arr_push(arr_t *arr, item_t item){
	if(!arr_expand(arr)){
		return 0;
	}
	((item_t*)(arr->data))[arr->length] = item;
	arr->length++;
	return 1;
}

typedef struct {
	item_t *start;
	size_t length;
} queue_item_t;
typedef struct {
	size_t size;
	unsigned long front;
	unsigned long rear;
	queue_item_t *data;
} queue_t;
int queueInit(queue_t *queue, size_t size){
	queue->front = queue->rear = 0;
	queue->size = size;
	queue->data = NULL;
	if(size <= 0) {
		return 0;
	}
	queue->data = (queue_item_t*)malloc(sizeof(queue_item_t) * size);
	return (queue->data == NULL);
}
void queueClose(queue_t *queue){
	if(queue->data == NULL){
		return;
	}
	free(queue->data);
	queue->front = queue->rear = queue->size = 0;
	queue->data = NULL;
}
int queueIn(queue_t *queue, queue_item_t *item){
	queue_item_t *target = NULL;
	if (queue->rear - queue->front >= queue->size) {
		return 0;
	}
	target = queue->data + (queue->rear % queue->size);
	target->start = item->start;
	target->length = item->length;
	queue->rear++;
	return 1;
}
int queueOut(queue_t *queue, queue_item_t *target){
	queue_item_t *item = NULL;
	if (queue->rear == queue->front) {
		return 0;
	}
	item = queue->data + (queue->front % queue->size);
	target->start = item->start;
	target->length = item->length;
	queue->front++;
	return 1;
}

#define _le(a, b) ((a) <= (b))
#define _gt(a, b) ((a) > (b))
void __insertSort(item_t *arr, size_t size)
{
	size_t i, j;
	for (i = 0; i < size; i++) {
		for (j = i; j > 0 && _gt(arr[j - 1], arr[j]); j--) {
			item_t temp = arr[j];
			arr[j] = arr[j - 1];
			arr[j - 1] = temp;
		}
	}
}
void _qsort(item_t *arr0, size_t length)
{
	queue_t queue;
	queue_item_t queueItem;

	queueItem.start = arr0;
	queueItem.length = length;
	queueInit(&queue, length + 1);
	queueIn(&queue, &queueItem);
	while(queueOut(&queue, &queueItem)){
		item_t *arr = queueItem.start, *left, *right;
		item_t a, b, c, temp, pivotVal;
		size_t size = queueItem.length, midIdx;

		if (size <= 8) {
			__insertSort(arr, size);
			continue;
		}

		midIdx = (size >> 1);
		a = *arr, c = arr[size-1], b = arr[midIdx];
		temp = *arr;
		if ((_le(a,b) && _le(b,c)) || (_le(c,b) && _le(b,a))){
			*arr = arr[midIdx];
			arr[midIdx] = temp;
		} else if ((_le(a,c) && _le(c,b)) || (_le(b,c) && _le(c,a))) {
			*arr = arr[size-1];
			arr[size-1] = temp;
		}

		pivotVal = *arr;
		left = arr;
		right = arr + size - 1;
		while (left < right) {
			while (left < right && _le(*left, pivotVal)) {
				left++;
			}
			while (right > arr && _le(pivotVal, *right)) {
				right--;
			}
			if (left < right) {
				item_t temp = *left;
				*left = *right;
				*right = temp;
			}
		}
		*arr = *right;
		*right = pivotVal;

		queueItem.start = arr;
		queueItem.length = right - arr;
		queueIn(&queue, &queueItem);
		queueItem.start = right + 1;
		queueItem.length = size - (right - arr)  - 1;
		queueIn(&queue, &queueItem);
	}
	queueClose(&queue);
}
int main(size_t argc, char *argv[]){
	arr_t arr;
	size_t i;
	item_t input, *arrData;
	int reverse = 0;

	if (argc > 1 && strcmp(argv[1], "/r") == 0) {
		reverse = 1;
	}

	arr_init(&arr,sizeof(item_t),128);
	while(EOF!=scanf("%ld",&input)){
		arr_push(&arr, input);
	}
	arrData=(item_t*)(arr.data);
	_qsort(arrData, arr.length);
	if (reverse) {
		for(i=arr.length; i>0; i--){
			printf("%ld\n",arrData[i-1]);
		}
	} else {
		for(i=0; i<arr.length; i++){
			printf("%ld\n",arrData[i]);
		}
	}
	arr_close(&arr);
	return 0;
}
