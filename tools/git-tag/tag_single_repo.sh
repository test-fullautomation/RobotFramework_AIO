#!/bin/bash

# Verify input argument
if [[ $# != 1 ]]; then
  echo "Error: Invalid number of arguments."
  echo "Usage: $0 <path_to_repo>"
  exit 1
fi

repo_location=$(realpath "$1")
if [ ! -d "$repo_location" ]; then
  echo "Given repo location '${repo_location}' does not exist"
  exit 1
fi

# Define common information => adapt them for your project and requirement
git_server="github"
project="test-fullautomation"
infix_tag=""
repo_name=$(basename ${repo_location})
commit_sha=""
# version.py file should be placed under package_name folder as below structure
# repo_name
#     |__ package_name 
#              |__ version.py
#              |__ ...
# Update below glob pattern incase the repo structure is not as above 
version_file_pattern=${repo_location}/*/version.py  

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
# Check if the version.py does not exist
if [ -z "$version_file" ]; then
  echo "No version.py file is found under '${repo_location}'"
  exit 1
else
  echo "Found version file at '${version_file}'"
fi

version_info=$(grep -E 'VERSION\s+=' ${version_file} | awk -F'"' '{print $2}')
# Check if the version is empty
if [ -z "$version_info" ]; then
  echo "Version information not found or empty"
  exit 1
fi

# Call git-tag tool to tag repo
python "$(dirname $0)/git-tag.py" rel/${version_info} ${config_file}