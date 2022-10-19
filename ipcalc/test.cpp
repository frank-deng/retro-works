#include "test.hpp"
#include "ipv4.h"
#include "ipv6.h"

void Test::run(){
    uint32_t ipv4AddrBin = 0;
    ipv6addr_t addr6={0,0,0,0,0,0,0,0}, addr6a={0xffff,0xffff,0xffff,0xffff,0xffff,0xffff,0xffff,0xffff};
    char ipbuf[46];
    puts("IP conversion:");
    EXP_TRUE(ipv4_pton("192.168.1.1", &ipv4AddrBin));
    EXP_EQ(0xc0a80101, ipv4AddrBin);
    EXP_TRUE(ipv4_pton("127.0.0.1", &ipv4AddrBin));
    EXP_EQ(0x7f000001, ipv4AddrBin);
    EXP_TRUE(ipv4_pton("192.168.0.1", &ipv4AddrBin));
    EXP_EQ(0xc0a80001, ipv4AddrBin);
    EXP_TRUE(ipv4_pton("0.0.0.0", &ipv4AddrBin));
    EXP_EQ(0, ipv4AddrBin);
    EXP_TRUE(ipv4_pton("0.0.0.1", &ipv4AddrBin));
    EXP_EQ(0x1, ipv4AddrBin);
    EXP_TRUE(ipv4_pton("192.168.101.1", &ipv4AddrBin));
    EXP_EQ(0xc0a86501, ipv4AddrBin);
    EXP_TRUE(ipv4_pton("192.168.100.1", &ipv4AddrBin));
    EXP_EQ(0xc0a86401, ipv4AddrBin);

    EXP_FALSE(ipv4_pton("192.168.00.1", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("192.168.001.1", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("00.0.1.1", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("01.0.1.1", &ipv4AddrBin));

    EXP_FALSE(ipv4_pton("192.168.1.0xa", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton(".192.168.1.1", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("hahaha", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("192.168.1", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("192.168.1.", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("192.168.1.1.", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("192.168.1.1.1", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("192.168.1.666", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("666.168.1.1", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("1234.168.1.1", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("1234.168.1", &ipv4AddrBin));
    EXP_FALSE(ipv4_pton("192.168..1", &ipv4AddrBin));
    
    puts("Netmask conversion:");
    EXP_EQ(0, ipv4_ptonm("0.0.0.0"));
    EXP_EQ(16, ipv4_ptonm("255.255.0.0"));
    EXP_EQ(24, ipv4_ptonm("255.255.255.0"));
    EXP_EQ(32, ipv4_ptonm("255.255.255.255"));
    EXP_EQ(19, ipv4_ptonm("255.255.224.0"));

    EXP_EQ(25, ipv4_ptonm("255.255.255.128"));
    EXP_EQ(26, ipv4_ptonm("255.255.255.192"));
    EXP_EQ(27, ipv4_ptonm("255.255.255.224"));
    EXP_EQ(28, ipv4_ptonm("255.255.255.240"));
    EXP_EQ(29, ipv4_ptonm("255.255.255.248"));
    EXP_EQ(30, ipv4_ptonm("255.255.255.252"));
    EXP_EQ(31, ipv4_ptonm("255.255.255.254"));
    EXP_EQ(-1, ipv4_ptonm("255.223.0.0"));
    
    puts("Convert binary ipv4 addr to str:");
    EXP_NE(NULL, ipv4_ntop(0xc0a80101, ipbuf));
    EXP_STREQ("192.168.1.1", ipv4_ntop(0xc0a80101, ipbuf));
    EXP_NE(NULL, ipv4_ntop(0xc0a80101, ipbuf));
    EXP_STREQ("0.0.0.0", ipv4_ntop(0x0, ipbuf));
    EXP_STREQ("0.0.0.1", ipv4_ntop(0x1, ipbuf));
    EXP_STREQ("255.255.255.255", ipv4_ntop(0xffffffff, ipbuf));
    EXP_STREQ("255.255.0.0", ipv4_ntop(0xffff0000, ipbuf));

    puts("IPv6 conversion");
    EXP_STREQ("0000:0000:0000:0000:0000:0000:0000:0000", ipv6_ntop(&addr6, ipbuf, IPV6_FORMAT_FULL));
    EXP_TRUE(ipv6_pton(ipbuf, &addr6a));
    EXP_MEMEQ(sizeof(addr6), &addr6, &addr6a);

    memset(&addr6, 0xff, sizeof(addr6));
    EXP_TRUE(ipv6_pton("2001:DB8:85a3::8a2e:370:7334", &addr6));
    addr6a.d[0] = 0x2001;
    addr6a.d[1] = 0xdb8;
    addr6a.d[2] = 0x85a3;
    addr6a.d[3] = 0;
    addr6a.d[4] = 0;
    addr6a.d[5] = 0x8a2e;
    addr6a.d[6] = 0x370;
    addr6a.d[7] = 0x7334;
    EXP_MEMEQ(sizeof(addr6), &addr6, &addr6a);
    EXP_STREQ("2001:0db8:85a3:0000:0000:8a2e:0370:7334", ipv6_ntop(&addr6a, ipbuf, IPV6_FORMAT_FULL));
}

int main(int argc, char *argv[])
{
    Test test;
    return 0;
}