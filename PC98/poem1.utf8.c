#include <stdio.h>
#include <string.h>
#include <dos.h>
#include <stdlib.h>
#include <jctype.h>
typedef unsigned char uint8_t;
typedef unsigned short uint16_t;

#define LINE_COUNT 33
static char *poem[]={
  "雨ニモマケズ",
  "宮澤賢治",
  "",
  "雨ニモマケズ",
  "風ニモマケズ",
  "雪ニモ夏ノ暑サニモマケヌ",
  "丈夫ナカラダヲモチ",
  "慾ハナク",
  "決シテ瞋ラズ",
  "イツモシヅカニワラッテヰル",
  "一日ニ玄米四合ト",
  "味噌ト少シノ野菜ヲタベ",
  "アラユルコトヲ",
  "ジブンヲカンジョウニ入レズニ",
  "ヨクミキキシワカリ",
  "ソシテワスレズ",
  "野原ノ松ノ林ノ蔭ノ",
  "小サナ萓ブキノ小屋ニヰテ",
  "東ニ病気ノコドモアレバ",
  "行ッテ看病シテヤリ",
  "西ニツカレタ母アレバ",
  "行ッテソノ稲ノ朿ヲ負ヒ",
  "南ニ死ニサウナ人アレバ",
  "行ッテコハガラナクテモイヽトイヒ",
  "北ニケンクヮヤソショウガアレバ",
  "ツマラナイカラヤメロトイヒ",
  "ヒドリノトキハナミダヲナガシ",
  "サムサノナツハオロオロアルキ",
  "ミンナニデクノボートヨバレ",
  "ホメラレモセズ",
  "クニモサレズ",
  "サウイフモノニ",
  "ワタシハナリタイ"
};
union REGS inregs, outregs;
static uint16_t far* vram = 0xA0000000;
static uint16_t far* vramattr = 0xA0002000;

void clrscr(){
	_fmemset((void far *)vram, 0, 4000);
	_fmemset((void far *)vramattr, 0, 4000);
}
void cputchar(uint16_t ch, uint16_t x, uint16_t y, uint16_t attr){
	uint16_t offset = (y<<6) + (y<<4) + x;
	uint16_t far *p_vram = (uint16_t far*)(vram + offset);
	uint16_t far *p_vramattr = (uint16_t far*)(vramattr + offset);
	
	if (ch > 0xFF){
		*p_vram = ch - 0x20;
		*(p_vram + 1) = ch + 0x60;
		*(p_vramattr) = attr;
		*(p_vramattr + 1) = attr;
	} else {
		*p_vram = ch;
		*p_vramattr = attr;
	}
}
#define MARGIN_TOP 1
void main(){
  unsigned int x=78-3*2-1,y=MARGIN_TOP,i,ch;
  unsigned char *p;

  /*Init screen*/
	putchar('\x1e');
	inregs.x.dx = 0;
	inregs.h.ah = 0x13;
	int86(0x18, &inregs, &outregs);
	outp(0x62, 0x4b);
	outp(0x60, 0x0f);
	inregs.h.ah=0x03;
	int86(0x18,&inregs,&outregs);
	clrscr();

  /*Display lines*/
  for(i=0;i<LINE_COUNT;i++){
    y=MARGIN_TOP;
    for(p=poem[i]; *p!='\0'; p+=2){
      ch=*p; ch<<=8; ch |= *(p+1);
      ch=jmstojis(ch);
      ch=(ch<<8)|(0xFF&(ch>>8));
      cputchar(ch,x,y,0xe1);
      y++;
    }
    x-=2;
  }

  /*Wait for keypress*/
	inregs.h.ah=0x05;
	int86(0x18,&inregs,&outregs);
  asm hlt;
	inregs.h.ah=0x05;
	int86(0x18,&inregs,&outregs);
	while(0==outregs.h.bh){
    asm hlt;
		inregs.h.ah=0x05;
		int86(0x18,&inregs,&outregs);
	}

  /*Recover screen*/
	inregs.h.ah=0x03;
	int86(0x18,&inregs,&outregs);
	outp(0x62, 0x4b);
	outp(0x60, 0x8f);
	putchar('\x1e');
	printf("\033[2J");
}

