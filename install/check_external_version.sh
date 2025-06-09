#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 -i <input_file> -o <output_file>"
    echo "  -i, --input   Path to the input requirements file (e.g., python_requirements.txt)"
    echo "  -o, --output  Path to the output CSV file (e.g., package_updates.csv)"
    exit 1
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -i|--input) input_file="$2"; shift ;;
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

# Create or clear the output CSV file
printf "%-5s,%-30s,%15s,%15s,%s\n" "source" "package_name" "current_version" "new_version" "link_to_new_version" > "$output_file"

# Function to fetch the latest version from PyPI
get_latest_version() {
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

# Read input file line by line
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines and comments
    if [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]]; then
        continue
    fi

    # Parse package==version using regex
    if [[ "$line" =~ ^([a-zA-Z0-9_-]+)==([0-9a-zA-Z.]+) ]]; then
        package_name="${BASH_REMATCH[1]}"
        current_version="${BASH_REMATCH[2]}"
        new_version=$(get_latest_version "$package_name")

        # Log errors to console
        if [[ "$new_version" == "Not found" ]]; then
            echo "Error: Package '$package_name' not found on PyPI."
        elif [[ "$new_version" == "Error fetching version" ]]; then
            echo "Error: Failed to fetch version for package '$package_name' from PyPI."
        elif [[ "$new_version" =~ ^[0-9][0-9a-zA-Z.]*$ ]]; then
            # Basic validation: ensure new_version starts with a digit
            :
        else
            echo "Error: Invalid version format for package '$package_name' (current: $current_version)."
            new_version="Invalid version format"
        fi

        # Write to CSV
        printf "%-5s,%-30s,%15s,%15s,%s\n" "pypi" "$package_name" "$current_version" "$new_version" "https://pypi.org/project/$package_name/" >> "$output_file"
    fi
done < "$input_file"
