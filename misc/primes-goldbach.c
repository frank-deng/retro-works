#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <pthread.h>
#include <sys/sysinfo.h>

/* Prime table for prime numbers smaller than 128 */
static const unsigned long prime_table[] =
{
	2,
	3,
	5,
	7,
	11,
	13,
	17,
	19,
	23,
	29,
	31,
	37,
	41,
	43,
	47,
	53,
	59,
	61,
	67,
	71,
	73,
	79,
	83,
	89,
	97,
	101,
	103,
	107,
	109,
	113,
	127,
};

#define PRIME_TABLE_LEN 31
#define PRIME_TABLE_MAX 128

/* Miller-Rabin 32-bit */
static inline uint32_t rand_num(uint32_t range) {
	return (((uint32_t)mrand48()) % range);
}
static inline uint32_t exp_mod(uint32_t a0, uint32_t b, uint32_t n) {
	uint64_t a = a0, result = 1;
	while (b) {
		if (b & 1) {
			result = (result * a) % n;
		}
		a = (a * a) % n;
		b /= 2;
	}
	return result;
}
static inline int miller_rabin_test(uint32_t n, uint8_t times) {
	uint32_t x, pre, u = n - 1, i, k = 0;

	/* Get shifted bits */
	while(!(u & 1)) {
		k++;
		u /= 2;
	}

	while (times--) {
		/* Get random number */
		x = rand_num(n - 2) + 2;

		/* Start calculation */
		pre = x = exp_mod(x, u, n);
		for (i = 0; i < k; i++) {
			x = (uint64_t)x * x % n;
			if ((1 == x) && (pre != 1) && (pre != (n - 1))) {
				return 0;
			} else if (1 == x) {
				break;
			}
			pre = x;
		}
		if (x != 1) {
			return 0;
		}
	}

	return 1;
}

#ifdef __x86_64__
/* Miller-Rabin 64-bit */
static inline uint64_t rand_num_64(uint64_t range) {
	uint64_t rand_hi, rand_md, rand_lo, result;
	rand_hi = lrand48();
	rand_md = lrand48();
	rand_lo = lrand48();
	result = (rand_hi << 42) + (rand_md << 21) + rand_lo;
	return (result % range);
}
static inline uint64_t exp_mod_64(uint64_t a0, uint64_t b, uint64_t n) {
	__uint128_t a = a0, result = 1;
	while (b) {
		if (b & 1) {
			result = (result * a) % n;
		}
		a = (a * a) % n;
		b /= 2;
	}
	return result;
}
static inline int miller_rabin_test_64(uint64_t n, uint8_t times) {
	uint64_t x, pre, u;
	uint8_t i, k = 0;

	/* Get shifted bits */
	u = n - 1;
	while(!(u & 1)) {
		k++;
		u /= 2;
	}

	while (times--) {
		/* Get random number */
		x = rand_num_64(n - 2) + 2;

		/* Start calculation */
		pre = x = exp_mod_64(x, u, n);
		for (i = 0; i < k; i++) {
			x = (__uint128_t)x * x % n;
			if ((1 == x) && (pre != 1) && (pre != (n - 1))) {
				return 0;
			} else if (1 == x) {
				break;
			}
			pre = x;
		}
		if (x != 1) {
			return 0;
		}
	}

	return 1;
}
#endif

/* Integrates the functionality of Trial Division & Miller-Rabin */
int isprime(unsigned long num) {
	uint8_t i;

	/* Deal with 2 and even numbers */
	if (2 == num) {
		return 1;
	} else if (!(num & 1)) {
		return 0;
	}

	/* Query prime table if the number is smaller than PRIME_TABLE_MAX*/
	if (num <= PRIME_TABLE_MAX) {
		size_t start = 0, end = PRIME_TABLE_LEN, mid;
		while (start < end) {
			mid = start + (end - start) / 2;
			if (num < prime_table[mid]) {
				end = mid;
			} else if (num > prime_table[mid]) {
				start = mid + 1;
			} else {
				return 1;
			}
		}
		return 0;
	}

	/* Trial Division */
	for (i = 1; i < PRIME_TABLE_LEN; i++) {
		if (0 == (num % prime_table[i])) {
			return 0;
		} else if (prime_table[i] * prime_table[i] >= num) {
			break;
		}
	}
	
	/* Determine times of Miller-Rabin test */
	if (num < PRIME_TABLE_MAX * PRIME_TABLE_MAX) {
		return 1;
	}

	/* Miller-Rabin test */
#ifdef __x86_64__
	if (num > 0xFFFFFFFFUL) {
		return miller_rabin_test_64(num, 16);
	}
	else
#endif
	{
		return miller_rabin_test(num, 16);
	}
}

typedef struct {
	unsigned long start;
	unsigned long stop;
	char filename[FILENAME_MAX];
} param_t;
void* primes_thread(void *param) {
	unsigned long num = ((param_t*)param)->start, stop = ((param_t*)param)->stop;
	FILE *fp = fopen(((param_t*)param)->filename, "w");

	if (num < 2) {
		num = 2;
	}
	while (num < stop) {
		if (isprime(num)) {
			fprintf(fp, "%lu\n", num);
		}
		num++;
	}
	fclose(fp);
}
void* goldbach_thread(void *param) {
	unsigned long num = ((param_t*)param)->start, stop = ((param_t*)param)->stop;
	unsigned long tn, tn_max;
	int exception;

	//Check the value of start & stop
	if (num < 6) {
		num = 6;
	} else if (num & 1) {
		num++;
	}

	//Start calculation
	while (num < stop) {
		exception = 1;
		tn_max = num / 2;
		for (tn = 3; tn <= tn_max; tn += 2) {
			if (isprime(tn) && isprime(num - tn)) {
				exception = 0;
				break;
			}
		}
		//This should never happen
		if (exception) {
			printf("%lu\n", num);
		}
		num += 2;
	}
}

#define THREAD_MAX 128
void primes_mode(unsigned long start, unsigned long stop) {
	param_t param[THREAD_MAX];
	pthread_t thread_all[THREAD_MAX];
	uint8_t thread_count = get_nprocs(), i;
	unsigned long block = (stop - start) / thread_count;
	char data[24];
	FILE *fp0, *fp;

	//Execute!!!
	for (i = 0; i < thread_count; i++) {
		param[i].start = (i ? stop - block * (thread_count - i) : start);
		param[i].stop = stop - block * (thread_count - i - 1);
		if (i) {
			sprintf(param[i].filename, "primes.txt.%d", i);
		} else {
			strcpy(param[i].filename, "primes.txt");
		}
		pthread_create(thread_all + i, NULL, primes_thread, (void*)(param + i));
	}

	//Wait for the first thread to exit, then open the target file generated by the first thread.
	pthread_join(thread_all[0], NULL);
	fp0 = fopen(param[0].filename, "a");

	//Wait for threads and merge files one by one.
	for (i = 1; i < thread_count; i++) {
		pthread_join(thread_all[i], NULL);
		fp = fopen(param[i].filename, "r");
		while(fgets(data, 23, fp)) {
			fputs(data, fp0);
		}
		fclose(fp);
		remove(param[i].filename);
	}
	fclose(fp0);
}
void goldbach_mode(unsigned long start, unsigned long stop) {
	param_t param[THREAD_MAX];
	pthread_t thread_all[THREAD_MAX];
	uint8_t thread_count = get_nprocs(), i;
	unsigned long block = (stop - start) / thread_count;

	for (i = 0; i < thread_count; i++) {
		param[i].start = (i ? stop - block * (thread_count - i) : start);
		param[i].stop = stop - block * (thread_count - i - 1);
		pthread_create(thread_all + i, NULL, goldbach_thread, (void*)(param + i));
	}
	for (i = 0; i < thread_count; i++) {
		pthread_join(thread_all[i], NULL);
	}
}

int main(int argc, char *argv[]) {
	int goldbach = 0;
	unsigned long start, stop;

	if (argc < 2) {
		fprintf(stderr, "Usage: %s [-g] min max\n", argv[0]);
		return 1;
	}

	//Check args
	if (!strcmp(argv[1], "-g")) {
		//Enter Goldbach mode
		goldbach = 1;
		if (argc < 4) {
			fputs("Invalid arguments.\n", stderr);
			return 1;
		}
		start = strtoul(argv[2], NULL, 0);
		stop = strtoul(argv[3], NULL, 0);
	} else {
		//Enter Prime-Gen mode
		if (argc < 3) {
			fputs("Invalid arguments.\n", stderr);
			return 1;
		}
		start = strtoul(argv[1], NULL, 0);
		stop = strtoul(argv[2], NULL, 0);
	}
	if (start >= stop) {
		fputs("Invalid range.\n", stderr);
		return 1;
	}

	srand48(time(NULL));
	if (goldbach) {
		goldbach_mode(start, stop);
	} else {
		primes_mode(start, stop);
	}
	return 0;
}

