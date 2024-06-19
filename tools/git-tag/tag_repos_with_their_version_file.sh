#!/bin/bash

# This script helps to tag repo(s) with the version from its version.py file
# Flow of this tool:
# 1. Process repo configuration to get list of repo names
# 2. Clone (update existing) repo
# 3. Get version info from version.py under repo
# 4. Tag repo with that version info with git-tag.py tool

#
# import common bash scripts
#
. $(dirname $0)/../../include/bash/common.sh

git_server="github"
project="test-fullautomation"
git_base_url="https://github.com"

function tag_single_repo(){
   # Verify input argument
   if [[ $# != 2 ]]; then
      errormsg "Error: Invalid number of arguments.\nUsage: tag_single_repo <path_to_repo> <version_filename>"
   fi

   repo_location=$(realpath "$1")
   version_file=$2

   if [ ! -d "$repo_location" ]; then
      errormsg "Given repo location '${repo_location}' does not exist"
   fi

   # Define common information => adapt them for your project and requirement
   infix_tag=""
   repo_name=$(basename ${repo_location})
   package_name=$repo_name
   commit_sha=""
   # ${version_file}, e.g version.py file should be placed under package_name folder as below structure
   # repo_name
   #     |__ package_name 
   #              |__ version.py
   #              |__ ...
   # Update below glob pattern incase the repo structure is not as above 
   version_file_pattern=${repo_location}/*/$version_file

   # Prepare configuration file for tagging single repo
   config_content='{
      "'"${git_server}"'" : {
         "project" : "'"${project}"'",
         "infix_tag": "'"${infix_tag}"'",
         "repos"   : {
            "'"${repo_name}"'": "'"${commit_sha}"'"
         }
      }
   }'

   config_file="single_repo_config.json"
   # Remove existing configuration file to make sure this file is up-to-date
   if [ -f "$config_file" ]; then
      rm "$config_file"
   fi

   echo "$config_content" > "$config_file"

   # Get version information from version.py file under repo folder
   version_file=$(ls $version_file_pattern 2>/dev/null)
   # Check existence of the filename which contains version information
   if [ -z "$version_file" ]; then
      errormsg "No $version_file file is found under '${repo_location}'"
   else
      echo "Found version file at '${version_file}'"
      # Get package name for pypi verification
      # repos with prefix robotframework- : the package name is the same as the repository name.
      # repos with prefix python- : the package name is different from the repository name.
      if [[ $repo_name =~ ^python-.* ]];then
         package_name=$(basename "$(dirname $version_file)")
      fi
   fi

   version_info=$(grep -E 'VERSION\s+=' ${version_file} | sed "s/'/\"/g" | awk -F'"' '{print $2}')
   # Check if the version is empty
   if [ -z "$version_info" ]; then
      errormsg "Version information not found or empty"
   fi

   # Call git-tag tool to tag repo
   python "$(dirname $0)/git-tag.py" rel/${version_info} ${config_file}
   logresult "$?" "tagged repo '$repo_name' with tag 'rel/$version_info'" "tag '$repo_name' with tag 'rel/$version_info'"

   verify_pkg_version $package_name $version_info
}

list_repo=()
repos_conf_file=$1

# Verify input argument
if [[ $# != 1 ]]; then
   errormsg "Invalid number of arguments.\nUsage: $0 <path_to_repo_config>"
fi

if [ ! -f "$repos_conf_file" ]; then
   errormsg "Given repo configuration file '${repos_conf_file}' does not exist"
fi

# Process each repo in repositories configuration file
while IFS= read -r line || [[ -n "$line" ]]; do
   trimmed_line=$(echo "$line" | awk '{$1=$1;print}')

   # Check if the line contains filename (separate by "=" char) 
   # to get version information.
   # Default version file is version.py
   version_filename="version.py"
   if [[ $trimmed_line == *"="* ]]; then
      # Extract repository name and version file
      repo_name="${trimmed_line%%=*}"
      version_filename="${trimmed_line#*=}"
   else
      repo_name=$trimmed_line
   fi

   echo
   greenmsg "Processing repo: $repo_name"
   clone_update_repo ../$repo_name "https://github.com/$project/$repo_name.git" "$TAG_NAME"
   tag_single_repo ../$repo_name $version_filename
done < "${repos_conf_file}"