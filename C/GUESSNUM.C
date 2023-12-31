#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#if defined(__DOS__)
#include <dos.h>
#include <conio.h>
#else
#include<signal.h>
#include<unistd.h>
#endif

#if !defined(max)
#define max(x, y) ((x) > (y) ? (x) : (y))
#endif
#if !defined(min)
#define min(x, y) ((x) < (y) ? (x) : (y))
#endif

#define BCD_INVALID_NUM (0xffff)

static inline uint16_t int2bcd_s(uint16_t n)
{
    uint16_t digit=(n%10),result=digit,map=(1<<digit);
    
    n/=10; digit=n%10;
    if ((map & (1<<digit)) != 0) {
         return BCD_INVALID_NUM;
    }
    map |= (1<<digit);
    result |= (digit<<4);
    
    n/=10; digit=n%10;
    if ((map & (1<<digit)) != 0) {
         return BCD_INVALID_NUM;
    }
    map |= (1<<digit);
    result |= (digit<<8);
    
    n/=10; digit=n%10;
    if ((map & (1<<digit)) != 0) {
         return BCD_INVALID_NUM;
    }
    result |= (digit<<12);
    
    return result;
}
static inline uint16_t int2bcd_m(uint16_t n)
{
    uint16_t result=(n%10);
    n/=10;
    result |= ((n%10)<<4);
    n/=10;
    result |= ((n%10)<<8);
    n/=10;
    result |= ((n%10)<<12);
    return result;
}
static inline uint16_t gen_answer(bool allow_dup_digit)
{
    uint16_t n,res;
    do{
        n=rand();
        res=allow_dup_digit?int2bcd_m(n):int2bcd_s(n);
    }while(BCD_INVALID_NUM==res);
    return res;
}
static inline uint8_t check_s(uint16_t ans, uint16_t guess)
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
static inline uint8_t check_m(uint16_t ans, uint16_t guess)
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

#define GUESS_CHANCES 16
#define CANDIDATES_COUNT 5040
#define BUF_SIZE 10080
#define NUM_START 123
#define NUM_END 9876
#define MASTERMIND_MAX 10000

static uint16_t numbers_pool[BUF_SIZE];
static uint16_t numbers_buf[BUF_SIZE];
static void init_guess()
{
    uint16_t n,n2,*np;
    for(n=NUM_START,np=numbers_pool; n<=NUM_END; n++){
		n2=int2bcd_s(n);
		if(n2==BCD_INVALID_NUM){
	   	 continue;
		}
		*np=n2; np++;
    }
}
static uint8_t guess_s(){
    uint16_t ans=gen_answer(false), times=0, count=CANDIDATES_COUNT;
    uint16_t n,n2,*nums=numbers_pool,*np,*np2,*np_end;
    uint8_t cmp;

    // Start guess
    while (times < GUESS_CHANCES) {
        if(0==count){
            return 0;
        }
        
	    times++;
	    n=nums[rand()%count];
	    cmp=check_s(ans,n);
	    if(0x40==cmp){
		    break;
	    }
        
        if(nums!=numbers_buf){
            // First guess
            np=nums; np2=numbers_buf;
            nums=numbers_buf;
        }else{
       	 np=np2=numbers_buf; 
        }
        
        np_end=np+count;
        while(np<np_end){
        	n2=*np;
            if(n!=n2 && check_s(n2,n)==cmp){
            	*np2=n2; np2++;
            }
            np++;
        }
        count=np2-numbers_buf;
    }
    return times;
}
static uint8_t guess_m(){
    uint16_t ans=gen_answer(true), times=1, count=MASTERMIND_MAX;
    uint16_t n,n2,nbcd,*nums=numbers_buf,*np,*np2,*np_end;
    uint8_t cmp;
    
    // First guess
    n=int2bcd_m(rand()%MASTERMIND_MAX);
    cmp=check_m(ans,n);
	if(0x40==cmp){
        return times;
	}
    for(n2=0,np=numbers_buf; n2<MASTERMIND_MAX; n2++){
        nbcd=int2bcd_m(n2);
        if(nbcd==n || check_m(n,nbcd)!=cmp){
            continue;
        }
        *np=nbcd; np++;
    }
    count=np-numbers_buf;
    
    // Later guesses
    while (times < GUESS_CHANCES) {
        if(0==count){
            return 0;
        }
        
	    times++;
	    n=nums[rand()%count];
	    cmp=check_m(ans,n);
	    if(0x40==cmp){
		    break;
	    }
        
    	np=np2=numbers_buf; np_end=np+count;
        while(np<np_end){
        	n2=*np;
            if(n!=n2 && check_m(n2,n)==cmp){
            	*np2=n2; np2++;
            }
            np++;
        }
        count=np2-numbers_buf;
    }
    return times;
}

static inline void goto_rowcol(uint8_t row, uint8_t col)
{
#if defined(__DOS__)
    union REGPACK regs;
    regs.h.ah = 0x02;
    regs.h.bh = 0;
    regs.h.dh = row;
    regs.h.dl = col;
    intr(0x10,&regs);
#else
    printf("\033[%u;%uH",row+1,col+1);
#endif
}
static inline void clrscr()
{
#if defined(__DOS__)
    union REGPACK regs;
	regs.x.ax = 0x0600;
    regs.h.bh = 0x07;
    regs.x.cx = 0;
    regs.h.dh = 24;
    regs.h.dl = 79;
    intr(0x10,&regs);
#else
    printf("\033[2J");
#endif
    goto_rowcol(0,0);
}

static bool running=true;
#if defined(__DOS__)
static void (interrupt far *OrigKeyboardVect)();
static void (interrupt far *OrigTimerVect)();
static uint16_t timer_counter=0;
void interrupt far KeyboardHandler() {
	uint8_t code=inp(0x60);
    uint8_t temp=inp(0x61);
    outp(0x61,temp|0x80);
    outp(0x61,temp&0x7f);
    if(0x1==code){
        running=false;
    }
	outp(0x20,0x20);
}
void interrupt far TimerHandler() {
	timer_counter++;
	outp(0x20,0x20);
}
#else
void do_exit_signal(int signo)
{
    if(signo==SIGINT){
        running=false;
    }
}
#endif
void init()
{
    srand(time(NULL));
    init_guess();
    clrscr();
    printf("Guesses %10s %10s\n", "Normal", "Mastermind");
#if defined(__DOS__)
	OrigKeyboardVect=_dos_getvect(0x09);
    OrigTimerVect=_dos_getvect(0x08);
    _dos_setvect(0x09,KeyboardHandler);
    _dos_setvect(0x08,TimerHandler);
#else
	signal(SIGINT,do_exit_signal);
#endif
}
void before_exit()
{
#if defined(__DOS__)
	_dos_setvect(0x09,OrigKeyboardVect);
    _dos_setvect(0x08,OrigTimerVect);
#endif
}
void print_report(uint32_t report_s[GUESS_CHANCES], uint32_t report_m[GUESS_CHANCES])
{
    uint8_t i,last_record=GUESS_CHANCES;
    uint32_t total_s=0, total_m=0;
    goto_rowcol(1,0);
    while(last_record>8){
        if(report_s[last_record-1]!=0 || report_m[last_record-1]!=0){
            break;
        }
        last_record--;
    }
    for(i=0; i<last_record; i++){
        total_s+=report_s[i];
        total_m+=report_m[i];
        printf("%-2u      %10lu %10lu\n", i+1, report_s[i], report_m[i]);
    }
    printf("Total: %lu\n", total_s);
}

void read_file(char *path, uint32_t report_s[GUESS_CHANCES], uint32_t report_m[GUESS_CHANCES])
{
    char buf[80];
    uint8_t i,guesses,last_record=GUESS_CHANCES;
    FILE *fp=fopen(path, "r");
    if(NULL==fp){
        return;
    }
    fgets(buf,sizeof(buf)-2,fp);
    for(i=0; i<GUESS_CHANCES; i++){
        if(3!=fscanf(fp,"%u,%lu,%lu\n",&guesses,&report_s[i],&report_m[i])){
            break;
        }
    }
    fclose(fp);
}
void write_file(char *path, uint32_t report_s[GUESS_CHANCES], uint32_t report_m[GUESS_CHANCES])
{
    uint8_t i,last_record=GUESS_CHANCES;
    FILE *fp=fopen(path, "w");
    if(NULL==fp){
        return;
    }
    while(last_record>8){
        if(report_s[last_record-1]!=0 || report_m[last_record-1]!=0){
            break;
        }
        last_record--;
    }
    fprintf(fp,"Guesses,Normal,Mastermind\n");
    for(i=0; i<last_record; i++){
        fprintf(fp,"%u,%lu,%lu\n",i+1,report_s[i],report_m[i]);
    }
    fclose(fp);
}
int main(int argc, char *argv[])
{
    char *fname="guessnum.csv";
    uint32_t report_s[GUESS_CHANCES]={0,0,0,0,0,0,0,0,0,0,0,0};
    uint32_t report_m[GUESS_CHANCES]={0,0,0,0,0,0,0,0,0,0,0,0};
    unsigned int interval=0, file_write_counter=0, i;
    time_t t0=time(NULL),t;
    init();
    read_file(fname,report_s,report_m);
    print_report(report_s,report_m);
    while(running){
        report_s[guess_s()-1]++;
        report_m[guess_m()-1]++;
#if defined(__DOS__)
        if(timer_counter>20){
            timer_counter=0;
            print_report(report_s,report_m);
        }
#else
        t=time(NULL);
        if(t!=t0){
            t0=t;
            print_report(report_s,report_m);
        }
#endif
    }
    before_exit();
    write_file(fname,report_s,report_m);
    return 0;
}
