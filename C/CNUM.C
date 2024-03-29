#include <stdio.h>

typedef char int8_t;
typedef unsigned char bool;

char *numConv[]={"��","Ҽ","��","��","��","��","½","��","��","��"};
#define DISP_10 "ʰ"
#define DISP_100 "��"
#define DISP_1000 "Ǫ"
#define DISP_10000 "��"
#define DISP_1E8 "��"
#define DISP_1E16 "��"
#define DISP_1E24 "��"

bool conv1000(char* src, int8_t len){
	char *p=src; int8_t digit, i; bool allZero=1, outZero=0;
	for(p=src, i=0; '\0'!=*p && i<len; p++,i++){
		if(*p>'0' && *p<='9'){
			allZero=0;
			break;
		}
	}
	if(allZero){
		return 0;
	}
	for(i=len, p=src; i>0 && '\0'!=*p; i--,p++){
		digit=*p-'0';
		if(!digit){
			outZero=1;
			continue;
		}
		if(outZero){
			printf(numConv[0]);
		}
		outZero=0;
		printf(numConv[digit]);
		switch(i){
			case 2:
				printf(DISP_10);
			break;
			case 3:
				printf(DISP_100);
			break;
			case 4:
				printf(DISP_1000);
			break;
		}
	}
	return 1;
}
bool conv10000(char *src, int8_t len){
	bool hasNum0=0, hasNum1=0;
	if(len<=4){
		return conv1000(src,len);
	}
	hasNum0=conv1000(src,len-4);
	if(hasNum0){
		printf(DISP_10000);
	}
	src+=(len-4);
	hasNum1=conv1000(src,4);
	return hasNum0 || hasNum1;
}
void conv(char *src,int8_t len){
	int8_t firstLen=len&(0x7), nonZero=1, i;
	if(!firstLen){
		firstLen=8;
	}
	conv10000(src,firstLen);
	len-=firstLen;
	if(!len){
		return;
	}
	src+=firstLen;
	while(len>0){
		if(nonZero){
			switch(len>>3){
				case 3:
					printf(DISP_1E24);
				break;
				case 2:
					printf(DISP_1E16);
				break;
				case 1:
					printf(DISP_1E8);
				break;
			}
		}
		nonZero=conv10000(src,8);
		len-=8;
		src+=8;
	}
}
int main(int argc, char* argv[]){
	char *num=NULL, *p=NULL;
	size_t len=0;

	if(argc<2){
		fputs("Usage: cnum number\n",stderr);
		return 1;
	}
	num=argv[1];
	for(p=num,len=0; *p; p++,len++){
		if(*p<'0' || *p>'9'){
			fputs("Invalid number\n",stderr);
			return 1;
		}
		if(len>=32){
			fputs("Number too large\n",stderr);
			return 1;
		}
	}
	conv(num,len);
	putchar('\n');
	return 0;
}