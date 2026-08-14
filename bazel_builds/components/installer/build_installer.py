# =============================================================================
# build_installer.py - Inno Setup Compiler Wrapper
# =============================================================================
#
# This script wraps the Inno Setup Compiler (ISCC.exe) and is invoked by Bazel
# as a py_binary tool during the installer build process.
#
# Purpose:
#   - Validate ISCC.exe exists and meets version requirements
#   - Invoke ISCC.exe with proper arguments and path conversions
#   - Handle output file placement for Bazel's expected output location
#   - Provide clear error messages for build failures
#
# Called by: inno_setup_installer rule (inno_setup.bzl)
# Arguments: See main() argparse definition
#
# =============================================================================

"""
Inno Setup Compiler wrapper script for Bazel builds.

This script is executed by Bazel as part of the inno_setup_installer rule.
It handles the invocation of ISCC.exe with proper arguments, version checking,
and output file management.
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def get_iscc_version(iscc_path: str) -> tuple:
    """Determines the installed ISCC version.
    
    Runs ISCC.exe without arguments to get version information from its
    output. Parses the version string to extract major and minor version.
    
    Args:
        iscc_path: Absolute path to ISCC.exe
    
    Returns:
        Tuple of (major, minor) version numbers, e.g., (6, 3) for ISCC 6.3
        Returns (0, 0) if version cannot be determined.
    
    Note:
        ISCC returns exit code 1 when run without arguments, which is
        expected behavior - we use check=False to handle this.
    """
    try:
        result = subprocess.run(
            [iscc_path],
            capture_output=True,
            text=True,
            check=False,  # ISCC returns exit code 1 without arguments
        )
        # Output may be in stderr (error) or stdout (success)
        output = result.stdout + result.stderr
        
        # Look for "Inno Setup X" or "Inno Setup X.Y" in output
        match = re.search(r'Inno Setup (\d+)(?:\.(\d+))?', output)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2)) if match.group(2) else 0
            return (major, minor)
    except OSError as e:
        print(f"WARNING: Could not determine ISCC version: {e}")
    return (0, 0)


def main():
    """Main entry point for the installer build script.
    
    Parses command-line arguments, validates inputs, runs ISCC.exe,
    and ensures the output file is placed at the expected location.
    
    Exit Codes:
        0: Success
        1: Error (ISCC not found, version too old, build failed, etc.)
    """
    # -------------------------------------------------------------------------
    # Argument Parsing
    # -------------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Build Windows installer using Inno Setup Compiler",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
    python build_installer.py \\
        --iscc "C:/Program Files/Inno Setup 6/ISCC.exe" \\
        --iss installer.iss \\
        --source-dir ./staging \\
        --output ./output/setup.exe \\
        --version 1.0.0
        """
    )
    parser.add_argument(
        "--iscc", required=True,
        help="Path to ISCC.exe (Inno Setup Compiler)"
    )
    parser.add_argument(
        "--iss", required=True,
        help="Path to the .iss script template file"
    )
    parser.add_argument(
        "--source-dir", required=True,
        help="Directory containing files to be installed (staging directory)"
    )
    parser.add_argument(
        "--output", required=True,
        help="Output path for the generated installer executable"
    )
    parser.add_argument(
        "--version", default="1.0.0",
        help="Version string for the installer (default: 1.0.0)"
    )
    parser.add_argument(
        "--min-iscc-version", default="5.0",
        help="Minimum required ISCC version, e.g., '6.3' (default: 5.0)"
    )
    args = parser.parse_args()

    # -------------------------------------------------------------------------
    # Path Resolution
    # -------------------------------------------------------------------------
    # Convert relative paths to absolute paths for ISCC
    output_path = Path(args.output).resolve()
    output_dir = output_path.parent
    output_name = output_path.stem  # Filename without .exe extension

    source_dir = Path(args.source_dir).resolve()

    # -------------------------------------------------------------------------
    # Status Output
    # -------------------------------------------------------------------------
    print("=== Inno Setup Installer Build ===")
    print(f"ISCC:       {args.iscc}")
    print(f"ISS:        {args.iss}")
    print(f"Source:     {source_dir}")
    print(f"Output:     {output_path}")
    print(f"Version:    {args.version}")

    # -------------------------------------------------------------------------
    # Validation: ISCC Existence
    # -------------------------------------------------------------------------
    if not Path(args.iscc).exists():
        print(f"ERROR: ISCC.exe not found: {args.iscc}")
        print("       Please install Inno Setup or update the iscc_path parameter.")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # Validation: ISCC Version
    # -------------------------------------------------------------------------
    iscc_version = get_iscc_version(args.iscc)
    print(f"ISCC Version: {iscc_version[0]}.{iscc_version[1]}")
    
    # Parse minimum version requirement
    min_parts = args.min_iscc_version.split('.')
    min_version = (int(min_parts[0]), int(min_parts[1]) if len(min_parts) > 1 else 0)
    
    if iscc_version < min_version:
        print(f"ERROR: ISCC version {iscc_version[0]}.{iscc_version[1]} is too old!")
        print(f"       Minimum required version: {args.min_iscc_version}")
        print("       Please update Inno Setup or adjust the ISS script.")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # Validation: Source Directory
    # -------------------------------------------------------------------------
    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        print("       The staging step may have failed.")
        sys.exit(1)

    # -------------------------------------------------------------------------
    # Prepare Output Directory
    # -------------------------------------------------------------------------
    output_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # Build: Invoke ISCC.exe
    # -------------------------------------------------------------------------
    # ISCC command-line options:
    #   /D<name>=<value>  Define preprocessor variable
    #   /F<filename>      Output filename (without .exe)
    #   /O<path>          Output directory
    #
    # The ISS script can use these via {#SourceDir}, {#OutputDir}, {#AppVersion}
    
    cmd = [
        args.iscc,
        f"/DSourceDir={source_dir}",      # Source files location
        f"/DOutputDir={output_dir}",      # Output directory
        f"/DAppVersion={args.version}",   # Application version
        f"/F{output_name}",               # Output filename (without .exe)
        args.iss,                          # ISS script file
    ]

    print(f"\nExecuting: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Inno Setup compilation failed (exit code {e.returncode})")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

    # -------------------------------------------------------------------------
    # Post-Build: Verify Output
    # -------------------------------------------------------------------------
    expected_output = output_dir / f"{output_name}.exe"
    if not expected_output.exists():
        print(f"ERROR: Expected output file was not created: {expected_output}")
        print("       Check ISCC output above for errors.")
        sys.exit(1)

    # Move output to Bazel's expected location if different
    # (ISCC may place output in a different directory than Bazel expects)
    if expected_output != output_path:
        shutil.move(str(expected_output), str(output_path))

    print(f"\n=== Installer successfully created: {output_path} ===")


if __name__ == "__main__":
    main()
