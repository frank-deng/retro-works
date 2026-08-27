// wcl -0 -d0 -ox -mt -fe=sudoku.com sudoku.c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define HELP_TEXT "Usage:\n    %s file\n    %s map_file file\n"
#define MSG_TIMEOUT (2)
#define CYCLES_BEFORE_MSG (256)
#define CALC_PROC "\rCalculating...%c"
#define END_CALC "\a\r"

#define OPEN_FILE_FAILED "Failed to open Sudoku file.\n"
#define LINE_NOT_NINE_NUM "Not 9 numbers at line %u.\n"
#define NOT_NINE_ROWS "Rows must be 9.\n"
#define OPEN_JIGSAW_FILE_FAILED "Failed to open Sudoku jigsaw map file.\n"
#define GROUP_TOO_MANY_CELLS "Group #%u has more than 9 cells.\n"
#define DUP_NUM_POS "Duplicated number at line %u, row %u, column %u.\n"

#define NO_ANSWER_POS "No answer at row %d, column %d.\n"
#define NO_ANSWER "No answer.\n"

typedef unsigned char u8;
typedef unsigned short u16;

enum{
    E_OK,
    E_AGAIN,
    E_INVAL,
    E_FAIL,
};

typedef struct {
    u8 x;
    u8 y;
    u8 grp;
    u16 map;
} table_item_t;

static u8 group[9][9] = {
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
static u8 board[9][9] = {
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

static u16 mapx[9],mapy[9],mapgrp[9];
static table_item_t table[81];
static u8 table_len=0;

static u8 trailing_zeros(u16 n)
{
    u8 res=0;
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
static u8 next_num(u16 map, u8 n)
{
    if(0==map){
        return 0;
    }
    map &= ~((((u16)1)<<(n+1))-1);
    if(0==map){
        return 0;
    }
    return trailing_zeros(map);
}
static u8 elem_cnt(u16 n)
{
    u8 res=0;
    while(n){
        n&=(n-1);
        res++;
    }
    return res;
}
void printboard(int jigsaw){
    u8 x, y;
    for (y = 0; y < 9; y++){
        for (x = 0; x < 9; x++){
            printf("%d ", board[y][x]);
            if (!jigsaw && (2 == (x % 3))){
                printf(" ");
            }
        }
        puts("");
        if (!jigsaw && (2 == (y % 3))){
            puts("");
        }
    }
}
int read_jigsaw_map(char *filename)
{
    u8 x=0, y=0, grp_cells[9]={0,0,0,0,0,0,0,0,0}, n;
    u16 linenum=1;
    char buf[80],*p;
    int ret=E_OK;
    FILE *fp = fopen(filename, "r");
    if (NULL==fp){
        fprintf(stderr, OPEN_JIGSAW_FILE_FAILED);
        return E_FAIL;
    }
    while(fgets(buf,sizeof(buf),fp)!=NULL){
	if(buf[0]=='#'){
	    linenum++;
	    continue;
	}
	x=0;
	for(p=buf; *p!='\0' && (p-buf)<sizeof(buf); p++){
	    if(*p<'1' || *p>'9'){
                continue;
	    }
	    if(x>=9){
                fprintf(stderr,LINE_NOT_NINE_NUM,linenum);
                ret=E_INVAL;
                goto finally_exit;
	    }
	    n=*p-'1';
	    group[y][x]=n;
            grp_cells[n]++;
	    if(grp_cells[n]>9){
                fprintf(stderr,GROUP_TOO_MANY_CELLS,n+1);
                ret=E_INVAL;
                goto finally_exit;
	    }
	    x++;
	}
	if(x>0){
	    if(y>=9){
                fprintf(stderr,NOT_NINE_ROWS);
                ret=E_INVAL;
                goto finally_exit;
	    }else if(x!=9){
                fprintf(stderr,LINE_NOT_NINE_NUM,linenum);
                ret=E_INVAL;
                goto finally_exit;
	    }
	    y++;
	}
	linenum++;
    }
    if(y!=9){
        fprintf(stderr,NOT_NINE_ROWS);
        ret=E_INVAL;
        goto finally_exit;
    }
finally_exit:
    fclose(fp);
    return ret;
}
int read_sudoku(char *filename){
    u8 x=0, y=0, grp, n;
    u16 nmap, linenum=1;
    char buf[80],*p;
    int ret=E_OK;
    FILE *fp = fopen(filename, "r");
    if (NULL==fp){
        fprintf(stderr, OPEN_FILE_FAILED);
        return E_FAIL;
    }
    while(fgets(buf,sizeof(buf),fp)!=NULL){
	if(buf[0]=='#'){
	    linenum++;
	    continue;
	}
	x=0;
	for(p=buf; *p!='\0' && (p-buf)<sizeof(buf); p++){
	    if((*p<'0' || *p>'9') && (*p!='.')){
                continue;
	    }
	    if(x>=9){
                fprintf(stderr,LINE_NOT_NINE_NUM,linenum);
                ret=E_INVAL;
                goto finally_exit;
	    }
	    grp=group[y][x];
	    if(*p=='0' || *p=='.'){
                table[table_len].x = x;
                table[table_len].y = y;
                table[table_len].grp = grp;
                table_len++;
	    }else{
		n=*p-'0';
		nmap=1;
		nmap<<=n;
                if((mapx[x] & nmap)||(mapy[y] & nmap)||(mapgrp[grp] & nmap)){
                    fprintf(stderr, DUP_NUM_POS, linenum, y+1, x+1);
                    ret=E_INVAL;
                    goto finally_exit;
                }
                mapx[x] |= nmap;
                mapy[y] |= nmap;
                mapgrp[grp] |= nmap;
		board[y][x]=n;
	    }
	    x++;
	}
	if(x>0){
	    if(y>=9){
                fprintf(stderr,NOT_NINE_ROWS);
                ret=E_INVAL;
                goto finally_exit;
	    }else if(x!=9){
                fprintf(stderr,LINE_NOT_NINE_NUM,linenum);
                ret=E_INVAL;
                goto finally_exit;
	    }
	    y++;
	}
	linenum++;
    }
    if(y!=9){
        fprintf(stderr,NOT_NINE_ROWS);
        ret=E_INVAL;
        goto finally_exit;
    }
finally_exit:
    fclose(fp);
    return ret;
}
int calc_sudoku_step1(){
    u8 x, y, grp, n, i, j;
    u16 nmap;
    int running=1;
    while(running){
        running=0;
	j=0;
        for (i = 0; i < table_len; i++) {
            x = table[i].x;
            y = table[i].y;
            grp = table[i].grp;
            nmap = (~(mapx[x] | mapy[y] | mapgrp[grp])) & 0x3fe;
            if(0==nmap){
                fprintf(stderr, NO_ANSWER_POS, x+1, y+1);
                return E_INVAL;
            }else if(0 != (nmap&(nmap-1))){
		table[j].x = x;
		table[j].y = y;
		table[j].grp = grp;
		j++;
            }else{
                board[y][x] = trailing_zeros(nmap);
                mapx[x] |= nmap;
                mapy[y] |= nmap;
                mapgrp[grp] |= nmap;
                running=1;
            }
        }
    	table_len=j;
    }
    return ((table_len==0) ? E_OK : E_AGAIN);
}
static u8 get_min_cell()
{
    u8 i,x,y,n,res=0,cnt=100;
    u16 map;
    for(i=0;i<table_len;i++){
        x = table[i].x;
        y = table[i].y;
	n=board[y][x];
	if(n!=0){
	    continue;
	}
	map=table[i].map & ~(mapx[x]|mapy[y]|mapgrp[table[i].grp]);
	if(!map){
	    return 0xff;
	}
	n=elem_cnt(map);
	if(n<cnt){
	    cnt=n;
	    res=i;
	}
    }
    return res;
}
int calc_sudoku_step2(){
    u8 i,x,y,grp,n;
    u16 map;
    u8 stack[81];
    u8 *stack_bottom=stack+table_len;
    u8 *sp=stack_bottom;
    for(i=0;i<table_len;i++){
	x=table[i].x;
        y=table[i].y;
	grp=table[i].grp;
	table[i].map=(~(mapx[x]|mapy[y]|mapgrp[grp]))&0x3fe;
    }
    memset(mapx, 0, sizeof(mapx));
    memset(mapy, 0, sizeof(mapy));
    memset(mapgrp, 0, sizeof(mapgrp));
    while(sp>stack){
	i=get_min_cell();
	if(i!=0xff){
	    sp--;
	    *sp=i;
	}
	n=0;
	while(!n && sp<stack_bottom){
	    i=*sp;
	    x=table[i].x;
            y=table[i].y;
	    grp=table[i].grp;
	    n=board[y][x];
	    if(n){
		map=~(((u16)1)<<n);
		mapx[x]&=map;
		mapy[y]&=map;
		mapgrp[grp]&=map;
	    }
	    map=table[i].map & (~(mapx[x]|mapy[y]|mapgrp[grp]));
	    n=next_num(map,n);
            board[y][x]=n;
	    if(!n){
		sp++;
	    }else{
		map=(((u16)1)<<n);
		mapx[x]|=map;
		mapy[y]|=map;
		mapgrp[grp]|=map;
	    }
	}
	if(sp>=stack_bottom){
            return E_FAIL;
	}
    }
    return E_OK;
}
void print_help(const char *app_name)
{
        fprintf(stderr, HELP_TEXT, app_name, app_name);
}
int main(int argc, char *argv[]){
    int res; char *mapfile=NULL, *sudoku_file=NULL;
    if (argc < 2){
	print_help(argv[0]);
        return 1;
    }
    if(argc > 2){
        mapfile=argv[1];
        sudoku_file=argv[2];
    }else{
        sudoku_file=argv[1];
    }
    if(mapfile!=NULL && E_OK!=read_jigsaw_map(mapfile)){
        return 1;
    }
    if (E_OK != read_sudoku(sudoku_file)){
        return 1;
    }
    res = calc_sudoku_step1();
    if (res == E_AGAIN){
        if(calc_sudoku_step2()!=E_OK){
            fprintf(stderr, NO_ANSWER);
            return 1;
        }
    }else if (res != E_OK) {
        return 1;
    }
    printboard(mapfile!=NULL);
    return 0;
}

