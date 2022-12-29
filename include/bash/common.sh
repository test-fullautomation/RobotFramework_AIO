########################################################################################
#
# this script provides common functions for the install and build process
#
#########################################################################################

ESC_SEQ="\x1b["
COL_RESET=$ESC_SEQ"39;49;00m"
COL_BLACK=$ESC_SEQ"30;01m"
COL_RED=$ESC_SEQ"31;01m"
COL_GREEN=$ESC_SEQ"32;01m"
COL_YELLOW=$ESC_SEQ"33;01m"
COL_BLUE=$ESC_SEQ"34;01m"
COL_MAGENTA=$ESC_SEQ"35;01m"
COL_CYAN=$ESC_SEQ"36;01m"

BG_BLACK='\033[40m'      
BG_RED='\033[41m'         
BG_GREEN='\033[42m'     
BG_YELLOW='\033[43m'    
BG_BLUE='\033[44m'      
BG_PURPLE='\033[45m'    
BG_CYAN='\033[46m'      
BG_WHITE='\033[47m'     

mypath=$(realpath $(dirname $0))

TAG_REGEX="^(rel|dev)(\/aio)?\/[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?$"

function errormsg(){
   echo -e "${COL_RED}>>>> ERROR: $1!${COL_RESET}"
   echo
   exit 1
}

function goodmsg(){
   echo -e "${COL_GREEN}>>>> $1.${COL_RESET}"
   echo
}

function greenmsg(){
   echo -e "${COL_GREEN}> $1.${COL_RESET}"   
}

function logresult(){
	if [ "$1" -eq 0 ]; then
	    goodmsg "Successfully $2"
	else
		errormsg "FATAL: Could not $3"
	fi
}

# Clone or update repository
# Arguments:
#	$repo_path : location to clone repo into
#	$repo_url  : repo url
function clone_update_repo () {
	repo_path=$1
	repo_url=$2
	target_commit=$3

	if [ -d "$repo_path" ]; then
		echo "Cleaning and updating repo $repo_path"
		git -C "$repo_path" remote set-url origin "$repo_url" &&
		git -C "$repo_path" fetch --all --tags --force &&
		git -C "$repo_path" reset --hard @{u} &&
		git -C "$repo_path" clean -f -d -x

		# try to remove existing directory and clone repo again
		if [ "$?" -ne 0 ]; then
			echo "Cloning $repo_url again"
			rm -rf "$repo_path"
			git clone "$repo_url" "$repo_path"
		fi
	else
		echo "Cloning $repo_url"
		git clone "$repo_url" "$repo_path"
	fi
	if [ "$?" -ne 0 ]; then
		exit 1
	fi

	if [ -n "$target_commit" ]; then
		echo "Checking out to '$target_commit' tag"
		git -C "$repo_path" checkout $target_commit
		logresult "$?" "switched to '$target_commit' tag" "checkout '$target_commit' tag from '$repo_url'"
	fi
}