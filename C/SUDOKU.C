#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define HELP_TEXT "Usage: %s file\n"
#define START_CALC "Calculating Sudoku..."
#define END_CALC "Finished.\n"
#define INVALID_NUM_POS "Invalid number at line %d, column %d.\n"
#define DUP_NUM_POS "Duplicated number detected at line %d, column %d.\n"
#define OPEN_FILE_FAILED "Failed to open Sudoku file.\n"
#define NO_ANSWER_POS "No ansert at line %d, column %d.\n"
#define NO_ANSWER "No answer.\n"

enum{
    E_OK,
    E_AGAIN,
    E_INVAL,
    E_FAIL,
};

typedef struct {
    uint8_t x;
    uint8_t y;
    uint8_t grp;
    uint16_t map;
    uint8_t last_num;
} stack_item_t;

static uint8_t group[9][9] = {
    {0,0,0,1,1,1,2,2,2},
    {0,0,0,1,1,1,2,2,2},
    {0,0,0,1,1,1,2,2,2},
    {3,3,3,4,4,4,5,5,5},
    {3,3,3,4,4,4,5,5,5},
    {3,3,3,4,4,4,5,5,5},
    {6,6,6,7,7,7,8,8,8},
    {6,6,6,7,7,7,8,8,8},
    {6,6,6,7,7,7,8,8,8},
};
static uint8_t board[9][9] = {
    {0,0,0,0,0,0,0,0,0},
    {0,0,0,0,0,0,0,0,0},
    {0,0,0,0,0,0,0,0,0},
    {0,0,0,0,0,0,0,0,0},
    {0,0,0,0,0,0,0,0,0},
    {0,0,0,0,0,0,0,0,0},
    {0,0,0,0,0,0,0,0,0},
    {0,0,0,0,0,0,0,0,0},
    {0,0,0,0,0,0,0,0,0},
};

static uint16_t mapx[9],mapy[9],mapgrp[9];
static stack_item_t stack[81];
static uint8_t stack_len=0;

static inline uint8_t trailing_zeros(uint16_t n)
{
    uint8_t res=0;
    if(0==(n&0xff)){
        res+=8;
        n>>=8;
    }
    if(0==(n&0xf)){
        res+=4;
        n>>=4;
    }
    if(0==(n&0x3)){
        res+=2;
        n>>=2;
    }
    if(0==(n&0x1)){
        res+=1;
        n>>=1;
    }
    return res;
}
static inline uint8_t next_num(uint16_t map, uint8_t n)
{
    if(0==map){
        return 0;
    }
    while(n<9){
        n++;
        if(map&(1<<n)){
            return n;
        }
    }
    return 0;
}
void printboard(){
    uint8_t x, y;
    for (y = 0; y < 9; y++){
        for (x = 0; x < 9; x++){
            printf("%d ", board[y][x]);
            if (2 == (x % 3)){
                printf(" ");
            }
        }
        puts("");
        if (2 == (y % 3)){
            puts("");
        }
    }
}
int read_sudoku(char *filename){
    uint8_t x, y, grp;
    uint16_t nmap;
    stack_item_t *sp=stack;
    unsigned int n;
    FILE *fp = fopen(filename, "r");
    if (NULL==fp){
        fprintf(stderr, OPEN_FILE_FAILED);
        return E_FAIL;
    }
    for (y = 0; y < 9; y++){
        for (x = 0; x < 9; x++){
            fscanf(fp, "%u", &n);
            if (n > 9) {
                fprintf(stderr, INVALID_NUM_POS, y+1, x+1);
                return E_INVAL;
            }
            board[y][x]=n;
            grp=group[y][x];
            if (0==n){
                sp->x = x;
                sp->y = y;
                sp->grp = grp;
                sp++;
                stack_len++;
            } else {
                nmap = (((uint16_t)1)<<n);
                if((mapx[x] & nmap)||(mapy[y] & nmap)||(mapgrp[grp] & nmap)){
                    fprintf(stderr, DUP_NUM_POS, y+1, x+1);
                    return E_INVAL;
                }
                mapx[x] |= nmap;
                mapy[y] |= nmap;
                mapgrp[grp] |= nmap;
            }
        }
    }
    fclose(fp);
    return E_OK;
}
int calc_sudoku_step1(){
    uint8_t x, y, grp, n, i;
    uint16_t nmap;
    bool running=true;
    stack_item_t *sp=stack, *sp0=stack;
    while(running){
        running=false;
        sp=sp0=stack;
        for (i = 0; i < stack_len; i++, sp++) {
            x = sp->x;
            y = sp->y;
            grp = sp->grp;
            nmap = (~(mapx[x] | mapy[y] | mapgrp[grp])) & 0x3fe;
            if(0==nmap){
                fprintf(stderr, NO_ANSWER_POS, x+1, y+1);
                return E_INVAL;
            }else if(0 != (nmap&(nmap-1))){
                sp0->x = x;
                sp0->y = y;
                sp0->grp = grp;
                sp0++;
            }else{
                board[y][x] = trailing_zeros(nmap);
                mapx[x] |= nmap;
                mapy[y] |= nmap;
                mapgrp[grp] |= nmap;
                running=true;
            }
        }
        stack_len = sp0-stack;
    }
    return ((stack_len==0) ? E_OK : E_AGAIN);
}
int calc_sudoku_step2(){
    uint8_t x, y, grp, n, i;
    uint16_t map;
    stack_item_t *sp=stack, *stack_tail=stack+stack_len;
    for (i = 0; i < stack_len; i++, sp++) {
        x = sp->x;
        y = sp->y;
        grp = sp->grp;
        sp->last_num = 0;
        sp->map = (~(mapx[x] | mapy[y] | mapgrp[grp])) & 0x3fe;
    }
    memset(mapx, 0, sizeof(mapx));
    memset(mapy, 0, sizeof(mapy));
    memset(mapgrp, 0, sizeof(mapgrp));
    
    sp=stack;
    while(sp<stack_tail){
        x = sp->x;
        y = sp->y;
        grp = sp->grp;
        n = sp->last_num;
        if(n>0){
            map = (~(1<<n));
            mapx[x]&=map;
            mapy[y]&=map;
            mapgrp[grp]&=map;
        }
        map = sp->map & (~(mapx[x] | mapy[y] | mapgrp[grp])) & 0x3fe;
        n = next_num(map, n);
        sp->last_num = board[y][x] = n;
        if(0==n){
            if(sp==stack){
                return E_INVAL;
            }
            sp--;
        }else{
            map = (1<<n);
            mapx[x]|=map;
            mapy[y]|=map;
            mapgrp[grp]|=map;
            sp++;
        }
    }
    return E_OK;
}
int main(int argc, char *argv[]){
    int res;
    if (argc < 2){
        fprintf(stderr, HELP_TEXT, argv[0]);
        exit(1);
    }
    if (E_OK != read_sudoku(argv[1])){
        exit(1);
    }
    res = calc_sudoku_step1();
    if (res == E_AGAIN){
        fprintf(stderr, START_CALC);
        if(calc_sudoku_step2()!=E_OK){
            fprintf(stderr, NO_ANSWER);
            return 1;
        }
        fprintf(stderr, END_CALC);
    }else if (res != E_OK) {
        return 1;
    }
    printboard();
    return 0;
}
