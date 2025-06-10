#!/bin/bash

mypath=$(realpath $(dirname $0))

# Load Version definition of package tools
source $mypath/versions.conf

# Function to display usage
usage() {
    echo "Usage: $0 -i <input_file> -v <vscode_input_file> -o <output_file>"
    echo "  -i, --input        Path to the Python requirements file (e.g., python_requirements.txt)"
    echo "  -v, --vscode-input Path to the VS Code extensions CSV file (e.g., vscode_requirements.csv, optional)"
    echo "  -o, --output       Path to the output CSV file (e.g., package_updates.csv)"
    exit 1
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -i|--input) input_file="$2"; shift ;;
        -v|--vscode-input) vscode_input_file="$2"; shift ;;
        -o|--output) output_file="$2"; shift ;;
        *) echo "Unknown parameter: $1"; usage ;;
    esac
    shift
done

# Check if input and output files are provided
if [[ -z "$input_file" || -z "$output_file" ]]; then
    echo "Error: Both input and output files must be specified."
    usage
fi

# Check if input file exists
if [[ ! -f "$input_file" ]]; then
    echo "Error: Input file '$input_file' not found."
    exit 1
fi

# Check if vscode input file exists (if provided)
if [[ -n "$vscode_input_file" && ! -f "$vscode_input_file" ]]; then
    echo "Error: VS Code input file '$vscode_input_file' not found."
    exit 1
fi

# Create or clear the output CSV file with header
printf "%-5s,%-30s,%15s,%15s,%s\n" "source" "package_name" "current_version" "new_version" "link_to_new_version" > "$output_file"

# Function to fetch the latest version from PyPI
get_latest_pypi_version() {
    local package_name=$1
    local response
    response=$(curl -s -m 5 "https://pypi.org/pypi/$package_name/json")
    if [[ $? -ne 0 ]]; then
        echo "Error fetching version"
        return
    fi
    # Check if response contains valid JSON and a version
    local version
    version=$(echo "$response" | jq -r '.info.version // empty')
    if [[ -z "$version" ]]; then
        echo "Not found"
    else
        echo "$version"
    fi
}

# Function to check VSCodium version
check_vscodium_version() {
    local package_name="vscodium"
    local new_version
    local link="https://github.com/VSCodium/vscodium/releases"

    # Fetch latest version from GitHub releases
    local response
    response=$(curl -s -m 5 "https://api.github.com/repos/VSCodium/vscodium/releases/latest")
    if [[ $? -ne 0 ]]; then
        new_version="Error fetching version"
        echo "Error: Failed to fetch latest version VSCodium from GitHub."
    else
        new_version=$(echo "$response" | jq -r '.tag_name // empty' | sed 's/^v//')
        if [[ -z "$new_version" ]]; then
            new_version="Not found"
            echo "Error: Latest VSCodium version not found on GitHub."
        fi
    fi

    # Write to CSV
    printf "%-5s,%-30s,%15s,%15s,%s\n" "github" "$package_name" "$VERSION_VSCODIUM" "$new_version" "$link" >> "$output_file"
}

check_vscode_extensions() {
    local vscode_input_file=$1
    # Read CSV line by line (no header assumed)
    while IFS=',' read -r publisher extension current_version || [[ -n "$publisher" ]]; do
        # Skip empty or incomplete lines
        if [[ -z "$publisher" || -z "$extension" || -z "$current_version" ]]; then
            continue
        fi

        # Construct package_name as publisher.extension
        package_name="$publisher.$extension"
        link="https://marketplace.visualstudio.com/items?itemName=$package_name"

        # Fetch latest version from Open VSX Registry
        local response
        response=$(curl -s -m 5 "https://open-vsx.org/api/$publisher/$extension")
        if [[ $? -ne 0 ]]; then
            new_version="Error fetching version"
            echo "Error: Failed to fetch latest version for extension '$package_name' from Open VSX Registry."
        else
            # Check if response is valid JSON
            if echo "$response" | jq -e . >/dev/null 2>&1; then
                new_version=$(echo "$response" | jq -r '.version // empty')
                if [[ -z "$new_version" ]]; then
                    new_version="Not found"
                    echo "Error: Extension '$package_name' not found on Open VSX Registry."
                fi
            else
                new_version="Invalid response"
                echo "Error: Invalid response for extension '$package_name' from Open VSX Registry."
            fi
        fi

        # Write to CSV with right-aligned fields, using current_version from file
        printf "%-5s,%-30s,%15s,%15s,%s\n" "vscode_marketplace" "$package_name" "$current_version" "$new_version" "$link" >> "$output_file"
    done < "$vscode_input_file"
}

# Check VSCodium version and add to CSV
check_vscodium_version

# Check VS Code extensions if input file is provided
if [[ -n "$vscode_input_file" ]]; then
    check_vscode_extensions "$vscode_input_file"
fi

# Read Python requirements file line by line
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines and comments
    if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
        continue
    fi

    # Parse package==version using regex
    if [[ "$line" =~ ^([a-zA-Z0-9_-]+)==([0-9a-zA-Z.]+) ]]; then
        package_name="${BASH_REMATCH[1]}"
        current_version="${BASH_REMATCH[2]}"
        new_version=$(get_latest_pypi_version "$package_name")

        # Log errors to console
        if [[ "$new_version" == "Not found" ]]; then
            echo "Error: Package '$package_name' not found on PyPI."
        elif [[ "$new_version" == "Error fetching version" ]]; then
            echo "Error: Failed to fetch version for package '$package_name' from PyPI."
        elif [[ "$new_version" =~ ^[0-9][0-9a-zA-Z.]*$ ]]; then
            # Ensure new_version starts with a digit
            :
        else
            echo "Error: Invalid version format for package '$package_name' (current: $current_version)."
            new_version="Invalid version format"
        fi

        # Write to CSV
        printf "%-5s,%-30s,%15s,%15s,%s\n" "pypi" "$package_name" "$current_version" "$new_version" "https://pypi.org/project/$package_name/" >> "$output_file"
    fi
done < "$input_file"
