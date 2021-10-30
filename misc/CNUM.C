#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef char int8_t;
typedef unsigned char bool;

char *numConv[]={
	"Áã",
	"Ò¼",
	"·¡",
	"Èþ",
	"ËÁ",
	"Îé",
	"Â½",
	"Æâ",
	"°Æ",
	"¾Á"
};
#define DISP_10 "Ê°"
#define DISP_100 "°Û"
#define DISP_1000 "Çª"
#define DISP_10000 "Íò"
#define DISP_1E8 "ÒÚ"
#define DISP_1E16 "¾©"
#define DISP_1E24 "ïö"

bool conv1000(char* src, int8_t len){
	char *p=src; int8_t digit, i; bool allZero=1, outZero=0;
	for(i=len, p=src; i>0 && '\0'!=*p; i--,p++){
		digit=*p-'0';
		if(digit){
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
bool padZero(char *src, int8_t len){
	char *p=src; bool foundZero=0;
	while(*p && len){
		if('0'==*p){
			foundZero=1;
		}else if(*p>='1' && *p<='9'){
			return foundZero;
		}
		p++; len--;
	}
	return 0;
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
void conv(char *src){
	int8_t len=strlen(src), firstLen=len&(0x7), nonZero=1, i;
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
	conv(num);
	putchar('\n');
	return 0;
}