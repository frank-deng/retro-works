#include <stdio.h>
#include <malloc.h>

typedef unsigned char u8_t;
typedef unsigned int uint;
typedef u8_t(*callback_t)(uint*, uint, void*);

void combination(uint n, uint r, callback_t cb, void *data)
{
	uint *arr = NULL, i, j, newVal;
	arr = (uint*)malloc(sizeof(uint) * r);
	if (arr == NULL) {
		return;
	}
	for (i = 0; i < r; i++) {
		arr[i] = i;
	}
	while (arr[0] < (n - r + 1)) {
		if (!(*cb)(arr, r, data)) {
			break;
		}
		for (i = r; i > 0; i--) {
			arr[i - 1]++;
			if (arr[i - 1] >= (n - r + i)) {
				continue;
			}
			if (i >= r) {
				break;
			}
			newVal = arr[i - 1];
			for (j = i; j < r; j++) {
				newVal++;
				arr[j] = newVal;
			}
			break;
		}
	}
	free(arr);
}
u8_t __callback(uint *arr, uint length, void *data)
{
	char **str = (char**)data;
	uint i;
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
	uint n, r;
	if (argc < 3) {
		fputs("Usage: comb.exe r n0 [n1] [n2] ...", stderr);
		return 1;
	}
	n = argc - 2;
	r = strtoul(argv[1], NULL, 0);
	if (r <= 0) {
		fprintf(stderr, "r must be greater than 0.\n", n);
		return 1;
	} else if (r > n) {
		fprintf(stderr, "r must be lower or equal to %u.\n", n);
		return 1;
	}
	combination(n, r, __callback, argv + 2);
	return 0;
}
