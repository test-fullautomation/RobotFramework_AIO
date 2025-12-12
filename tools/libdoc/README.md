# generate_libdoc.py

This script automates the generation of Robot Framework library documentation (libdoc) for Python libraries and classes in the RobotFramework_AIO project.

## Usage
Run the script from the command line:

```bash
python generate_libdoc.py
```

## Configuration
Edit `config/aio_libdoc_config.json` to specify:
- `repository_path`: Path to the library repository.
- `output_directory`: Where to save generated documentation.
- `source_folders`: Folders to scan for Python files.
- `include_patterns`: Patterns for files or class paths (use `::` for class path).
- `exclude_patterns`: Patterns to exclude files.

### Example include_patterns
- `qlogger.*` — matches files like `qlogger.py`.
- `connection.*::QConnectBase.connection_manager.ConnectionManager` — generates documentation for the specified class path.

## Output
- HTML documentation files are generated in the specified output directory.
- Each documentation file includes a link to the repository README.

## Error Handling
- Invalid class paths are logged as errors.
- Exceptions during documentation generation are logged.

## License
Copyright 2020-2025 Robert Bosch GmbH

Licensed under the Apache License, Version 2.0 (the \"License\"); you
may not use this file except in compliance with the License. You may
obtain a copy of the License at

> [![License: Apache
> v2](https://img.shields.io/pypi/l/robotframework.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an \"AS IS\" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## Author
XC-CT/EMC51-Mai Minh Tri
