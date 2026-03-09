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
vscode_jsonp=$mypath/../../vscode-jsonp/jsonp-?.?.?.vsix
destDir=$(realpath $mypath/../..)
wheelHouseDir=$mypath/../wheelhouse

use_cntlm="No"
python_only="No"
vscode_only="No"
pandoc_only="No"
android_only="No"
use_cache="No"

UNAME=$(uname)

# Load Version definition of package tools
source $mypath/versions.conf

echo "VS Codium version $VERSION_VSCODIUM"
echo "Node.js version $VERSION_NODEJS"
echo "Android SDK Build Tool version $VERSION_BUILD_TOOL"
echo "Android SDK Platform Tool version $VERSION_PLATFORM_TOOL"
echo "Appium Inspector version $VERSION_APPIUM_INSPECTOR"
echo "Appium Server version $VERSION_APPIUM_SERVER"

function parse_arg() {
	while [ "$#" -gt 0 ]; do
	case "$1" in
		-c) echo "Using cntlm";use_cntlm="Yes"; shift 1;;

		--use-cntlm) echo "Using cntlm";use_cntlm="Yes"; shift;;
		--python) echo "Create Python repo only";python_only="Yes"; shift;;
		--vscode) echo "Create vscode repo only";vscode_only="Yes"; shift;;
		--pandoc) echo "Create pandoc repo only";pandoc_only="Yes"; shift;;
		--android) echo "Create android repo only";android_only="Yes"; shift;;
		--cache-folder=*)
			cache_folder="${1#*=}"
			cache_folder="${cache_folder//\\//}"
			use_cache="Yes"
			echo "Cache folder: $cache_folder"
			shift
			;;

		-*) echo "unknown option: $1" >&2; exit 1;;
	esac
	done
}

parse_arg "$@"
if [[ "$use_cache" == "No" ]]; then
	rm -R -- "$sourceDir"/*
else
	sourceDir=$cache_folder
	echo "Using cache folder '$sourceDir' for installing dependencies tools"
fi
if [ ! -d "$sourceDir" ]; then
	mkdir "$sourceDir"
fi

if [ "$UNAME" == "Linux" ] ; then
	os=linux
	os_short=linux
	arch=
	platform=linux-x64
	download_python_url=https://github.com/indygreg/python-build-standalone/releases/download/20250205/cpython-3.13.2+20250205-x86_64-unknown-linux-gnu-install_only.tar.gz

	download_vscode_url=https://github.com/VSCodium/vscodium/releases/download/${VERSION_VSCODIUM}/VSCodium-linux-x64-${VERSION_VSCODIUM}.tar.gz

	archived_python_file=$sourceDir/cpython-3.13.2+20250205-x86_64-unknown-linux-gnu-install_only.tar.gz
	archived_vscode_file=$sourceDir/VSCodium-linux-x64-${VERSION_VSCODIUM}.tar.gz

	nodejs_ext=tar.xz
	appium_inspector_ext=AppImage
	android_tools_version=6858069 # Compatible with java 11
elif [[ "$UNAME" == CYGWIN* || "$UNAME" == MINGW* ]] ; then
	os=windows
	os_short=win
	arch=-x64
	platform=win32-x64
	download_python_url=https://github.com/astral-sh/python-build-standalone/releases/download/20250205/cpython-3.13.2+20250205-x86_64-pc-windows-msvc-shared-install_only.tar.gz
	download_vscode_url=https://github.com/VSCodium/vscodium/releases/download/${VERSION_VSCODIUM}/VSCodium-win32-x64-${VERSION_VSCODIUM}.zip
	download_pandoc_url=https://github.com/jgm/pandoc/releases/download/2.18/pandoc-2.18-windows-x86_64.zip

	archived_python_file=$sourceDir/cpython-3.13.2+20250205-x86_64-pc-windows-msvc-shared-install_only.tar.gz
	archived_vscode_file=$sourceDir/VSCodium-win32-x64-${VERSION_VSCODIUM}.zip
	archived_pandoc_file=$sourceDir/pandoc-2.18-windows-x86_64.zip

	nodejs_ext=zip
	appium_inspector_ext=zip
	android_tools_version=13114758
else
	errormsg "Operation system '$UNAME' is not supported."
fi

#
# import common bash scripts
#
. $mypath/../include/bash/common.sh

function restart_cntlm(){
	if [ "$UNAME" == "Linux" ] ; then
		sudo systemctl restart cntlm
	elif [[ "$UNAME" == CYGWIN* || "$UNAME" == MINGW* ]] ; then
		net stop cntlm
		sleep 3
		net start cntlm
	fi
	sleep 1
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
	alternative_url=$4

	retry_counter=0
	max_retries=5
	success=false

	if [ -f "$package_out" ]; then
		echo "Using cached file '$package_out'"
		return 0
	fi

	echo curl $proxy_args "$package_url" -o "$package_out"
	while [[ "$retry_counter" -lt "$max_retries" && "$success" == "false" ]];do
		response=$(curl $proxy_args -L -k "$package_url" -o "$package_out" -w "\n%{http_code}")
		http_status=$(echo "$response" | tail -n1)

		if [[ $? -eq 0 && "$http_status" -eq 200 ]]; then
			success=true
			goodmsg "Successfully downloaded $package_name"
		else
			if [[ -n $alternative_url ]]; then
				response=$(curl $proxy_args -L -k "$alternative_url" -o "$package_out" -w "\n%{http_code}")
				http_status=$(echo "$response" | tail -n1)

				if [[ $? -eq 0 && "$http_status" -eq 200 ]]; then
					success=true
					goodmsg "Successfully downloaded $package_name"
				fi
			fi

			if [ "$success" == "false" ]; then
				((retry_counter++))
				echo "Failed to download $package_url (attempt: $retry_counter)"
				sleep 1
				if [ "$use_cntlm" == "Yes" ]; then
					restart_cntlm
				fi
			fi
		fi
	done

	if [ "$success" == "false" ]; then
		errormsg "FATAL: Could not download $package_url after $max_retries attempts"
	fi
}

function packaging_vscode() {
	MY_PUBLISHER="test-fullautomation"
	rm -rf "$sourceDir/vscodium"
	if [ "$UNAME" == "Linux" ] ; then
		mkdir -p "$sourceDir/vscodium"
		tar --force-local -xf "$archived_vscode_file" -C "$sourceDir/vscodium"
	elif [[ "$UNAME" == CYGWIN* || "$UNAME" == MINGW* ]] ; then
		/usr/bin/yes A | unzip "$archived_vscode_file" -d "$sourceDir/vscodium"
	fi

	logresult "$?" "unzipped Visual Studio Codium" "unzip Visual Studio Codium"

	mkdir -p "$sourceDir/vscodium/data"
	cp -rf "$vscodeData/data/user-data" "$sourceDir/vscodium/data/"

	echo "Copy vscode-welcome extension"

	# Find the .vsix file and copy it
	vsix_file=$(find "$mypath/../../vscode-welcome" -name "*.vsix" -type f | head -n 1)
	cp -rf "$vsix_file" "$vscodeData/extensions/"

	# Extract the name of the .vsix file
	vsix_name=$(basename $vsix_file .vsix)

	mkdir -p "$vscodeData/extensions/$MY_PUBLISHER.$vsix_name"

	vscodium_setting_file="$sourceDir/vscodium/data/user-data/User/settings.json"
	# add proxy configuration in vscodium setting if given
	if [ "$VSCODIUM_PROXY" != "" ] ; then
		if [[ -f "$vscodium_setting_file" ]]; then
			sed -i -E "s|\"http.proxy\": \"\"|\"http.proxy\": \"$VSCODIUM_PROXY\"|g" "$vscodium_setting_file"
		else
			echo "Vscodium setting file '$vscodium_setting_file' does not exist"
		fi
	fi

	echo "Add workbench.colorCustomizations for terminal colors"
	if grep -q '"workbench.colorCustomizations"' "$vscodium_setting_file"; then
		echo "Replace existing workbench.colorCustomizations"
		sed -i -E '/"workbench.colorCustomizations":\s*\{[^}]*\}/c\
    "workbench.colorCustomizations": {\
        "terminal.integrated.customGlyphs": true,\
        "terminal.ansiMagenta": "#C71585",\
        "terminal.ansiBrightMagenta": "#FF69B4",\
        "terminal.ansiRed": "#FF4040",\
        "terminal.ansiBrightRed": "#FF0000"\
    },' "$vscodium_setting_file"
	else
		echo "append workbench.colorCustomizations before closing brace"
		sed -i -E '$ s/}/    "workbench.colorCustomizations": {\
        "terminal.integrated.customGlyphs": true,\
        "terminal.ansiMagenta": "#C71585",\
        "terminal.ansiBrightMagenta": "#FF69B4",\
        "terminal.ansiRed": "#FF4040",\
        "terminal.ansiBrightRed": "#FF0000"\
    },\n}/' "$vscodium_setting_file"
	fi

   if grep -q '"robotframeworkWelcome.hasSeenWelcome"' "$vscodium_setting_file"; then
       echo "robotframeworkWelcome.hasSeenWelcome exists, updating to true"
       sed -i -E 's/"robotframeworkWelcome.hasSeenWelcome":\s*(true|false)/"robotframeworkWelcome.hasSeenWelcome": true/' "$vscodium_setting_file"
   else
       echo "Append robotframeworkWelcome.hasSeenWelcome with true before closing brace"
       sed -i -E '$ s/}/    "robotframeworkWelcome.hasSeenWelcome": true,\n}/' "$vscodium_setting_file"
   fi

	# Ensure "workbench.startupEditor" is set to "none"
	if grep -q '"workbench.startupEditor"' "$vscodium_setting_file"; then
	    echo "workbench.startupEditor exists, updating to none"
	    sed -i -E 's/"workbench.startupEditor":\s*"[^"]*"/"workbench.startupEditor": "none"/' "$vscodium_setting_file"
	else
	    echo "Append workbench.startupEditor with none before closing brace"
	    sed -i -E '$ s/}/    "workbench.startupEditor": "none",\n}/' "$vscodium_setting_file"
	fi

	echo "Install extension for visual codium from *.vsix files under config/robotvscode/extensions folder"
	chmod +x "$sourceDir/vscodium/bin/codium"
	for extfile in $vscodeData/extensions/*.vsix; do
		"$sourceDir/vscodium/bin/codium" --install-extension "$extfile" --user-data-dir "$sourceDir/vscodium/data"
		logresult "$?" "installed ${extfile#$vscodeData/extensions/} Extension" "install ${extfile#$vscodeData/extensions/} Extension"
	done

	if [ -f ${vscode_jsonp} ]; then
		jsonp_ext_pathfile=$(ls ${vscode_jsonp})
		json_ext_filename=$(basename $jsonp_ext_pathfile)
		echo "Install ${json_ext_filename} extension from vscode-jsonp repo"
		"$sourceDir/vscodium/bin/codium" --install-extension "${jsonp_ext_pathfile}" --user-data-dir "$sourceDir/vscodium/data"
		logresult "$?" "installed ${json_ext_filename} Extension" "install ${json_ext_filename} Extension"
	fi

	echo "Install extension for visual codium defined in $mypath/vscode_requirement.csv"

	while IFS=, read -r publisher name version dump || [[ -n $publisher ]]
	do
		version=$(echo $version|tr -d '\n'|tr -d '\r')
		url=https://open-vsx.org/api/${publisher}/${name}/${version}/file/${publisher}.${name}-${version}.vsix
		if [ "$name" == "debugpy" ]; then
			url=https://open-vsx.org/api/${publisher}/${name}/${platform}/${version}/file/${publisher}.${name}-${version}@${platform}.vsix
		fi

		microsoft_url=https://${publisher}.gallery.vsassets.io/_apis/public/gallery/PUBLISHER/${publisher}/extension/${name}/${version}/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage
		our_url=https://github.com/${publisher}/${name}/releases/download/${name}-${version}/${name}.vsix

		if [[ -n "$name" ]]; then
			# Download the test-fullautomation asset.
			if [ "$publisher" == "$MY_PUBLISHER" ]; then
            	download_package "${name}-${version} Extension" "$our_url" "$sourceDir/${name}-${version}.vsix"
        	# Download the Open-VSX Community extension.
			elif [ ! -f "${sourceDir}/${name}-${version}.vsix" ]; then
				download_package "${name}-${version} Extension" "$url" "$sourceDir/${name}-${version}.vsix" "$microsoft_url"
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

function packaging_android() {
	# https://dl.google.com/android/repository/tools_r25.2.3-macosx.zip
	download_android_tools=https://dl.google.com/android/repository/commandlinetools-${os_short}-${android_tools_version}_latest.zip
	download_android_emulator=https://redirector.gvt1.com/edgedl/android/repository/emulator-${os}_x64-13402964.zip
	download_android_buildtools=https://dl.google.com/android/repository/build-tools_r${VERSION_BUILD_TOOL}-${os}.zip
	download_android_platformtools=https://dl.google.com/android/repository/platform-tools_r${VERSION_PLATFORM_TOOL}-${os}.zip
	download_nodejs=https://nodejs.org/dist/v${VERSION_NODEJS}/node-v${VERSION_NODEJS}-${os_short}-x64.${nodejs_ext}
	download_appium_inspector=https://github.com/appium/appium-inspector/releases/download/v${VERSION_APPIUM_INSPECTOR}/Appium-Inspector-${os}-${VERSION_APPIUM_INSPECTOR}${arch}.${appium_inspector_ext}

	archived_android_tools=android-tools.zip
	archived_android_emulator=android-emulator.zip
	archived_android_buildtools=android-buildtools.zip
	archived_android_platformtools=android-platformtools.zip
	archived_nodejs=nodejs.${nodejs_ext}
	archived_appium_inspector=appium-inspector.${appium_inspector_ext}

	echo "Packaging Android ..."
	rm -rf $destDir/devtools
	mkdir $destDir/devtools

	npm_proxy_args=""
	if [ "$use_cntlm" == "Yes" ]; then
		npm_proxy_args="--proxy=http://localhost:3128"
	fi

	# download Node.js installer
	echo "Downloading Node.js"
	download_package "Node.js" $download_nodejs ${sourceDir}/${archived_nodejs}
	if [ "$nodejs_ext" == "zip" ]; then
		# Not using cntlm proxy for Windows runner
		npm_proxy_args=""
		/usr/bin/yes A | unzip ${sourceDir}/${archived_nodejs} -d $destDir/devtools
		mv $destDir/devtools/node-* $destDir/devtools/nodejs
		PATH="$destDir/devtools/nodejs:$PATH"
		npm_bin=$destDir/devtools/nodejs/npm
	else
	   mkdir $destDir/devtools/nodejs
		tar --force-local -xf ${sourceDir}/${archived_nodejs} -C $destDir/devtools/nodejs --strip-components=1
		PATH="$destDir/devtools/nodejs/bin:$PATH"
		npm_bin=$destDir/devtools/nodejs/bin/npm
	fi

	# download appium packages:
	# 	- appium server
	echo "Installing appium server"
	$npm_bin install --prefix $destDir/devtools/nodejs appium@${VERSION_APPIUM_SERVER} -g --verbose ${npm_proxy_args}
	logresult "$?" "installed appium server" "install appium server"

	#  - UIAutomator2 driver for appium
	echo "Installing UIAutomator2 driver for appium"
	export APPIUM_SKIP_CHROMEDRIVER_INSTALL=1
	$npm_bin install --prefix $destDir/devtools/nodejs appium-uiautomator2-driver -g --verbose ${npm_proxy_args}
	logresult "$?" "installed UIAutomator2 driver for appium" "install UIAutomator2 driver for appium"
	# APPIUM_HOME=./android appium driver install uiautomator2
	# APPIUM_HOME=./android appium => scan appium drivers under APPIUM_HOME

	# 	- appium inspector
	echo "Downloading Appium Inspector"
	download_package "Appium Inspector" ${download_appium_inspector} ${sourceDir}/${archived_appium_inspector}
	if [ "$appium_inspector_ext" == "zip" ]; then
		/usr/bin/yes A | unzip ${sourceDir}/${archived_appium_inspector} -d $destDir/devtools/Appium-Inspector
	else
		cp ${sourceDir}/${archived_appium_inspector} $destDir/devtools/Appium-Inspector.${appium_inspector_ext}
	fi


	mkdir -p $destDir/devtools/Android/cmdline-tools
	mkdir -p $destDir/devtools/Android/build-tools
	mkdir -p $destDir/devtools/Android/platforms
	mkdir -p $destDir/devtools/Android/system-images/android-34/google_apis
	# download Android SDK Tools
	echo "Downloading Android Cmdline Tools"
	download_package "Android SDK Tools" ${download_android_tools} ${sourceDir}/${archived_android_tools}
	/usr/bin/yes A | unzip ${sourceDir}/${archived_android_tools} -d $destDir/devtools/Android/cmdline-tools
	mv $destDir/devtools/Android/cmdline-tools/cmdline-tools $destDir/devtools/Android/cmdline-tools/latest

	echo "Downloading Android Platform Tools"
	download_package "Android Platform Tools" ${download_android_platformtools} ${sourceDir}/${archived_android_platformtools}
	/usr/bin/yes A | unzip ${sourceDir}/${archived_android_platformtools} -d $destDir/devtools/Android

	echo "Downloading Android Build Tools"
	download_package "Android Build Tools" ${download_android_buildtools} ${sourceDir}/${archived_android_buildtools}
	/usr/bin/yes A | unzip ${sourceDir}/${archived_android_buildtools} -d $destDir/devtools/Android/build-tools
	mv $destDir/devtools/Android/build-tools/android-* $destDir/devtools/Android/build-tools/${VERSION_BUILD_TOOL}

	echo "Download Android Emulator"
	download_package "Android Emulator" ${download_android_emulator} ${sourceDir}/${archived_android_emulator}
	/usr/bin/yes A | unzip ${sourceDir}/${archived_android_emulator} -d $destDir/devtools/Android
}

#
#  Packaging python for Windows
#
####################################################
function packaging_python_windows() {
	rm -rf "$sourceDir/python"
	tar --force-local -xzf "$archived_python_file" -C "$sourceDir"
	rm -rf "$destDir/python3"
	mv "$sourceDir/python" "$destDir/python3"


	# !! ATTENTION !!
	# embedded python has problems with to recognize a PIP installation.
	# below ._pth touches make PIP working
	# Note: Use ._pth can cause other poblems: https://stackoverflow.com/questions/47851452/add-package-path-to-python-pth-file-using-environment-variables
	#       There are no way to add script path to ._pth now
	CURDIR=$(pwd)
	PYDIR=$(cd $destDir/python3; pwd -W)
	cd $CURDIR

	proxy_args=""
	if [ "$use_cntlm" == "Yes" ]; then
		proxy_args="--proxy 127.0.0.1:3128"
	fi

	# call pip to initialize pip
	$destDir/python3/python.exe -m pip install --upgrade pip
	$destDir/python3/python.exe -m pip install --upgrade setuptools
	$destDir/python3/python.exe -m pip install wheel --upgrade

	# !! ATTENTION !!
	# Here we need to avoid that libraries are installed to C:\Users\<userid>\AppData\Roaming\Python\Python39.
	# This would create a conflict with an already existing python version. RobotFramework's python should be
	# fully transparent for the existing system.
	#
	$destDir/python3/python.exe -m pip wheel -w $wheelHouseDir -r "$mypath/python_requirements.txt" $proxy_args
	logresult "$?" "downloaded required packages for Python" "download required packages for Python"
	# Workaround for pyfranca
	$destDir/python3/python.exe -m pip wheel -w $wheelHouseDir pyfranca
	logresult "$?" "downloaded pyfranca package" "download pyfranca package"
	# Copy file to handle traceback color python
	cp $mypath/../config/python/* $destDir/python3/Lib/site-packages/
}

#
#  Packaging python for Linux
#
####################################################
function packaging_python_linux() {
	rm -rf "$sourceDir/python"
	tar --force-local -I zstd -xvf $archived_python_file -C "$sourceDir"
	rm -rf "$destDir/python3lx"
	mv "$sourceDir/python" "$destDir/python3lx"
	logresult "$?" "created Python repository" "create Python repository"

	# Upgrade pip
	$destDir/python3lx/bin/python3 -m pip install --upgrade pip

	# !! ATTENTION !!
	# Here we need to avoid that libraries are installed to C:\Users\<userid>\AppData\Roaming\Python\Python39.
	# This would create a conflict with an already existing python version. RobotFramework's python should be
	# fully transparent for the existing system.
	#
	$destDir/python3lx/bin/python3 -m pip wheel -w $wheelHouseDir -r "$mypath/python_requirements_lx.txt"
	logresult "$?" "downloaded required packages for Python" "download required packages for Python"
	# Copy file to handle traceback color python
	cp $mypath/../config/python/* $destDir/python3lx/lib/python3.13/site-packages
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
	# if [ ! -f "$archived_vscode_file" ]; then
	download_package "Visual Studio Code" "$download_vscode_url" "$archived_vscode_file"
	# fi
	packaging_vscode
	goodmsg "make_vscode done"
}

function make_python() {
	# if [ ! -f "$archived_python_file" ]; then
	download_package "Python" "$download_python_url" "$archived_python_file"
	# fi

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

function make_android() {
	packaging_android
}

function make_all() {
	make_python
	make_vscode
	make_android
	# make_pandoc
	goodmsg "make_all done"
}

echo -e "${COL_GREEN}####################################################################################${COL_RESET}"
echo -e "${COL_GREEN}#                                                                                  #${COL_RESET}"
echo -e "${COL_GREEN}#          Creating VSCode and Python Repository from OSS ...                      #${COL_RESET}"
echo -e "${COL_GREEN}#                                                                                  #${COL_RESET}"
echo -e "${COL_GREEN}####################################################################################${COL_RESET}"


if [[ "$python_only" == "Yes" ]]; then
	make_python
elif [[ "$vscode_only" == "Yes" ]]; then
	make_vscode
elif [[ "$pandoc_only" == "Yes" ]]; then
	make_pandoc
elif [[ "$android_only" == "Yes" ]]; then
	make_android
else
	make_all
fi
