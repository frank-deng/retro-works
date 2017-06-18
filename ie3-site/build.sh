#!/bin/bash
jekyll b

cd _site
for fname in $(ls *.html); do
	fname=$(basename ${fname});
	iconv -ct gbk "${fname}" > "${fname%.*}.htm"
done;
rm *.html &>/dev/null
cd ..

SITEDIR=$(date +%y%m%d)
mkdir $SITEDIR
cp -aR _site/* $SITEDIR
rm site.zip &>/dev/null
zip -r $SITEDIR $SITEDIR/*
rm -r $SITEDIR

