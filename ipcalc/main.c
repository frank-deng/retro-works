#include <string.h>
#include "ipv4.h"

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
    print(HELP_TEXT);
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

    print("Wildcard: ");
    print(ipv4_ntop(wildcard, strbuf));
    print(" = ");
    print(utostr(32 - data.netmask, strbuf));
    print("\r\n");

    print("Netmask: ");
    print(ipv4_ntop(~wildcard, strbuf));
    print(" = ");
    print(utostr(data.netmask, strbuf));
    print("\r\n");

    print("Available hosts: ");
    print(utostr(wildcard < 1 ? 0 : wildcard - 1, strbuf));
    print("\r\n");

    print("Network IP: ");
    print(ipv4_ntop((data.ipaddr & (~wildcard)), strbuf));
    print("\r\n");

    print("Broadcast IP: ");
    print(ipv4_ntop((data.ipaddr | wildcard), strbuf));
    print("\r\n");

    if (data.netmask <= 30) {
        print("IP Range: ");
        print(ipv4_ntop((data.ipaddr & (~wildcard)) + 1, strbuf));
        print(" - ");
        print(ipv4_ntop((data.ipaddr | wildcard) - 1, strbuf));
        print("\r\n");
    }
    return 0;
}