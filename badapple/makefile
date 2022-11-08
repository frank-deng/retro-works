TARGET=badapple.exe
OBJS=badapple.obj keyboard.obj timer.obj video.obj frame.obj wav.obj debug.obj
CFLAGS=-mh -0 -q

$(TARGET): $(OBJS)
	wcl $(CFLAGS) -fe=$@ $<

badapple.obj: badapple.c timer.h keyboard.h video.h frame.h wav.h
	wcc $(CFLAGS) -fo=$@ $[.
keyboard.obj: keyboard.c keyboard.h
	wcc $(CFLAGS) -fo=$@ $[.
timer.obj: timer.c timer.h
	wcc $(CFLAGS) -fo=$@ $[.
video.obj: video.c video.h
	wcc $(CFLAGS) -fo=$@ $[.
frame.obj: frame.c frame.h
	wcc $(CFLAGS) -fo=$@ $[.
wav.obj: wav.c wav.h
	wcc $(CFLAGS) -fo=$@ $[.
debug.obj: debug.c
	wcc $(CFLAGS) -fo=$@ $[.

.NOCHECK
clean:
	-del $(TARGET)
	-del *.obj
	-del *.err