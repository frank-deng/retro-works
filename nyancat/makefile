TARGET=nyancat.com

$(TARGET): nyancat.asm frames.inc music.inc
	nasm -o $@ $<

frames.inc: imagegen.py
	python3 $^ $@

music.inc: musicgen.py nyancat.musicxml
	python3 $^ $@

.PHONY:clean
clean:
	-rm $(TARGET) 

