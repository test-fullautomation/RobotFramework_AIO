# =============================================================================
# inno_setup.bzl - Custom Bazel Rule for Inno Setup Installer Creation
# =============================================================================
#
# This module defines a custom Bazel rule that builds Windows installers using
# Inno Setup (ISCC.exe). The rule handles:
#   1. Collecting all input files from the bundle
#   2. Staging files to a temporary directory with correct paths
#   3. Invoking ISCC.exe to create the final installer executable
#
# Usage:
#   load(":inno_setup.bzl", "inno_setup_installer")
#
#   inno_setup_installer(
#       name = "my_installer",
#       bundle = [":my_bundle"],
#       iss_template = "installer.iss",
#       version = "1.0.0",
#       installer_name = "setup_myapp",
#   )
#
# Dependencies:
#   - //components/installer:build_installer_tool (Python script to run ISCC)
#   - //components/installer:stage_files_tool (Python script for file staging)
#
# =============================================================================

"""
Custom Starlark rule for building Windows installers with Inno Setup.

This rule wraps the Inno Setup Compiler (ISCC.exe) and integrates it into
the Bazel build graph, providing proper dependency tracking and caching.
"""

def _inno_setup_installer_impl(ctx):
    """Implementation function for the inno_setup_installer rule.
    
    This function is called by Bazel during the analysis phase to define
    the actions needed to build the installer. It performs two main actions:
    
    1. Staging Action: Copies all bundle files to a staging directory with
       the correct directory structure expected by the ISS script.
    
    2. Build Action: Runs ISCC.exe to compile the installer from the
       staged files and ISS template.
    
    Args:
        ctx: The rule context providing access to attributes, actions, and outputs.
    
    Returns:
        DefaultInfo provider containing the output installer executable.
    """
    
    # The final output file (installer executable)
    output = ctx.outputs.installer
    
    # Staging directory where all bundle files will be copied
    # This is necessary because Bazel sandbox paths differ from the
    # installation paths defined in the ISS script
    staging_dir = ctx.actions.declare_directory(ctx.label.name + "_staging")
    
    # Manifest file listing all input files (one path per line)
    # Used by the staging tool to know which files to copy
    manifest = ctx.actions.declare_file(ctx.label.name + "_manifest.txt")
    
    # Collect all input files from the bundle targets
    # Each bundle target may contain multiple files (e.g., a filegroup)
    input_files = []
    for src in ctx.attr.bundle:
        input_files.extend(src.files.to_list())
    
    if not input_files:
        fail("No input files found in bundle. Check that bundle targets produce files.")
    
    # Write the manifest file containing all input file paths
    # Format: one absolute path per line
    ctx.actions.write(
        output = manifest,
        content = "\n".join([f.path for f in input_files]),
    )
    
    # -------------------------------------------------------------------------
    # Action 1: Stage Files
    # -------------------------------------------------------------------------
    # Copy all bundle files to the staging directory with correct paths.
    # The staging tool reads the manifest and copies files while preserving
    # or transforming the directory structure as needed.
    #
    # Execution requirements:
    #   - local: Must run on local machine (not remote execution)
    #   - no-sandbox: Needs access to filesystem outside sandbox
    
    ctx.actions.run(
        outputs = [staging_dir],
        inputs = input_files + [manifest],
        executable = ctx.executable._stager,
        arguments = [
            "--output-dir", staging_dir.path,
            "--manifest", manifest.path,
        ],
        mnemonic = "StagingFiles",
        progress_message = "Staging files for installer %s" % ctx.label.name,
        execution_requirements = {
            "local": "1",
            "no-sandbox": "1",
        },
    )
    
    # -------------------------------------------------------------------------
    # Action 2: Build Installer
    # -------------------------------------------------------------------------
    # Run ISCC.exe to compile the installer from the staged files.
    # The build tool wraps ISCC.exe and handles path conversion and error handling.
    
    args = ctx.actions.args()
    args.add("--iscc", ctx.attr.iscc_path)
    args.add("--iss", ctx.file.iss_template.path)
    args.add("--source-dir", staging_dir.path)
    args.add("--output", output.path)
    args.add("--version", ctx.attr.version)
    
    ctx.actions.run(
        outputs = [output],
        inputs = [staging_dir, ctx.file.iss_template],
        executable = ctx.executable._builder,
        arguments = [args],
        mnemonic = "InnoSetup",
        progress_message = "Building installer %s" % output.short_path,
        execution_requirements = {
            "local": "1",      # ISCC.exe must run locally (Windows only)
            "no-sandbox": "1", # Needs filesystem access for compilation
        },
    )
    
    # Return the DefaultInfo provider with the output file
    # This makes the installer available to downstream targets and `bazel build`
    return [DefaultInfo(files = depset([output]))]


# =============================================================================
# Rule Definition
# =============================================================================

inno_setup_installer = rule(
    implementation = _inno_setup_installer_impl,
    attrs = {
        # -------------------------------------------------------------------------
        # Public Attributes (set by user)
        # -------------------------------------------------------------------------
        
        "bundle": attr.label_list(
            mandatory = True,
            doc = """List of targets containing files to include in the installer.
            
            Typically filegroups that aggregate component files. All files from
            these targets will be staged and included in the installer.
            
            Example: [":my_bundle", "//components/python:python_runtime"]
            """,
        ),
        
        "iss_template": attr.label(
            mandatory = True,
            allow_single_file = [".iss"],
            doc = """Inno Setup Script (.iss) template file.
            
            This file defines the installer configuration including:
            - Application metadata (name, version, publisher)
            - Installation directories
            - Files to install (using {src} placeholders)
            - Registry entries, shortcuts, etc.
            """,
        ),
        
        "iscc_path": attr.string(
            default = "C:/workplace/Programme/InnoSetup/ISCC.exe",
            doc = """Absolute path to the Inno Setup Compiler (ISCC.exe).
            
            This should point to the ISCC.exe executable on the build machine.
            Note: This breaks hermeticity but is necessary for Windows-only tools.
            """,
        ),
        
        "version": attr.string(
            default = "1.0.0",
            doc = """Version string for the installer.
            
            This is passed to ISCC.exe and can be used in the ISS script
            via preprocessor defines (e.g., {#Version}).
            """,
        ),
        
        "installer_name": attr.string(
            default = "install_python",
            doc = """Base name for the output installer executable (without .exe).
            
            The final output will be {installer_name}.exe
            Example: "setup_myapp" -> "setup_myapp.exe"
            """,
        ),
        
        # -------------------------------------------------------------------------
        # Private Attributes (internal implementation details)
        # -------------------------------------------------------------------------
        
        "_builder": attr.label(
            default = "//:build_installer_tool",
            executable = True,
            cfg = "exec",
            doc = """Python tool that invokes ISCC.exe.
            
            This tool handles:
            - Path conversion (Bazel paths to Windows paths)
            - Error handling and logging
            - Version injection into ISS script
            """,
        ),
        
        "_stager": attr.label(
            default = "//:stage_files_tool",
            executable = True,
            cfg = "exec",
            doc = """Python tool that stages files for the installer.
            
            This tool:
            - Reads the manifest file
            - Copies files to staging directory
            - Preserves or transforms directory structure
            """,
        ),
    },
    
    outputs = {
        "installer": "%{installer_name}.exe",
    },
    
    doc = """Builds a Windows installer using Inno Setup.
    
    This rule creates a Windows installer (.exe) by:
    1. Collecting files from the bundle targets
    2. Staging them to a temporary directory
    3. Running ISCC.exe to compile the installer
    
    The installer is a proper Bazel output that benefits from:
    - Dependency tracking (rebuilds when inputs change)
    - Caching (reuses previous build if inputs unchanged)
    - Parallel execution (can build multiple installers in parallel)
    
    Limitations:
    - Windows only (ISCC.exe is a Windows executable)
    - Requires local execution (no remote build support)
    - ISCC.exe path breaks hermeticity
    """,
)

