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
int main(){
	arr_t arr;
	size_t i;
	item_t input, *arrData;

	arr_init(&arr,sizeof(item_t),8);
	while(EOF!=scanf("%d",&input)){
		arr_push(&arr,&input);
	}
	arrData=(item_t*)(arr.data);
	for(i=0; i<arr.length; i++){
		printf("%d\n",arrData[i]);
	}
	arr_close(&arr);
	return 0;
}

