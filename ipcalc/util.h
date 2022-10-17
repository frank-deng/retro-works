#ifndef util_h_
#define util_h_

#include <stdint.h>

typedef struct {
    uint16_t d[8];
} uint128_t;

inline void u128and(uint128_t *a, uint128_t *b)
{
    uint8_t i;
    for (i = 0; i < 8; i++) {
        a->d[i] &= b->d[i];
    }
}
inline void u128or(uint128_t *a, uint128_t *b)
{
    uint8_t i;
    for (i = 0; i < 8; i++) {
        a->d[i] |= b->d[i];
    }
}
inline void u128not(uint128_t *a)
{
    uint8_t i;
    for (i = 0; i < 8; i++) {
        a->d[i] = ~(a->d[i]);
    }
}
inline void u128xor(uint128_t *a, uint128_t *b)
{
    uint8_t i;
    for (i = 0; i < 8; i++) {
        a->d[i] ^= b->d[i];
    }
}
inline void u128add(uint128_t *a, uint128_t *b)
{
    uint8_t i;
    uint32_t tmp, inc = 0;
    for (i = 0; i < 8; i++) {
        tmp = a->d[i];
        tmp += b->d[i];
        tmp += inc;
        a->d[i] = tmp & 0xffff;
        inc = tmp >> 16;
    }
}
inline void u128sub(uint128_t *a, uint128_t *b)
{
    uint8_t i;
    int32_t tmp, dec = 0;
    for (i = 0; i < 8; i++) {
        tmp = a->d[i];
        tmp -= b->d[i];
        tmp += dec;
        a->d[i] = tmp & 0xffff;
        dec = tmp >> 16;
    }
}
inline uint16_t u128shr(uint128_t *v, uint8_t n)
{
    uint8_t i;
    uint16_t res = 1;
    n &= 0xf;
    res <<= n;
    res -= 1;
    res &= v->d[0];
    for (i = 0; i < 7; i++) {
        v->d[i] >>= n;
        v->d[i] |= (v->d[i+1]) << (15-n);
    }
    v->d[i] >>= n;
    return res;
}
inline uint16_t u128mulu8(uint128_t *v, uint8_t n)
{
    uint8_t i;
    uint128_t tmp;
    for (i = 0; i < 7; i++) {
        tmp.d[i] = 0;
    }
    return 0;
}
inline char *u128tostr(uint128_t *v, char *buf)
{
    return buf;
}

#define isdigit(c) ((c)>='0' && (c)<='9')

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
