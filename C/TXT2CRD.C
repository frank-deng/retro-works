#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <malloc.h>

#define MAGIC_NUM ("MGC")
#define TITLE_FLAG (".title:")
#define TEXT_FLAG (".text:")
#define HELP_TEXT ("Usage: %s input.txt output.crd\n")
#define INVALID_FILE ("Unable to open file")

struct headerLine_s {
	char reserved[6];
	uint32_t offset;
	uint8_t flag;
	char text[41];
};

int parseFile(FILE *out, FILE *fp)
{
	uint32_t count = 0, idx = 0;
	char buf[512];
	size_t contentOffset;
	struct headerLine_s header;

	while (fgets(buf, sizeof(buf), fp) != NULL) {
		if (0 == strncmp(buf, TITLE_FLAG, sizeof(TITLE_FLAG) - 1)) {
			count++;
		}
	}
	rewind(fp);

	fseek(fp, 0, SEEK_SET);
	fwrite(MAGIC_NUM, sizeof(MAGIC_NUM), 1, out);
	while (fgets(buf, sizeof(buf), fp) != NULL) {
		if (0 == strncmp(buf, TITLE_FLAG, sizeof(TITLE_FLAG) - 1)) {
			memset(&header, 0, sizeof(header));
			strcpy(header.text, buf + sizeof(TITLE_FLAG) - 1);
			header.offset = contentOffset;
			fseek(5 + 52 * idx);
			fwrite(&header, sizeof(MAGIC_NUM), 1, out);
		}
	}

	return 0;
}
int main(int argc, char *argv[])
{
	int status = 0;
	char *err = NULL;
	char *fpath = NULL;
	char *dpath = NULL;
	FILE *fp = NULL;
	FILE *out = NULL;

	if (argc < 3) {
		fprintf(stderr, HELP_TEXT, argv[0]);
		return 1;
	}
	fpath = argv[1];
	dpath = argv[2];
	fp = fopen(fpath, "r");
	err = checkFile(fp);
	if (NULL != err) {
		fprintf(stderr, "%s: %s\n", err, fpath);
		status = 1;
		goto FinallyExit;
	}
	out = fopen(argv[2], "wb");
	if (NULL == out) {
		fprintf(stderr, "Unable to open file: %s\n", dpath);
		status = 1;
		goto FinallyExit;
	}
	parseFile(out, fp);
FinallyExit:
	if (NULL != fp) {
		fclose(fp);
	}
	if (NULL != out) {
		fclose(out);
	}
	return status;
}

