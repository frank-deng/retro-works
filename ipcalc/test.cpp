#include "test.hpp"
#include "ipv4.h"

void Test::run(){
    uint32_t ipv4AddrBin = 0;
    char ipbuf[16];
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
}

int main(int argc, char *argv[])
{
    Test test;
    return 0;
}