#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define MAX_NUM 13
#define MIN_NUM 1
#define MAX_ANS 100
#define MIN_ANS 0
#define NUM_CNT 4
#define OP_CNT 3
#define ANS_MIN 0
#define ANS_MAX 100

typedef enum {
    OP_ADD, OP_SUB, OP_MUL, OP_DIV, OP_MAX
} op_t;

static inline double calc(double a, op_t op0, double b)
{
    double res=INFINITY;
    switch(op0){
        case OP_ADD:
        	res=a+b;
        break;
        case OP_SUB:
        	res=a-b;
        break;
        case OP_MUL:
        	res=a*b;
        break;
        case OP_DIV:
        	if(b>0 || b<-0){
                res=a/b;
            }
        break;
    }
    return res;
}

// abcd### a#(b#(c#d))
static inline double expr0calc(double *n, op_t *op){
    return calc(n[0], op[0], calc(n[1], op[1], calc(n[2], op[2], n[3])));
}

// abc#d## a#((b#c)#d)
static inline double expr1calc(double *n, op_t *op){
    return calc(n[0], op[0], calc(calc(n[1], op[1], n[2]), op[2], n[3]));
}

// abc##d# (a#(b#c))#d
static inline double expr2calc(double *n, op_t *op){
    return calc(calc(n[0], op[0], calc(n[1], op[1], n[2])), op[2], n[3]);
}

// ab#cd## (a#b)#(c#d)
static inline double expr3calc(double *n, op_t *op){
    return calc(calc(n[0], op[0], n[1]), op[1], calc(n[2], op[2], n[3]));
}

// ab#c#d# ((a#b)#c)#d
static inline double expr4calc(double *n, op_t *op){
    return calc(calc(calc(n[0], op[0], n[1]), op[1], n[2]), op[2], n[3]);
}

static int calc_res(double *n, op_t *op, unsigned int ans)
{
    if(fabs(expr0calc(n,op)-(double)ans)<0.0001){
        return 0;
    }
    if(fabs(expr1calc(n,op)-(double)ans)<0.0001){
        return 1;
    }
    if(fabs(expr2calc(n,op)-(double)ans)<0.0001){
        return 2;
    }
    if(fabs(expr3calc(n,op)-(double)ans)<0.0001){
        return 3;
    }
    if(fabs(expr4calc(n,op)-(double)ans)<0.0001){
        return 4;
    }
    return -1;
}

static bool cycle_opers(unsigned int a, unsigned int b, unsigned int c, unsigned int d, unsigned int ans)
{
    op_t op[OP_CNT];
    double n[NUM_CNT];
    n[0]=(double)a;
    n[1]=(double)b;
    n[2]=(double)c;
    n[3]=(double)d;
    for(op[0]=OP_ADD; op[0]<OP_MAX; op[0]++){
        for(op[1]=OP_ADD; op[1]<OP_MAX; op[1]++){
            for(op[2]=OP_ADD; op[2]<OP_MAX; op[2]++){
                res=calc_res(n,op,ans);
                if(res>=0){
                    return true;
                }
    		}
    	}
    }
finish:
    return false;
}

static bool check_ans(unsigned int a, unsigned int b, unsigned int c, unsigned int d, unsigned int ans)
{
    unsigned int i,j,k;
    unsigned int n[]={a,b,c,d};
    for(i=0;i<NUM_CNT;i++){
        for(j=0;j<NUM_CNT;j++){
            if(i==j){
               continue;
            }
            for(k=0;k<NUM_CNT;k++){
                if(i==k || j==k){
               		continue;
            	}
                if(cycle_opers(n[i],n[j],n[k],n[6-i-j-k],ans)){
                    return true;
                }
            }
    	}
    }
finish:
    return false;
}

unsigned int get_num_cumb_count()
{
    unsigned int a,b,c,d,cnt=0;
    for(a=MIN_NUM; a<=MAX_NUM; a++){
        for(b=a; b<=MAX_NUM; b++){
        	for(c=b; c<=MAX_NUM; c++){
        		for(d=c; d<=MAX_NUM; d++){
                    cnt++;
    			}
    		}
    	}
    }
    return cnt;
}

unsigned int get_ans_combs(unsigned int ans)
{
    unsigned int a,b,c,d,cnt=0;
    for(a=MIN_NUM; a<=MAX_NUM; a++){
        for(b=a; b<=MAX_NUM; b++){
        	for(c=b; c<=MAX_NUM; c++){
        		for(d=c; d<=MAX_NUM; d++){
                    if(check_ans(a,b,c,d,ans)){
                    	cnt++;
                    }
    			}
    		}
    	}
    }
    return cnt;
}

int main()
{
    unsigned int ans;
    for(ans=ANS_MIN; ans<=ANS_MAX; ans++){
        unsigned int combs=get_ans_combs(ans);
        printf("%u,%u\n",ans,combs);
    }
    return 0;
}