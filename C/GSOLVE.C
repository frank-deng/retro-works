#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define GUESS_CHANCES 16
#if !defined(min)
#define min(x, y) ((x) < (y) ? (x) : (y))
#endif

uint16_t uint2bcd(uint16_t num)
{
    uint8_t i=0;
    uint16_t res=0;
    while(num!=0){
        res|=((num%10)<<(4*i));
        num/=10;
        i++;
    }
    return res;
}
bool has_dup_digit(uint16_t num)
{
    uint16_t map=0,dmap;
    uint8_t digit,i;
    for(i=0; i<(sizeof(num)*2); i++){
        digit=(num&0xf);
        dmap=(((uint16_t)1)<<digit);
        if(map&dmap){
            return true;
        }
        map|=dmap;
        num>>=4;
    }
    return false;
}
uint8_t check(uint16_t ans, uint16_t guess)
{
    uint8_t result = 0, i, valAns, valGuess;
    uint8_t existAns[10] = {0,0,0,0,0,0,0,0,0,0};
    uint8_t existGuess[10] = {0,0,0,0,0,0,0,0,0,0};
    for (i = 0; i < 4; i++) {
        valAns = ans & 0xf;
        valGuess = guess & 0xf;
        ans >>= 4;
        guess >>= 4;
        if (valAns == valGuess) {
            result += 0x10;
            continue;
        }
        existAns[valAns]++;
        existGuess[valGuess]++;
    }
    for (i = 0; i < 10; i++) {
        result += min(existAns[i], existGuess[i]);
    }
    return result;
}
void print_help(const char *app_name)
{
    char *app_name_last_posix=strrchr(app_name,'/');
    char *app_name_last_win=strrchr(app_name,'\\');
    if(NULL!=app_name_last_posix){
        app_name=app_name_last_posix+1;
    }else if(NULL!=app_name_last_win){
        app_name=app_name_last_win+1;
    }
    fprintf(stderr,"Usage: %s [-m] NNNN,XaYb NNNN,XaYb ...\n",app_name);
}
int main(int argc, char** argv){
    int optind=1;
    bool mastermind=false;
    uint16_t g_num[GUESS_CHANCES],n0,n;
    uint8_t g_res[GUESS_CHANCES],len,i;
    bool passed;
    if(optind<argc && strcmp(argv[optind],"-m")==0){
        mastermind=true;
        optind++;
    }
    for(i=0; optind<argc && len<GUESS_CHANCES; optind++,i++){
        unsigned int num=0xffff,a=0xff,b=0xff;
        sscanf(argv[optind],"%u,%ua%ub",&num,&a,&b);
        if(num>9999 || a>3 || b>4){
            fprintf(stderr,"Invalid input at parameter %u.\n",i+1);
            print_help(argv[0]);
            return 1;
        }
        n=uint2bcd((uint16_t)num);
        if(!mastermind && has_dup_digit(n)){
            fprintf(stderr,"Duplicated digit at parameter %u.\n",i+1);
            return 1;
        }
        g_num[i]=n;
        g_res[i]=(uint8_t)((a<<4)|b);
    }
    len=i;
    if(len<=0){
        print_help(argv[0]);
        return 1;
    }
    
    for(n0=0;n0<=9999;n0++){
        n=uint2bcd(n0);
        if(!mastermind && has_dup_digit(n)){
            continue;
        }
        passed=true;
        for(i=0;i<len;i++){
            if(check(n,g_num[i])!=g_res[i]){
                passed=false;
                break;
            }
        }
        if(passed){
            printf("%04x ",n);
        }
    }
    puts("");
    return 0;
}
