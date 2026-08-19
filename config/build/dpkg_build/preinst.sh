#!/bin/bash

if [ -x "/opt/rfwaio/robotvscode/bin/codium" ]; then
   IDE_NAME="VSCodium"
elif [ -x "/opt/rfwaio/robotvscode/bin/code" ]; then
   IDE_NAME="VSCode"
else
   IDE_NAME="VSCodium"
fi

DO_UPDATE_VSCODIUM_FLAG=false
[ -f /var/lib/robotframework-aio-do-update-vscodium ] && DO_UPDATE_VSCODIUM_FLAG=true

if $DO_UPDATE_VSCODIUM_FLAG; then
   # Dev mode
   # Define the options with corresponding characters
   EXTRA_CMPTS=(
      "    N : No extra package - only the core framework and libraries"
      "    A : Android package (includes Node.js, Appium server, Appium Inspector, Android SDK tools)" 
      "    V : $IDE_NAME package"
      "        1 : Fresh Install of $IDE_NAME"
      "            - Performs a clean setup with default settings."
      "            - No previous extensions or user configurations are retained."
      "        2 : Upgrade Existing $IDE_NAME"
      "            - Updates the current installation to the latest version."
      "            - Preserves all existing extensions and user settings."
      "Enter : All packages (default choice after 30s, includes Android + $IDE_NAME Upgrade [V2])"
   )
   DEFAULT_OPT="AV2"
else
   # End-user mode
   EXTRA_CMPTS=(
      "    N : No extra package - only the core framework and libraries"
      "    A : Android package (includes Node.js, Appium server, Appium Inspector, Android SDK tools)" 
      "    V : $IDE_NAME package"
      "Enter : All packages (default choice after 30s)"
   )
   DEFAULT_OPT="AV"
fi

# Display the menu and read user input with timeout
echo "Select one or more extra components:"
for option in "${EXTRA_CMPTS[@]}"; do
   echo "$option"
done

if $DO_UPDATE_VSCODIUM_FLAG; then
   read -rt 30 -p "Enter your choices (e.g., AV2 for both Android and $IDE_NAME (upgrade/overwrite) packages): " choices
else
   read -rt 30 -p "Enter your choices (e.g., AV for both Android and $IDE_NAME packages): " choices
fi
   

# Set default value if input is empty
if [ -z "$choices" ]; then
   choices=$DEFAULT_OPT
fi

SELECTED_CMPTS=()

# Process user input
if [[ "$choices" =~ [Nn] ]]; then
   SELECTED_CMPTS=() # No extras overrides everything
else
   if [[ "$choices" =~ [Aa] ]]; then
      SELECTED_CMPTS+=("Android")
   fi
   if $DO_UPDATE_VSCODIUM_FLAG; then
      # Dev mode
      if [[ "$choices" =~ V1|v1 ]]; then
         SELECTED_CMPTS+=("$IDE_NAME (fresh install)")
      elif [[ "$choices" =~ V2|v2|V|v ]]; then
         SELECTED_CMPTS+=("$IDE_NAME (upgrade/overwrite)")
      fi
   else
      if [[ "$choices" =~ V|v ]]; then
         SELECTED_CMPTS+=("$IDE_NAME")
      fi
   fi
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
