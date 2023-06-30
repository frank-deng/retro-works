10 DEFINT A-Z: KEY OFF: CLS
20 for m=0 to 640 step 16
30 locate 1,1,1,6,7:print m;"KB OK";
40 if inkey$<>"" then goto 70
50 t#=timer: while (timer-t#)<.2: wend
60 next m
70 locate 1,1,1:print 640;"KB OK";
80 beep:t#=timer: while (timer-t#)<1: wend
100 CLS: locate 1,1,1: system: end
