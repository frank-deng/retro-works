TARGET=ipcalc.com test.com
OBJS=ipv4.obj
HEADERS=ipv4.h
CFLAGS=-ms -0 -q -d0 -os
LDFLAGS=-mt -0 -q -d0 -os

.NOCHECK
compilework: $(TARGET)

ipcalc.com: $(OBJS) main.obj
	wcl $(LDFLAGS) -fe=$@ $<

test.com: $(OBJS) test.obj
	wcl $(LDFLAGS) -fe=$@ $<

main.obj: main.c $(HEADERS)
	wcc $(CFLAGS) -fo=$@ $[.

test.obj: test.cpp test.hpp $(HEADERS)
	wpp $(CFLAGS) -fo=$@ $[.

ipv4.obj: ipv4.c $(HEADERS)
	wcc $(CFLAGS) -fo=$@ $[.

.NOCHECK
clean:
	-del *.obj
	-del *.err
	-del $(TARGET)
