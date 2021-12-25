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
	size_t start;
	size_t end;
	queue_item_t *data;
} queue_t;

static void __bubbleSort(item_t *arr, size_t start, size_t end){
	size_t i,j; item_t temp;
	for(i=start;i<end-1;i++){
		for(j=i+1;j<end;j++){
			if(arr[i]>arr[j]){
				temp=arr[i];
				arr[i]=arr[j];
				arr[j]=temp;
			}
		}
	}
}
static void __qsort(item_t *arr, size_t start, size_t end){
	size_t left, right;
	item_t pivotVal, temp;
	if((end-start)<5){
		__bubbleSort(arr,start,end);
		return;
	}
	pivotVal=arr[start];
	left=start+1;
	right=end-1;
	while(left<right){
		while(left<end-1 && arr[left]<=pivotVal){
			left++;
		}
		while(right>start && arr[right]>=pivotVal){
			right--;
		}
		if(left>=right){
			break;
		}
		temp=arr[left]; arr[left]=arr[right]; arr[right]=temp;
	}
	if(right>start){
		arr[start]=arr[right]; arr[right]=pivotVal;
		__qsort(arr,start,right);
	}
	if(right<(end-1)){
		__qsort(arr,right+1,end);
	}
}
void qsort(item_t *arr, size_t length){
	__qsort(arr,0,length);
}
int main(){
	arr_t arr;
	unsigned long i;
	item_t input, *arrData;

	arr_init(&arr,sizeof(item_t),128);
	while(EOF!=scanf("%d",&input)){
		arr_push(&arr,&input);
	}
	arrData=(item_t*)(arr.data);
	qsort(arrData,arr.length);
	for(i=0; i<arr.length; i++){
		printf("%d\n",arrData[i]);
	}
	arr_close(&arr);
	return 0;
}
