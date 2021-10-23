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
		parentPos=(pos-1)/2;
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
item_t heap_top(heap_t *heap){
	return ((item_t*)(heap->data))[0];
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
void print_data(item_t *src, size_t length){
	size_t i;
	for(i=0; i<length; i++){
		printf("%8d",src[i]);
	}
	putchar('\n');
}
int main(){
	heap_t heapL, heapR;
	item_t input, topL, topR;
	heap_init(&heapL, MAX_HEAP, sizeof(item_t), 128);
	heap_init(&heapR, MIN_HEAP, sizeof(item_t), 128);
	while(EOF!=scanf("%d",&input)){
		if(!heapL.length && !heapR.length){
			heap_push(&heapL,input);
			continue;
		}
		topL=heap_top(&heapL);
		if(!heapR.length){
			if(input>=topL){
				heap_push(&heapR,input);
			}else{
				heap_push(&heapR,heap_pop(&heapL));
				heap_push(&heapL,input);
			}
			continue;
		}
		topR=heap_top(&heapR);
		if(input<=topL){
			heap_push(&heapL,input);
			if((heapL.length-heapR.length) > 1){
				heap_push(&heapR,heap_pop(&heapL));
			}
		}else if(input>=topR){
			heap_push(&heapR,input);
			if(heapR.length!=heapL.length){
				heap_push(&heapL,heap_pop(&heapR));
			}
		}else if(heapL.length != heapR.length){
			heap_push(&heapR,input);
		}else{
			heap_push(&heapL,input);
		}
	}
	if(heapL.length==heapR.length){
		printf("%d %d\n",heap_top(&heapL), heap_top(&heapR));
	}else{
		printf("%d\n",heap_top(&heapL));
	}
	heap_close(&heapL);
	heap_close(&heapR);
	return 0;
}

