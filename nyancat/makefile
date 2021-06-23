TARGET=nyancat.com
OBJS=nyancat.obj
CFLAGS=-q -0 -bc -d0
LDFLAGS=-lr -mt

$(TARGET): $(OBJS)
	wcl $(CFLAGS) $(LDFLAGS) -fe=$@ $**

nyancat.obj: nyancat.c
	wcc $(CFLAGS) -fo=$@ $**

clean:
	-del $(OBJS) $(TARGET)
