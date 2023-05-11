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
extra_packages=""
for package in ${texlive_packages[@]}; do
  extra_packages+="$package,"
done

TEXLIVE_DIR="C:/texlive/aio"

# choco install texlive --version=2022.20221202 --params "'/collections:pictures,latex,latexextra,latexrecommended'" --execution-timeout 5400
choco install texlive --params "'/collections:pictures,latex /InstallationPath:${TEXLIVE_DIR} /extraPackages:${extra_packages}'"

export GENDOC_LATEXPATH="${TEXLIVE_DIR}/bin/windows"
export RobotPlantUMLPath="../robotvscode/data/extensions/jebbs.plantuml-2.17.5-universal"
export GENDOC_PLANTUML_PATH="${RobotPlantUMLPath}"
