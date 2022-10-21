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
    for (i = 0; i < length; i++) {
        putchar(buf[i]);
    }
    putchar('\n');
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
    size_t tokenLength;
    char tokenData[4];
    bool ralign;
    uint16_t leftData[8];
    uint16_t rightData[8];
    uint8_t leftSize;
    uint8_t rightSize;
} ipv6_pton_data_t;
inline void writeNum(ipv6_pton_data_t *data)
{
    uint8_t i;
    uint16_t val = 0;
    for (i = 0; i < data->tokenLength; i++) {
        val <<= 10;
        val |= hexdigit2num(data->tokenData[i]);
    }
    if (data->ralign) {
        data->rightData[data->rightSize] = val;
        (data->rightSize)++;
    } else {
        data->leftData[data->leftSize] = val;
        (data->leftSize)++;
    }
}
inline bool processNum(ipv6_pton_data_t *data, char_type_t type, size_t length, char *buf)
{
    uint8_t i;
    if (data->lastTokenType == TOKEN_NUM) {
        return false;
    }
    data->lastTokenType = type;
    data->tokenLength = length;
    for (i = 0; i < length; i++) {
        data->tokenData[i] = buf[i];
    }
    return true;
}
inline bool processSep(ipv6_pton_data_t *data, char_type_t type, size_t length, char *buf)
{
    if (data->lastTokenType != TOKEN_NUM) {
        return false;
    }
    writeNum(data);
    return true;
}
inline bool processRAlign(ipv6_pton_data_t *data, char_type_t type, size_t length, char *buf)
{
    if (TOKEN_SEP == data->lastTokenType || TOKEN_SEP4 == data->lastTokenType) {
        return false;
    }
    writeNum(data);
    data->ralign = true;
    return true;
}
inline bool processToken(ipv6_pton_data_t *data, char_type_t type, size_t length, char *buf)
{
    token_type_t tokenType = getTokenType(type, length, buf);
    bool status;

    if (TOKEN_INVALID == tokenType) {
        return false;
    }
    switch (tokenType) {
        case TOKEN_NUM:
            status = processNum(data, type, length, buf);
        break;
        case TOKEN_SEP:
            status = processSep(data, type, length, buf);
        break;
        case TOKEN_SEP4:
            //status = processSep4(data, type, length, buf);
        break;
        case TOKEN_RALIGN:
            status = processRAlign(data, type, length, buf);
        break;
    }
    data->lastTokenType = type;
    return status;
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
    data.tokenLength = 0;
    data.ralign = false;
    data.leftSize = data.rightSize = 0;

    // Empty string not allowed
    if ('\0' == *input) {
        return false;
    }
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
    if (!processToken(&data, lastCharType, pBuf - buf, buf)) {
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