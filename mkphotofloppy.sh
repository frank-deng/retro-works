#!/bin/bash
SOURCE="${1}"
TARGET="${2}"
quality=50
counter=1
imgcounter=1

TEMPFILE=$(tempfile);
IMGFILE='';

mknewdisk() {
	IMGFILE="${TARGET}/"photo$(printf %03d $imgcounter).img;
	dd if=/dev/zero of="${IMGFILE}" bs=512 count=2880 &>/dev/null
	mformat -i "${IMGFILE}" -f 1440
	imgcounter=$((imgcounter+1));
}

mknewdisk
find "${SOURCE}" -type f -iname \*.jpg | sort | while read file; do
	newfile=DSC$(printf %05d $counter).jpg;
	convert "${file}" -strip -resize '640x640>' -quality $quality "${TEMPFILE}"
	mcopy -i "${IMGFILE}" "${TEMPFILE}" ::/"${newfile}" &>/dev/null
	if [[ $? -ne 0 ]]; then
		mknewdisk
		mcopy -i "${IMGFILE}" "${TEMPFILE}" ::/"${newfile}" &>/dev/null
	fi;
	counter=$((counter+1));
done;
rm "${TEMPFILE}"

