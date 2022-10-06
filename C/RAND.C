#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define RAND_N 624
#define RANDOM_MAX (0xffffffff)

typedef unsigned long uint32_t;
typedef unsigned short uint16_t;

typedef struct {
		uint32_t mt[RAND_N];
		uint16_t index;
} rand_t;

#define N RAND_N
#define M 397
#define R 31
#define A 0x9908B0DF
#define F 1812433253
#define U 11
#define S 7
#define B 0x9D2C5680
#define T 15
#define C 0xEFC60000
#define L 18
#define MASK_LOWER ((1ul << R) - 1)
#define MASK_UPPER (1ul << R)

void initRandom(rand_t* rand, uint32_t seed)
{
		uint16_t i;
		rand->mt[0] = seed;
		for (i = 1; i < N; i++) {
				rand->mt[i] = (F * (rand->mt[i - 1] ^ (rand->mt[i - 1] >> 30)) + i);
		}
		rand->index = N;
}
static void twist(rand_t* rand)
{
		uint32_t  i, x, xA;
		for (i = 0; i < N; i++) {
				x = (rand->mt[i] & MASK_UPPER) + (rand->mt[(i + 1) % N] & MASK_LOWER);
				xA = x >> 1;
				if (x & 0x1) {
						xA ^= A;
				}
				rand->mt[i] = rand->mt[(i + M) % N] ^ xA;
		}
		rand->index = 0;
}
uint32_t getRandom(rand_t* rand)
{
		uint32_t y;
		uint16_t i = rand->index;
		if (rand->index >= N) {
				twist(rand);
				i = rand->index;
		}
		y = rand->mt[i];
		rand->index = i + 1;
		y ^= (y >> U);
		y ^= (y << S) & B;
		y ^= (y << T) & C;
		y ^= (y >> L);
		return y;
}

int main(int argc, char *argv[])
{
	unsigned long count = 0;
	long min = 0, max = 0x7fffffff;
		rand_t randData;

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
		initRandom(&randData, (uint32_t)rand() * (uint32_t)rand());
	while(count--){
		long result = getRandom(&randData) & 0x7fffffff;
		result = (result % (max - min)) + min;
		printf("%ld\n", result);
	}
	return 0;
}

