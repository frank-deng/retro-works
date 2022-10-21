#ifndef util_h_
#define util_h_

#include <stdint.h>

#define hexdigit2num(c) ((c)>='a' ? (c)-'a'+10 : (c)>='A' ? (c)-'A'+10 : (c)-'0')

inline char *u16tohex(uint16_t v, char *buf, bool upper)
{
    uint8_t i, n;
    char *p = buf;
    for (i = 0; i < 4; i++) {
        n = (v >> ((3 - i) << 2)) & 0xf;
        *p = (n<=9 ? n+'0' : upper ? (n-10+'A') : (n-10+'a'));
        p++;
    }
    *p = '\0';
    return buf;
}

#endif
