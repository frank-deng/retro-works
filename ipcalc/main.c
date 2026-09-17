#include <string.h>
#include "ipv4.h"
#include "ipv6.h"
#include "langpack.h"

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
    bool isipv6, ipConvStatus;
    if (argc < 2) {
        goto ParseFailed;
    }
    input = argv[1];
    netmaskInput = strchr(input, '/');
    if (NULL == netmaskInput) {
        fputs(gettext(TEXT_NETMASK_MISSING), stderr);
        goto ParseFailed;
    }
    strncpy(ipstrbuf, input, netmaskInput - input);
    ipstrbuf[netmaskInput - input] = '\0';
    netmaskInput++;
    isipv6 = isipv6addr(ipstrbuf);
    if (isipv6) {
        data->isipv6 = true;
        ipConvStatus = ipv6_pton(ipstrbuf, &(data->ipv6addr));
        data->netmask = ipv6_ptonm(netmaskInput);
    } else {
        data->isipv6 = false;
        ipConvStatus = ipv4_pton(ipstrbuf, &(data->ipaddr));
        data->netmask = ipv4_ptonm(netmaskInput);
    }
    if (!ipConvStatus) {
        fputs(gettext(isipv6 ? TEXT_INVALID_IPV6ADDR : TEXT_INVALID_IPADDR), stderr);
        goto ParseFailed;
    }
    if (INVALID_NETMASK == data->netmask) {
        fputs(gettext(TEXT_INVALID_NETMASK), stderr);
        goto ParseFailed;
    }
    return true;
ParseFailed:
    fputs(gettext(TEXT_HELP), stderr);
    return false;
}
int main(int argc, char *argv[])
{
    ArgData_t data;
    char strbuf[64];
    initlang();
    if (!parseArgs(&data, argc, argv)) {
        return 1;
    }

    if (data.isipv6) {
        uint8_t availHostsBits = 128 - data.netmask;
        printf(gettext(TEXT_IPV6_ADDR_COMP), ipv6_ntop(&(data.ipv6addr), strbuf, IPV6_FORMAT_COMP));
        printf(gettext(TEXT_IPV6_ADDR_UNCOMP), ipv6_ntop(&(data.ipv6addr), strbuf, IPV6_FORMAT_UNCOMP));
        printf(gettext(TEXT_IPV6_ADDR_FULL), ipv6_ntop(&(data.ipv6addr), strbuf, IPV6_FORMAT_FULL));
        if (availHostsBits > 31) {
            printf(gettext(TEXT_IPV6_AVAIL_HOSTS2), availHostsBits);
        } else if (availHostsBits >= 1) {
            printf(gettext(TEXT_IPV6_AVAIL_HOSTS), 1UL << availHostsBits);
        }
        if (availHostsBits >= 1) {
            ipv6_apply_netmask(&data.ipv6addr, availHostsBits, false);
            printf(gettext(TEXT_IPV6_ADDR_RANGE), ipv6_ntop(&(data.ipv6addr), strbuf, IPV6_FORMAT_FULL));
            ipv6_apply_netmask(&data.ipv6addr, availHostsBits, true);
            printf(gettext(TEXT_IPV6_ADDR_RANGE2), ipv6_ntop(&(data.ipv6addr), strbuf, IPV6_FORMAT_FULL));
        }
    } else {
        uint32_t wildcard = (1UL << (32 - data.netmask)) - 1;
        printf(gettext(TEXT_IPV4_WILDCARD), ipv4_ntop(wildcard, strbuf), 32 - data.netmask);
        printf(gettext(TEXT_IPV4_NETMASK), ipv4_ntop(~wildcard, strbuf), data.netmask);
        printf(gettext(TEXT_IPV4_AVAIL_HOSTS), wildcard < 1 ? 0 : wildcard - 1);
        printf(gettext(TEXT_IPV4_NETWORK_ADDR), ipv4_ntop((data.ipaddr & (~wildcard)), strbuf));
        if (data.netmask <= 30) {
            printf(gettext(TEXT_IPV4_ADDR_RANGE), ipv4_ntop((data.ipaddr & (~wildcard)) + 1, strbuf));
            puts(ipv4_ntop((data.ipaddr | wildcard) - 1, strbuf));
        }
        printf(gettext(TEXT_IPV4_BROADCAST_ADDR), ipv4_ntop((data.ipaddr | wildcard), strbuf));
    }
    return 0;
}