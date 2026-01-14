#!/bin/bash

# Define the options with corresponding characters
EXTRA_CMPTS=(
   "    N : No extra package - only the core framework and libraries"
   "    A : Android package (includes Node.js, Appium server, Appium Inspector, Android SDK tools)" 
   "    V : Vscodium package"
   "        1 : Fresh Install of VSCodium"
   "            - Performs a clean setup with default settings."
   "            - No previous extensions or user configurations are retained."
   "        2 : Upgrade Existing VSCodium"
   "            - Updates the current installation to the latest version."
   "            - Preserves all existing extensions and user settings."
   "Enter : All packages (default choice after 30s, includes Android + Vscodium Upgrade [V2])"
   )
DEFAULT_OPT="AV2"

# Display the menu and read user input with timeout
echo "Select one or more extra components:"
for option in "${EXTRA_CMPTS[@]}"; do
   echo "$option"
done
read -rt 30 -p "Enter your choices (e.g., AV for both Android and VSCodium packages): " choices

# Set default value if input is empty
if [ -z "$choices" ]; then
   choices=$DEFAULT_OPT
fi

# mkdir /opt/ngoan-dev
# Process user input
SELECTED_CMPTS=()
if [[ "$choices" =~ [Nn] ]]; then
   SELECTED_CMPTS=() # No extras overrides everything
elif [[ "$choices" =~ [Aa] ]]; then
   SELECTED_CMPTS+=("Android")
fi
if [[ "$choices" =~ V1|v1 ]]; then
   SELECTED_CMPTS+=("Vscodium (fresh install)")
elif [[ "$choices" =~ V2|v2|V|v ]]; then
   SELECTED_CMPTS+=("Vscodium (upgrade/overwrite)")
fi

# Print selected options
if [ ${#SELECTED_CMPTS[@]} -eq 0 ]; then
   echo "No extra component is selected."
else
   # Print selected components
   echo "Selected component(s):"
   for component in "${SELECTED_CMPTS[@]}"; do
      echo "- $component"
   done
fi

# Export selected components to temporary file which used for post installation
SELECTED_CMPTS_FILE=/tmp/robfw_aio_selected_cmpts.tmp
printf "%s\n" "${SELECTED_CMPTS[@]}" > ${SELECTED_CMPTS_FILE}

# Continue installation
exit 0
