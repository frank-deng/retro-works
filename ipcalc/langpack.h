#ifndef langpack_h
#define langpack_h

#include <string.h>
#if defined(__DOS__)
#include <dos.h>
#endif

#define TAG_STR(v) (#v)

typedef enum {
    LANG_EN,
    LANG_ZH_GB2312,
    LANG_MAX
} lang_t;
typedef enum {
    TEXT_HELP,
    TEXT_IPV4_WILDCARD,
    TEXT_IPV4_NETMASK,
    TEXT_IPV4_AVAIL_HOSTS,
    TEXT_IPV4_NETWORK_ADDR,
    TEXT_IPV4_ADDR_RANGE,
    TEXT_IPV4_BROADCAST_ADDR,
    TEXT_IPV6_ADDR_COMP,
    TEXT_IPV6_ADDR_UNCOMP,
    TEXT_IPV6_ADDR_FULL,
    TEXT_IPV6_AVAIL_HOSTS,
    TEXT_IPV6_AVAIL_HOSTS2,
    TEXT_IPV6_ADDR_RANGE,
    TEXT_IPV6_ADDR_RANGE2,
    TEXT_INVALID_IPADDR,
    TEXT_INVALID_IPV6ADDR,
    TEXT_NETMASK_MISSING,
    TEXT_INVALID_NETMASK,
    TEXT_MAX
} lang_text_t;

static char* g_langData[LANG_MAX][TEXT_MAX] = {
    {
         "\
Usage: ipcalc ipaddr/netmask\n\
       ipcalc ipv6addr/netmask\n\
",
         "Wildcard:        %s = %u\n",
         "Netmask:         %s = %u\n",
         "Available hosts: %lu\n",
         "Network IP:      %s\n",
         "IP Range:        %s - ",
         "Broadcast IP:    %s\n",
         "IPv6 Address Compressed:   %s\n",
         "IPv6 Address Uncompressed: %s\n",
         "IPv6 Address Full:         %s\n",
         "Available hosts:           %lu\n",
         "Available hosts:           2^%u\n",
         "IP Range:                  %s -\n",
         "                           %s\n",
         "Malformed IP Address.\n",
         "Malformed IPv6 Address.\n",
         "Netmask Missing.\n",
         "Malformed Netmask.\n",
    },
    {
         "\
使用方法：ipcalc IPv4地址/子网掩码\n\
          ipcalc IPv6地址/子网掩码\n\
",
         "通配符：    %s = %u\n",
         "子网掩码：  %s = %u\n",
         "可用地址数：%lu\n",
         "网络地址：  %s\n",
         "IP地址范围：%s - ",
         "广播地址：  %s\n",
         "IPv6地址（压缩格式）：  %s\n",
         "IPv6地址（未压缩格式）：%s\n",
         "IPv6地址（完整格式）：  %s\n",
         "可用地址数：            %lu\n",
         "可用地址数：            2^%u\n",
         "IP地址范围：            %s -\n",
         "                        %s\n",
         "IP地址格式错误。\n",
         "IPv6地址格式错误。\n",
         "缺少子网掩码。\n",
         "子网掩码格式错误。\n",
    },
};

static lang_t g_lang = LANG_EN;
static inline void initlang()
{
#if defined(__DOS__)
    union REGPACK regs;
    regs.x.ax = 0xdb00;
    intr(0x2f,&regs);
    if (regs.x.bx == 0x5450) {
        g_lang = LANG_ZH_GB2312;
    }
#endif
}
static inline char* gettext(lang_text_t text)
{
    char *res = g_langData[g_lang][text];
    if (NULL == res) {
        res = g_langData[LANG_EN][text];
    }
    return NULL == res ? TAG_STR(text) : res;
}

#endif
