guessnum-stat : guessnum-stat.o
	gcc -O3 -pthread -o $@ $^

guessnum-stat.o : guessnum-stat.c guessnum-stat.h
	gcc -O3 -pthread -c -o $@ $<

guessnum-stat.h : guessnum-stat.h.php
	php $< > $@

.PHONY:clean
clean:
	-rm *.o guessnum-stat guessnum-stat.h

