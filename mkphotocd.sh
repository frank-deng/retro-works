#!/bin/bash
SOURCE="${1}"
TARGET="${2}"
TEMPDIR=$(mktemp -d);
quality=80
counter=1
find "${SOURCE}" -maxdepth 1 -type f -iname \*.jpg | sort | while read file; do
	newfile=DSC$(printf %05d $counter).jpg;
	convert "${file}" -strip -resize '640x640>' -quality $quality "JPEG:${TEMPDIR}/${newfile}"
	counter=$((counter+1));
done;
genisoimage -o "${TARGET}" "${TEMPDIR}"
rm -r "${TEMPDIR}"
