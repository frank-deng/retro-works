10 DEFINT A-Z: KEY OFF: CLS
20 for m=0 to 640 step 16
30 locate 1,1,1,6,7:print m;"KB";
40 t#=timer: while (timer-t#)<.05: wend
50 next m
60 print " OK";
70 beep:t#=timer: while (timer-t#)<1: wend
80 PRINT "":PRINT ""
81  PRINT "-----------------"
90  PRINT " Floppy A: 1.2M"
100 PRINT " Floppy B: 360k"
110 PRINT "-----------------"
130 t#=timer: while (timer-t#)<1: wend
140 system: end
