#ifndef util_h_
#define util_h_

#include <stdint.h>

#define isdigit(c) ((c)>='0' && (c)<='9')

static inline char *u8tostr(uint8_t v, char *buf)
{
    uint8_t d;
    char *p = buf;
    d = (v / 100) % 10;
    if (d != 0) {
        *p = '0' + d;
        p++;
    }
    d = (v / 10) % 10;
    if (d != 0 || p != buf) {
        *p = '0' + d;
        p++;
    }
    d = v % 10;
    *p = '0' + d;
    p++;
    *p = '\0';
    return buf;
}

static inline char *u32tostr(uint32_t v, char *buf)
{
    uint32_t div = 1000000000;
    uint8_t d, i;
    char *p = buf;
    for (i = 0; i < 10; i++) {
        d = (v / div) % 10;
        div /= 10;
        if (d != 0 || p != buf) {
            *p = '0' + d;
            p++;
        }
    }
    if (p == buf) {
        *p = '0';
        p++;
    }
    *p = '\0';
    return buf;
}

static inline void printChar(char ch);
#pragma aux printChar = \
    "mov ah,2"\
    "int 0x21"\
    modify [ah]\
    parm [dl]

inline void print(char *str)
{
    char *p;
    for (p = str; *p != '\0'; p++) {
        printChar(*p);
    }
}

#endif
