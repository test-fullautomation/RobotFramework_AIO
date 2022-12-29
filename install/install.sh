#!/bin/bash
########################################################################################
#
# this script 
# 	- downloads VSCodium
#   - adds preconfigured workspace
#   - puts all to the directory ./build/../robotdeveclipse
#
# - downloads python (embedded version)
#   - adds pip (python paket manager)
#   - installs all required python packages
#
# - does cleanup of all temporary data
#
#########################################################################################

#sporadically the script stops with strange error messages.
#This is active to have a chance to find the cause.
#set -x

#setlocal enabledelayedexpansion
mypath=$(realpath $(dirname $0))
sourceDir=$mypath/../download
vscodeData=$mypath/../config/robotvscode/
vscodeIcons=$mypath/../config/robotvscode/icons
pythonTools=$mypath/../config/python
destDir=$(realpath $mypath/../..)

use_cntlm="No"
python_only="No"
vscode_only="No"
pandoc_only="No"

UNAME=$(uname)

if [ "$UNAME" == "Linux" ] ; then
	download_python_url=https://github.com/indygreg/python-build-standalone/releases/download/20210303/cpython-3.9.2-x86_64-unknown-linux-gnu-pgo-20210303T0937.tar.zst
	download_vscode_url=https://github.com/VSCodium/vscodium/releases/download/1.73.0.22306/VSCodium-linux-x64-1.73.0.22306.tar.gz

	archived_python_file=$sourceDir/cpython-3.9.2-x86_64-unknown-linux-gnu-pgo-20210303T0937.tar.zst
	archived_vscode_file=$sourceDir/VSCodium-linux-x64-1.73.0.22306.tar.gz
elif [[ "$UNAME" == CYGWIN* || "$UNAME" == MINGW* ]] ; then
	download_python_url=https://github.com/indygreg/python-build-standalone/releases/download/20221002/cpython-3.9.14+20221002-x86_64-pc-windows-msvc-shared-install_only.tar.gz
	download_vscode_url=https://github.com/VSCodium/vscodium/releases/download/1.73.0.22306/VSCodium-win32-x64-1.73.0.22306.zip
	download_pandoc_url=https://github.com/jgm/pandoc/releases/download/2.18/pandoc-2.18-windows-x86_64.zip

	archived_python_file=$sourceDir/cpython-3.9.14+20221002-x86_64-pc-windows-msvc-shared-install_only.tar.gz
	archived_vscode_file=$sourceDir/VSCodium-win32-x64-1.73.0.22306.zip
	archived_pandoc_file=$sourceDir/pandoc-2.18-windows-x86_64.zip
else
	errormsg "Operation system '$UNAME' is not supported."
fi

#
# import common bash scripts
#
. $mypath/../include/bash/common.sh

function parse_arg() {
	while [ "$#" -gt 0 ]; do
	case "$1" in
		-c) echo "Using cntlm";use_cntlm="Yes"; shift 1;;

		--use-cntlm) echo "Using cntlm";use_cntlm="Yes"; shift;;
		--python) echo "Create Python repo only";python_only="Yes"; shift;;
		--vscode) echo "Create vscode repo only";vscode_only="Yes"; shift;;
		--pandoc) echo "Create vscode repo only";pandoc_only="Yes"; shift;;

		-*) echo "unknown option: $1" >&2; exit 1;;
	esac
	done
}
#
#  download packages function
#
####################################################

function download_package(){
	proxy_args=""
	if [ "$use_cntlm" == "Yes" ]; then
		proxy_args="--proxy-ntlm -x 127.0.0.1:3128"
	fi
	package_name=$1
	package_url=$2
	package_out=$3

	echo curl $proxy_args "$package_url" -o "$package_out"
	curl $proxy_args -L "$package_url" -o "$package_out"
	logresult "$?" "downloaded $package_name" "download $package_name"
}

function packaging_vscode() {
	if [ "$UNAME" == "Linux" ] ; then
		mkdir -p "$sourceDir/vscodium"
		tar -xvvf "$archived_vscode_file" -C "$sourceDir/vscodium"
	elif [[ "$UNAME" == CYGWIN* || "$UNAME" == MINGW* ]] ; then
		/usr/bin/yes A | unzip "$archived_vscode_file" -d "$sourceDir/vscodium"
	fi
	
	logresult "$?" "unzipped Visual Studio Codium" "unzip Visual Studio Codium"

	mkdir "$sourceDir/vscodium/data"
	cp -rf "$vscodeData/data/user-data" "$sourceDir/vscodium/data/"

	echo "Install extension for visual codium from *.vsix files under config/robotvscode/extensions folder"
	chmod +x "$sourceDir/vscodium/bin/codium"
	for extfile in $vscodeData/extensions/*.vsix; do
		"$sourceDir/vscodium/bin/codium" --install-extension "$extfile" --user-data-dir "$sourceDir/vscodium/data"
		logresult "$?" "installed ${extfile#$vscodeData/extensions/} Extension" "install ${extfile#$vscodeData/extensions/} Extension"
	done

	echo "Install extension for visual codium defined in $mypath/vscode_requirement.csv"
	while IFS=, read -r publisher name version dump
	do
		version=$(echo $version|tr -d '\n'|tr -d '\r')
		url=https://open-vsx.org/api/${publisher}/${name}/${version}/file/${publisher}.${name}-${version}.vsix

		if [[ -n "$name" ]]; then
			if [ ! -f "${sourceDir}/${name}-${version}.vsix" ]; then
				download_package "${name}-${version} Extension" "$url" "$sourceDir/${name}-${version}.vsix"
			fi
			
			"$sourceDir/vscodium/bin/codium" --install-extension "${sourceDir}/${name}-${version}.vsix" --user-data-dir "$sourceDir/vscodium/data"
			logresult "$?" "installed ${name}-${version}.vsix Extension" "install ${name}-${version}.vsix Extension"
		fi
	done < "$mypath/vscode_requirement.csv"
	
	echo "Creating preconfigured VSCodium repository ..."
	cp -R -a "$vscodeIcons/." "$sourceDir/vscodium/icons"


	cp -R -a "$sourceDir/vscodium/." "$destDir/robotvscode/"
	cp -R -a "$vscodeData/data/user-data/User/workspaceStorage" "$destDir/robotvscode/data/user-data/User"
	logresult "$?" "created Robot VSCodium repository" "create Robot VSCodium repository" 
}

function packaging_pandoc_windows() {
	/usr/bin/yes A | unzip "$archived_pandoc_file" -d "$destDir/pandoc"
	logresult "$?" "unzipped Pandoc" "unzip Pandoc"

	# Add pandoc to PATH env
	export PATH=$PATH:$destDir/pandoc
}

#
#  Packaging python for Windows
#
####################################################
function packaging_python_windows() {
	tar -xzf "$archived_python_file" -C "$sourceDir"
	rm -rf "$destDir/python39"
	mv "$sourceDir/python" "$destDir/python39"

	# tkinter and tcl are not available in using embedded python
	# they are also not able to be installed via pip
	cp -R -a "$pythonTools"/* "$destDir/python39" 
	logresult "$?" "created Python repository" "create Python repository" 

	# !! ATTENTION !!
	# embedded python has problems with to recognize a PIP installation.
	# below ._pth touches make PIP working
	# Note: Use ._pth can cause other poblems: https://stackoverflow.com/questions/47851452/add-package-path-to-python-pth-file-using-environment-variables
	#       There are no way to add script path to ._pth now
	CURDIR=$(pwd)
	PYDIR=$(cd $destDir/python39; pwd -W)
	cd $CURDIR

	proxy_args=""
	if [ "$use_cntlm" == "Yes" ]; then
		proxy_args="--proxy 127.0.0.1:3128"
	fi

	# call pip to initialize pip
	$destDir/python39/python.exe -m pip install --upgrade pip
	$destDir/python39/python.exe -m pip install wheel

	# !! ATTENTION !!
	# Here we need to avoid that libraries are installed to C:\Users\<userid>\AppData\Roaming\Python\Python39.
	# This would create a conflict with an already existing python version. RobotFramework's python should be
	# fully transparent for the existing system.
	# 
	$destDir/python39/python.exe -m pip install -r "$mypath/python_requirements.txt" $proxy_args

	logresult "$?" "installed required packges for Python" "install required packges for Python"

}

#
#  Packaging python for Linux
#
####################################################
function packaging_python_linux() {
	tar -I zstd -xvf $archived_python_file -C "$sourceDir"
	rm -rf "$destDir/python39lx"
	mv "$sourceDir/python" "$destDir/python39lx"
	logresult "$?" "created Python repository" "create Python repository" 

	# !! ATTENTION !!
	# Here we need to avoid that libraries are installed to C:\Users\<userid>\AppData\Roaming\Python\Python39.
	# This would create a conflict with an already existing python version. RobotFramework's python should be
	# fully transparent for the existing system.
	# 
	$destDir/python39lx/install/bin/python3 -m pip install -r "$mypath/python_requirements_lx.txt"
	#fi
	logresult "$?" "installed required packges for Python" "install required packges for Python"
}

#
#  Main functions for install
#
####################################################
function cleanall() {
	#Cleanup all downloaded raw data 
	echo "Cleanup temporary data ..."
	rm -rf "$sourceDir"
	goodmsg "done"
}

function make_vscode() {
	if [ ! -f "$archived_vscode_file" ]; then
		download_package "Visual Studio Code" "$download_vscode_url" "$archived_vscode_file"
	fi
	packaging_vscode
	goodmsg "make_vscode done"
}

function make_python() {
	if [ ! -f "$archived_python_file" ]; then
		download_package "Python" "$download_python_url" "$archived_python_file"
	fi

	if [ "$UNAME" == "Linux" ] ; then
		packaging_python_linux
	elif [[ "$UNAME" == CYGWIN* || "$UNAME" == MINGW* ]] ; then
		packaging_python_windows
	fi
	
	goodmsg "make_python done"
}

function make_pandoc() {
	if [ "$UNAME" == "Linux" ] ; then
		echo "pandoc is already installed with apt-get."
	elif [[ "$UNAME" == CYGWIN* || "$UNAME" == MINGW* ]] ; then
		if [ ! -f "$archived_pandoc_file" ]; then
			download_package "Pandoc" "$download_pandoc_url" "$archived_pandoc_file"
		fi
		packaging_pandoc_windows
		goodmsg "make_pandoc done"
	fi
}

function make_all() {
	make_python
	make_vscode
	make_pandoc
	goodmsg "make_all done"
}

echo -e "${COL_GREEN}####################################################################################${COL_RESET}"
echo -e "${COL_GREEN}#                                                                                  #${COL_RESET}"
echo -e "${COL_GREEN}#          Creating VSCode and Python Repository from OSS ...                      #${COL_RESET}"
echo -e "${COL_GREEN}#                                                                                  #${COL_RESET}"
echo -e "${COL_GREEN}####################################################################################${COL_RESET}"

parse_arg "$@"

if [ ! -d "$sourceDir" ]; then
	mkdir "$sourceDir"
else
	rm -R -- "$sourceDir"/*
fi

if [[ "$python_only" == "Yes" ]]; then
	make_python
elif [[ "$vscode_only" == "Yes" ]]; then
	make_vscode
elif [[ "$pandoc_only" == "Yes" ]]; then
	make_pandoc
else
	make_all
fi
