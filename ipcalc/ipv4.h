#ifndef ipv4_h_
#define ipv4_h_

#include <stdbool.h>
#include <stdio.h>
#include "util.h"

#ifdef __cplusplus
extern "C" {
#endif

bool ipv4_pton(const char *, uint32_t *);
uint8_t ipv4_ptonm(char *);
char *ipv4_ntop(uint32_t, char *);

#ifdef __cplusplus
}
#endif

#endif