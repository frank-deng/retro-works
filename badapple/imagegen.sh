#!/bin/bash

SOURCE=${1}
TARGET='.'
if [[ ! -z ${2} ]]; then
  TARGET="${2}"
fi

ffmpeg -i ${SOURCE} -vf scale=160:104,fps=fps=8/1 -q 0 "${TARGET}/%04d.png"
find "${TARGET}" -iname \*.png -exec mogrify -monochrome +dither {} \;

