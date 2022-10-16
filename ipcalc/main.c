#include <stdio.h>
#include <string.h>
#include "ipv4.h"

#define HELP_TEXT ("\
Usage: ipcalc ipaddr/netmask\
")

typedef struct {
    uint32_t ipaddr;
    int8_t netmask;
} ArgData_t;
static inline bool parseArgs(ArgData_t *data, int argc, char *argv[])
{
    char *input = NULL, *sep = NULL;
    char ipstrbuf[16];
    if (argc < 2) {
        goto ParseFailed;
    }
    input = argv[1];
    sep = strchr(input, '/');
    if (NULL == sep) {
        goto ParseFailed;
    }
    strncpy(ipstrbuf, input, sep - input);
    ipstrbuf[sep - input] = '\0';
    if (!ipv4_pton(ipstrbuf, &(data->ipaddr))) {
        goto ParseFailed;
    }
    data->netmask = ipv4_ptonm(sep + 1);
    if (data->netmask < 0) {
        goto ParseFailed;
    }
    return true;
ParseFailed:
    fputs(HELP_TEXT, stderr);
    return false;
}
int main(int argc, char *argv[])
{
    ArgData_t data;
    char ipstrbuf[16];
    uint32_t ipMin, ipMax, wildcard;
    if (!parseArgs(&data, argc, argv)) {
        return 1;
    }
    wildcard = (1UL << (32 - data.netmask)) - 1;
    printf("Wildcard: %s = %u\n", ipv4_ntop(wildcard, ipstrbuf), 32 - data.netmask);
    printf("Netmask: %s = %u\n", ipv4_ntop(~wildcard, ipstrbuf), data.netmask);
    if (data.netmask == 32) {
        printf("First IP: %s\n", ipv4_ntop(data.ipaddr, ipstrbuf));
    } else if (data.netmask == 31) {
        printf("First IP: %s\n", ipv4_ntop((data.ipaddr & (~wildcard)), ipstrbuf));
        printf("Last IP: %s\n", ipv4_ntop((data.ipaddr | wildcard), ipstrbuf));
    } else {
        printf("Network IP: %s\n", ipv4_ntop((data.ipaddr & (~wildcard)), ipstrbuf));
        printf("First IP: %s\n", ipv4_ntop((data.ipaddr & (~wildcard)) + 1, ipstrbuf));
        printf("Last IP: %s\n", ipv4_ntop((data.ipaddr | wildcard) - 1, ipstrbuf));
        printf("Broadcast IP: %s\n", ipv4_ntop((data.ipaddr | wildcard), ipstrbuf));
    }
    return 0;
}
