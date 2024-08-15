#!/bin/bash

VSCODIUM="$RobotVsCode/bin/codium"
REQUIRED_VERSION=1.90.2

PUBLISHER="GitHub"
declare -A EXTENSIONS
EXTENSIONS=(
    ["copilot-chat"]="0.16.1"
    ["copilot"]="1.212.0"
)

# Create user temp folder to store downloading extension files
USER_TMP="$HOME/tmp"
mkdir -p "$USER_TMP"

# verify installation of VsCodium and its version
if ! command -v "$VSCODIUM" &> /dev/null; then
   echo "VSCodium for RobotFramework is not installed."
   exit 1
fi

installed_version=$("$VSCODIUM" --version --user-data-dir=$RobotVsCode/data | head -n 1)

if [ "$installed_version" != "$REQUIRED_VERSION" ]; then
   echo "Installed VSCodium version is ${installed_version} different from expected version ${REQUIRED_VERSION}."
   exit 1
fi

# verify Github Copilot extension installation status
for extension in "${!EXTENSIONS[@]}"; do
   version="${EXTENSIONS[$extension]}"

   extension_info=$("$VSCODIUM" --list-extensions --show-versions --user-data-dir=$RobotVsCode/data | grep ".$extension@")
   if [ -z "$extension_info" ]; then
      echo "Extension $extension is not installed."
   else
      installed_ext_version=$(echo "$extension_info" | awk -F '@' '{print $2}')
      if [ "${installed_ext_version}" != "${version}" ]; then
         echo "Extension $extension version $installed_ext_version is installed. Reininstall it with version $version"
      else
         echo "Extension $extension version $installed_ext_version is already installed"
         continue
      fi
   fi

   echo "Processing $PUBLISHER.$extension, version $version"

   # Construct the download URL
   url="https://${PUBLISHER}.gallery.vsassets.io/_apis/public/gallery/PUBLISHER/${PUBLISHER}/extension/${extension}/${version}/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"
#    url="https://marketplace.visualstudio.com/_apis/public/gallery/PUBLISHERs/${PUBLISHER}/vsEXTENSIONS/${extension}/${version}/vspackage"
   
   # download the VSIX file
	retry_counter=0
	max_retries=5
	success=false
   while [[ "$retry_counter" -lt "$max_retries" && "$success" == "false" ]];do
      curl -L -k "$url" -o "$USER_TMP/${PUBLISHER}.${extension}-${version}.vsix" 
      if [ $? -eq 0 ]; then
         success=true
         echo "Extension ${PUBLISHER}.${extension}-${version} downloaded successfully."
      else
         ((retry_counter++))
         echo "Failed to download extension ${PUBLISHER}.${extension}-${version} (attempt: $retry_counter)."
         sleep 1
      fi
   done
   if [ "$success" == "false" ]; then
		echo "Could not download extension ${PUBLISHER}.${extension}-${version} after $max_retries attempts"
      exit 1
	fi

   # install the extension using VSCodium
   "$VSCODIUM" --install-extension "$USER_TMP/${PUBLISHER}.${extension}-${version}.vsix" --user-data-dir=$RobotVsCode/data
   if [ $? -eq 0 ]; then
      echo "Extension ${PUBLISHER}.${extension}-${version} is installed successfully."
   else
      echo "Failed to install extension ${PUBLISHER}.${extension}-${version}."
      exit 1
   fi

   # clean the downloaded VSIX file
   rm "$USER_TMP/${PUBLISHER}.${extension}-${version}.vsix"

   echo
   echo "Please refer to the following article to get a GitHub Copilot license or subscription:"
   echo "$PLACEHOLDER_REF_URL"
done