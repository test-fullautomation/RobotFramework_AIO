import os
import sys
import json
import re
import subprocess
from PythonExtensionsCollection.String.CString import CString

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

        # Iterate over each object in the configuration
        for config in config_objects:
            repository_path = config['repository_path']
            source_folders = config['source_folders']
            include_patterns = config['include_patterns']
            exclude_patterns = config['exclude_patterns']
            output_directory = config['output_directory']

            # Find all Python files in the source_folders, excluding files matching exclude_patterns
            exclude_regex = [re.compile(pattern) for pattern in exclude_patterns]
            include_regex = [re.compile(pattern) for pattern in include_patterns]

            for folder in source_folders:
                folder_path = CString.NormalizePath(f"{repository_path}/{folder}")
                for root, _, files in os.walk(folder_path):
                    root = CString.NormalizePath(f"{root}")
                    for file in files:
                        if file.endswith('.py'):
                            # Check if the file matches any exclude pattern
                            if should_process_file(file, include_patterns, exclude_patterns, include_regex, exclude_regex):
                                source_path = CString.NormalizePath(f"{root}/{file}")
                                output_folder_path = CString.NormalizePath(f"{repository_path}/{output_directory}")

                                # Ensure the output directory exists
                                os.makedirs(output_folder_path, exist_ok=True)
                                output_file_path = os.path.splitext(file)[0] + '.html'
                                output_file_path = CString.NormalizePath(f"{output_folder_path}/{output_file_path}")
                                try:
                                    subprocess.run([sPythonPath, '-m', 'robot.libdoc', source_path, output_file_path], check=True)
                                    print(f"Documentation generated successfully for: {source_path}")
                                except subprocess.CalledProcessError as e:
                                    print(f"Error occurred while generating documentation: {e}")
                                except Exception as e:
                                    print(f"An unexpected error occurred: {e}")
    except FileNotFoundError as e:
        print(f"Configuration file not found: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON configuration: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in the function: {e}")

def should_process_file(file, include_patterns, exclude_patterns, include_regex, exclude_regex):
    """Determine if a file should be processed based on include and exclude patterns."""
    if len(include_patterns) == 0 and len(exclude_patterns) > 0:
        # Case 1: No include patterns, only exclude patterns
        return not any(regex.search(file) for regex in exclude_regex)
    elif len(include_patterns) > 0 and len(exclude_patterns) > 0:
        # Case 2: Both include and exclude patterns
        return any(regex.search(file) for regex in include_regex) and not any(regex.search(file) for regex in exclude_regex)
    elif len(include_patterns) > 0 and len(exclude_patterns) == 0:
        # Case 3: Only include patterns
        return any(regex.search(file) for regex in include_regex)
    return False

generate_libdoc_for_files()