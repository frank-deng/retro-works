#ifndef util_h_
#define util_h_

#include <limits.h>
#include <ctype.h>
#include <stdint.h>

#define INVALID_NETMASK (0xff)

#define hexdigit2num(c) ((c)>='a' ? (c)-'a'+10 : (c)>='A' ? (c)-'A'+10 : (c)-'0')

static inline unsigned int atouint(char *input, unsigned int max, bool *status)
{
    unsigned int n = 0;
    char *p = NULL;
    // Empty string and string with leading zero not allowed
    if ('\0' == *input || ('0' == *input && '\0' != *(input+1))) {
        goto ErrorHandler;
    }
    // First try to parse input as dec number
    for (p = input; *p != '\0'; p++) {
        if (!isdigit(*p)) {
            goto ErrorHandler;
        }
        n *= 10;
        n += *p - '0';
        if (n > max) {
            goto ErrorHandler;
        }
    }
    if (NULL != status) {
        *status = true;
    }
    return n;
ErrorHandler:
    if (NULL != status) {
        *status = false;
    }
    return 0;
}

static inline bool isipv6addr(char *str)
{
    char *p = str;
    while ('\0' != *p) {
        if (':' == *p) {
            return true;
        }
        p++;
    }
    return false;
}

#define UINT_MAX_DIGITS ((sizeof(unsigned int) << 1) * 5 / 4)
static inline uint8_t utodec(unsigned int v, char *buf)
{
    char _stack[UINT_MAX_DIGITS], *stackTop = _stack, *p = buf;
    if (0 == v) {
        *p = '0';
        p++;
    } else {
        while (v > 0) {
            *stackTop = (v % 10) + '0';
            stackTop++;
            v /= 10;
        }
        while (stackTop > _stack) {
            stackTop--;
            *p = *stackTop;
            p++;
        }
    }
    *p = '\0';
    return (uint8_t)(p - buf);
}

#define UINT_MAX_XDIGITS (sizeof(unsigned int) << 1)
static inline uint8_t utohex(unsigned int v, char *buf, uint8_t padding, bool upper)
{
    uint8_t i, n;
    char *p = buf;
    bool zeroval = true;
    if (padding < 1) {
        padding = 1;
    }
    for (i = UINT_MAX_XDIGITS; i > 0; i--) {
        n = (v >> ((i - 1) << 2)) & 0xf;
        if (n > 0) {
            zeroval = false;
        } else if (zeroval && i > padding) {
            continue;
        }
        *p = (n<=9 ? n+'0' : upper ? (n-10+'A') : (n-10+'a'));
        p++;
    }
    *p = '\0';
    return (uint8_t)(p - buf);
}

#endif
