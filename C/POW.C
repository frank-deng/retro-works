#include <stdio.h>
#include <stdlib.h>
#include <string.h>

double myPow(double x, long n0)
{
	double result = 1.0;
	long n = n0;
	if (n < 0) {
		x = 1 / x;
		n = -n;
	}
	while (n != 0) {
		if (n & 1) {
			result *= x;
		}
		x *= x;
		n >>= 1;
	}
	return result;
}
int main(int argc, char *argv[])
{
	double x = 0.0;
	long n = 0;
	if (argc < 3) {
		printf("Usage: pow x n\n");
		return 0;
	}
	x = strtod(argv[1], NULL);
	n = strtol(argv[2], NULL, 0);
	printf("%.16lg ^ %ld = %.16lg\n", x, n, myPow(x, n));
	return 0;
}
