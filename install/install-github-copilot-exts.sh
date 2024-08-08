#!/bin/bash

publisher="GitHub"
declare -A extensions
extensions=(
    ["copilot-chat"]="0.16.1"
    ["copilot"]="1.212.0"
)

for extension in "${!extensions[@]}"; do
   version="${extensions[$extension]}"

   echo "Processing $publisher.$extension, version $version"

   # Construct the download URL
   url="https://${publisher}.gallery.vsassets.io/_apis/public/gallery/publisher/${publisher}/extension/${extension}/${version}/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"
#    url="https://marketplace.visualstudio.com/_apis/public/gallery/publishers/${publisher}/vsextensions/${extension}/${version}/vspackage"
   
   # Download the VSIX file
   curl -L -k "$url" -o "${publisher}.${extension}-${version}.vsix" 

   # Install the extension using VSCode
   $RobotVsCode/bin/codium --install-extension "${publisher}.${extension}-${version}.vsix"

   # Cleanup the downloaded VSIX file
   rm "${publisher}.${extension}-${version}.vsix" 
done