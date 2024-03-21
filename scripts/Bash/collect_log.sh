####################################################################################################################
# This script is designed to assist in collecting all log files on GitLab based on testtrigger_config.json.
# It will search for the keyword 'FILES_SAVE' to identify the directory containing log files and include it as part 
# of the artifacts.
####################################################################################################################
#!/bin/bash

# Check if any arguments are provided
if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <path_to_test_trigger>"
  exit 1
fi

test_config=$1

# Getting value from testtrigger_config.json file
target_dir_test_log=$(cat $test_config | grep "FILES_SAVE" | awk -F '[:,]' '/"FILES_SAVE"/ {gsub(/"/, "", $2); if ($2 != "") print $2}')


# Transfer serial value into array
IFS=$'\n' read -rd '' -a value_array <<<"$target_dir_test_log"

echo "Collecting all log files"

cp -rf console_log.txt aiotestlogfiles

# Iterate each value 
for target_dir in "${value_array[@]}"; do

    # Source log file
    source_log_file=$(echo "$target_dir" | sed 's#../../robotframework_aio/aiotestlogfiles/##g')
    echo "Fetching log files from: $source_log_file"
    # Desitantion log file
    destination_log_file=$(echo "$target_dir" | sed 's#../../##g')
    
    mkdir -p $destination_log_file 
    cp -rf $source_log_file/* $destination_log_file 
done

echo "All test logfiles have been successfully collected"