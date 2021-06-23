TARGET=nyancat.com

$(TARGET): nyancat.asm frames.inc
	nasm -o $@ $<

nyancat.asm:frames.inc
	python3 imagegen.py frames.inc

.PHONY:clean
clean:
	-rm $(TARGET)

