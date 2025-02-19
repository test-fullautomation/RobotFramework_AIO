#!/bin/bash
########################################################################################

#setlocal enabledelayedexpansion
mypath=$(realpath $(dirname $0))
sourceDir=$mypath/../download
vscodeData=$mypath/../config/robotvscode/
vscodeIcons=$mypath/../config/robotvscode/icons
vscode_jsonp=$mypath/../../vscode-jsonp/jsonp-?.?.?.vsix
destDir=$(realpath $mypath/../..)

use_cntlm="No"
python_only="No"
vscode_only="No"
pandoc_only="No"
android_only="No"

UNAME=$(uname)

# Load Version definition of package tools
source $mypath/versions.conf

if [ "$UNAME" == "Linux" ] ; then
	os=linux
	os_short=linux
	arch=
	platform=linux-x64
elif [[ "$UNAME" == CYGWIN* || "$UNAME" == MINGW* ]] ; then
	os=windows
	os_short=win
	arch=-x64
	platform=win32-x64
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

	retry_counter=0
	max_retries=5
	success=false

	echo curl $proxy_args "$package_url" -o "$package_out"
	while [[ "$retry_counter" -lt "$max_retries" && "$success" == "false" ]];do
		curl $proxy_args -L -k "$package_url" -o "$package_out"

		if [ $? -eq 0 ]; then
			success=true
			goodmsg "Successfully downloaded $package_name"
		else
			((retry_counter++))
			echo "Failed to download $package_url (attempt: $retry_counter)"
			sleep 1
			if [ "$use_cntlm" == "Yes" ]; then
				restart_cntlm
			fi
		fi
	done

	if [ "$success" == "false" ]; then
		errormsg "FATAL: Could not download $package_url after $max_retries attempts"
	fi
}

function packaging_android() {
	download_android_emulator_hypervisor_driver=https://github.com/google/android-emulator-hypervisor-driver/releases/download/v2.2/aehd-windows_v2_2_0.zip
	download_android_google_apis=https://dl.google.com/android/repository/sys-img/google_apis/x86_64-34_r13.zip

	archived_android_emulator_hypervisor_driver=aehd-windows_v2_2_0.zip
	archived_android_google_apis=x86_64-34_r13.zip

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
		npm_bin=$destDir/devtools/nodejs/npm
	else
	   mkdir $destDir/devtools/nodejs
		tar -xf ${sourceDir}/${archived_nodejs} -C $destDir/devtools/nodejs --strip-components=1
		PATH="$destDir/devtools/nodejs/bin:$PATH"
		npm_bin=$destDir/devtools/nodejs/bin/npm
	fi

	echo "Downloading Android Emulator hypervisor driver"
	download_package "AEHD" ${download_android_emulator_hypervisor_driver} ${mypath}/${archived_android_emulator_hypervisor_driver}
	/usr/bin/yes A | unzip ${mypath}/${archived_android_emulator_hypervisor_driver} -d $mypath/devtools/Android

	mkdir  $destDir/system-images
	mkdir  $destDir/system-images/android-34
	mkdir  $destDir/system-images/android-34/google_apis

	echo "Downloading Android Google APIs"
	download_package "Android Google APIs" ${download_android_google_apis} ${mypath}/${archived_android_google_apis}
	/usr/bin/yes A | unzip ${mypath}/${archived_android_google_apis} -d $mypath/devtools/Android/system-images/android-34/google_apis
	rm -rf $destDir/system-images/android-34/google_apis/x86_64-34_r13
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

function make_android() {
	packaging_android
}

if [ ! -d "$sourceDir" ]; then
	mkdir "$sourceDir"
else
	rm -R -- "$sourceDir"/*
fi

make_android
