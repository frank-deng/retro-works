#!/bin/bash
jekyll b

cd _site
for fname in $(ls *.html); do
	fname=$(basename ${fname});
	iconv -ct gbk "${fname}" > "${fname%.*}.htm"
done;
rm *.html &>/dev/null
find . -iname \*.jpg -exec mogrify -resize '600x300>' {} \;
cd ..
genisoimage -o mysite.iso -V MYSITE _site/
