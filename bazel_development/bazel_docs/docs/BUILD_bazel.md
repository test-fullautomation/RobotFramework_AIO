# BUILD.bazel

**Pfad:** `BUILD.bazel`  
**Absoluter Pfad:** `C:\workplace\ROBFW\components\bazel_aio\BUILD.bazel`  
**Typ:** Bazel Build File (definiert Targets und Dependencies)

---

## Inhalt

```python
# Root BUILD file - makes the workspace root a Bazel package
load("@rules_python//python:defs.bzl", "py_binary")
# # # load("//tools:test_suite_runner.bzl", "create_test_runner")

exports_files(["requirements_lock.txt"])

# ============================================================================
# Global platform configuration settings
# ============================================================================
# These can be referenced from any BUILD.bazel file in the workspace using:
#   //:is_windows or //:is_linux
# ============================================================================

config_setting(
    name = "is_windows",
    constraint_values = ["@platforms//os:windows"],
    visibility = ["//visibility:public"],
)

config_setting(
    name = "is_linux",
    constraint_values = ["@platforms//os:linux"],
    visibility = ["//visibility:public"],
)

# ============================================================================
# PyTestLog2DB Upload Tool
# ============================================================================
# Uploads pytest XML results to database using credentials from environment
# variables to avoid hardcoding sensitive information.
#
# Required environment variables:
#   TESTDB_SERVER   : Database server (IP or URL)
#   TESTDB_USER     : Database user
#   TESTDB_PASSWORD : Database password
#   TESTDB_DATABASE : Database schema name
#
# Optional environment variables:
#   TESTDB_RESULTXML: Path to XML file/dir (default: test_logfiles)
#   TESTDB_RECURSIVE: Set to '1' or 'true' for recursive search
#   TESTDB_UUID     : UUID for identifying the import
#   TESTDB_VARIANT  : Variant information
#   TESTDB_VERSIONS : Version information
#   TESTDB_CONFIG   : Config file path
#   TESTDB_DRYRUN   : Set to '1' or 'true' for dry-run mode
#   TESTDB_APPEND   : Set to '1' or 'true' to append to existing UUID
#
# Usage examples:
#   Windows:
#     $env:TESTDB_SERVER="192.168.1.100"
#     $env:TESTDB_USER="testuser"
#     $env:TESTDB_PASSWORD="secret"
#     $env:TESTDB_DATABASE="testresults"
#     $env:TESTDB_DRYRUN="1"
#     bazel run //:upload_test_results
#
#   Linux:
#     export TESTDB_SERVER="192.168.1.100"
#     export TESTDB_USER="testuser"
#     export TESTDB_PASSWORD="secret"
#     export TESTDB_DATABASE="testresults"
#     export TESTDB_DRYRUN="1"
#     bazel run //:upload_test_results
# ============================================================================

py_binary(
    name = "upload_test_results",
    srcs = ["upload_results_to_db.py"],
    main = "upload_results_to_db.py",
    visibility = ["//visibility:public"],
    # Note: PyTestLog2DB and RobotLog2DB cannot be included as dependencies
    # because they have circular dependency issues in their package dependencies.
    # These tools must be installed in an external Python environment
    # specified via the RobotPythonPath environment variable.
    deps = [],
)

```

---

## Datei-Informationen

- **Größe:** 2926 bytes
- **Zeilen:** 76
- **Verzeichnis:** `C:\workplace\ROBFW\components\bazel_aio`

---

## Navigation

**Übergeordnetes Verzeichnis:** `(Root)`

