TARGET=guessnum-stat
INSTALLDIR=/usr/local/bin
CC=gcc
CFLAGS=-O3
LD=gcc
LDFLAGS=-pthread
LIBS=
OBJS=guessnum-stat.o
HEADER=guessnum-stat.h

${TARGET} : ${OBJS}
	${LD} ${LDFLAGS} -o ${TARGET} ${OBJS} ${LIBS}

$(OBJS) : $(HEADER)

guessnum-stat.h : guessnum-stat.h.php
	php guessnum-stat.h.php > guessnum-stat.h

.PHONY:clean
clean:
	-rm ${OBJS} ${HEADER} ${TARGET}

.PHONY:install
install:
	-cp ${TARGET} ${INSTALLDIR}
