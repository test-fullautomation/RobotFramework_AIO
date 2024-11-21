# PowerShell Script
$VSCODIUM = "$env:RobotVsCode\bin\codium.cmd"
$REQUIRED_VERSION = "1.90.2"
$PUBLISHER = "GitHub"
$EXTENSIONS = @{
    "copilot-chat" = "0.16.1"
    "copilot"      = "1.212.0"
}

# Initialize variables
$PROXY = ""
$PROXY_AUTH = "False"
$PROXY_CREDENTIAL = ""
$PROXY_USER = $env:USERNAME.ToLower()
$PROXY_PASS = ""

# Function to display usage information
function Print-Usage {
    Write-Host "Usage: install-copilot.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  --proxy <proxy-url>       Set the proxy server URL (e.g., http://proxy.example.com:8080)"
    Write-Host "  --proxy-auth              If set, prompts the user to provide the password for proxy authentication"
    Write-Host "  --help                    Display this help message"
}

# Parse command-line arguments
for ($i = 0; $i -lt $args.Count; $i++) {
    switch ($args[$i]) {
        "--proxy" {
            if ($i + 1 -lt $args.Count -and -not ($args[$i + 1] -like "--*")) {
                $PROXY = $args[$i + 1]
                $i++
            }
            else {
                Write-Host "Error: Missing argument for --proxy"
                Print-Usage
                exit 1
            }
        }
        "--proxy-auth" {
            $PROXY_AUTH = "True"
        }
        "--help" {
            Print-Usage
            exit 0
        }
        default {
            Write-Host "Error: Invalid argument '$($args[$i])'"
            Print-Usage
            exit 1
        }
    }
}

# Verify installation of VsCodium and its version
if (-not (Test-Path $VSCODIUM)) {
    Write-Host "VSCodium for RobotFramework is not installed."
    exit 1
}

$installed_version = & "$VSCODIUM" --version --user-data-dir=$env:RobotVsCode\data | Select-Object -First 1
if ($installed_version -ne $REQUIRED_VERSION) {
    Write-Host "Installed VSCodium version is '$installed_version' different from expected version '$REQUIRED_VERSION'."
    exit 1
}

# Check if PROXY is specified and set up proxy arguments
if ($PROXY -ne "") {
    # Match embedded credentials in the proxy URL
    if ($PROXY -match "^(http|https|ftp|socks4|socks4a|socks5|socks5h)://([^:@]+):([^:@]+)@(.*)") {
        $proxy_host = $matches[4]
        Write-Host "Using proxy '${proxy_host}' with embedded credentials in URL"
    }
    elseif ($PROXY_AUTH -eq "False") {
        Write-Host "Using proxy '$PROXY' without any credentials"
    }
    else {
        # Prompt the user for the password
        $PROXY_PASS = Read-Host -AsSecureString "Enter password for proxy authentication with user $PROXY_USER"
        # Convert SecureString to plain text for proxy arguments (if security allows)
        $plainPass = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($PROXY_PASS))
        $PROXY_CREDENTIAL = New-Object System.Management.Automation.PSCredential($PROXY_USER, $PROXY_PASS)
    }
}

# Verify GitHub Copilot extension installation status
foreach ($extension in $EXTENSIONS.Keys) {
    $version = $EXTENSIONS[$extension]

    $extension_info = & "$VSCODIUM" --list-extensions --show-versions --user-data-dir=$env:RobotVsCode\data | Select-String -Pattern ".$extension@"
    if (-not $extension_info) {
        Write-Host "Extension '$extension' is not installed."
    } else {
        $installed_ext_version = ($extension_info -split "@")[1]
        if ($installed_ext_version -ne $version) {
            Write-Host "Extension '$extension' version '$installed_ext_version' is installed. Reinstall it with version $version"
        } else {
            Write-Host "Extension '$extension' version '$installed_ext_version' is already installed"
            continue
        }
    }

    Write-Host "Processing '$PUBLISHER.$extension', version '$version'"

    # Construct the download URL
    $url = "https://${PUBLISHER}.gallery.vsassets.io/_apis/public/gallery/PUBLISHER/${PUBLISHER}/extension/${extension}/${version}/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"

    # Download the VSIX file
    $retry_counter = 0
    $max_retries = 5
    $success = $False

    while ($retry_counter -lt $max_retries -and -not $success) {
        try {
            if ($PROXY -ne "") {
                if ($PROXY_AUTH -eq "True" -and $PROXY_CREDENTIAL -ne ""){
                    Invoke-WebRequest -Uri $url -OutFile "$env:TMP\$($PUBLISHER).$extension-$version.vsix" -Proxy $PROXY -ProxyCredential $PROXY_CREDENTIAL
                } else {
                    Invoke-WebRequest -Uri $url -OutFile "$env:TMP\$($PUBLISHER).$extension-$version.vsix" -Proxy $PROXY
                }
            } else {
                Invoke-WebRequest -Uri $url -OutFile "$env:TMP\$($PUBLISHER).$extension-$version.vsix"
            }
            
            $success = $True
            # Write-Host "Extension $PUBLISHER.$extension-$version downloaded successfully."
        } catch {
            $retry_counter++
            Write-Host "Failed to download extension '$PUBLISHER.$extension-$version' (attempt: $retry_counter)."
            Start-Sleep -Seconds 1
        }
    }

    if (-not $success) {
        Write-Host "Could not download extension '$PUBLISHER.$extension-$version' after $max_retries attempts."
        Write-Host "If you're behind a proxy, please ensure you've set the '--proxy' argument correctly and verify the proxy URL."
        exit 1
    }

    # Install the extension using VSCodium
    & "$VSCODIUM" --install-extension "$env:TMP\$($PUBLISHER).$extension-$version.vsix" --user-data-dir=$env:RobotVsCode\data
    if ($?) {
        Write-Host "Extension '$PUBLISHER.$extension-$version' is installed successfully."
    } else {
        Write-Host "Failed to install extension '$PUBLISHER.$extension-$version'."
        exit 1
    }

    # Clean the downloaded VSIX file
    Remove-Item "$env:TMP\$($PUBLISHER).$extension-$version.vsix"
    Write-Host
}
Write-Host "Please refer to the following article to get a GitHub Copilot license or subscription:"
Write-Host "$PLACEHOLDER_REF_URL"