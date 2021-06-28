#include <stdio.h>

void dumpData(unsigned char *data, unsigned int len){
    unsigned int i=0;
    for(i=0; i<len; i++){
        printf("%02x  ",*(data+i));
    }
    puts("");
}
