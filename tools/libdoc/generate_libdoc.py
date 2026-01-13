# ******************************************************************************
#
#  Copyright 2020-2023 Robert Bosch GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# ******************************************************************************
#
# generate_libdoc.py
#
# XC-CT/EMC51-Mai Minh Tri
#
# ------------------------------------------------------------------------------
#
# 23.09.2025
#
# ------------------------------------------------------------------------------
import os
import sys
import json
import re
import subprocess
from PythonExtensionsCollection.String.CString import CString
from bs4 import BeautifulSoup
from importlib.util import spec_from_file_location, module_from_spec

sPythonPath = CString.NormalizePath(sys.executable)

def generate_libdoc_for_files():
    """Load configuration, process each object, and generate output files."""
    try:
        # Determine the path to the configuration file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = CString.NormalizePath(f"{script_dir}/config/aio_libdoc_config.json")

        # Load the JSON configuration file
        with open(config_path, 'r', encoding='utf-8') as f:
            config_objects = json.load(f)

        # Process each configuration object
        for config in config_objects:
            process_config(config)

    except FileNotFoundError as e:
        print(f"Configuration file not found: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON configuration: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def is_class_path(pattern):
    """
    Checks if the pattern contains '::', indicating it is intended to reference a class path.
    Returns True if '::' is present, otherwise False.
    Example:
        'connection.*::QConnectBase.connection_manager.ConnectionManager' -> True
        'qlogger.*' -> False
    """
    return '::' in pattern

def has_valid_class_path(pattern):
    """
    Returns True if the string contains '::' and the part after '::' is a valid Python class/module path.
    """
    try:
        _, class_path = pattern.split('::', 1)
        if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+$', class_path):
            print(f"[ERROR] Invalid class path in pattern: '{pattern}' (class path: '{class_path}')")
            return False
        return True
    except Exception as e:
        print(f"[ERROR] Exception while checking class path in pattern: '{pattern}' - {e}")
        return False

def process_config(config):
    """Process a single configuration object."""
    repository_path = config['repository_path']
    source_folders = config['source_folders']
    include_patterns = config['include_patterns']
    exclude_patterns = config['exclude_patterns']
    output_directory = config['output_directory']

    # Compile regex patterns once
    exclude_regex = [re.compile(pattern) for pattern in exclude_patterns]
    include_regex = [re.compile(pattern) for pattern in include_patterns]

    for folder in source_folders:
        folder_path = CString.NormalizePath(f"{repository_path}/{folder}")
        version = get_version_from_source_path(folder_path)
        for root, _, files in os.walk(folder_path):
            root = CString.NormalizePath(root)
            # Handle patterns that reference a class path (with '::')
            patterns_to_remove = []
            for pattern in include_patterns:
                if is_class_path(pattern) and has_valid_class_path(pattern):
                    # Generate libdoc for class path pattern
                    generate_libdoc(pattern, root, version, repository_path, output_directory, is_class_path=True)
                    patterns_to_remove.append(pattern)  # Mark for removal after loop
            for pattern in patterns_to_remove:
                include_patterns.remove(pattern)
            # Handle regular file patterns
            for file in files:
                if file.endswith('.py') and should_process_file(file, include_regex, exclude_regex):
                    generate_libdoc(file, root, version, repository_path, output_directory)

def generate_libdoc(file, root, version, repository_path, output_directory, is_class_path=False):
    """Generate libdoc for a single file or class path."""
    output_file_path = ""
    base_name = ""
    # Extract base name before .py, .*, or ::
    if isinstance(file, str):
        # If class path, extract before '::'
        if '::' in file:
            base_name = re.split(r'\.py$|\.\*$', file.split('::')[0])[0]
        else:
            base_name = re.split(r'\.py$|\.\*$', file)[0]
    else:
        base_name = file
    try:
        if repository_path not in sys.path:
            sys.path.append(CString.NormalizePath(f"{repository_path}"))
        source_path = CString.NormalizePath(f"{root}/{file}")
        output_folder_path = CString.NormalizePath(f"{repository_path}/{output_directory}")
        os.makedirs(output_folder_path, exist_ok=True)
        if is_class_path:
            pattern_prefix = file.split('::')[0].split('.')[0]
            output_file_path = CString.NormalizePath(f"{output_folder_path}/{pattern_prefix}.html")
            source_path = file.split('::')[1]
        else:
            output_file_path = CString.NormalizePath(f"{output_folder_path}/{os.path.splitext(file)[0]}.html")

        # Change to the directory containing the Python file before generating libdoc
        original_cwd = os.getcwd()
        os.chdir(root)
        try:
            subprocess.run(
                [sPythonPath, '-m', 'robot.libdoc', '--version', version, '--name', base_name, source_path, output_file_path],
                check=True
            )
        finally:
            # Always restore the original working directory
            os.chdir(original_cwd)
        print(f"Documentation generated successfully for: {source_path}")

        add_readme_link_to_libdoc(output_file_path, repository_path)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while generating documentation for {file}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred for {file}: {e}")

def get_version_from_source_path(source_path):
    """Search for version.py in the folder and subfolders, and retrieve the version string."""
    try:
        for root, _, files in os.walk(source_path):
            if 'version.py' in files:
                version_file_path = os.path.join(root, 'version.py')
                spec = spec_from_file_location("version", version_file_path)
                version_module = module_from_spec(spec)
                spec.loader.exec_module(version_module)
                return getattr(version_module, 'VERSION', 'unknown')
        print(f"version.py not found in {source_path} or its subdirectories.")
        return 'unknown'
    except Exception as e:
        print(f"Failed to retrieve version from {source_path}: {e}")
        return 'unknown'

def should_process_file(file, include_regex, exclude_regex):
    """Determine if a file should be processed based on include and exclude patterns."""
    if include_regex and not any(regex.search(file) for regex in include_regex):
        return False
    if exclude_regex and any(regex.search(file) for regex in exclude_regex):
        return False
    return True

def add_readme_link_to_libdoc(output_path, repository_path):
    try:
        # Generate the README URL
        repository_name = os.path.basename(os.path.normpath(repository_path))
        readme_url = f"https://github.com/test-fullautomation/{repository_name}/blob/develop/README.md"

        # Read the HTML content from the file
        with open(output_path, "r", encoding="utf-8") as file:
            html_content = file.read()

        # Parse the HTML content
        soup = BeautifulSoup(html_content, "html.parser")

        # Find the <script> tag with id="base-template"
        script_tag = soup.find("script", id="base-template")
        if not script_tag:
            print("Script tag with id 'base-template' not found.")
            return

        # Extract and parse the content of the <script> tag
        script_content = script_tag.string
        script_soup = BeautifulSoup(script_content, "html.parser")

        # Find the metadata table
        metadata_table = script_soup.find("table", class_="metadata")
        if not metadata_table:
            print("Table with class 'metadata' not found inside the script content.")
            return

        # Create a new row for the README link
        new_row = script_soup.new_tag("tr")

        # Add a new <th> for the row
        new_th = script_soup.new_tag("th")
        new_th.string = "README:"
        new_row.append(new_th)

        # Add a new <td> with the README link
        new_td = script_soup.new_tag("td")
        new_a = script_soup.new_tag("a", href=readme_url)
        new_a.string = "GitHub"
        new_td.append(new_a)
        new_row.append(new_td)

        # Append the new row to the metadata table
        metadata_table.append(new_row)

        # Update the script tag content
        script_tag.string = str(script_soup)

        # Write the updated HTML back to the file
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(str(soup))

        print("README link successfully added to the libdoc.")
    except FileNotFoundError:
        print(f"Error: File not found at path '{output_path}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

generate_libdoc_for_files()