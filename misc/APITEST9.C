/* 主题：打印字库读取 */
/*
	 1    DispChinese     读取Postscript字库点阵          INT 7EH
*/
#include                <dos.h>
#include                <stdio.h>
#include                <stdlib.h>

int InitEnv()
{
	 union REGS regs;
	 regs.x.ax = 0xdb00;
	 int86(0x2f,&regs,&regs);
	 if (regs.x.bx != 0x5450) {
			return 1;
	 }
	 regs.h.ah = 0;
	 regs.h.al = 0x1;
	 int86(0x79,&regs,&regs);
	 if (0 != regs.x.flags & 0x40) {
		return 2;
	 }
	 regs.x.ax = 0xff0b;
	 int86(0x16,&regs,&regs);
	 regs.h.ah = 0;
	 regs.h.al = 10;
	 int86(0x10, &regs, &regs);
	 regs.x.ax = 0xff01;
	 regs.h.bl = 1;
	 regs.h.bh = 0;
	 int86(0x10, &regs, &regs);
	 return 0;
}
void RestoreEnv()
{
	union REGS regs;
	 regs.x.ax = 0xff07;
	 int86(0x16,&regs,&regs);
	 regs.h.ah = 0;
	 regs.h.al = 3;
	 int86(0x10, &regs, &regs);
	 regs.x.ax = 0xff01;
	 regs.h.bl = 1;
	 regs.h.bh = 1;
	 int86(0x10, &regs, &regs);
}
void SetPixel(int Col,int Row,int Color)
{
	 union REGS regs;

	 regs.h.ah = 0xc;
	 regs.h.al = Color;
	 regs.x.cx = Col;
	 regs.x.dx = Row;
	 int86(0x10,&regs,&regs);
}

/******************************************************************************
		参数说明:   x,y             显示汉字的左上角坐标
								FrColor         显示汉字的前景色
								BgColor         显示汉字的背景色
								ChineseCode     欲显示的汉字
								Font            使用的字库编号
								Fontx           显示汉字的水平宽度
								Fonty           显示汉字的垂直高度
******************************************************************************/
int DispChinese(int x,int y,int FrColor,int BgColor,char *ChineseCode,
								 int Font,int Fontx,int Fonty)
{
	 union REGS           regs;
	 struct SREGS         sregs;
	 struct Int7eStru{
			unsigned char     Word[2];                /* 汉字机内码     */
			unsigned int      Font;                   /* 字库编号       */
			unsigned int      Fontx,Fonty;            /* 汉字高度和宽度 */
			unsigned int      Top,Bot;                /* 起始线和终止线 */
			unsigned int      Attribute;              /* 属性           */
			unsigned int      BufLen;                 /* 缓冲区长度     */
	 }Int7eArg;

	 unsigned char        *DotBuf,*s,c;
	 int                  i,j,n;
	 size_t BufLen;
	 if ('\0' == ChineseCode[0]) {
		 BufLen = ((Fontx + 7) / 2 * Fonty) * 2 + 3 * 1024;
	 } else {
		 BufLen = ((Fontx + 7) / 8 * Fonty) * 2 + 3 * 1024;
	 }
	 DotBuf=calloc(1, BufLen);

	 if (DotBuf == NULL) return 0;

	 Int7eArg.Word[0]=ChineseCode[1];
	 Int7eArg.Word[1]=ChineseCode[0];             /* 汉字编码必须倒一下   */
	 Int7eArg.Font=Font;                          /* 字库编号             */
	 Int7eArg.Fontx=Fontx;                        /* 汉字宽度             */
	 Int7eArg.Fonty=Fonty;                        /* 汉字高度             */
	 Int7eArg.Top=0;                              /* 起始线, 0表示顶端    */
	 Int7eArg.Bot=Fonty-1;                        /* 终止线, Fonty-1为尾端*/
	 Int7eArg.Attribute=1;                        /* 属性=1, 表示显示格式 */
	 Int7eArg.BufLen=BufLen;
																								/* 缓冲区大小           */
	 regs.x.si=FP_OFF(&Int7eArg);
	 regs.x.di=FP_OFF(DotBuf);
	 sregs.ds=FP_SEG(&Int7eArg);
	 sregs.es=FP_SEG(DotBuf);

	 printf("%d\n", Int7eArg.Fontx);
	 int86x(0x7e,&regs,&regs,&sregs);
	 printf("%d %d\n", Int7eArg.Fonty, Int7eArg.Fontx);

	 s=DotBuf;
	 for (i=0;i<Fonty;i++){
			for (j=0;j<Int7eArg.Fontx;j++){
				 if (!(j % 8)){
						c=*s;
						s++;
						n=0x80;
				 }
				 if (c & n) {
					 SetPixel(x+j,y+i,FrColor);
				 } else {
					 SetPixel(x+j, y+i, BgColor);
				 }
				 n>>=1;
			}
	 }
	 free(DotBuf);
	 return 1;
}

void main(void)
{
	int errCode = InitEnv();
	 if (errCode != 0) { /* RDPS的模块号为1 */
			printf("Failed to init environment! errorcode: %d\n", errCode);
			exit(0);
	 }
	 if (!DispChinese(220,110,15,20,"\0A",2,8,16)){
			printf("内存不够\n\7");
	 }
	 getch();
	 RestoreEnv();
}
