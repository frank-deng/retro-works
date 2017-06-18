#!/bin/bash
jekyll b

cd _site
for fname in $(ls *.html); do
	fname=$(basename ${fname});
	iconv -ct gbk "${fname}" > "${fname%.*}.htm"
done;
rm *.html &>/dev/null
cd ..
genisoimage -o mysite.iso -V MYSITE _site/
