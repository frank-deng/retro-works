#include <stdio.h>
#include <malloc.h>

typedef enum __heap_type_t{
	MIN_HEAP,
	MAX_HEAP
}heap_type_t;
typedef struct __heap_t{
	heap_type_t type;
	size_t length;
	size_t itemSize;
	size_t size;
	void* data;
}heap_t;
int heap_init(heap_t* heap,	heap_type_t type,	size_t itemSize, size_t size){
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

typedef int item_t;
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
		temp=heapData[parentPos];
		heapData[parentPos]=heapData[pos];
		heapData[pos]=temp;
		pos=parentPos;
	}
	return 1;
}
item_t heap_pop(heap_t *heap){
	item_t *arrData=(item_t*)(heap->data), heapTopOrig,
		value, leftVal, rightVal, temp;
	size_t pos=0, length, leftPos, rightPos;
	if(!(heap->length)){
		return 0;
	}
	heapTopOrig=arrData[0];
	(heap->length)--;
	if(!(heap->length)){
		return heapTopOrig;
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
				temp=arrData[leftPos];
				arrData[leftPos]=arrData[pos];
				arrData[pos]=temp;
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
			temp=arrData[leftPos];
			arrData[leftPos]=arrData[pos];
			arrData[pos]=temp;
			pos=leftPos;
		}else{
			temp=arrData[rightPos];
			arrData[rightPos]=arrData[pos];
			arrData[pos]=temp;
			pos=rightPos;
		}
	}
	return heapTopOrig;
}
int main(){
	int maxn=0,i;
	size_t count;
	heap_t heap;
	item_t heapTop, input, *sorted;

	scanf("%d%u",&maxn,&count);
	heap_init(&heap, maxn?MIN_HEAP:MAX_HEAP, sizeof(item_t), count+1);
	sorted=(item_t*)malloc(sizeof(item_t)*count);

	while(EOF!=scanf("%d",&input)){
		if(heap.length<count){
			heap_push(&heap, input);
			continue;
		}
		heapTop=((item_t*)(heap.data))[0];
		if((maxn && input>heapTop) || (!maxn && input<heapTop)){
			heap_push(&heap,input);
			heap_pop(&heap);
		}
	}
	i=0;
	while(heap.length){
		sorted[i]=heap_pop(&heap);
		i++;
	}
	while(i--){
		printf("%d\n",sorted[i]);
	}
	free(sorted);
	heap_close(&heap);
	return 0;
}