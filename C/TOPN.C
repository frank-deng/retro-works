#include <stdio.h>
#include <malloc.h>

typedef enum{
	MIN_HEAP,
	MAX_HEAP
}heap_type_t;
typedef struct{
	heap_type_t type;
	size_t length;
	size_t itemSize;
	size_t size;
	void* data;
}heap_t;
int heap_init(heap_t* heap,	heap_type_t type, size_t itemSize, size_t size)
{
	heap->type=type;
	heap->length=0;
	heap->size=size;
	heap->itemSize=itemSize;
	heap->data=(void*)malloc(itemSize*size);
	return heap->data ? 1 : 0;
}
void heap_close(heap_t *heap)
{
	if (heap->data != NULL) {
		free(heap->data);
		heap->data=NULL;
	}
	heap->length=heap->size=heap->itemSize=0;
}
#define __swap(type, arr, p0, p1) do{\
	type temp = (arr)[(p0)];\
	(arr)[(p0)] = (arr)[(p1)];\
	(arr)[(p1)] = (temp);\
}while(0)

typedef long item_t;
int heap_push(heap_t *heap, item_t value){
	size_t sizeNew;
	void* dataNew;
	size_t pos=heap->length, parentPos;
	item_t *heapData;

	/* Heap space memory expansion */
	if(heap->length >= heap->size){
		sizeNew=heap->size+((heap->size)>>1);
		dataNew=(void*)realloc(heap->data,(heap->itemSize)*sizeNew);
		if(!dataNew){
			return 0;
		}
		heap->data=dataNew;
		heap->size=sizeNew;
	}

	/* Handle heap push */
	heapData=(item_t*)(heap->data);
	heapData[heap->length]=value;
	heap->length++;
	while(pos){
		parentPos=(pos-1)>>1;
		if((MIN_HEAP==heap->type && heapData[parentPos]<=heapData[pos])
			|| (MAX_HEAP==heap->type && heapData[parentPos]>=heapData[pos])){
			break;
		}
		__swap(item_t, heapData, parentPos, pos);
		pos=parentPos;
	}
	return 1;
}
int heap_pop(heap_t *heap, item_t *item)
{
	item_t *arrData=(item_t*)(heap->data), heapTopOrig,
		value, leftVal, rightVal, temp;
	size_t pos=0, length, leftPos, rightPos;
	if(!(heap->length)){
		return 0;
	}
	*item = arrData[0];
	(heap->length)--;
	if(!(heap->length)){
		return 1;
	}
	arrData[0]=arrData[heap->length];
	length=heap->length;
	while(pos<length){
		value=arrData[pos]; leftPos=(pos<<1)+1; rightPos=(pos<<1)+2;
		if(rightPos>=length){
			if(leftPos>=length){
				break;
			}
			leftVal=arrData[leftPos];
			if((MIN_HEAP==heap->type && leftVal<value)
				||(MAX_HEAP==heap->type && leftVal>value)){
				__swap(item_t, arrData, leftPos, pos);
			}
			break;
		}
		leftVal=arrData[leftPos]; rightVal=arrData[rightPos];
		if((MIN_HEAP==heap->type && value<=leftVal && value<=rightVal)
			||(MAX_HEAP==heap->type && value>=leftVal && value>=rightVal)){
			break;
		}
		if((MIN_HEAP==heap->type && leftVal<=rightVal)
			||(MAX_HEAP==heap->type && leftVal>=rightVal)){
			__swap(item_t, arrData, leftPos, pos);
			pos=leftPos;
		}else{
			__swap(item_t, arrData, rightPos, pos);
			pos=rightPos;
		}
	}
	return 1;
}
void printHelp()
{
	fputs("Usage: topn.exe count\n", stderr);
	fputs("    count parameter in negative value means smallest n numbers.", stderr);
}
int main(int argc, char *argv[])
{
	int maxn=0;
	long inputCount = 0;
	size_t count, resultCount = 0, i;
	heap_t heap;
	item_t heapTop, input, outval, *sorted;

	if (argc <= 1) {
		printHelp();
		return 1;
	}
	inputCount = atol(argv[1]);
	if (inputCount == 0) {
		printHelp();
		return 1;
	}

	if (inputCount < 0) {
		maxn = 0;
		count = -inputCount;
	} else {
		maxn = 1;
		count = inputCount;
	}

	heap_init(&heap, maxn?MIN_HEAP:MAX_HEAP, sizeof(item_t), count+1);
	sorted=(item_t*)malloc(sizeof(item_t)*count);

	while(EOF!=scanf("%ld",&input)){
		if(heap.length<count){
			heap_push(&heap, input);
			continue;
		}
		heapTop=((item_t*)(heap.data))[0];
		if((maxn && input>heapTop) || (!maxn && input<heapTop)){
			heap_push(&heap, input);
			heap_pop(&heap, &outval);
		}
	}
	resultCount = 0;
	while(heap_pop(&heap, &outval)){
		sorted[resultCount]=outval;
		resultCount++;
	}
	if (maxn) {
		for(i = resultCount; i > 0; i--) {
			printf("%ld\n", sorted[i - 1]);
		}
	} else {
		for (i = 0; i < resultCount; i++) {
			printf("%ld\n", sorted[i]);
		}
	}
	free(sorted);
	heap_close(&heap);
	return 0;
}
