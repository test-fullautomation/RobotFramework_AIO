#!/bin/bash
########################################################################################
#
# this script 
# - downloads Visual Studio Code
#   - adds plugins
#   - adds preconfigured workspace
#   - puts all to the directory ./build/../robotvscode
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
wgetPath=wget
proxyPath=$mypath/settings.ini
sourceDir=$mypath/../download
vscodeData=$mypath/../config/robotvscode/
vscodeIcons=$mypath/../config/robotvscode/icons
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
	xmlstarlet=xmlstarlet
	$xmlstarlet sel -t -v "mirrors/mirror/@url" $1 | head -n 1;
}

echo -e "${COL_GREEN}####################################################################################${COL_RESET}"
echo -e "${COL_GREEN}#                                                                                  #${COL_RESET}"
echo -e "${COL_GREEN}#          Creating Visual Studio Code and Python Repository from OSS ...          #${COL_RESET}"
echo -e "${COL_GREEN}#                                                                                  #${COL_RESET}"
echo -e "${COL_GREEN}####################################################################################${COL_RESET}"


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
	#rm -rf "$sourceDir"
	mkdir "$sourceDir"
fi

if [ "$using_proxy" == "yes" ]; then
	proxy=$(myini proxy.proxy)
	if [ "$proxy" == "" ]; then
		read -p "Please enter proxy address : " proxy
	fi
	
	proxy_user=$(myini proxy.username)
	if [ "$proxy_user" == "" ]; then
		read -p "Please enter proxy username : " proxy_user
	fi
	
	proxy_pass=$(myini proxy.password)
	if [ "$proxy_pass" == "" ]; then
		read -s -p "Please  enter proxy password: " proxy_pass
	fi
	
	echo

	cntlm_installed=$(apt -qq list cntlm | grep installed)
	echo "$cntlm_installed"
	if [ "$cntlm_installed" == "" ]; then
		apt-get install cntlm -y
	fi
	echo "$proxy_pass" | cntlm -u $proxy_user -f -H	

	#cp "$sourceDir/../config/proxychains.conf" .
	#proxy_url=${proxy/:*/}
	#proxy_port=${proxy/*:/}
	#echo "http	$proxy_url	$proxy_port	$proxy_user	$proxy_pass" >> ./proxychains.conf
	#echo "https	$proxy_url	$proxy_port	$proxy_user	$proxy_pass" >> ./proxychains.conf

fi

# 
#	download and creating vscode reposistory
#
####################################################
if [ ! -f "$sourceDir/VSCode-linux-x64.tar.gz" ]; then
	curl --proxy $proxy -U $proxy_user:"$proxy_pass" https://az764295.vo.msecnd.net/stable/899d46d82c4c95423fb7e10e68eba52050e30ba3/code-stable-x64-1639562789.tar.gz -o "$sourceDir/VSCode-linux-x64.tar.gz"
fi
logresult "$?" "downloaded Visual Studio Code" "download Visual Studio Code"

tar -xvvf "$sourceDir/VSCode-linux-x64.tar.gz" -C "$sourceDir" && mv "$sourceDir/VSCode-linux-x64" "$sourceDir/vscode"
logresult "$?" "unzipped Visual Studio Code" "unzip Visual Studio Code"

echo "Install extension for visual code"
mkdir "$sourceDir/vscode/data"
cp -rf "$vscodeData/data/user-data" "$sourceDir/vscode/data/"

if [ ! -f "$sourceDir/ms-python-release.vsix" ]; then
	# Install vscode-python extension
	curl --proxy $proxy -U $proxy_user:"$proxy_pass" -L https://github.com/microsoft/vscode-python/releases/download/2021.11.1422169775/ms-python-release.vsix -o "$sourceDir/ms-python-release.vsix"
	logresult "$?" "downloaded VScode-Python Extension" "download VScode-Python Extension"
fi
chmod 777 "$sourceDir/ms-python-release.vsix"
chmod +x "$sourceDir/vscode/bin/code"
"$sourceDir/vscode/bin/code" --install-extension "$sourceDir/ms-python-release.vsix" --user-data-dir "$sourceDir/vscode/data"
logresult "$?" "installed VScode-Python Extension" "install VScode-Python Extension"
	
if [ ! -f "$sourceDir/robotframework-lsp.vsix" ]; then
	# Install vscode robotframework language-server extension (robotframework-lsp)
	curl --proxy $proxy -U $proxy_user:"$proxy_pass" -L https://open-vsx.org/api/robocorp/robotframework-lsp/0.31.0/file/robocorp.robotframework-lsp-0.31.0.vsix -o "$sourceDir/robotframework-lsp.vsix"
	logresult "$?" "downloaded robotframework-lsp" "download robotframework-lsp"
fi
"$sourceDir/vscode/bin/code" --install-extension "$sourceDir/robotframework-lsp.vsix" --user-data-dir "$sourceDir/vscode/data"
logresult "$?" "installed VScode-Python Extension" "install VScode-Python Extension"
	
if [ ! -f "$sourceDir/JavaScriptSnippets.vsix" ]; then
	curl --proxy $proxy -U $proxy_user:"$proxy_pass" -L https://open-vsx.org/api/xabikos/JavaScriptSnippets/1.8.0/file/xabikos.JavaScriptSnippets-1.8.0.vsix -o "$sourceDir/JavaScriptSnippets.vsix"
	logresult "$?" "downloaded JavaScriptSnippets" "download JavaScriptSnippets"
fi
"$sourceDir/vscode/bin/code" --install-extension "$sourceDir/JavaScriptSnippets.vsix" --user-data-dir "$sourceDir/vscode/data"
logresult "$?" "installed JavaScriptSnippets.vsix" "install JavaScriptSnippets.vsix"

if [ ! -f "$sourceDir/vscode-xml.vsix" ]; then
	curl --proxy $proxy -U $proxy_user:"$proxy_pass" -L https://open-vsx.org/api/redhat/vscode-xml/0.18.1/file/redhat.vscode-xml-0.18.1.vsix -o "$sourceDir/vscode-xml.vsix"
	logresult "$?" "downloaded vscode-xml.vsix" "download vscode-xml.vsix"
fi
"$sourceDir/vscode/bin/code" --install-extension "$sourceDir/JavaScriptSnippets.vsix" --user-data-dir "$sourceDir/vscode/data"
logresult "$?" "installed vscode-xml.vsix" "install vscode-xml.vsix"
	
if [ ! -f "$sourceDir/bash-ide-vscode.vsix" ]; then
	curl --proxy $proxy -U $proxy_user:"$proxy_pass" -L https://open-vsx.org/api/mads-hartmann/bash-ide-vscode/1.11.0/file/mads-hartmann.bash-ide-vscode-1.11.0.vsix -o "$sourceDir/bash-ide-vscode.vsix"
	logresult "$?" "bash-ide-vscode.vsix" "download bash-ide-vscode.vsix"
fi
"$sourceDir/vscode/bin/code" --install-extension "$sourceDir/JavaScriptSnippets.vsix" --user-data-dir "$sourceDir/vscode/data"
logresult "$?" "installed bash-ide-vscode.vsix" "install bash-ide-vscode.vsix"
	
"$sourceDir/vscode/bin/code" --install-extension "$sourceDir/robotframework-lsp.vsix" --user-data-dir "$sourceDir/vscode/data"
logresult "$?" "installed robotframework-lsp" "install robotframework-lsp"
	
echo "Creating preconfigured Visual Studio Code repository ..."
#unzip "$vscodeData/data.zip" -d "$sourceDir/vscode/"
cp -R -a "$vscodeIcons/." "$sourceDir/vscode/icons"

cp -R -a "$sourceDir/vscode/." "$destDir/robotvscode/"
logresult "$?" "created Robot Visual Code repository" "create Robot Visual Code repository" 

if [ ! -f "$sourceDir/cpython-3.9.2-x86_64-unknown-linux-gnu-pgo-20210303T0937.tar.zst" ]; then
	n=0
	until [ "$n" -ge 20 ]
	do
	   n=$((n+1)) 
	   echo -e "${COL_CYAN}Try $n/20: download of portable python for linux${COL_RESET}"
	   curl --proxy $proxy -U $proxy_user:"$proxy_pass" -L https://github.com/indygreg/python-build-standalone/releases/download/20210303/cpython-3.9.2-x86_64-unknown-linux-gnu-pgo-20210303T0937.tar.zst -o "$sourceDir/cpython-3.9.2-x86_64-unknown-linux-gnu-pgo-20210303T0937.tar.zst" && break
	   sleep 30
	   false
	done
fi
logresult "$?" "downloaded Python" "download Python"

curl --proxy $proxy -U $proxy_user:"$proxy_pass" -L https://bootstrap.pypa.io/get-pip.py -o "$sourceDir/get-pip.py"
logresult "$?" "downloaded PIP (pip installs packages for python)" "download PIP (pip installs packages for python)"

#
#  preparing and creating Python repository
#
####################################################

tar -I zstd -xvf $sourceDir/cpython-3.9.2-x86_64-unknown-linux-gnu-pgo-20210303T0937.tar.zst -C "$sourceDir"
rm -rf "$destDir/python39lx"
mv "$sourceDir/python" "$destDir/python39lx"
logresult "$?" "created Python repository" "create Python repository" 

# !! ATTENTION !!
# embedded python has problems with to recognize a PIP installation.
CURDIR=$(pwd)
cd $CURDIR
if [ "$using_proxy" == "yes" ]; then
   $destDir/python39lx/install/bin/python3 "$sourceDir/get-pip.py" --proxy="http://$proxy_user:$proxy_pass@$proxy"
else
   $destDir/python39lx/install/bin/python3 "$sourceDir/get-pip.py"
fi
logresult "$?" "installed PIP (pip installs packages for python)" "install PIP (pip installs packages for python)"

# !! ATTENTION !!
# Here we need to avoid that libraries are installed to C:\Users\<userid>\AppData\Roaming\Python\Python39.
# This would create a conflict with an already existing python version. RobotFramework's python should be
# fully transparent for the existing system.
# 
if [ "$using_proxy" == "yes" ]; then
    $destDir/python39lx/install/bin/python3 -m pip install -r "$mypath/python_requirements_lx.txt" --proxy="http://$proxy_user:$proxy_pass@$proxy"
else
    $destDir/python39lx/install/bin/python3 -m pip install -r "$mypath/python_requirements_lx.txt" 
fi

#fi
logresult "$?" "installed required packges for Python" "install required packges for Python"

#Cleanup all downloaded raw data 
echo "Cleanup temporary data ..."
#rm -rf "$sourceDir"
goodmsg "done."
