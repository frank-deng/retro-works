#include <ctype.h>
#include <stdlib.h>
#include <stdio.h>
#include "ipv4.h"
#include "ipv6.h"

typedef enum {
    CHAR_TYPE_DIGIT,
    CHAR_TYPE_SEP,
    CHAR_TYPE_SEP4,
    CHAR_TYPE_OTHER,
    CHAR_TYPE_MAX
} char_type_t;
inline char_type_t getCharType(char ch)
{
    if (isxdigit(ch)) {
        return CHAR_TYPE_DIGIT;
    } else if (':' == ch) {
        return CHAR_TYPE_SEP;
    } else if ('.' == ch) {
        return CHAR_TYPE_SEP4;
    }
    return CHAR_TYPE_OTHER;
}

typedef enum {
    TOKEN_START,
    TOKEN_NUM,
    TOKEN_SEP,
    TOKEN_RALIGN,
    TOKEN_SEP4,
    TOKEN_INVALID
} token_type_t;
inline token_type_t getTokenType(char_type_t type, size_t length, char *buf)
{
    int8_t i;
    if (CHAR_TYPE_DIGIT == type) {
        return TOKEN_NUM;
    } else if (CHAR_TYPE_SEP4 == type) {
        return TOKEN_SEP4;
    } else if (CHAR_TYPE_SEP == type) {
        return length > 1 ? TOKEN_RALIGN : TOKEN_SEP;
    }
    return TOKEN_INVALID;
}

typedef struct {
    token_type_t lastTokenType;
    char lastTokenData[5];
    bool ralign;
    uint16_t leftData[8];
    uint16_t rightData[8];
    uint8_t leftSize;
    uint8_t rightSize;
    uint8_t ipv4NumCount;
} ipv6_pton_data_t;
inline bool writeNumIPv4(ipv6_pton_data_t *data)
{
    char *p = data->lastTokenData;
    uint16_t val = 0;
    // Number with leading 0 is not allowed by IPv4
    if ('0' == *p && '\0' != *(p + 1)) {
        return false;
    }
    // Check whether all characters are dec digits and value is lower than 255
    while ('\0' != *p) {
        if (!isdigit(*p)) {
            return false;
        }
        val *= 10;
        val += (*p - '0');
        if (val > 0xff) {
            return false;
        }
        p++;
    }
    if (data->ralign) {
        if (data->ipv4NumCount & 1) {
            data->rightData[data->rightSize] = val << 8;
            (data->rightSize)++;
        } else {
            data->rightData[data->rightSize-1] |= val;
        }
    } else {
        if (data->ipv4NumCount & 1) {
            data->leftData[data->leftSize] = val << 8;
            (data->leftSize)++;
        } else {
            data->leftData[data->leftSize-1] |= val;
        }
    }
    return true;
}
inline bool writeNum(ipv6_pton_data_t *data)
{
    char *p = NULL;
    uint16_t val = 0;
    if ((data->leftSize + data->rightSize) >= 8) {
        return false;
    }
    if (data->ipv4NumCount > 0) {
        return writeNumIPv4(data);
    }
    for (p = data->lastTokenData; '\0' != *p; p++) {
        val <<= 4;
        val |= hexdigit2num(*p);
    }
    if (data->ralign) {
        data->rightData[data->rightSize] = val;
        (data->rightSize)++;
    } else {
        data->leftData[data->leftSize] = val;
        (data->leftSize)++;
    }
    return true;
}
inline bool processNum(ipv6_pton_data_t *data, size_t length, char *buf)
{
    uint8_t i;
    if (TOKEN_NUM == data->lastTokenType) {
        return false;
    }
    for (i = 0; i < length; i++) {
        data->lastTokenData[i] = buf[i];
    }
    data->lastTokenData[length] = '\0';
    return true;
}
inline bool processSep(ipv6_pton_data_t *data)
{
    if (data->lastTokenType != TOKEN_NUM || 
        data->ipv4NumCount > 0) {
        return false;
    }
    return writeNum(data);
}
inline bool processRAlign(ipv6_pton_data_t *data)
{
    bool status = true;
    if (TOKEN_SEP == data->lastTokenType ||
        TOKEN_SEP4 == data->lastTokenType || 
        data->ipv4NumCount > 0) {
        return false;
    }
    if (TOKEN_NUM == data->lastTokenType) {
        status = writeNum(data);
    }
    data->ralign = true;
    return status;
}
inline bool processSep4(ipv6_pton_data_t *data)
{
    if (data->lastTokenType != TOKEN_NUM || data->ipv4NumCount >= 4) {
        return false;
    }
    (data->ipv4NumCount)++;
    return writeNum(data);
}
inline bool processToken(ipv6_pton_data_t *data, char_type_t type, size_t length, char *buf)
{
    bool status;
    token_type_t tokenType = getTokenType(type, length, buf);
    if (TOKEN_INVALID == tokenType) {
        return false;
    }
    switch (tokenType) {
        case TOKEN_NUM:
            status = processNum(data, length, buf);
        break;
        case TOKEN_SEP:
            status = processSep(data);
        break;
        case TOKEN_SEP4:
            status = processSep4(data);
        break;
        case TOKEN_RALIGN:
            status = processRAlign(data);
        break;
    }
    data->lastTokenType = tokenType;
    return status;
}
inline bool processEnd(ipv6_pton_data_t *data)
{
    if (TOKEN_RALIGN == data->lastTokenType) {
        
        return (data->leftSize < 8);
    }
    if (TOKEN_NUM != data->lastTokenType || (data->ipv4NumCount > 0 && data->ipv4NumCount != 3)) {
        return false;
    }
    if (data->ipv4NumCount > 0) {
        (data->ipv4NumCount)++;
    }
    if (!writeNum(data)) {
        return false;
    }
    if ((!data->ralign && data->leftSize != 8) || (data->leftSize + data->rightSize > 8)) {
        return false;
    }
    return true;
}
static uint8_t g_charTypeLenMax[CHAR_TYPE_MAX] = { 4, 2, 1, 0 };
bool ipv6_pton(const char *input, ipv6addr_t *addr)
{
    ipv6_pton_data_t data;
    char *p = NULL;
    uint8_t i;
    char_type_t lastCharType;
    char buf[4], *pBuf = buf;
    data.lastTokenType = TOKEN_START;
    data.ralign = false;
    data.leftSize = data.rightSize = 0;
    data.ipv4NumCount = 0;
    for (p = (char*)input; *p != '\0'; p++) {
        char_type_t charType = getCharType(*p);
        if (CHAR_TYPE_OTHER == charType) {
             return false;
        }
        if (pBuf > buf && lastCharType != charType) {
            // Process token
            if (!processToken(&data, lastCharType, pBuf - buf, buf)) {
                return false;
            }
            pBuf = buf;
        }
        // Process character
        if ((pBuf - buf) >= g_charTypeLenMax[charType]) {
            return false;
        }
        lastCharType = charType;
        *pBuf = *p;
        pBuf++;
    }
    // Process last token
    if ((pBuf > buf) && !processToken(&data, lastCharType, pBuf - buf, buf)) {
        return false;
    }
    // Process end
    if (!processEnd(&data)) {
        return false;
    }

    // Write ipv6 bin to target
    for (i=0; i<8; i++) {
        if (i < data.leftSize) {
            addr->d[i] = data.leftData[i];
        } else if (i >= (8 - data.rightSize)) {
            addr->d[i] = data.rightData[i + data.rightSize - 8];
        } else {
            addr->d[i] = 0;
        }
    }
    return true;
}
static char *ipv6_ntop_uncomp(ipv6addr_t *addr, char *buf) {
    uint8_t i;
    char *p = buf;
    for (i = 0; i < 8; i++) {
        if(i != 0){
            *p = ':';
            p++;
        }
        utoa(addr->d[i], p, 16);
        while(*p != '\0'){
            p++;
        }
    }
    return buf;
}
static char *ipv6_ntop_full(ipv6addr_t *addr, char *buf) {
    uint8_t i, j;
    char *p = buf;
    for (i = 0; i < 8; i++) {
        if(i != 0){
            *p = ':';
            p++;
        }
        u16tohex(addr->d[i], p, false);
        while(*p != '\0'){
            p++;
        }
    }
    return buf;
}
char *ipv6_ntop(ipv6addr_t *addr, char *buf, ipv6_output_format_t format)
{
    int8_t zeroStart = -1, zeroLen = 0;
    uint8_t i;
    uint32_t ipv4data;
    char *p = buf;
    switch(format){
        case IPV6_FORMAT_FULL:
            return ipv6_ntop_full(addr, buf);        
        break;
        case IPV6_FORMAT_UNCOMP:
            return ipv6_ntop_uncomp(addr, buf);
        break;
    }

    // Check zero segment range
    for (i = 0; i < 8; i++) {
        if (zeroStart < 0) {
            if (addr->d[i] == 0) {
                zeroStart = i;
                zeroLen = 1;
            }
        } else {
            if (addr->d[i] != 0) {
                break;
            }
            zeroLen++;
        }
    }

    // Print as ::
    if (zeroStart == 0 && zeroLen == 8) {
        buf[0] = buf[1] = ':';
        buf[2] = '\0';
        return buf;
    }
    
    // Print as ::1
    if (zeroStart == 0 && zeroLen == 7 && 1 == addr->d[7]) {
        buf[0] = buf[1] = ':';
        buf[2] = '1';
        buf[3] = '\0';
        return buf;
    }

    // Print as ipv4 addr
    if (zeroStart == 0 && zeroLen >= 6) {
        buf[0] = buf[1] = ':';
        ipv4_ntop(((uint32_t)(addr->d[6]) << 16) | addr->d[7], buf + 2);
        return buf;
    }

    // Print as ipv6
    for (i = 0; i < 8; i++) {
        if (i > zeroStart && i < zeroStart + zeroLen) {
            continue;
        }
        if (i > 0 || i == zeroStart) {
            *p = ':';
            p++;
        }
        if (zeroStart == i) {
            continue;
        }
        utoa(addr->d[i], p, 16);
        while(*p != '\0'){
            p++;
        }
    }
    *p = '\0';

    return buf;
}
uint8_t ipv6_ptonm(char *input)
{
    uint16_t n = 0;
    char *p = NULL;
    // Empty string and string with leading zero not allowed
    if ('\0' == *input || ('0' == *input && '\0' != *(input+1))) {
        return INVALID_NETMASK;
    }
    for (p = input; *p != '\0'; p++) {
         if (!isdigit(*p)) {
             return INVALID_NETMASK;
         }
         n *= 10;
         n += *p - '0';
         if (n > 128) {
             return INVALID_NETMASK;
         }
    }
    return (uint8_t)n;
}
void ipv6_apply_netmask(ipv6addr_t *addr, uint8_t netmask, bool nonzero)
{
    uint8_t procSegs = netmask >> 4, procBits = netmask & 0xf;
    uint8_t i = 7;
    while (procSegs) {
        addr->d[i] = nonzero ? 0xffff : 0;
        i--;
        procSegs--;
    }
    if (procBits > 0) {
        if (nonzero) {
            addr->d[i] |= ((uint16_t)1 << procBits) - 1;
        } else {
            addr->d[i] &= ~(((uint16_t)1 << procBits) - 1);
        }
    }
}
