#!/bin/bash
SOURCE="${1}"
TARGET="${2}"
quality=80
counter=1
find "${SOURCE}" -type f -iname \*.jpg | sort | while read file; do
	newfile=DSC$(printf %05d $counter).jpg;
	convert "${file}" -resize '640x480>' -quality $quality "${TARGET}/${newfile}"
	counter=$((counter+1));
done;

