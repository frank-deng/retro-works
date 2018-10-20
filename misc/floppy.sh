#!/bin/bash

TEMPFILE=$(tempfile)
dd if=/dev/zero of="${TEMPFILE}" bs=512 count=2880
mformat -i "${TEMPFILE}" -f 1440
mcopy -i "${TEMPFILE}" "${2}"/* ::/
cp "${TEMPFILE}" "${1}"
rm "${TEMPFILE}"
