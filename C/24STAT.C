#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <math.h>

#define MAX_NUM 13
#define MIN_NUM 1
#define NUM_CNT 4
#define OP_CNT 3
#define ANS_MIN 0
#define ANS_MAX 99

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

static int calc_res(double *n, op_t *op, double ans)
{
    double res;
    
    // abcd### a#(b#(c#d))
    res=calc(n[0], op[0], calc(n[1], op[1], calc(n[2], op[2], n[3])));
    if(fabs(res-ans)<0.0001){
        return 0;
    }
    
    // abc#d## a#((b#c)#d)
    res=calc(n[0], op[0], calc(calc(n[1], op[1], n[2]), op[2], n[3]));
	if(fabs(res-ans)<0.0001){
        return 1;
    }
    
    // abc##d# (a#(b#c))#d
    res=calc(calc(n[0], op[0], calc(n[1], op[1], n[2])), op[2], n[3]);
    if(fabs(res-ans)<0.0001){
        return 2;
    }
    
    // ab#cd## (a#b)#(c#d)
    res=calc(calc(n[0], op[0], n[1]), op[1], calc(n[2], op[2], n[3]));
    if(fabs(res-ans)<0.0001){
        return 3;
    }
    
    // ab#c#d# ((a#b)#c)#d
    res=calc(calc(calc(n[0], op[0], n[1]), op[1], n[2]), op[2], n[3]);
    if(fabs(res-ans)<0.0001){
        return 4;
    }
    
    return -1;
}
static void print_expr(int idx, unsigned int* n0, unsigned int *n, op_t *op, unsigned int ans)
{
    const char *expr[]={
    	"%u%c(%u%c(%u%c%u))=%u","%u%c((%u%c%u)%c%u))=%u","(%u%c(%u%c%u))%c%u=%u",
        "(%u%c%u)%c(%u%c%u)=%u","((%u%c%u)%c%u)%c%u=%u",
    };
    const char opc[]={'+','-','*','/'};
    printf("%u,%u,%u,%u,",n0[0],n0[1],n0[2],n0[3]);
    if(idx>=0){
    	printf(expr[idx],n[0],opc[op[0]],n[1],opc[op[1]],n[2],opc[op[2]],n[3],ans);
    }else{
        printf("No Answer");
    }
    printf("\n");
}

static int cycle_opers(double *n, op_t *op, double ans)
{
    for(op[0]=OP_ADD; op[0]<OP_MAX; op[0]++){
        for(op[1]=OP_ADD; op[1]<OP_MAX; op[1]++){
           for(op[2]=OP_ADD; op[2]<OP_MAX; op[2]++){
                int res=calc_res(n,op,ans);
                if(res>=0){
                    return res;
                }
			}
    	}
    }
    return -1;
}

static int check_ans(unsigned int *nsrc, unsigned int ans, unsigned int *nbuf, op_t *op)
{
    unsigned int i,j,k;
    int res=-1;
    double ndbl[NUM_CNT];
    for(i=0;i<NUM_CNT;i++){
        for(j=0;j<NUM_CNT;j++){
            if(i==j){
               continue;
            }
            for(k=0;k<NUM_CNT;k++){
                if(i==k || j==k){
               		continue;
            	}
                nbuf[0]=nsrc[i];
                nbuf[1]=nsrc[j];
                nbuf[2]=nsrc[k];
                nbuf[3]=nsrc[6-i-j-k];
                ndbl[0]=(double)(nbuf[0]); ndbl[1]=(double)(nbuf[1]);
                ndbl[2]=(double)(nbuf[2]); ndbl[3]=(double)(nbuf[3]);
                res=cycle_opers(ndbl,op,(double)ans);
                if(res>=0){
                    return res;
                }
            }
    	}
    }
    return res;
}

unsigned int get_ans_combs(unsigned int ans, bool show_expr)
{
    unsigned int cnt=0;
    unsigned int n[NUM_CNT],n2[NUM_CNT];
    op_t op[OP_CNT];
    for(n[0]=MIN_NUM; n[0]<=MAX_NUM; n[0]++){
        for(n[1]=n[0]; n[1]<=MAX_NUM; n[1]++){
        	for(n[2]=n[1]; n[2]<=MAX_NUM; n[2]++){
        		for(n[3]=n[2]; n[3]<=MAX_NUM; n[3]++){
                    int expr=check_ans(n,ans,n2,op);
                    if(expr>=0){
                    	cnt++;
                    }
                    if(show_expr){
                        print_expr(expr,n,n2,op,ans);
                    }
    			}
    		}
    	}
    }
    return cnt;
}

int main(int argc, char *argv[])
{
    unsigned int ans;
    if(argc>=2){
        ans=(unsigned int)strtoul(argv[1],NULL,10);
        if(ans>ANS_MAX || ans<ANS_MIN){
            fprintf(stderr,"Answer must between %u and %u.\n",ANS_MIN,ANS_MAX);
            return 1;
        }
        get_ans_combs(ans,true);
        return 0;
    }
    for(ans=ANS_MIN; ans<=ANS_MAX; ans++){
        printf("%u,%u\n",ans,get_ans_combs(ans,false));
    }
    return 0;
}