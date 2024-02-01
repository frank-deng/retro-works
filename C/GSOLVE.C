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
uint8_t check_s(uint16_t ans, uint16_t guess)
{
    uint8_t result = 0, i, valAns, valGuess;
    uint16_t existAns = 0, existGuess = 0;
    for (i = 0; i < 4; i++) {
        valAns = ans & 0xf;
        valGuess = guess & 0xf;
        ans >>= 4;
        guess >>= 4;
        if (valAns == valGuess) {
            result += 0x10;
            continue;
        }
        existAns |= (1 << valAns);
        existGuess |= (1 << valGuess);
    }
    existGuess &= existAns;
    while (existGuess != 0) {
        result++;
        existGuess = existGuess & (existGuess - 1);
    }
    return result;
}
uint8_t check_m(uint16_t ans, uint16_t guess)
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

typedef struct{
    uint16_t num;
    uint8_t res;
}guess_input_t;

bool parse_input(const char *str,bool mastermind,guess_input_t *input)
{
    unsigned int num,a,b;
    uint16_t num_bcd;
    if(sscanf(str,"%u,%ua%ub",&num,&a,&b)!=3){
        return false;
    }
    num_bcd=uint2bcd((uint16_t)num);
    if(!mastermind && has_dup_digit(num_bcd)){
        return false;
    }
    input->num=num_bcd;
    input->res=(uint8_t)((a<<4)|b);
    return true;
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
    unsigned char opt;
    bool mastermind=false;
    guess_input_t guess[GUESS_CHANCES];
    uint8_t len,i,cmp;
    uint16_t n0,n;
    bool passed;
    if(strcmp(argv[optind],"-m")==0){
        mastermind=true;
        optind++;
    }
    
    len=argc-optind;
    if(len<=0){
        fprintf(stderr,"Guess history required.\n");
        print_help(argv[0]);
        return 1;
    }
    if(len>GUESS_CHANCES){
        len=GUESS_CHANCES;
    }
    for(i=0;i<len;i++){
        if(!parse_input(argv[optind+i],mastermind,&guess[i])){
            fprintf(stderr,"Invalid input at parameter %u.\n",i+1);
            print_help(argv[0]);
            return 1;
        }
    }
    for(n0=0;n0<=9999;n0++){
        n=uint2bcd(n0);
        if(!mastermind && has_dup_digit(n)){
            continue;
        }
        passed=true;
        for(i=0;i<len;i++){
            cmp=(mastermind ? check_m(guess[i].num,n) : check_s(guess[i].num,n));
            if(cmp!=guess[i].res){
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
