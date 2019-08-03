#!/bin/bash
DOC_BEGIN="\\documentclass{article}
\\usepackage{color}
\\pagestyle{empty}
\\pagecolor{black}
\\begin{document}{
  \\fontsize{20.74}{20.74}
  \\color{white}
  \\begin{eqnarray*}
"
DOC_END="\\end{eqnarray*}
}\\end{document}
"

TEMPDIR=$(mktemp -d)
DIR="$(pwd)"
echo -n "${DOC_BEGIN}" > "${TEMPDIR}/output.tex"
cat "${1}" >> "${TEMPDIR}/output.tex"
echo -n "${DOC_END}" >> "${TEMPDIR}/output.tex"
cd "${TEMPDIR}"
pdflatex -interaction=nonstopmode output.tex
cd "${DIR}"
gs -q -dNOPAUSE -dBATCH -dFIXEDMEDIA -sDEVICE=pdfwrite -o -\
  -dDEVICEWIDTHPOINTS=1224 -dDEVICEHEIGHTPOINTS=792\
  -c "<</BeginPage{2.4 1 scale}>> setpagedevice" \
  -r300x300 "${TEMPDIR}/output.pdf"\
  | convert -trim +adjoin -transparent black +antialias - "${2}"
rm -r "${TEMPDIR}"
