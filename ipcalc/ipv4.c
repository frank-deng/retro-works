#include <ctype.h>
#include <stdlib.h>
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
    ipv4_pton_data_t ipv4PtonData = {'\0', 0, 0, 0};
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
int8_t ipv4_get_netmask(uint32_t input)
{
    uint32_t n = ~input;
    if ((n & (n + 1)) != 0) {
        return -1;
    }
    return (int8_t)count_leading_zero(n);
}
int8_t ipv4_ptonm(char *input)
{
    bool parseAsNumberSucc = true;
    uint32_t n = 0;
    char *p = NULL;
    // Empty string not allowed
    if ('\0' == *input) {
        return -1;
    }
    // First try to parse input as dec number
    for (p = input; *p != '\0'; p++) {
         if (!isdigit(*p)) {
             parseAsNumberSucc = false;
             break;
         }
         n *= 10;
         n += *p - '0';
         if (n > 32) {
             parseAsNumberSucc = false;
             break;
         }
    }
    if (parseAsNumberSucc) {
        return (int8_t)n;
    }
    // Try to parse input as ip
    if (!ipv4_pton(input, &n)) {
         return -1;
    }
    n = ~n;
    if ((n & (n + 1)) != 0) {
        return -1;
    }
    return (int8_t)count_leading_zero(n);
}
char *ipv4_ntop(uint32_t input, char *buf)
{
    uint8_t i;
    char *p = buf;
    for (i = 0; i < 4; i++) {
        if (i != 0) {
            *p = '.';
            p++;
        }
        utoa(((input >> (8 * (3 - i))) & 0xff), p, 10);
        while (*p != '\0') {
            p++;
        }
    }
    return buf;
}