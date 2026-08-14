# =============================================================================
# stage_files.py - File Staging Tool for Installer Builds
# =============================================================================
#
# This script copies files from Bazel sandbox paths to a staging directory
# with the correct directory structure expected by the Inno Setup script.
#
# Purpose:
#   - Read a manifest file listing all input files
#   - Transform Bazel sandbox paths to installation-relative paths
#   - Copy files to staging directory preserving directory structure
#
# Called by: inno_setup_installer rule (inno_setup.bzl)
# Arguments: --output-dir <staging_dir> --manifest <manifest_file>
#
# Path Transformation Examples:
#   Bazel Path                                              -> Staging Path
#   external/+http_archive+python_portable_windows/python.exe -> python.exe
#   external/+http_archive+python_portable_windows/Lib/os.py  -> Lib/os.py
#   bazel-out/.../site-packages/requests/__init__.py          -> Lib/site-packages/requests/__init__.py
#
# =============================================================================

"""
File staging tool for Inno Setup installer builds.

This script transforms Bazel sandbox paths to the correct installation directory
structure and copies files to a staging directory for use by ISCC.exe.
"""

import argparse
import shutil
import sys
from pathlib import Path


def extract_relative_path(full_path: str) -> str:
    """Extracts the installation-relative path from a Bazel sandbox path.
    
    Bazel places files in sandbox paths like:
        external/+http_archive+python_portable_windows/python.exe
        bazel-out/x64_windows-fastbuild/bin/.../site-packages/pkg/__init__.py
    
    This function transforms these to the target installation structure:
        python.exe
        Lib/site-packages/pkg/__init__.py
    
    Target Directory Structure (Python distribution):
        python.exe           # Main interpreter
        pythonw.exe          # Windowed interpreter
        python3.dll          # Core DLL
        Lib/                 # Standard library
            site-packages/   # Third-party packages
        DLLs/                # Extension modules
        include/             # Header files
        Scripts/             # Entry point scripts
    
    Args:
        full_path: Full Bazel sandbox path to a file
    
    Returns:
        Relative path suitable for the installation directory
    
    Examples:
        >>> extract_relative_path("external/+http_archive+python_portable_windows/python.exe")
        'python.exe'
        
        >>> extract_relative_path("external/+http_archive+python_portable_windows/Lib/os.py")
        'Lib/os.py'
        
        >>> extract_relative_path("bazel-out/.../site-packages/requests/__init__.py")
        'Lib/site-packages/requests/__init__.py'
    """
    parts = Path(full_path).parts
    
    # Case 1: Python runtime from http_archive (python_portable_windows)
    # Look for the repository marker in the path
    for i, part in enumerate(parts):
        if "python_portable" in part.lower():
            # Everything after the repository name is the relative path
            rel_parts = parts[i + 1:]
            if rel_parts:
                return str(Path(*rel_parts))
            break
    
    # Case 2: site-packages from pip_install
    # These need to be placed under Lib/site-packages/
    for i, part in enumerate(parts):
        if part == "site-packages":
            # Prepend Lib/ to create: Lib/site-packages/...
            return str(Path("Lib", *parts[i:]))
    
    # Fallback: Use filename only (should not happen in normal use)
    print(f"WARNING: Could not resolve path structure: {full_path}")
    return Path(full_path).name


def main():
    """Main entry point for the staging script.
    
    Reads a manifest file containing paths to all input files,
    transforms each path to the target installation structure,
    and copies files to the staging directory.
    
    Exit Codes:
        0: Success
        1: Error (manifest not found, etc.)
    """
    # -------------------------------------------------------------------------
    # Argument Parsing
    # -------------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Stage files for Inno Setup installer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This tool reads a manifest file (one file path per line) and copies
each file to the staging directory with the correct directory structure
expected by the Inno Setup script.
        """
    )
    parser.add_argument(
        "--output-dir", required=True,
        help="Staging directory where files will be copied"
    )
    parser.add_argument(
        "--manifest", required=True,
        help="Manifest file containing list of files to stage (one path per line)"
    )
    args = parser.parse_args()

    # -------------------------------------------------------------------------
    # Prepare Output Directory
    # -------------------------------------------------------------------------
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Read Manifest
    # -------------------------------------------------------------------------
    manifest = Path(args.manifest)
    if not manifest.exists():
        print(f"ERROR: Manifest file not found: {manifest}")
        sys.exit(1)

    with open(manifest, "r", encoding="utf-8") as f:
        files = [line.strip() for line in f if line.strip()]

    print(f"=== Staging {len(files)} files to {output_dir} ===")

    # -------------------------------------------------------------------------
    # Copy Files with Path Transformation
    # -------------------------------------------------------------------------
    for src_path in files:
        src = Path(src_path)
        
        # Skip missing files with warning
        if not src.exists():
            print(f"WARNING: File not found (skipping): {src}")
            continue

        # Transform Bazel sandbox path to installation-relative path
        rel_path = extract_relative_path(src_path)
        dest = output_dir / rel_path

        # Create parent directories as needed
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Copy file or directory
        if src.is_file():
            # copy2 preserves metadata (timestamps, permissions)
            shutil.copy2(src, dest)
        elif src.is_dir():
            # Remove existing directory to ensure clean copy
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)

    print("=== Staging completed ===")


if __name__ == "__main__":
    main()
