#!/bin/bash

# Define variables
# download_url="https://mirror.ctan.org/systems/texlive/tlnet"
download_url="https://ftp.math.utah.edu/pub/tex/historic/systems/texlive/2023"
archive_file="install-tl.zip"
TEXDIR="C:/texlive/aio"
collections=("pictures" "latex")
extraPackages=(
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

# Download and extract TexLive installer package
mkdir -p download
echo "Downloading Textlive installer package"
if curl -L "$download_url/$archive_file" -o "download/$archive_file"; then
  unzip "download/$archive_file" -d download/
  mv download/install-tl-* download/install-tl
else
  echo "Error downloading TexLive installer package."
  exit 1
fi


mkdir -p "$TEXDIR"
echo "Create texlive profile file"
profileContent="selected_scheme scheme-full
TEXDIR $TEXDIR\n"
for collection in "${collections[@]}"; do
    profileContent+="collection-$collection 1\n"
done
echo -e "$profileContent" > "download/texlive.profile"

# Perform texlive installation
# use -repository ${download_url}/tlnet-final argument for historic texlive
if cd download/install-tl/ && ./install-tl-windows.bat -no-verify-downloads -repository ${download_url}/tlnet-final -no-gui -profile=../texlive.profile && cd ../../; then
    echo "TexLive installation completed successfully."
else
    echo "Error running TexLive installer."
    exit 1
fi

# Find actual path of tlmgr.bat under $TEXDIR
tlmgrPath=$(find "$TEXDIR" -name "tlmgr.bat" -type f -print -quit)

if [ -n "$tlmgrPath" ] && [ -f "$tlmgrPath" ]; then
  # Install extra packages
  for package in "${extraPackages[@]}"; do
    echo "install $package with tlmgr"
    if "$tlmgrPath" install "$package" --no-verify-downloads; then
      echo "Package '$package' installed successfully."
    else
      echo "Error installing package '$package'."
      exit 1
    fi
  done
else
  echo "Cannot find location of tlmgr.bat."
  exit 1
fi


# Set environment variable GENDOC_LATEXPATH for genpackagedoc
pdflatexDir=$(find "$TEXDIR" -name "pdflatex.exe" -type f -exec dirname {} \; -quit)
if [ -n "$pdflatexDir" ] && [ -d "$pdflatexDir" ]; then
  export GENDOC_LATEXPATH=$pdflatexDir
else
  echo "Cannot find location of pdflatex binary."
  exit 1
fi


echo "TexLive installation and configuration completed successfully."
