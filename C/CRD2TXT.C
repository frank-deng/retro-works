#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <malloc.h>

#define MAGIC_NUM ("MGC")
#define HELP_TEXT ("Usage: %s input.crd [output.txt]\n")
#define INVALID_FILE ("Unable to open file")
#define UNSUPPORTED_FILE_TYPE ("Unsupported file type")

struct headerLine_s {
	char reserved[6];
	uint32_t offset;
	uint8_t flag;
	char text[41];
};
struct cardHeader_s {
	uint16_t flag;
	uint16_t textLen;
};

char *checkFile(FILE *fp)
{
	char buf[sizeof(MAGIC_NUM)];
	if (NULL == fp) {
		return INVALID_FILE;
	}
	fseek(fp, 0, SEEK_SET);
	fread(buf, sizeof(MAGIC_NUM) - 1, 1, fp);
	if (memcmp(MAGIC_NUM, buf, sizeof(MAGIC_NUM) - 1) != 0) {
		return UNSUPPORTED_FILE_TYPE;
	}
	return NULL;
}
unsigned int countNewLines(char *str)
{
	char *p = str;
	unsigned int count = 1;
	for (p = str; *p != '\0'; p++) {
		switch (*p) {
			case '\r':
				continue;
			break;
			case '\n':
				count++;
			break;
		}
	}
	return count;
}
int parseContent(FILE *dst, FILE *fp, uint32_t offset)
{
	struct cardHeader_s cardHeader;
	char *buf = NULL;

	fseek(fp, offset, SEEK_SET);
	fread(&cardHeader, sizeof(cardHeader), 1, fp);
	if (cardHeader.flag != 0) {
		return 0;
	}
	buf = malloc(cardHeader.textLen + 1);
	fread(buf, cardHeader.textLen, 1, fp);
	buf[cardHeader.textLen] = '\0';
	fprintf(dst, ".text:%u\n", countNewLines(buf));
	fprintf(dst, "%s\n\n", buf);
	free(buf);
	return 1;
}
int parseFile(FILE *dst, FILE *fp)
{
	uint16_t cardsCount = 0, cardIdx;
	struct headerLine_s header;

	fseek(fp, 3, SEEK_SET);
	fread(&cardsCount, sizeof(uint16_t), 1, fp);
	for (cardIdx = 0; cardIdx < cardsCount; cardIdx++) {
		fseek(fp, 5 + 52 * cardIdx, SEEK_SET);
		fread(&header, sizeof(header), 1, fp);
		fprintf(dst, ".title:%s\n", header.text);
		parseContent(dst, fp, header.offset);
	}
	return 0;
}
int main(int argc, char *argv[])
{
	char *err = NULL;
	char *fpath = NULL;
	char *dpath = NULL;
	FILE *fp = NULL;
	FILE *out = stdout;

	if (argc < 2) {
		fprintf(stderr, HELP_TEXT, argv[0]);
		return 1;
	}
	fpath = argv[1];
	fp = fopen(fpath, "rb");
	err = checkFile(fp);
	if (NULL != err) {
		fprintf(stderr, "%s: %s\n", err, fpath);
		return 1;
	}
	if (argc >= 3) {
		dpath = argv[2];
		out = fopen(dpath, "w");
		if (NULL == out) {
			fprintf(stderr, "Unable to open file: %s\n", dpath);
			return 1;
		}
	}
	parseFile(out, fp);
	return 0;
}

