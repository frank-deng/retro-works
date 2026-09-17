#include <stdlib.h>
#include <ctype.h>
#include "ipv4.h"

typedef struct {
    char lastChar;
    uint8_t segments;
    uint16_t numval;
    uint32_t result;
} ipv4_pton_data_t;
static inline bool processDigit(ipv4_pton_data_t *data, char ch)
{
    if (0 == data->numval && '0' == data->lastChar) {
        return false;
    }
    data->numval *= 10;
    data->numval += ch - '0';
    if (data->numval > 0xff) {
        return false;
    }
    return true;
}
static inline bool processDot(ipv4_pton_data_t *data)
{
    if (!isdigit(data->lastChar) || data->segments >= 3) {
        return false;
    }
    (data->segments)++;
    data->result <<= 8;
    data->result |= (uint8_t)(data->numval);
    data->numval = 0;
    return true;
}
static inline bool processEnd(ipv4_pton_data_t *data)
{
    if (!isdigit(data->lastChar) || data->segments != 3) {
        return false;
    }
    data->result <<= 8;
    data->result |= (uint8_t)(data->numval);
    return true;
}
bool ipv4_pton(const char *str, uint32_t *target)
{
    char *p = NULL;
    ipv4_pton_data_t ipv4PtonData = {true, '\0', 0, 0};
    for (p = (char*)str; *p != '\0'; p++) {
        if (isdigit(*p)) {
            if (!processDigit(&ipv4PtonData, *p)) {
                return false;
            }
        } else if ('.' == *p) {
            if (!processDot(&ipv4PtonData)) {
                return false;
            }
        } else {
            return false;
        }
        ipv4PtonData.lastChar = *p;
    }
    if (!processEnd(&ipv4PtonData)) {
        return false;
    }
    *target = ipv4PtonData.result;
    return true;
}

static inline uint8_t count_leading_zero(uint32_t input)
{
    uint8_t result = 0;
    uint32_t tmp;
    tmp = (input >> 16) & 0xffff;
    if (tmp != 0) {
        input = tmp;
    } else {
        result += 16;
    }

    tmp = (input >> 8) & 0xff;
    if (tmp != 0) {
        input = tmp;
    } else {
        result += 8;
    }

    tmp = (input >> 4) & 0xf;
    if (tmp != 0) {
        input = tmp;
    } else {
        result += 4;
    }

    tmp = (input >> 2) & 0x3;
    if (tmp != 0) {
        input = tmp;
    } else {
        result += 2;
    }

    if ((input & 0x2) == 0) {
        result++;
    } else {
        return result;
    }
    if ((input & 0x1) == 0) {
        result++;
    }
    return result;
}
uint8_t ipv4_ptonm(char *input)
{
    bool parseAsNumberSucc = true;
    // Try to parse input as number
    uint32_t n = atouint(input, 32, &parseAsNumberSucc);
    if (parseAsNumberSucc) {
        return (uint8_t)n;
    }
    // Try to parse input as ip
    if (!ipv4_pton(input, &n)) {
         return INVALID_NETMASK;
    }
    n = ~n;
    if ((n & (n + 1)) != 0) {
        return INVALID_NETMASK;
    }
    return count_leading_zero(n);
}
char *ipv4_ntop(uint32_t input, char *buf)
{
    char *p = buf;
    uint8_t i;
    for (i = 0; i < 4; i++) {
        if(i != 0){
            *p = '.';
            p++;
        }
        p += utodec((input>>((3-i)<<3)) & 0xff, p);
    }
    return buf;
}