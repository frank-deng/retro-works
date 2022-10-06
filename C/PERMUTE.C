#include <stdio.h>
#include <string.h>

typedef unsigned char u8_t;
typedef u8_t(*permute_callback_t)(u8_t*, u8_t, void*);
typedef u8_t(*permute_compare_t)(u8_t, u8_t, void*);

#define __swap(type, arr, p0, p1) do{\
	type temp = (arr)[(p0)];\
	(arr)[(p0)] = (arr)[(p1)];\
	(arr)[(p1)] = (temp);\
}while(0)
u8_t __permute(u8_t *arr, u8_t start, u8_t end,
	permute_compare_t compare, permute_callback_t callback, void *data)
{
	u8_t i, ret;
	if (start == end) {
		return (*callback)(arr, end+1, data);
	}
	for (i = start; i <= end; i++) {
		if (i > start &&
				(
					!(*compare)(arr[i], arr[start], data) ||
					!(*compare)(arr[i], arr[i - 1], data)
				)
			){
			continue;
		}
		__swap(u8_t, arr, start, i);
		if (!__permute(arr, start+1, end, compare, callback, data)) {
			return 0;
		}
		__swap(u8_t, arr, start, i);
	}
	return 1;
}
void permute(u8_t size, permute_compare_t compare,
	permute_callback_t callback, void *data)
{
	u8_t arr[255], i;
	for (i = 0; i < size; i++) {
		arr[i] = i;
	}
	__permute(arr, 0, size-1, compare, callback, data);
}
u8_t permuteCompare(u8_t i, u8_t j, void *data)
{
	char **str = (char**)data;
	return strcmp(str[i], str[j]);
}
u8_t permuteHandler(u8_t *arr, u8_t length, void* data)
{
	char **str = (char**)data;
	u8_t i;
	for (i = 0; i < length; i++) {
		if (i) {
			putchar(' ');
		}
		printf("%s", str[arr[i]]);
	}
	putchar('\n');
	return 1;
}
int main(int argc, char *argv[])
{
	if (argc < 2) {
		fputs("Usage: permute.exe n0 [n1] [n2] ...\n", stderr);
		return 1;
	}
	permute(argc - 1,
		permuteCompare,
		permuteHandler,
		argv + 1);
	return 0;
}
