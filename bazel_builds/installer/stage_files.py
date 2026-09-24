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
import os
import shutil
import stat
import sys
from pathlib import Path


def _long_path(path: Path) -> str:
    """Returns a Windows extended-length path string ("\\\\?\\C:\\...") for
    the given path, bypassing the legacy MAX_PATH (260 char) limit.

    Background:
        VS Code's bundled extensions (e.g. GitHub Copilot's
        node_modules.asar.unpacked tree) contain files with very deeply
        nested paths. Combined with the staging directory's own path
        prefix (bazel-out/.../installer_set_1_staging/VSCode/...), the
        resulting absolute path can exceed 260 characters even after all
        prior shortening measures (see extract_relative_path() docstring:
        "Python" instead of "PortablePython", project moved to C:\\BZL,
        etc.). Windows historically rejects such paths with
        FileNotFoundError, even though the path is perfectly valid.

        The "\\\\?\\" prefix tells the Windows API to skip path parsing/
        normalization and MAX_PATH checks entirely, allowing paths up to
        ~32,767 characters. This works regardless of whether the
        system-wide "Enable Win32 long paths" policy is turned on, so it
        does not depend on any configuration of the build machine.

        Requires an absolute path (relative paths are not valid with this
        prefix), hence the os.path.abspath() call. No-op on non-Windows
        platforms since MAX_PATH does not apply there.

    Args:
        path: The path to convert.

    Returns:
        On Windows: an extended-length path string.
        On other platforms: the plain string form of the path.
    """
    if os.name != "nt":
        return str(path)
    abs_path = os.path.abspath(str(path))
    if abs_path.startswith("\\\\?\\"):
        return abs_path
    if abs_path.startswith("\\\\"):
        # UNC path (\\server\share\...) needs the \\?\UNC\ prefix variant
        return "\\\\?\\UNC\\" + abs_path.lstrip("\\")
    return "\\\\?\\" + abs_path


def _make_writable(path: Path) -> None:
    """Clears the read-only attribute on a file or (recursively) directory.

    Bazel marks action outputs read-only on Windows (and POSIX) to prevent
    accidental modification. shutil.copy2 preserves this mode bit on the
    copy, which means a later incremental build that needs to overwrite or
    delete that staged file (e.g. via shutil.rmtree or a second copy2 to the
    same destination) fails with PermissionError: [WinError 5] Zugriff
    verweigert. Call this right after copying to keep the staging directory
    freely modifiable for subsequent staging runs.
    """
    if path.is_dir():
        for root, dirs, files in os.walk(_long_path(path)):
            for name in dirs:
                os.chmod(os.path.join(root, name), stat.S_IWRITE | stat.S_IREAD)
            for name in files:
                os.chmod(os.path.join(root, name), stat.S_IWRITE | stat.S_IREAD)
    else:
        os.chmod(_long_path(path), stat.S_IWRITE | stat.S_IREAD)


def extract_relative_path(full_path: str) -> str:
    """Extracts the installation-relative path from a Bazel sandbox path.
    
    Bazel places files in sandbox paths like:
        external/+http_archive+python_portable_windows/python.exe
        bazel-out/x64_windows-fastbuild/bin/.../site-packages/pkg/__init__.py
    
    This function transforms these to the target installation structure:
        python.exe
        Lib/site-packages/pkg/__init__.py
    
    Target Directory Structure (installation root "{app}"):
        Python/                # Everything belonging to the Python distribution
            python.exe        # Main interpreter
            pythonw.exe       # Windowed interpreter
            python3.dll       # Core DLL
            Lib/              # Standard library
                site-packages/  # Third-party packages (all pip_install_dir components)
            DLLs/             # Extension modules
            include/          # Header files
            Scripts/          # Entry point scripts
        VSCode/               # Portable VS Code distribution (unrelated to Python)
            Code.exe
            ...
    
    Python and VS Code are kept in strictly separate subdirectories so that
    the two components never mix inside the installation folder (see
    installer.iss: [Files] copies the whole staging tree as-is into "{app}",
    so the subfolder names chosen here directly become the final on-disk
    layout).
    
    NOTE: The Python subdirectory is deliberately named "Python" (not
    "PortablePython") to keep staged paths as short as possible - some
    transitive dependencies (e.g. appium's deeply nested
    site-packages/appium/options/android/common/... modules) already come
    close to Windows' legacy MAX_PATH (260 chars) limit, and ISCC 5.5.1
    (currently in use, see components/inno_setup) has no long-path support.
    
    Args:
        full_path: Full Bazel sandbox path to a file
    
    Returns:
        Relative path suitable for the installation directory
    
    Examples:
        >>> extract_relative_path("external/+http_archive+python_portable_windows/python.exe")
        'Python/python.exe'
        
        >>> extract_relative_path("external/+http_archive+python_portable_windows/Lib/os.py")
        'Python/Lib/os.py'
        
        >>> extract_relative_path("bazel-out/.../site-packages/requests/__init__.py")
        'Python/Lib/site-packages/requests/__init__.py'
        
        >>> extract_relative_path("external/+http_archive+vscode_windows_x64/Code.exe")
        'VSCode/Code.exe'
    """
    parts = Path(full_path).parts
    
    # Case 0: Portable VS Code distribution from http_archive (vscode_windows_x64,
    # see components/vscode/MODULE.bazel). Must be checked before the generic
    # "python_portable" case below since the repository names don't overlap,
    # but keeping this first documents that VS Code is intentionally kept OUT
    # of the Python/ tree.
    for i, part in enumerate(parts):
        if "vscode_windows_x64" in part.lower():
            rel_parts = parts[i + 1:]
            if rel_parts:
                return str(Path("VSCode", *rel_parts))
            break
    
    # Case 1: Python runtime from http_archive (python_portable_windows)
    # Look for the repository marker in the path
    for i, part in enumerate(parts):
        if "python_portable" in part.lower():
            # Everything after the repository name is the relative path,
            # nested under Python/ to keep it separate from other
            # components (e.g. VSCode/). Kept short ("Python", not
            # "PortablePython") to avoid Windows MAX_PATH issues - see
            # docstring note above.
            rel_parts = parts[i + 1:]
            if rel_parts:
                return str(Path("Python", *rel_parts))
            break

    # Case 1b: Inno Setup Compiler from inno_setup_install repository_rule
    # (components/inno_setup). Place it under an "inno_setup/" subfolder so
    # it doesn't collide with the Python runtime's own top-level files.
    for i, part in enumerate(parts):
        if "inno_setup_portable" in part.lower():
            rel_parts = parts[i + 1:]
            if rel_parts:
                return str(Path("inno_setup", *rel_parts))
            break

    # Case 2: site-packages from pip_install
    # These need to be placed under Lib/site-packages/
    #
    # IMPORTANT: Multiple independent pip_install_dir targets (e.g.
    # py_modules_set_1, py_modules_set_2, robotframework_testsuitesmanagement)
    # all use the same default out_dir name "site-packages". Since this
    # function only matches on the directory NAME (not on which Bazel
    # target/repository it came from), every one of them maps to the exact
    # same destination "Lib/site-packages". This is intentional - packages
    # from different components should end up merged together in the same
    # site-packages folder of the final installation - but it means the
    # caller (main()) MUST merge multiple source directories into this same
    # destination instead of deleting/overwriting it for each new source
    # (see the dirs_exist_ok=True copytree call below).
    #
    # Special case "site-packages-deps": Some components (e.g.
    # python-extensions-collection) need TWO pip_install targets in the
    # SAME Bazel package - one pip_install_dir for transitive PyPI
    # dependencies, one pip_install_from_source for the package itself
    # (built from a git_repository source tree). Two actions in the same
    # package cannot both declare an output literally named "site-packages"
    # (Bazel would reject this as "conflicting actions" - two different
    # actions producing the same output path). The transitive-deps target
    # therefore uses out_dir="site-packages-deps" instead (see that
    # component's BUILD.bazel) - matched here via startswith() so it still
    # merges into the exact same "Lib/site-packages" destination as every
    # other component's plain "site-packages" output.
    for i, part in enumerate(parts):
        if part == "site-packages" or part.startswith("site-packages-"):
            # Prepend Python/Lib/ to create: Python/Lib/site-packages/...
            # so these end up alongside the Python runtime, not mixed with
            # VSCode/. The destination segment is always normalized to the
            # literal name "site-packages" (regardless of the actual source
            # out_dir name, e.g. "site-packages-deps"), so that all
            # variants merge into the one true site-packages directory.
            rel_parts = parts[i + 1:]
            return str(Path("Python", "Lib", "site-packages", *rel_parts))


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

        # Create parent directories as needed. Uses the extended-length
        # path form since VS Code's bundled extensions (e.g. GitHub
        # Copilot's node_modules.asar.unpacked tree) can produce staging
        # paths that exceed Windows' legacy 260-char MAX_PATH limit - see
        # _long_path() docstring for details.
        os.makedirs(_long_path(dest.parent), exist_ok=True)

        # Copy file or directory
        if src.is_file():
            # copy2 preserves metadata (timestamps, permissions). Bazel
            # marks action outputs read-only, so the copy inherits that -
            # clear it again so the staging dir stays freely modifiable
            # (both for merging further sources into the same destination
            # further down in this loop, and for any subsequent rebuild).
            if os.path.exists(_long_path(dest)):
                _make_writable(dest)
            shutil.copy2(_long_path(src), _long_path(dest))
            _make_writable(dest)
        elif src.is_dir():
            # Merge instead of replace: several independent components
            # (e.g. py_modules_set_1, py_modules_set_2,
            # robotframework_testsuitesmanagement) all produce a directory
            # literally named "site-packages", which extract_relative_path()
            # intentionally maps to the SAME destination "Lib/site-packages"
            # so their packages end up side by side in the final
            # installation. Deleting the destination here (as a plain
            # shutil.rmtree + copytree would) would wipe out whatever a
            # previous source already staged there - and since those files
            # were copied with copy2 (preserving Bazel's read-only bit),
            # that rmtree would additionally fail on Windows with
            # PermissionError. dirs_exist_ok=True merges the tree instead.
            if os.path.exists(_long_path(dest)):
                _make_writable(dest)
            shutil.copytree(_long_path(src), _long_path(dest), dirs_exist_ok=True)
            _make_writable(dest)

    print("=== Staging completed ===")


if __name__ == "__main__":
    main()
