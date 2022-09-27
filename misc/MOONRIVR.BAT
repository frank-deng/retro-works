bmp2cga.EXE /COLOR3 MOONRIVR.BMP MOONRIVR.PIC
text2bmp.exe TEMP.BMP 2,0,56,70,0,1,1 Moon River
bmp2cga.exe /COLOR3 TEMP.BMP MOONRIVR.TM1 
text2bmp.exe TEMP.BMP 2,0,56,70,0,1,0 Moon River
bmp2cga.exe /COLOR1 TEMP.BMP MOONRIVR.TX1 
text2bmp.exe TEMP.BMP 10,0,32,32,0,1,1 Audrey Hepburn
bmp2cga.exe /COLOR3 TEMP.BMP MOONRIVR.TM2 
text2bmp.exe TEMP.BMP 10,0,32,32,0,1,0 Audrey Hepburn
bmp2cga.exe /COLOR2 TEMP.BMP MOONRIVR.TX2 
del TEMP.BMP
