TARGET=lib2048.so
${TARGET}: lib2048.cpp
	g++ -fPIC -shared -o $@ $<

.PHONY: clean
clean:
	-rm ${TARGET} *.o
