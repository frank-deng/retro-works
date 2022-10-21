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
        return MATCH_DIGIT;
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
} ipv6_data_t;
bool processToken(ipv6_pton_data_t *data, char_type_t type, size_t length, char *buf)
{
    token_type_t tokenType = getTokenType(type, length, buf);
    if (TOKEN_INVALID == tokenType) {
        return false;
    }
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
    for (p = (char*)input; *p != '\0'; p++) {
        char_type_t charType = getCharType(*p);
        if (CHAR_TYPE_INVALID == charType) {
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
    if (lastCharType == CHAR_EMPTY) {
        return false;
    }
    if (!processToken(&data, buf, pBuf - buf)) {
        return false;
    }
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