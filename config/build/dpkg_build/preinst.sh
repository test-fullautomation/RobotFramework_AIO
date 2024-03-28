#!/bin/bash

#!/bin/bash

# Define the options with corresponding characters
EXTRA_CMPTS=(
   "    N : No extra package - only the core framework and libraries"
   "    A : Android package (includes Node.js, Appium server, Appium Inspector, Android SDK tools)" 
   "    V : Vscodium package"
   "Enter : All packages (default choice after 30s)"
   )
DEFAULT_OPT="AV"

# Display the menu and read user input with timeout
echo "Select one or more extra components:"
for option in "${EXTRA_CMPTS[@]}"; do
   echo "$option"
done
read -rt 30 -p "Enter your choices (e.g., AC for both Android and VSCodium packages): " choices

# Set default value if input is empty
if [ -z "$choices" ]; then
   choices=$DEFAULT_OPT
fi

# mkdir /opt/ngoan-dev
# Process user input
SELECTED_CMPTS=()
for choice in $(echo "$choices" | grep -o .); do
    case $choice in
        "N" | "n")
            SELECTED_CMPTS=()
            break
            ;;
        "A" | "a")
            SELECTED_CMPTS+=("Android")
            # cp -r /usr/share/ngoan-dev/core /opt/ngoan-dev/android
            ;;
        "V" | "v")
            SELECTED_CMPTS+=("Vscodium")
            # cp -r /usr/share/ngoan-dev/core /opt/ngoan-dev/vscode
            ;;
        *)
            echo "Invalid choice: $choice"
            exit 1
            ;;
    esac
done

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
