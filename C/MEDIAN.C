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
int heap_init(heap_t* heap,	heap_type_t type, size_t itemSize, size_t size){
	heap->type=type;
	heap->length=0;
	heap->size=size;
	heap->itemSize=itemSize;
	heap->data=(void*)malloc(itemSize*size);
	return heap->data ? 1 : 0;
}
void heap_close(heap_t *heap){
	free(heap->data);
	heap->length=heap->size=heap->itemSize=0;
	heap->data=NULL;
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
	item_t *heapData, temp;

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
		__swap(item_t, heapData, pos, parentPos);
		pos=parentPos;
	}
	return 1;
}
int heap_top(heap_t *heap, item_t *value){
	if (!heap->length) {
		return 0;
	}
	*value = ((item_t*)(heap->data))[0];
	return 1;
}
int heap_pop(heap_t *heap, item_t *valueOut){
	item_t *arrData=(item_t*)(heap->data),
		value, leftVal, rightVal, temp;
	size_t pos=0, length, leftPos, rightPos;
	if(!(heap->length)){
		return 0;
	}
	*valueOut = arrData[0];
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
				__swap(item_t, arrData, pos, leftPos);
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
			__swap(item_t, arrData, pos, leftPos);
			pos=leftPos;
		}else{
			__swap(item_t, arrData, pos, rightPos);
			pos=rightPos;
		}
	}
	return 1;
}
int main(){
	heap_t heapL, heapR;
	item_t input, topL, topR, val;
	heap_init(&heapL, MAX_HEAP, sizeof(item_t), 128);
	heap_init(&heapR, MIN_HEAP, sizeof(item_t), 128);
	while(EOF!=scanf("%ld", &input)){
		if(!heapL.length && !heapR.length){
			heap_push(&heapL, input);
			continue;
		}
		heap_top(&heapL, &topL);
		if(!heapR.length){
			if(input>=topL){
				heap_push(&heapR, input);
			}else{
				heap_pop(&heapL, &val);
				heap_push(&heapR, val);
				heap_push(&heapL, input);
			}
			continue;
		}
		heap_top(&heapR, &topR);
		if(input<=topL){
			heap_push(&heapL,input);
			if((heapL.length-heapR.length) > 1){
				heap_pop(&heapL, &val);
				heap_push(&heapR, val);
			}
		}else if(input>=topR){
			heap_push(&heapR,input);
			if(heapR.length!=heapL.length){
				heap_pop(&heapR, &val);
				heap_push(&heapL, val);
			}
		}else if(heapL.length != heapR.length){
			heap_push(&heapR,input);
		}else{
			heap_push(&heapL,input);
		}
	}

	if (heapL.length) {
		heap_top(&heapL, &topL);
		if(heapL.length==heapR.length){
			heap_top(&heapR, &topR);
			printf("%ld %ld\n", topL, topR);
		}else{
			printf("%ld\n", topL);
		}
	}
	heap_close(&heapL);
	heap_close(&heapR);
	return 0;
}
