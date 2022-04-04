#include <stdio.h>
#include <string.h>
#include <malloc.h>
#include <ctype.h>

#define HELP_INFO "Usage: find2 [/I] findstr < [drive:][path]filename"

#define BUFFER_SIZE 2048

#define setBit(data, offset, val) \
do { \
	if (val) { \
		((unsigned char*)(data))[(size_t)(offset) >> 3] |= \
			(1 << ((offset) & 0x7)); \
	} else { \
		((unsigned char*)(data))[(size_t)(offset) >> 3] &= \
			~(1 << ((offset) & 0x7)); \
	} \
} while (0)

#define getBit(data, offset) \
	(((unsigned char*)(data))[(size_t)(offset) >> 3] & \
		(1 << ((offset) & 0x7)))

#define offset(w, i, j) ((size_t)((i) * (w) + (j)))

int charCmp(char pat, char ch, int ignoreCase)
{
	if (pat == '?') {
		return 1;
	} else if (ignoreCase) {
		return toupper(pat) == toupper(ch);
	}
	return pat == ch;
}
int isMatch(const char *pat, const char *str, const int ignoreCase)
{
	size_t _strLen = strlen(str), patLen = strlen(pat),
		rowSize = patLen + 1,
		dataSize = (((_strLen + 1) * rowSize) >> 3) + 1;
	size_t i, j;
	unsigned char *data = NULL;
	int result = 0;

	if (_strLen <= 1) {
		return 0;
	}

	data = (unsigned char*)calloc(sizeof(unsigned char), dataSize);
	if (data == NULL) {
		return 0;
	}

	setBit(data, 0, 1);
	for (j = 1; j <= patLen; j++) {
		if (pat[j - 1] == '*') {
			setBit(data, j, 1);
		} else {
			break;
		}
	}
	for (i = 1; i <= _strLen; i++) {
		for (j = 1; j <= patLen; j++) {
			if (pat[j - 1] == '*') {
				setBit(data, offset(rowSize, i, j),
					getBit(data, offset(rowSize, i - 1, j)) |
						getBit(data, offset(rowSize, i, j - 1)));
			} else if (charCmp(pat[j - 1], str[i - 1], ignoreCase)) {
				setBit(data, offset(rowSize, i, j),
					getBit(data, offset(rowSize, i - 1, j - 1)));
			}
		}
	}
	result = getBit(data, offset(rowSize, _strLen, patLen));
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
	int ignoreCase = 0;
	size_t optind = 1;

	// Parse args
	if (argc < 2) {
		puts(HELP_INFO);
		return 1;
	}
	if (strcmp(argv[1], "/i") == 0 || strcmp(argv[1], "/I") == 0) {
		ignoreCase = 1;
		optind++;
	}
	search = argv[optind];

	// Main process
	while (fgets(buffer, BUFFER_SIZE, stdin) != NULL) {
		removeNewLine(buffer);
		if (isMatch(search, buffer, ignoreCase)) {
			puts(buffer);
		}
	}
	return 0;
}
