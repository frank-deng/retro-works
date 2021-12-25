#include <stdio.h>
#include <malloc.h>

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
	if (heap->data != NULL) {
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
	unsigned long start;
	unsigned long end;
	queue_item_t *data;
} queue_t;
int queueInit(qsortQueue_t *queue, size_t size){
    queue->front = queue->rear = 0;
    queue->size = size;
    queue->data = NULL;
    if(size <= 0) {
        return 0;
    }
    queue->data = (qsortQueueItem_t*)malloc(sizeof(qsortQueueItem_t) * size);
    return (queue->data == NULL);
}
void queueClose(qsortQueue_t *queue){
    if(queue->data == NULL){
        return;
    }
    free(queue->data);
    queue->front = queue->rear = queue->size = 0;
    queue->data = NULL;
}
int queueIn(qsortQueue_t *queue, qsortQueueItem_t *item){
    if (queue->rear - queue->front >= queue->size) {
        return 0;
    }
    qsortQueueItem_t *target = queue->data + (queue->rear % queue->size);
    target->start = item->start;
    target->length = item->length;
    queue->rear++;
    return 1;
}
int queueOut(qsortQueue_t *queue, qsortQueueItem_t *target){
    if (queue->rear == queue->front) {
        return 0;
    }
    qsortQueueItem_t *item = queue->data + (queue->front % queue->size);
    target->start = item->start;
    target->length = item->length;
    queue->front++;
    return 1;
}

#define __compare(a, b) ((a) - (b))
static void __insertSort(item_t *arr, size_t size)
{
    for (size_t i = 0; i < size; i++) {
        for (size_t j = i; j > 0 && __compare(arr[j - 1], arr[j]) > 0; j--) {
            int temp = arr[j];
            arr[j] = arr[j - 1];
            arr[j - 1] = temp;
        }
    }
}
void _qsort(item_t *arr0, size_t length)
{
    qsortQueue_t queue;
    qsortQueueItem_t queueItem = {
        arr0,
        length
    };
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
		if ((__compare(a,b) <= 0 && __compare(b,c) <= 0) || (__compare(c,b) <= 0 && __compare(b,a) <= 0)){
			*arr = arr[midIdx];
			arr[midIdx] = temp;
		} else if ((__compare(a,c) <= 0 && __compare(c,b) <= 0) || (__compare(b,c) <= 0 && __compare(c,a) <= 0)) {
			*arr = arr[size-1];
			arr[size-1] = temp;
		}

        pivotVal = *arr;
        *left = arr;
        *right = arr + size - 1;
        while (left < right) {
            while (left < right && __compare(*left, pivotVal) <= 0) {
                left++;
            }
            while (right > arr && __compare(pivotVal, *right) <= 0) {
                right--;
            }
            if (left < right) {
                int temp = *left;
                *left = *right;
                *right = temp;
            }
        }
        *arr = *right;
        *right = pivotVal;

        queueItem.start = arr;
        queueItem.length = right - arr;
        __queueIn(&queue, &queueItem);
        queueItem.start = right + 1;
        queueItem.length = size - (right - arr)  - 1;
        __queueIn(&queue, &queueItem);
    }
    __queueClose(&queue);
}
int main(){
	arr_t arr;
	size_t i;
	item_t input, *arrData;

	arr_init(&arr,sizeof(item_t),128);
	while(EOF!=scanf("%d",&input)){
		arr_push(&arr,&input);
	}
	arrData=(item_t*)(arr.data);
	_qsort(arrData, arr.length);
	for(i=0; i<arr.length; i++){
		printf("%d\n",arrData[i]);
	}
	arr_close(&arr);
	return 0;
}
