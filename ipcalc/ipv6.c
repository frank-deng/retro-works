#include <ctype.h>
#include <stdio.h>
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
    int8_t sep4Count;
} ipv6_pton_data_t;
inline bool writeNum(ipv6_pton_data_t *data)
{
    char *p = NULL;
    uint16_t val = 0;
    if ((data->leftSize + data->rightSize) >= 8) {
        return false;
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
        data->sep4Count >= 0) {
        return false;
    }
    return writeNum(data);
}
inline bool processRAlign(ipv6_pton_data_t *data)
{
    bool status;
    if (TOKEN_SEP == data->lastTokenType ||
        TOKEN_SEP4 == data->lastTokenType || 
        data->sep4Count >= 0) {
        return false;
    }
    status = writeNum(data);
    data->ralign = true;
    return status;
}
inline bool processSep4(ipv6_pton_data_t *data)
{
    char *p = data->lastTokenData;
    uint16_t val = 0;
    if (data->lastTokenType != TOKEN_NUM || data->sep4Count >= 3) {
        return false;
    }
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
    (data->sep4Count)++;
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
        return true;
    }
    if (TOKEN_NUM != data->lastTokenType || (data->sep4Count >= 0 && data->sep4Count != 3)) {
        return false;
    }
    return writeNum(data);
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
    data.sep4Count = -1;
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
char *ipv6_ntop(ipv6addr_t *addr, char *buf, ipv6_output_format_t format)
{
    switch(format){
        case IPV6_FORMAT_FULL:
            sprintf(buf, "%04x:%04x:%04x:%04x:%04x:%04x:%04x:%04x",
                addr->d[0], addr->d[1], addr->d[2], addr->d[3],
                addr->d[4], addr->d[5], addr->d[6], addr->d[7]);
        break;
        case IPV6_FORMAT_UNCOMP:
            sprintf(buf, "%x:%x:%x:%x:%x:%x:%x:%x",
                addr->d[0], addr->d[1], addr->d[2], addr->d[3],
                addr->d[4], addr->d[5], addr->d[6], addr->d[7]);
        break;
    }
    return buf;
}