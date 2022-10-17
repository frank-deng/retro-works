#ifndef util_h_
#define util_h_

#include <stdint.h>

#define isdigit(c) ((c)>='0' && (c)<='9')
#define ishexdigit(c) (((c)>='0' && (c)<='9') || ((c)>='A' && (c)<='F') || ((c)>='a' && (c)<='f'))
#define num2hexu(n) ((n)>9 ? ((n)-10+'A') : ((n)+'0'))
#define num2hexl(n) ((n)>9 ? ((n)-10+'a') : ((n)+'0'))

inline char *utostr(uint32_t v, char *buf)
{
    char tmp[11], *t = tmp, *p = buf;
    if (0 == v) {
        *p = '0';
        p++;
    } else {
        while (v) {
            *t = (v % 10) + '0';
            t++;
            v /= 10;
        }
        while (t > tmp) {
            t--;
            *p = *t;
            p++;
        }
    }
    *p = '\0';
    return buf;
}
inline char *u16tohex(uint16_t v, char *buf, bool upper)
{
    uint8_t i, d;
    char *p = buf;
    for (i = 0; i < 4; i++) {
        d = (v >> ((3 - i) << 2)) & 0xf;
        *p = (upper ? num2hexh(d) : num2hexl(d));
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
