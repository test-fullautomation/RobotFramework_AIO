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
VERSION_REGEX="^[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?$"
# Get version information from control file of linux package
# read 2. line, from there return after 10th character
# relative path from build script (caller)
control_pathfile="./config/build/dpkg_build/control"
if [ -f $control_pathfile ]; then
	VERSION=`sed '2q;d' $control_pathfile | cut -c 10-`
fi

function errormsg(){
   echo -e "${COL_RED}>>>> ERROR: $1!${COL_RESET}"
   echo
   exit 1
}

function warningmsg(){
   echo -e "${COL_YELLOW}>>>> WARN: $1!${COL_YELLOW}"
   echo
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

function create_testsuitmanagement_package_context_file(){
	if [[ ! "$AIO_VERSION" =~ $VERSION_REGEX ]]; then
		echo "get bundle version from control file"
		AIO_VERSION=$VERSION
	fi

   package_context='{
		"installer_location" : "'"${INSTALLER_LOCATION}"'",
		"bundle_name"        : "'"${AIO_NAME}"'",
		"bundle_version"     : "'"${AIO_VERSION}"'",
		"bundle_version_date": "'"${AIO_VERSION_DATE}"'"
   }'

	# relative path from build script
	package_context_pathfile="../robotframework-testsuitesmanagement/RobotFramework_TestsuitesManagement/Config/package_context.json"
	if [ -f "$package_context_pathfile" ]; then
		rm "$package_context_pathfile"
	fi
	echo "Creating 'package_context.json' file for RobotFramework_TestsuitesManagement ..."
	echo "$package_context" > "$package_context_pathfile"
	logresult "$?" "created '$package_context_pathfile'" "create '$package_context_pathfile'"
}

function update_debian_control_file(){
	if [[ "$AIO_VERSION" =~ $VERSION_REGEX ]] && [ "$AIO_VERSION" != "$VERSION" ]; then
		echo "Update version info in control file to '$AIO_VERSION'"
		sed -i "s/\(Version: \)[0-9]\{1,\}.[0-9]\{1,\}.[0-9]\{1,\}.[0-9]\{1,\}/\1$AIO_VERSION/" $control_pathfile
	fi
}
# Clone or update repository
# Arguments:
#	$repo_path : location to clone repo into
#	$repo_url  : repo url
#	$commit_branch_tag  : target commit, branch or tag to point to
function clone_update_repo () {
	repo_path=$1
	repo_url=$2
	commit_branch_tag=$3

	# 1. Check is repo folder is existing or not
	# 2. Ensure the repo url is correct
	# 3. Fetch all from git server
	# 4. Discard all user changes includes untracked files
	# 5. Ensure the default branch change (from git server)
	# 6. Checkout to target branch/commit/tag
	# 7. Ensure branch/commit/tag is up-to-date with remote

	if [ -d "$repo_path" ]; then
		echo "Cleaning and updating repo $repo_path"

		current_url=$(git -C "$repo_path" remote get-url origin)
		if [ "$current_url" != "$repo_url" ]; then
			echo "Repo URL has changed, update remote origin to ${repo_url}"
			git -C "$repo_path" remote set-url origin "$repo_url"
		fi

		git -C "$repo_path" fetch --all
		echo "Clean all local changes/commits"
		git -C "$repo_path" reset --hard HEAD
		git -C "$repo_path" clean -f -d -x

		if [ -z "$commit_branch_tag" ]; then
			default_branch=$(git -C "$repo_path" remote show origin | grep "HEAD branch" | cut -d " " -f 5)
			git -C "$repo_path" checkout $default_branch
			git -C "$repo_path" reset --hard origin/$default_branch
			logresult "$?" "switched to '$default_branch'" "checkout to '$default_branch' from '$repo_url'"
		fi

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

	if [ -n "$commit_branch_tag" ]; then
		echo "Checking out to '$commit_branch_tag'"
		git -C "$repo_path" checkout $commit_branch_tag
		if [ "$?" -ne 0 ]; then
			errormsg	"Given tag/branch '$commit_branch_tag' is not existing" 
		fi
		git -C "$repo_path" pull origin $commit_branch_tag
		logresult "$?" "switched to '$commit_branch_tag'" "checkout to '$commit_branch_tag' from '$repo_url'"
	fi
}

function verify_pkg_version(){
   pkg_name=$1
   given_version=$2
   pkg_api_url="https://pypi.org/pypi/${pkg_name}/json"
   timesleep=10  # timesleep for each verification
   timeout=600   # timeout for verification loop
   counter=$(($timeout / $timesleep))
	success=False
	found=False

   while [ "$counter" -gt 0 ]; do
      # Send request and extract version info from response
		# "\n" before http_code to make sure the newline is added between 
		# the reponse data and status code 
		# Then status code can be extracted properly
      response=$(curl -s -w "\n%{http_code}" "$pkg_api_url")
      http_status=$(echo "$response" | tail -n1)

      if [ "$http_status" -eq 200 ]; then
			found=True
         # Extract version information using jq
         version=$(echo "$response" | head -n -1 | grep -o '"version"[[:space:]]*:[[:space:]]*"[^"]*' | awk -F'"' '{print $4}')

         # Print the extracted version
         echo "Latest version of ${pkg_name}: $version"
         if [ "$version" == "$given_version" ]; then
            goodmsg "Package '${pkg_name}-${version}' is published to pypi successfully."
				success=True
            break
         fi
      else
         warningmsg "Unable to fetch information for ${pkg_name}."
			# Package is not found on PyPi, retry with timesleep and counter
			# This ensures the package which is initially published on PyPi
			# break
      fi

      counter=$((counter - 1))
      sleep $timesleep
   done
	
	if [[ "$found" == "False" ]];then
		errormsg "Package ${pkg_name} is not available on pypi."
	fi

	if [[ "$success" == "False" ]];then
		errormsg "Latest version ${given_version} of ${pkg_name} is not published to pypi within ${timeout} seconds."
	fi
}