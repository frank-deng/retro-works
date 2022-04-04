#include <stdio.h>
#include <string.h>
#include <malloc.h>

#define HELP_INFO "Usage: find2 findstr < [drive:][path]filename"

#define BUFFER_SIZE 2048
#define SEARCH_STR_LEN 256

#define setBit(data, offset, val) \
do { \
	if (val) { \
		(data)[(size_t)(offset) >> 3] |= (1 << ((offset) & 0x7)); \
	} else { \
		(data)[(size_t)(offset) >> 3] &= ~(1 << ((offset) & 0x7)); \
	} \
} while (0)

#define getBit(data, offset) \
	((data)[(size_t)(offset) >> 3] & (1 << ((offset) & 0x7)))

#define offset(w, i, j) ((size_t)((i) * (w) + (j)))

int isMatch(const char *search, const char *str)
{
	size_t w = strlen(str) + 1, h = strlen(search) + 1,
		bufSize = ((w * h) >> 3) + 1;
	size_t i, j;
	unsigned char *data = NULL;

	if (w <= 1) {
		return 0;
	}

	data = (unsigned char*)calloc(sizeof(unsigned char), bufSize);
	if (data == NULL) {
		return 0;
	}

	setBit(data, 0, 1);
	for (j = 1; j < h; j++) {
		if (search[j - 1] == '*') {
			setBit(data, j, 1);
		} else {
			break;
		}
	}
	for (i = 1; i < w; i++) {
		for (j = 1; j < h; j++) {
			if (search[j - 1] == str[i - 1] || search[j - 1] == '?') {
				setBit(data, offset(h, i, j), getBit(data, offset(h, i - 1, j - 1)));
			} else if (search[j - 1] == '*') {
				if (getBit(data, offset(h, i - 1, j)) || getBit(data, offset(h, i, j - 1))) {
					setBit(data, offset(h, i, j), 1);
				}
			}
		}
	}
	int result = getBit(data, offset(h, w - 1, h - 1));
	free(data);
	return result;
}
void removeNewLine(char *str)
{
	while (*str != '\0') {
		if (*str == '\n' || *str == '\r') {
			*str = '\0';
			return;
		}
		str++;
	}
}
int main(int argc, char *argv[])
{
	char buffer[BUFFER_SIZE], *search = NULL;

	// Parse args
	if (argc < 2) {
		puts(HELP_INFO);
		return 1;
	}
	search = argv[1];

	// Main process
	while (fgets(buffer, BUFFER_SIZE, stdin) != NULL) {
		removeNewLine(buffer);
		if (isMatch(search, buffer)) {
			puts(buffer);
		}
	}
	return 0;
}
