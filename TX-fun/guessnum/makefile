TARGET=guessnum
INSTALLDIR=/usr/local/bin
CC=gcc
CFLAGS=-O3
LD=gcc
LDFLAGS=
LIBS=-lpthread
OBJS=guessnum.o
HEADER=guessnum.h

${TARGET} : ${OBJS}
	${LD} ${LDFLAGS} -o ${TARGET} ${OBJS} ${LIBS}

$(OBJS) : $(HEADER)

guessnum.h : guessnum.h.php
	php guessnum.h.php > guessnum.h

.PHONY:clean
clean:
	-rm ${OBJS} guessnum.h ${TARGET}

