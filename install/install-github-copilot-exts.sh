#!/bin/bash

VSCODIUM="$RobotVsCode/bin/codium"
REQUIRED_VERSION=1.90.2

PUBLISHER="GitHub"
declare -A EXTENSIONS
EXTENSIONS=(
   ["copilot-chat"]="0.16.1"
   ["copilot"]="1.212.0"
)

NTID=$(whoami)

PROXY=""
PROXY_AUTH="False"
PROXY_ARGS=""
PROXY_USER=${NTID,,}
PROXY_PASS=""

print_usage() {
   echo "Usage: $0 [OPTIONS]"
   echo
   echo "Options:"
   echo "  --proxy <proxy-url>       Set the proxy server URL (e.g., http://proxy.example.com:8080)"
   echo "  --proxy-auth              If set, prompts the user to provide the password for proxy authentication"
   echo "  --help                    Display this help message"
   echo
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
   case "$1" in
      --proxy)
         if [[ -z $2 || $2 == "--"* ]]; then
            echo "Error: Missing argument for --proxy"
            print_usage
            exit 1
         fi
         # echo $2
         PROXY="$2"
         shift 2
         ;;
      --proxy-auth)
         PROXY_AUTH="True"
         shift 1
         ;;
      --help)
         print_usage
         exit 0
         ;;
      *)
         echo "Error: Invalid argument '$1'"
         print_usage
         exit 1
         ;;
   esac
done


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
   echo "Installed VSCodium version is '${installed_version}' different from expected version '${REQUIRED_VERSION}'."
   exit 1
fi

if [ -n "$PROXY" ]; then
   if [[ "$PROXY" =~ ^(http|https|ftp|socks4|socks4a|socks5|socks5h)://([^:@]+):([^:@]+)@(.*) ]]; then
      echo "Using proxy '${BASH_REMATCH[4]}' with embedded credential in URL"
      PROXY_ARGS="-x $PROXY"
   elif [[ "$PROXY_AUTH" == "False" ]]; then
      echo "Using proxy '$PROXY' without any credential";
      PROXY_ARGS="-x $PROXY"
   else
      # Prompt the user for the password
      echo -n "Enter password for proxy authentication with user $PROXY_USER: "
      read -s PROXY_PASS
      echo
      PROXY_ARGS="-x $PROXY --proxy-user $PROXY_USER:$PROXY_PASS"
   fi
fi

# verify Github Copilot extension installation status
for extension in "${!EXTENSIONS[@]}"; do
   version="${EXTENSIONS[$extension]}"

   extension_info=$("$VSCODIUM" --list-extensions --show-versions --user-data-dir=$RobotVsCode/data | grep ".$extension@")
   if [ -z "$extension_info" ]; then
      echo "Extension '$extension' is not installed."
   else
      installed_ext_version=$(echo "$extension_info" | awk -F '@' '{print $2}')
      if [ "${installed_ext_version}" != "${version}" ]; then
         echo "Extension '$extension' version '$installed_ext_version' is installed. Reininstall it with version '$version'"
      else
         echo "Extension '$extension' version '$installed_ext_version' is already installed"
         continue
      fi
   fi

   echo "Processing '$PUBLISHER.$extension', version '$version'"

   # Construct the download URL
   url="https://${PUBLISHER}.gallery.vsassets.io/_apis/public/gallery/PUBLISHER/${PUBLISHER}/extension/${extension}/${version}/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"
#    url="https://marketplace.visualstudio.com/_apis/public/gallery/PUBLISHERs/${PUBLISHER}/vsEXTENSIONS/${extension}/${version}/vspackage"
   
   # download the VSIX file
	retry_counter=0
	max_retries=5
	success=false
   while [[ "$retry_counter" -lt "$max_retries" && "$success" == "false" ]];do
      curl -L -k "$url" -o "$USER_TMP/${PUBLISHER}.${extension}-${version}.vsix" $PROXY_ARGS
      if [ $? -eq 0 ]; then
         success=true
         echo "Extension '${PUBLISHER}.${extension}-${version}' downloaded successfully."
      else
         ((retry_counter++))
         echo "Failed to download extension ${PUBLISHER}.${extension}-${version} (attempt: $retry_counter)."
         sleep 1
      fi
   done
   if [ "$success" == "false" ]; then
		echo "Could not download extension '${PUBLISHER}.${extension}-${version}' after $max_retries attempts."
      echo "If you're behind a proxy, please ensure you've set the '--proxy' argument correctly and verify the proxy URL."
      exit 1
	fi

   # install the extension using VSCodium
   "$VSCODIUM" --install-extension "$USER_TMP/${PUBLISHER}.${extension}-${version}.vsix" --user-data-dir=$RobotVsCode/data
   if [ $? -ne 0 ]; then
   #    echo "Extension ${PUBLISHER}.${extension}-${version} is installed successfully."
   # else
      echo "Failed to install extension '${PUBLISHER}.${extension}-${version}'."
      exit 1
   fi

   # clean the downloaded VSIX file
   rm "$USER_TMP/${PUBLISHER}.${extension}-${version}.vsix"
   echo
done

echo "Please refer to the following article to get a GitHub Copilot license or subscription:"
echo "$PLACEHOLDER_REF_URL"