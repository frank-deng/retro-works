#ifndef ipv6_h_
#define ipv6_h_

#include <stdbool.h>
#include "util.h"

typedef struct {
    uint16_t d[8];
} ipv6addr_t;
typedef enum{
    IPV6_FORMAT_COMP,
    IPV6_FORMAT_UNCOMP,
    IPV6_FORMAT_FULL,
} ipv6_output_format_t;

#ifdef __cplusplus
extern "C" {
#endif

bool ipv6_pton(const char*, ipv6addr_t*);
uint8_t ipv6_ptonm(char *);
char *ipv6_ntop(ipv6addr_t*, char*, ipv6_output_format_t);
void ipv6_apply_netmask(ipv6addr_t *, uint8_t, bool);

#ifdef __cplusplus
}
#endif

#endif