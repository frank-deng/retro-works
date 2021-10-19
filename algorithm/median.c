#include <stdio.h>
#include <malloc.h>

typedef struct __arr_t{
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
	free(arr->data);
	arr->length=arr->size=arr->itemSize=0;
}
int arr_expand(arr_t *arr){
	size_t sizeNew=arr->size+((arr->size)>>1);
	void *dataNew=(void*)realloc(arr->data,(arr->itemSize)*sizeNew);
	if(!dataNew){
		return 0;
	}
	arr->data=dataNew;
	arr->size=sizeNew;
	return 1;
}

typedef int item_t;
int arr_push(arr_t *arr, item_t *item){
	if(arr->length >= arr->size){
		if(!arr_expand(arr)){
			return 0;
		}
	}
	((item_t*)(arr->data))[arr->length]=*item;
	arr->length++;
	return 1;
}
int minHeap_push(arr_t *arr, item_t *value){
	size_t pos=arr->length, parentPos;
	item_t *arrData, temp;
	if(!arr_push(arr,value)){
		return 0;
	}
	arrData=(item_t*)(arr->data);
	while(pos){
		parentPos=(pos-1)>>1;
		if(arrData[parentPos]<=arrData[pos]){
			break;
		}
		temp=arrData[parentPos];
		arrData[parentPos]=arrData[pos];
		arrData[pos]=temp;
		pos=parentPos;
	}
	return 1;
}
int maxHeap_push(arr_t *arr, item_t *value){
	size_t pos=arr->length, parentPos;
	item_t *arrData, temp;
	if(!arr_push(arr,value)){
		return 0;
	}
	arrData=(item_t*)(arr->data);
	while(pos){
		parentPos=(pos-1)>>1;
		if(arrData[parentPos]>=arrData[pos]){
			break;
		}
		temp=arrData[parentPos];
		arrData[parentPos]=arrData[pos];
		arrData[pos]=temp;
		pos=parentPos;
	}
	return 1;
}
item_t minHeap_pop(arr_t *arr){
	item_t *arrData=(item_t*)(arr->data), value, leftVal, rightVal, temp;
	size_t pos=0, length, leftPos, rightPos;
	if(!arr->length){
		return 0;
	}
	value=arrData[0];
	arrData[0]=arrData[arr->length - 1];
	(arr->length)--;
	if(!(arr->length)){
		return value;
	}
	length=arr->length;
	while(pos<length){
		value=arrData[pos]; leftPos=(pos<<1)+1; rightPos=(pos<<1)+2;
		if(rightPos>=length && leftPos>=length){
			break;
		}
		if(rightPos>=length && leftPos<length){
			if(arrData[leftPos]<value){
				temp=arrData[leftPos];
				arrData[leftPos]=arrData[pos];
				arrData[pos]=temp;
			}
			break;
		}
		leftVal=arrData[leftPos]; rightVal=arrData[rightPos];
		if(value<=leftVal && value<=rightVal){
			break;
		}
		if(leftVal<=rightVal){
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
	return value;
}
item_t maxHeap_pop(arr_t *arr){
	item_t *arrData=(item_t*)(arr->data), value, leftVal, rightVal, temp;
	size_t pos=0, length, leftPos, rightPos;
	if(!(arr->length)){
		return 0;
	}
	value=arrData[0];
	arrData[0]=arrData[arr->length - 1];
	(arr->length)--;
	if(!(arr->length)){
		return value;
	}
	length=arr->length;
	while(pos<length){
		value=arrData[pos]; leftPos=(pos<<1)+1; rightPos=(pos<<1)+2;
		if(rightPos>=length && leftPos>=length){
			break;
		}
		if(rightPos>=length && leftPos<length){
			if(arrData[leftPos]>value){
				temp=arrData[leftPos];
				arrData[leftPos]=arrData[pos];
				arrData[pos]=temp;
			}
			break;
		}
		leftVal=arrData[leftPos];
		rightVal=arrData[rightPos];
		if(value>=leftVal && value>=rightVal){
			break;
		}
		if(leftVal>=rightVal){
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
	return value;
}
int main(){
	arr_t minHeap, maxHeap;
	item_t input,temp,minHeapTop,maxHeapTop;
	arr_init(&minHeap,sizeof(item_t),100);
	arr_init(&maxHeap,sizeof(item_t),100);

	while(EOF!=scanf("%d",&input)){
		if(minHeap.length==maxHeap.length){
			maxHeap_push(&maxHeap,&input);
		}else{
			minHeap_push(&minHeap,&input);
		}
		if(!minHeap.length){
			continue;
		}
		minHeapTop=((item_t*)(minHeap.data))[0];
		maxHeapTop=((item_t*)(maxHeap.data))[0];
		while(minHeapTop<maxHeapTop){
			temp=minHeap_pop(&minHeap);
			maxHeap_push(&maxHeap,&temp);
			temp=maxHeap_pop(&maxHeap);
			minHeap_push(&minHeap,&temp);
		}
	}

	maxHeapTop=((item_t*)(maxHeap.data))[0];
	if(minHeap.length!=maxHeap.length){
		printf("%d\n",maxHeapTop);
	}else{
		minHeapTop=((item_t*)(minHeap.data))[0];
		printf("%d %d\n",maxHeapTop,minHeapTop);
	}

	arr_close(&minHeap);
	arr_close(&maxHeap);
	return 0;
}