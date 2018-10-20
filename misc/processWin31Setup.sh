#!/bin/bash

rm src/*
tar -zxf src.tgz
for n in 1 2 3 4 5 6 7 8 9 A B C; do
	rm "Disk${n}"/* "Disk${n}.img"
	mv "src/DISK${n}" "Disk${n}"
	dd if=/dev/zero of="Disk${n}.img" bs=512 count=2880
	mformat -i "Disk${n}.img" -f 1440
done

echo -n>filelist.txt
echo -n>failed.txt
cd ./src
ls|sed 's/\._$//g'|sed 's/_$//g'|while read filename; do
	grep -i -o ".:$filename" SETUP.INF|uniq|tr 'a-z' 'A-Z'>>../filelist.txt
	grep -i -o ".:$filename" CONTROL.INF|uniq|tr 'a-z' 'A-Z'>>../filelist.txt
done
cd ..
cat filelist.txt|sort|uniq|while read info;do
	idx=${info%%:*}
	fname=${info#*:}
	mv src/${fname}* "Disk${idx}" -i||echo $idx $fname>>failed.txt
done
mv src/* Disk1
for n in 1 2 3 4 5 6 7 8 9 A B C; do
	mcopy -i "Disk${n}.img" "Disk${n}"/* ::/
done