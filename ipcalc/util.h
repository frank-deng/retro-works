#ifndef util_h_
#define util_h_

#include <stdint.h>

#define ishexdigit(c) (((c)>='0' && (c)<='9') || ((c)>='A' && (c)<='F') || ((c)>='a' && (c)<='f'))
#define hexdigit2num(c) ((c)>='a' ? (c)-'a'+10 : (c)>='A' ? (c)-'A'+10 : (c)-'0')
#define num2hexu(n) ((n)>9 ? ((n)-10+'A') : ((n)+'0'))
#define num2hexl(n) ((n)>9 ? ((n)-10+'a') : ((n)+'0'))

inline char *u16tohex(uint16_t v, char *buf, bool upper)
{
    uint8_t i, d;
    char *p = buf;
    for (i = 0; i < 4; i++) {
        d = (v >> ((3 - i) << 2)) & 0xf;
        *p = (upper ? num2hexu(d) : num2hexl(d));
        p++;
    }
    *p = '\0';
    return buf;
}

#endif