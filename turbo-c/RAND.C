#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>

int main(int argc, char *argv[])
{
	unsigned long count = 0;
	long min = 0, max = LONG_MAX;
	if (argc < 2) {
		fputs("Usage: rand.exe count [MIN MAX]\n", stderr);
		return 1;
	}
	count = strtoul(argv[1], NULL, 0);
	if (count == 0) {
		fputs("Count must greater than 0.\n", stderr);
		return 1;
	}
	if (argc == 4) {
		min = strtol(argv[2], NULL, 0);
		max = strtol(argv[3], NULL, 0);
		if (min >= max) {
			fputs("MAX must greater than MIN.\n", stderr);
			return 1;
		}
	}

	randomize();
	while(count--){
		long result = rand() * rand() & 0x7fffffff;
		result = (result % (max - min)) + min;
		printf("%ld\n", result);
	}
	return 0;
}
