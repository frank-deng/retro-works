#include <string.h>
#include "ipv4.h"
#include "ipv6.h"

#define HELP_TEXT ("\
Usage: ipcalc ipaddr/netmask\r\n\
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
    char strbuf[16];
    uint32_t ipMin, ipMax, wildcard;
    if (!parseArgs(&data, argc, argv)) {
        return 1;
    }
    wildcard = (1UL << (32 - data.netmask)) - 1;

    printf("Wildcard: %s = %u\n", ipv4_ntop(wildcard, strbuf), 32 - data.netmask);
    printf("Netmask: %s = %u\n", ipv4_ntop(~wildcard, strbuf), data.netmask);
    printf("Available hosts: %lu\n", wildcard < 1 ? 0 : wildcard - 1);
    printf("Network IP: %s\n", ipv4_ntop((data.ipaddr & (~wildcard)), strbuf));
    if (data.netmask <= 30) {
        printf("IP Range: %s - ", ipv4_ntop((data.ipaddr & (~wildcard)) + 1, strbuf));
        puts(ipv4_ntop((data.ipaddr | wildcard) - 1, strbuf));
    }
    printf("Broadcast IP: %s\n", ipv4_ntop((data.ipaddr | wildcard), strbuf));
    return 0;
}
