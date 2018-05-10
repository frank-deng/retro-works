guessnum-stat : guessnum-stat.o
	gcc -O3 -pthread -o $@ $^

guessnum-stat.o : guessnum-stat.c
	gcc -O3 -pthread -c -o $@ $<

.PHONY:clean
clean:
	-rm *.o guessnum-stat

