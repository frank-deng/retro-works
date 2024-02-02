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

static inline uint16_t int2bcd(uint16_t n, bool *digit_unique_out)
{
    uint16_t digit=(n%10),result=digit,map=(1<<digit);
    bool digit_unique=true;

    n/=10;
    digit=n%10;
    if ((map & (1<<digit)) != 0) {
        digit_unique=false;
    }
    map |= (1<<digit);
    result |= (digit<<4);

    n/=10;
    digit=n%10;
    if ((map & (1<<digit)) != 0) {
        digit_unique=false;
    }
    map |= (1<<digit);
    result |= (digit<<8);

    n/=10;
    digit=n%10;
    if ((map & (1<<digit)) != 0) {
        digit_unique=false;
    }
    result |= (digit<<12);

    if(NULL!=digit_unique_out) {
        *digit_unique_out=digit_unique;
    }

    return result;
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
#define NUM_UNIQUE_COUNT 5040
#define NUM_TOTAL_COUNT 10000

static uint16_t numbers_pool[NUM_TOTAL_COUNT];
static uint16_t numbers_buf[NUM_TOTAL_COUNT];
static void init_guess()
{
    uint16_t n, nbcd, *n_unique=numbers_pool, *n_dup=numbers_pool+NUM_UNIQUE_COUNT;
    bool digit_unique=true;
    for(n=0; n<NUM_TOTAL_COUNT; n++) {
        nbcd=int2bcd(n,&digit_unique);
        if(digit_unique) {
            *n_unique=nbcd;
            n_unique++;
        } else {
            *n_dup=nbcd;
            n_dup++;
        }
    }
    srand(time(NULL));
}
static inline uint8_t guess_s() {
    uint16_t ans=numbers_pool[rand()%NUM_UNIQUE_COUNT], times=0, count=NUM_UNIQUE_COUNT;
    uint16_t n,n2,*nums=numbers_pool,*np,*np2,*np_end;
    uint8_t cmp;
    while (times < GUESS_CHANCES && count>0) {
        times++;
        n=nums[rand()%count];
        if(n==ans) {
            break;
        }
        cmp=check_s(ans,n);
        
        if(nums!=numbers_buf) {
            // First guess
            np=nums;
            np2=numbers_buf;
            nums=numbers_buf;
        } else {
            np=np2=numbers_buf;
        }

        np_end=np+count;
        while(np<np_end) {
            n2=*np;
            if(n!=n2 && check_s(n2,n)==cmp) {
                *np2=n2;
                np2++;
            }
            np++;
        }
        count=np2-numbers_buf;
    }
    if(times>=GUESS_CHANCES || 0==count) {
        return GUESS_CHANCES;
    }
    return times;
}
static inline uint8_t guess_m() {
    uint16_t ans=numbers_pool[rand()%NUM_TOTAL_COUNT], times=0, count=NUM_TOTAL_COUNT;
    uint16_t n,n2,*nums=numbers_pool,*np,*np2,*np_end;
    uint8_t cmp;
    while (times < GUESS_CHANCES && count>0) {
        times++;
        n=nums[rand()%count];
        if(n==ans) {
            break;
        }
        cmp=check_m(ans,n);

        if(nums!=numbers_buf) {
            // First guess
            np=nums;
            np2=numbers_buf;
            nums=numbers_buf;
        } else {
            np=np2=numbers_buf;
        }

        np_end=np+count;
        while(np<np_end) {
            n2=*np;
            if(n!=n2 && check_m(n2,n)==cmp) {
                *np2=n2;
                np2++;
            }
            np++;
        }
        count=np2-numbers_buf;
    }
    if(times>=GUESS_CHANCES || 0==count) {
        return GUESS_CHANCES;
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
static inline void _clrscr()
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
static void draw_screen()
{
    _clrscr();
#if defined(__DOS__)
    goto_rowcol(24,0);
    cprintf("Press Esc to quit.");
#else
    goto_rowcol(19,0);
    printf("Press Ctrl-c to quit.");
#endif
    goto_rowcol(0,0);
    printf("Guesses %10s %10s\n", "Normal", "Mastermind");
}

static bool running=true;
#if !defined(__DOS__)
static bool refresh=true;
static void do_exit_signal(int signo)
{
    running=false;
}
static void do_refresh_signal(int signo)
{
    refresh=true;
}
#endif

void print_report(uint32_t report_s[GUESS_CHANCES], uint32_t report_m[GUESS_CHANCES])
{
    uint8_t i,last_record=GUESS_CHANCES;
    uint32_t total_s=0, total_m=0;
    goto_rowcol(1,0);
    while(last_record>8) {
        if(report_s[last_record-1]!=0 || report_m[last_record-1]!=0) {
            break;
        }
        last_record--;
    }
    for(i=0; i<last_record; i++) {
        total_s+=report_s[i];
        total_m+=report_m[i];
        printf("%-2u      %10lu %10lu\n", i+1, report_s[i], report_m[i]);
    }
    printf("Total: %lu\n", total_s);
}

void read_file(char *path, uint32_t *report_s, uint32_t *report_m)
{
    char buf[80];
    uint8_t i;
    unsigned int guesses;
    unsigned long count_s,count_m;
    FILE *fp=fopen(path, "r");
    if(NULL==fp) {
        return;
    }
    fgets(buf,sizeof(buf),fp);
    for(i=0; i<GUESS_CHANCES && !feof(fp); i++) {
        fscanf(fp,"%u,%lu,%lu\n",&guesses,&count_s,&count_m);
        report_s[i]=(uint32_t)count_s;
        report_m[i]=(uint32_t)count_m;
    }
    fclose(fp);
}
void write_file(char *path, uint32_t *report_s, uint32_t *report_m)
{
    uint8_t i,last_record=GUESS_CHANCES;
    FILE *fp=fopen(path, "w");
    if(NULL==fp) {
        return;
    }
    while(last_record>8) {
        if(report_s[last_record-1]!=0 || report_m[last_record-1]!=0) {
            break;
        }
        last_record--;
    }
    fprintf(fp,"Guesses,Normal,Mastermind\n");
    for(i=0; i<last_record; i++) {
        fprintf(fp,"%u,%lu,%lu\n",i+1,report_s[i],report_m[i]);
    }
    fclose(fp);
}
int main(int argc, char *argv[])
{
    char *fname="guessnum.csv";
    uint32_t report_s[GUESS_CHANCES]= {0,0,0,0,0,0,0,0,0,0,0,0};
    uint32_t report_m[GUESS_CHANCES]= {0,0,0,0,0,0,0,0,0,0,0,0};
    time_t t_print=time(NULL),t_write=t_print,t;
    if(argc>1) {
        fname=argv[1];
    }
    read_file(fname,report_s,report_m);
    init_guess();
    draw_screen();
    print_report(report_s,report_m);
#if !defined(__DOS__)
    signal(SIGINT,do_exit_signal);
    signal(SIGQUIT,do_exit_signal);
    signal(SIGTERM,do_exit_signal);
    signal(SIGWINCH,do_refresh_signal);
#endif
    
    while(running) {
#if defined(__DOS__)
        if(kbhit() && 27==getch()){
            running=false;
            break;
        }
#else
        if(refresh){
            refresh=false;
            draw_screen();
            print_report(report_s,report_m);
        }
#endif
        report_s[guess_s()-1]++;
        report_m[guess_m()-1]++;
        t=time(NULL);
        if(t-t_print >= 1){
            print_report(report_s,report_m);
            t_print=t;
        }
        if(t-t_write >= 30){
            write_file(fname,report_s,report_m);
            t_write=t;
        }
    }
    _clrscr();
    write_file(fname,report_s,report_m);
    return 0;
}
