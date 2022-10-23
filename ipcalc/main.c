#include <string.h>
#include "ipv4.h"
#include "ipv6.h"

#define HELP_TEXT ("\
Usage: ipcalc ipaddr/netmask\r\n\
")
#define NETMASK_MISSING ("Netmask Missing.\n")
#define INVALID_IPADDR ("Invalid IP Address.\n")
#define INVALID_NETMASK_STR ("Invalid Netmask.\n")

typedef struct {
    bool isipv6;
    uint32_t ipaddr;
    ipv6addr_t ipv6addr;
    uint8_t netmask;
} ArgData_t;
static inline bool parseArgs(ArgData_t *data, int argc, char *argv[])
{
    char *input = NULL, *netmaskInput = NULL;
    char ipstrbuf[64] = "";
    bool ipConvStatus;
    if (argc < 2) {
        goto ParseFailed;
    }
    input = argv[1];
    netmaskInput = strchr(input, '/');
    if (NULL == netmaskInput) {
        fputs(NETMASK_MISSING, stderr);
        goto ParseFailed;
    }
    strncpy(ipstrbuf, input, netmaskInput - input);
    ipstrbuf[netmaskInput - input] = '\0';
    netmaskInput++;
    if (isipv6addr(ipstrbuf)) {
        data->isipv6 = true;
        ipConvStatus = ipv6_pton(ipstrbuf, &(data->ipv6addr));
        data->netmask = ipv6_ptonm(netmaskInput);
    } else {
        data->isipv6 = false;
        ipConvStatus = ipv4_pton(ipstrbuf, &(data->ipaddr));
        data->netmask = ipv4_ptonm(netmaskInput);
    }
    if (!ipConvStatus) {
        fputs(INVALID_IPADDR, stderr);
        goto ParseFailed;
    }
    if (INVALID_NETMASK == data->netmask) {
        fputs(INVALID_NETMASK_STR, stderr);
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
    char strbuf[64];
    if (!parseArgs(&data, argc, argv)) {
        return 1;
    }

    if (data.isipv6) {
        uint8_t availHostsBits = 128 - data.netmask;
        printf("IPv6 Address Compressed:   %s\n", ipv6_ntop(&(data.ipv6addr), strbuf, IPV6_FORMAT_COMP));
        printf("IPv6 Address Uncompressed: %s\n", ipv6_ntop(&(data.ipv6addr), strbuf, IPV6_FORMAT_UNCOMP));
        printf("IPv6 Address Full:         %s\n", ipv6_ntop(&(data.ipv6addr), strbuf, IPV6_FORMAT_FULL));
        if (availHostsBits > 31) {
            printf("Available hosts:           2^%u\n", availHostsBits);
        } else if (availHostsBits >= 1) {
            printf("Available hosts:           %lu\n", 1UL << availHostsBits);
        }
        if (availHostsBits >= 1) {
            ipv6_apply_netmask(&data.ipv6addr, availHostsBits, false);
            printf("IP Range:                  %s -\n", ipv6_ntop(&(data.ipv6addr), strbuf, IPV6_FORMAT_FULL));
            ipv6_apply_netmask(&data.ipv6addr, availHostsBits, true);
            printf("                           %s\n", ipv6_ntop(&(data.ipv6addr), strbuf, IPV6_FORMAT_FULL));
        }
    } else {
        uint32_t wildcard = (1UL << (32 - data.netmask)) - 1;
        printf("Wildcard:        %s = %u\n", ipv4_ntop(wildcard, strbuf), 32 - data.netmask);
        printf("Netmask:         %s = %u\n", ipv4_ntop(~wildcard, strbuf), data.netmask);
        printf("Available hosts: %lu\n", wildcard < 1 ? 0 : wildcard - 1);
        printf("Network IP:      %s\n", ipv4_ntop((data.ipaddr & (~wildcard)), strbuf));
        if (data.netmask <= 30) {
            printf("IP Range:        %s - ", ipv4_ntop((data.ipaddr & (~wildcard)) + 1, strbuf));
            puts(ipv4_ntop((data.ipaddr | wildcard) - 1, strbuf));
        }
        printf("Broadcast IP:    %s\n", ipv4_ntop((data.ipaddr | wildcard), strbuf));
    }
    return 0;
}
