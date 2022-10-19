#include <stdio.h>
#include "ipv6.h"

typedef struct {
    char lastChar;
    uint8_t digits;
    uint16_t numval;
    bool ralign;
    uint16_t leftData[8];
    uint16_t rightData[8];
    uint8_t leftSize;
    uint8_t rightSize;
} ipv6_pton_data_t;
static inline bool processDigit(ipv6_pton_data_t *data, char ch)
{
    if (!ishexdigit(ch) || data->digits >= 4) {
        return false;
    }
    data->numval <<= 4;
    data->numval |= hexdigit2num(ch);
    (data->digits)++;
    return true;
}
static inline bool processSep(ipv6_pton_data_t *data)
{
    if (':' == data->lastChar) {
        if (data->ralign) {
            return false;
        }
        data->ralign = true;
        return true;
    }
    if (data->digits <= 0 || (data->leftSize + data->rightSize) > 8) {
        return false;
    }
    if (data->ralign) {
        data->rightData[data->rightSize] = data->numval;
        (data->rightSize)++;
    } else {
        data->leftData[data->leftSize] = data->numval;
        (data->leftSize)++;
    }
    data->digits = 0;
    data->numval = 0;
    return true;
}
static inline bool processEnd(ipv6_pton_data_t *data)
{
    if (data->digits <= 0) {
        return true;
    }
    if ((data->leftSize + data->rightSize) >= 8) {
        return false;
    }
    if (data->ralign) {
        data->rightData[data->rightSize] = data->numval;
        (data->rightSize)++;
    } else {
        data->leftData[data->leftSize] = data->numval;
        (data->leftSize)++;
    }
    return true;
}
bool ipv6_pton(const char *input, ipv6addr_t *addr)
{
    ipv6_pton_data_t data;
    char *p = NULL;
    uint8_t i;
    data.lastChar='\0';
    data.digits=0;
    data.numval=0;
    data.ralign=false;
    data.leftSize=0;
    data.rightSize=0;
    for (p = (char*)input; *p != '\0'; p++) {
        if (ishexdigit(*p)) {
            if (!processDigit(&data, *p)) {
                return false;
            }
        } else if (':' == *p) {
            if (!processSep(&data)) {
                return false;
            }
        } else {
            return false;
        }
        data.lastChar = *p;
    }
    if (!processEnd(&data)) {
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