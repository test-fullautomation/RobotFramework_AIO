#!/bin/bash
########################################################################################
#
# this script 
# - downloads Visual Studio Code and installs initial plugins
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
wgetPath=$mypath/wget.exe
proxyPath=$mypath/settings.ini
sourceDir=$mypath/../download
vscodeData=$mypath/../config/robotvscode/
vscodeIcons=$mypath/../config/robotvscode/icons
pythonTools=$mypath/../config/python
destDir=$(realpath $mypath/../..)
using_proxy=No

#
# import common bash scripts
#
. $mypath/../include/bash/common.sh

function myini() {
	git config -f $proxyPath --get $1;
}

function emirror() {
	xmlstarlet=$mypath/xmlstarlet/xml.exe
	$xmlstarlet sel -t -v "mirrors/mirror/@url" $1 | head -n 1;
}

function parse_setting () {
	if [ ! -f "$proxyPath" ]; then
		errormsg "ini-file: '$proxyPath' is not existing"
	fi

	using_proxy=$(myini proxy.enable)

	if [ "$using_proxy" != "yes" ]; then
		if [ "$using_proxy" != "no" ]; then
			errormsg "./settings.ini proxy.enable can be either 'yes' or 'no'! Found: '$using_proxy'"
		fi
	fi

	if [ ! -d "$sourceDir" ]; then
		mkdir "$sourceDir"
	else	
		rm -R -- "$sourceDir"/*/
	fi

	if [ "$using_proxy" == "yes" ]; then
		proxy=$(myini proxy.proxy)
		if [ "$proxy" == "" ]; then
			read -p "Please enter proxy address : " proxy
		fi
		shopt -s extglob
		proxy="${proxy#http?(s)://}"
		
		proxy_user=$(myini proxy.username)
		if [ "$proxy_user" == "" ]; then
			read -p "Please enter proxy username : " proxy_user
		fi
		
		proxy_pass=$(myini proxy.password)
		if [ "$proxy_pass" == "" ]; then
			read -s -p "Please  enter proxy password: " proxy_pass
		fi
	fi
	
	if [ "$?" -ne 0 ]; then
		errormsg "Could not create Visual Studio Code and Python repository. Most likely you have an proxy configuration error. Please check your './wget/settings.ini' file."
	fi
}



#
#  download clean python source
#
####################################################
function download_python() {
	if [ "$using_proxy" == "yes" ]; then
		"$wgetPath" -P "$sourceDir" --proxy-user=$proxy_user --proxy-password="$proxy_pass" -e use_proxy=yes -e https_proxy=$proxy https://www.python.org/ftp/python/3.9.0/python-3.9.0-embed-amd64.zip
		logresult "$?" "downloaded Python" "download Python"
		
		curl -x $proxy -U $proxy_user:"$proxy_pass" https://bootstrap.pypa.io/get-pip.py -o "$sourceDir/get-pip.py"
		logresult "$?" "downloaded PIP (pip installs packages for python)" " download PIP (pip installs packages for python)"
	else
		"$wgetPath" -P "$sourceDir" https://www.python.org/ftp/python/3.9.0/python-3.9.0-embed-amd64.zip
		logresult "$?" "downloaded Python" "download Python"
		
		curl https://bootstrap.pypa.io/get-pip.py -o "$sourceDir/get-pip.py"
		logresult "$?" "downloaded PIP (pip installs packages for python)" "download PIP (pip installs packages for python)"
	fi
}

#
#  preparing and creating Python repository
#
####################################################
function packaging_python() {
	unzip "$sourceDir/python-3.9.0-embed-amd64.zip" -d "$destDir/python39"
	unzip "$destDir/python39/python39.zip" -d "$destDir/python39/"
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
	echo "$PYDIR" >> "$destDir/python39/Python39._pth"
	echo "$PYDIR\\DLLs" >> "$destDir/python39/Python39._pth"
	echo "$PYDIR\\lib" >> "$destDir/python39/Python39._pth"
	echo "$PYDIR\\lib\\plat-win" >> "$destDir/python39/Python39._pth"
	echo "$PYDIR\\lib\\site-packages" >> "$destDir/python39/Python39._pth"

	if [ "$using_proxy" == "yes" ]; then
		 $destDir/python39/python.exe "$sourceDir/get-pip.py" --proxy="http://$proxy_user:$proxy_pass@$proxy"
	else
		 $destDir/python39/python.exe "$sourceDir/get-pip.py"
	fi
	logresult "$?" "installed PIP (pip installs packages for python)" "install PIP (pip installs packages for python)"

	# call pip to initialize pip
	$destDir/python39/python.exe -m pip --version
	# remove pip workaround
	# If file exists after installation of RobotFramework AIO, then "import robot" will fail.
	# most likely all imports will fail (not tried).
	#remove pth to avoid bokeh build fail
	rm $destDir/python39/Python39._pth

	# !! ATTENTION !!
	# Here we need to avoid that libraries are installed to C:\Users\<userid>\AppData\Roaming\Python\Python39.
	# This would create a conflict with an already existing python version. RobotFramework's python should be
	# fully transparent for the existing system.
	# 
	if [ "$using_proxy" == "yes" ]; then
	    #missing Sphinx and setuptoolsp_pep8 created error when installing pyfranca =>  hardcode installation before processing python_requirements.txt
		$destDir/python39/python.exe -m pip install Sphinx --proxy="http://$proxy_user:$proxy_pass@$proxy"
		$destDir/python39/python.exe -m pip install setuptools_pep8 --proxy="http://$proxy_user:$proxy_pass@$proxy"
		$destDir/python39/python.exe -m pip install -r "$mypath/python_requirements.txt" --proxy="http://$proxy_user:$proxy_pass@$proxy"
	else
	    #missing Sphinx created error when installing pyfranca =>  hardcode installation before processing python_requirements.txt
		$destDir/python39/python.exe -m pip install Sphinx
		$destDir/python39/python.exe -m pip install setuptools_pep8
		$destDir/python39/python.exe -m pip install -r "$mypath/python_requirements.txt"
	fi
	logresult "$?" "installed required packges for Python" "install required packges for Python"

	# Install robotframework serial lib
	. $mypath/python_git_install.sh
	if [ "$using_proxy" == "yes" ]; then
		pyinstall_from_repo $PYDIR "$sourceDir" $proxy $proxy_user "$proxy_pass"
	else
		$destDir/python39/python.exe -m pip install install git+https://github.com/whosaysni/robotframework-seriallibrary.git@d5c33014acafc35f3190d345d422b43699a382f8
	fi

}

function download_vscode()
{
	"$wgetPath" -P "$sourceDir" --proxy-user=$proxy_user --proxy-password="$proxy_pass" -e use_proxy=yes -e https_proxy=$proxy https://az764295.vo.msecnd.net/stable/3a6960b964327f0e3882ce18fcebd07ed191b316/VSCode-win32-x64-1.62.2.zip
	logresult "$?" "downloaded Visual Studio Code" "download Visual Studio Code"
}

function packaging_vscode() {
	unzip "$sourceDir/VSCode-win32-x64-1.62.2.zip" -d "$sourceDir/vscode"
	logresult "$?" "unzipped Visual Studio Code" "unzip Visual Studio Code"

	echo "Install extension for visual code"
	mkdir "$sourceDir/vscode/data"

	"$sourceDir/vscode/bin/code" --install-extension "$vscodeData/extensions/tht13.rst-vscode-3.0.1.vsix" --user-data-dir "$sourceDir/vscode/data"
	logresult "$?" "installed tht13.rst-vscode-3.0.1.vsix Extension" "install tht13.rst-vscode-3.0.1.vsix Extension"
	
	while IFS=, read -r publisher name version
	do
		if [[ -n "$name" ]]; then
			if [ ! -f "${sourceDir}/${name}-${version}.vsix" ]; then
				"$wgetPath" -P "$sourceDir" --proxy-user=$proxy_user --proxy-password="$proxy_pass" -e use_proxy=yes -e https_proxy=$proxy https://open-vsx.org/api/${publisher}/${name}/${version}/file/${publisher}.${name}-${version}.vsix 
				#curl --proxy-ntlm -x $proxy -U $proxy_user:"$proxy_pass" -L https://open-vsx.org/api/${publisher}/${name}/${version}/file/${publisher}.${name}-${version}.vsix -o "$sourceDir/${name}-${version}.vsix"
				logresult "$?" "downloaded ${name}-${version} Extension" "download ${name}-${version} Extension"
			fi
			
			"$sourceDir/vscode/bin/code" --install-extension "${sourceDir}/${publisher}.${name}-${version}.vsix" --user-data-dir "$sourceDir/vscode/data"
			logresult "$?" "installed ${name}-${version}.vsix Extension" "install ${publisher}.${name}-${version}.vsix Extension"
		fi
	done < "$mypath/vscode_requirement.csv"
	
	echo "Creating preconfigured Visual Studio Code repository ..."
	#unzip "$vscodeData/data.zip" -d "$sourceDir/vscode/"
	cp -R -a "$vscodeIcons/." "$sourceDir/vscode/icons"

	cp -R -a "$sourceDir/vscode/." "$destDir/robotvscode/"
	cp -R -a "$vscodeData/data/user-data/User/workspaceStorage" "$destDir/robotvscode/data/user-data/User"
	logresult "$?" "created Robot Visual Code repository" "create Robot Visual Code repository" 
}

function cleanall() {
	#Cleanup all downloaded raw data 
	echo "Cleanup temporary data ..."
	rm -rf "$sourceDir"
	goodmsg "done"
}

function make_vscode() {
	parse_setting
	if [ ! -f "$sourceDir/VSCode-win32-x64-1.62.2.zip" ]; then
		download_vscode
	fi
	packaging_vscode
	goodmsg "done"
}

function make_python() {
	parse_setting
	if [ ! -f "$sourceDir/python-3.9.0-embed-amd64.zip" ]; then
		download_python
	fi
	packaging_python
	goodmsg "done"
}

function make_all() {
	parse_setting
	if [ ! -f "$sourceDir/VSCode-win32-x64-1.62.2.zip" ]; then
   		download_vscode
	fi
	packaging_vscode
	
	if [ ! -f "$sourceDir/python-3.9.0-embed-amd64.zip" ]; then
		download_python
	fi
	packaging_python

	goodmsg "done"
}

echo -e "${COL_GREEN}####################################################################################${COL_RESET}"
echo -e "${COL_GREEN}#                                                                                  #${COL_RESET}"
echo -e "${COL_GREEN}#          Creating Visual Studio Code and Python Repository from OSS ...          #${COL_RESET}"
echo -e "${COL_GREEN}#                                                                                  #${COL_RESET}"
echo -e "${COL_GREEN}####################################################################################${COL_RESET}"


if [[ "$1" == "python" ]]; then
	make_python
elif [[ "$1" == "vscode" ]]; then
    make_vscode
elif [[ "$1" == "check" ]]; then
    parse_setting
elif [[ "$1" == "pandoc" ]]; then
    make_pandoc
else
	make_all
fi
