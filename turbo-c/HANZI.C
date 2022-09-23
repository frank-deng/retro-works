#include <stdio.h>
#include <string.h>
#include <stdlib.h>

typedef enum {
    DEFAULT,
    DISPLAY_HELP,
    SET_MODE_ASCII,
    SET_OUTPUT_FILE,
    SET_FONT_FILE,
    SET_START_LINE
} getopt_action_t;
typedef struct {
    const char *arg;
    const char *arg2;
    unsigned char param;
    getopt_action_t action;
} getopt_table_t;
typedef struct {
    unsigned short x;
    unsigned short y;
    unsigned short length;
    unsigned char data[256];
} textdata_t;
typedef struct {
    char *font_file;
    char *output_file;
    int ascii_mode;
    unsigned short start_line;
    unsigned short line_step;
    unsigned short text_data_count;
    textdata_t text_data[64];
} getopt_t;

#define HELP_TEXT "\
Usage: hanzi.exe [/a] [/f|/font FONT_FILE] [/o|/out OUTPUT_FILE]\n\
                 [/l|/line START_LINE_NUM] text1 text2 ...\n\
"

static getopt_table_t g_getoptTable[] = {
    { "/a", "/ascii", 0,  SET_MODE_ASCII },
    { "/f", "/font", 1,  SET_FONT_FILE },
    { "/o", "/out", 1,  SET_OUTPUT_FILE },
    { "/l", "/line", 1,  SET_START_LINE },
    { "/h", "/help", 0,  DISPLAY_HELP },
    { NULL, NULL, 0, DEFAULT}
};
static unsigned short g_lineNum = 100;
static unsigned short g_lineNumStep = 10;
static FILE* g_font = NULL;
static FILE* g_output = NULL;
static int processOptind(char *arg, textdata_t *target)
{
    char buf[256] = "", *p = buf, *pTarget = (char*)(target->data);
    if (sscanf(arg, "%u,%u:%s", &(target->x), &(target->y), buf) != 3) {
        return 0;
    }
    target->length = 0;
    while (*p) {
        if ('\0' == *p) {
            break;
        }
        if ('\0' == *(p+1)) {
            break;
        }
        if ((unsigned char)*p < 0xa1) {
            p++;
            continue;
        }
        *pTarget = *p;
        *(pTarget + 1) = *(p + 1);
        p += 2;
        pTarget += 2;
        (target->length)++;
    }
    *pTarget = '\0';
    return 1;
}
static int getopt(getopt_t *dest, int argc, char *argv[])
{
    getopt_table_t *item = NULL;
    char *paramStr = NULL;
    int i, j;
    dest->font_file = "HZK16.FON";
    dest->output_file = NULL;
    dest->ascii_mode = 0;
    dest->start_line = 100;
    dest->line_step = 10;
    dest->text_data_count = 0;
    for (i = 1; i < argc; i++) {
        for (item = g_getoptTable; item->arg != NULL; item++) {
            if (!strcmp(argv[i], item->arg) || !strcmp(argv[i], item->arg2)) {
                break;
            }
        }

        if (NULL == item->arg) {
            if (processOptind(argv[i], dest->text_data + dest->text_data_count)) {
                (dest->text_data_count)++;
            }
            continue;
        }

        paramStr = NULL;
        if (item->param) {
            if (i + 1 >= argc) {
                return 0;
            }
            i++;
            paramStr = argv[i];
        }

        switch (item->action) {
            case DISPLAY_HELP:
                return 0;
            break;
            case SET_MODE_ASCII:
                dest->ascii_mode = 1;
            break;
            case SET_FONT_FILE:
                dest->font_file = paramStr;
            break;
            case SET_OUTPUT_FILE:
                dest->output_file = paramStr;
            break;
            case SET_START_LINE:
                dest->start_line = atoi(paramStr);
                if (!dest->start_line) {
                    return 0;
                }
            break;
        }
    }
    if (!dest->text_data_count) {
        return 0;
    }
    return 1;
}
int readFont(unsigned char *buf, unsigned char qu, unsigned char wei)
{
    unsigned long offset = 0;
    if (qu < 0xa1 || qu > 0xfe || wei < 0xa1 || wei > 0xfe) {
        return 0;
    }
    offset = qu - 0xa1;
    offset *= 94;
    offset += wei - 0xa1;
    offset *= 32;
    if (fseek(g_font, offset, SEEK_SET)) {
        return 0;
    }
    memset(buf, 0, 32);
    fread(buf, 32, 1, g_font);
    return 1;
}
int processChar(unsigned short x, unsigned short y, unsigned char qu, unsigned char wei)
{
    int i;
    unsigned char buf[32];
    if (!readFont(buf, qu, wei)) {
        return 0;
    }
    fprintf(g_output, "%d DATA %d,%d", g_lineNum, x, y);
    g_lineNum += g_lineNumStep;
    for (i = 0; i < 32; i += 2) {
        fprintf(g_output, ",&H%x", (((unsigned short)buf[i]) << 8) | buf[i+1]);
    }
    fprintf(g_output, "\r\n");
    return 1;
}
int processCharAscii(unsigned short x, unsigned short y, unsigned char qu, unsigned char wei)
{
    int i, j;
    unsigned char buf[32], value;
    unsigned short evenRow, oddRow, mask;
    if (!readFont(buf, qu, wei)) {
        return 0;
    }
    fprintf(g_output, "%d DATA %d,%d\r\n", g_lineNum, x, y);
    g_lineNum += g_lineNumStep;
    for (i = 0; i < 32; i += 4) {
        evenRow = (((unsigned short)buf[i]) << 8) | buf[i+1];
        oddRow = (((unsigned short)buf[i+2]) << 8) | buf[i+3];
        fprintf(g_output, "%d DATA ", g_lineNum);
        g_lineNum += g_lineNumStep;
        for (j = 0; j < 16; j++) {
            mask = 1 << (15 - j);
            if (j) {
                fprintf(g_output, ",");
            }
            value = 0;
            if (mask & evenRow) {
                value |= 1;
            }
            if (mask & oddRow) {
                value |= 2;
            }
            fprintf(g_output, "%d", value);
        }
        fprintf(g_output, "\r\n");
    }
    return 1;
}
int processStr(textdata_t *textdata, int asciiMode)
{
    unsigned int x = textdata->x;
    int i;
    unsigned char *p = textdata->data;
    for (i = 0; i < textdata->length; i++) {
        if (asciiMode){
            processCharAscii(x, textdata->y, *p, *(p + 1));
        } else {
            processChar(x, textdata->y, *p, *(p + 1));
        }
        p += 2;
        x += 16;
    }
    return 1;
}
int main(int argc, char *argv[])
{
    getopt_t opt;
    short charCount = 0;
    int i;

    if (!getopt(&opt, argc, argv)) {
        fputs(HELP_TEXT, stderr);
        return 1;
    }

    g_font = fopen(opt.font_file, "rb");
    if (NULL == g_font) {
        fputs("Failed to open font file.\n", stderr);
        return 1;
    }

    g_output = stdout;
    if (opt.output_file) {
        g_output = fopen(opt.output_file, "w");
        if (NULL == g_output) {
            fputs("Failed to open output file.\n", stderr);
            fclose(g_font);
            return 1;
        }
    }
    g_lineNum = opt.start_line;
    g_lineNumStep = opt.line_step;

    for (i = 0; i < opt.text_data_count; i++) {
        charCount += opt.text_data[i].length;
    }
	fprintf(g_output, "%u DATA %u\r\n", g_lineNum, charCount);
	g_lineNum += g_lineNumStep;

    for (i = 0; i < opt.text_data_count; i++) {
        processStr(opt.text_data + i, opt.ascii_mode);
    }

    fclose(g_font);
    if (g_output != stdout) {
        fclose(g_output);
    }
    return 0;
}
