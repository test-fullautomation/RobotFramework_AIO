
#setlocal enabledelayedexpansion
mypath=$(realpath $(dirname $0))
#
# import common bash scripts
#
. $mypath/../include/bash/common.sh

# Declare the repositories of python that can't be installed by pip behind proxy here
declare -a arRepos=(  
					# workaround for issues: https://github.com/whosaysni/robotframework-seriallibrary/issues/10
               # pol2hi: installed pip: robotframework-seriallibrary instead (added to requirements.sh)
               # commented out github develop version
					#"https://codeload.github.com/whosaysni/robotframework-seriallibrary/zip/refs/heads/develop"
)
					
# iterate over all repositories and install       
# pyinstall_from_repo [PythonDir] [Folder to store repo] [proxy] [proxy_user] [proxy_password]
function pyinstall_from_repo
{   
	if [ -z "$1" ]; then
	    errormsg "python folder was not set"
	fi
	
	if [ -z "$2" ]; then
	    errormsg "repo store folder was not set"
	fi
	
	if [ -z "$3" ]; then
	    echo "Warning: proxy was not set"
	fi

	if [ -z "$4" ]; then
	    echo "Warning: proxy user was not set"
	fi
	
	if [ -z "$5" ]; then
	    echo "Warning: proxy password was not set"
	fi
	
	
	for repo in "${arRepos[@]}"
	do
		echo -e "$COL_BLUE$BG_WHITE---- ${repo[0]}\n$COL_RESET$COL_BLUE$BG_WHITE -----------------------------------------$COL_RESET"
		#github is often busy, therefore retry to download
		n=0
		reponame=${repo//[:\/]/}
		rm "$2/${reponame}.zip"
		rm -rf "$2/${reponame}"
		until [ "$n" -ge 20 ]
		do
			# Because git is not stable (and we did not try clone any repo in install.sh), I use wget to clone the repo
			echo -e "${COL_CYAN}Try $n/20: download of ${repo} ${COL_RESET}"
			$mypath/wget.exe -O "$2/${reponame}.zip " --proxy-user=$4 --proxy-password="$5" -e use_proxy=yes -e https_proxy=$3 $repo && break
			sleep 30
		done
		
		unzip "$2/$reponame.zip" -d "$2/$reponame"
		CURDIR=$(pwd)
		cd $2/$reponame/*/
	    PYDIR=$1
		 ${PYDIR}/python.exe -m pip install . --proxy="http://$4:$5@$3"
	    logresult "$?" "installed ${repo}" "install ${repo}"
	   
	   echo
	   echo
	done
}

function pyinstall_noproxy
{
	if [ "$1" -eq "" ]; then
	    errormsg "python folder was not set"
	fi

}
