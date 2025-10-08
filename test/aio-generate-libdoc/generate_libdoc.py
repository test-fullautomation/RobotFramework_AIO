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
            for file in files:
                if file.endswith('.py') and should_process_file(file, include_regex, exclude_regex):
                    generate_libdoc(file, root, version, repository_path, output_directory)

def generate_libdoc(file, root, version, repository_path, output_directory):
    """Generate libdoc for a single file."""
    try:
        source_path = CString.NormalizePath(f"{root}/{file}")
        output_folder_path = CString.NormalizePath(f"{repository_path}/{output_directory}")
        os.makedirs(output_folder_path, exist_ok=True)

        output_file_path = CString.NormalizePath(f"{output_folder_path}/{os.path.splitext(file)[0]}.html")

        subprocess.run(
            [sPythonPath, '-m', 'robot.libdoc', '--version', version, source_path, output_file_path],
            check=True
        )
        print(f"Documentation generated successfully for: {source_path}")
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

generate_libdoc_for_files()