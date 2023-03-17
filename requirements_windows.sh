texlive_packages=(
"multirow"
"booktabs"
"framed"
"fvextra"
"courier"
"efbox"
"grffile"
"pdfpages"
"tcolorbox"
"wasysym"
"wasy"
"fancyvrb"
"xcolor"
"etoolbox"
"upquote"
"lineno"
"eso-pic"
"lstaddons"
"pdflscape"
"infwarerr"
"pgf"
"environ"
"trimspaces"
"listings"
"pdfcol"
)
# extra_packages=""
# for package in ${texlive_packages[@]}; do
#   extra_packages+="$package,"
# done

if [ -n $GENDOC_LATEXPATH ]; then
  TEXLIVE_DIR=${GENDOC_LATEXPATH%/bin/win32}
else
  TEXLIVE_DIR="C:/texlive/aio"
  export GENDOC_LATEXPATH="${TEXLIVE_DIR}/bin/win32"
fi

# choco install texlive --version=2022.20221202 --params "'/collections:pictures,latex,latexextra,latexrecommended'" --execution-timeout 5400
choco install texlive --params "'/collections:pictures,latex /InstallationPath:${TEXLIVE_DIR}'"

tlmgr="${TEXLIVE_DIR}/bin/win32/tlmgr.bat"

# Update TeX Live package database
$tlmgr update --self --all

# Install each package in the list
for package in ${texlive_packages[@]}; do
  $tlmgr install "$package"
done
