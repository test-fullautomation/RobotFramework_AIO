# =============================================================================
# pip_install.bzl - Custom Bazel Rule for pip Package Installation
# =============================================================================
#
# This module defines a custom Bazel rule that installs Python packages using
# pip during the build process. Unlike the standard rules_python pip_parse,
# this rule:
#   - Installs packages at build time (not analysis time)
#   - Uses the target Python interpreter (from python_portable_windows)
#   - Outputs packages to a directory that can be bundled into installers
#
# Usage:
#   load(":pip_install.bzl", "pip_install_dir")
#
#   pip_install_dir(
#       name = "py_modules",
#       requirements = "requirements.txt",
#       interpreter = "@python_portable_windows//:interpreter",
#       runtime = "@python_portable_windows//:runtime",
#   )
#
# Why a custom rule instead of rules_python pip_parse?
#   - pip_parse runs at repository/analysis time, not build time
#   - We need packages installed using the TARGET Python interpreter
#   - The output must be a directory that can be staged for the installer
#
# =============================================================================

"""
Custom Bazel rule for installing Python packages via pip.

This rule runs pip install during the build action phase, allowing packages
to be installed using the target Python interpreter and bundled into
installers.
"""

def _pip_install_impl(ctx):
    """Implementation function for the pip_install_dir rule.
    
    Executes pip install with the specified requirements file and target
    Python interpreter. Outputs packages to a directory that can be
    referenced by other targets.
    
    Args:
        ctx: The rule context providing access to attributes and actions.
    
    Returns:
        DefaultInfo provider with the output directory containing installed packages.
    
    Note:
        This action requires network access and must run without sandboxing
        to allow pip to download packages from PyPI.
    """
    # Declare output directory for installed packages
    out = ctx.actions.declare_directory(ctx.attr.out_dir)

    # Get Python interpreter and runtime files from the external repository
    interpreter = ctx.file.interpreter    # python.exe from portable distribution
    runtime = ctx.files.runtime           # All files from the Python distribution

    # Build pip install command arguments
    args = ctx.actions.args()
    args.add("-m").add("pip").add("install")    # Run pip as a module
    args.add("--requirement", ctx.file.requirements)  # Requirements file
    args.add("--target", out.path)              # Install to output directory
    args.add("--no-compile")                    # Skip .pyc compilation (saves time)
    args.add("--disable-pip-version-check")    # Skip pip update check
    args.add("--no-input")                      # Non-interactive mode
    
    # Optional: Require hash verification for security
    if ctx.attr.require_hashes:
        args.add("--require-hashes")

    # Execute pip install
    # Note: This action has special execution requirements:
    #   - requires-network: Needs to download packages from PyPI
    #   - no-sandbox: pip needs filesystem access beyond sandbox
    #   - no-remote: Must run locally, not on remote execution
    #
    # IMPORTANT: ctx.actions.run(env=...) does NOT automatically merge with
    # --action_env values from .bazelrc unless use_default_shell_env=True is
    # set. Without it, proxy variables declared via
    # "build --action_env=HTTPS_PROXY" etc. are silently discarded and the
    # pip subprocess runs with an empty/minimal environment. This previously
    # went unnoticed on machines with a warm --disk_cache (cached action
    # result, pip never actually re-executed) and only surfaced as a
    # "getaddrinfo failed" network error on a machine with a cold cache.
    ctx.actions.run(
        executable = interpreter,
        arguments = [args],
        inputs = depset([ctx.file.requirements] + runtime),
        outputs = [out],
        env = ctx.attr.env,
        use_default_shell_env = True,  # merge --action_env (e.g. HTTPS_PROXY) into env
        execution_requirements = {
            "requires-network": "",   # Allow network access for PyPI downloads
            "no-sandbox": "",         # Disable sandbox for pip operations
            "no-remote": "",          # Run locally only (not remote execution)
        },
        mnemonic = "PipInstall",
        progress_message = "pip install -> %s" % out.short_path,
    )

    return [DefaultInfo(files = depset([out]))]


# =============================================================================
# Rule Definition
# =============================================================================

pip_install_dir = rule(
    implementation = _pip_install_impl,
    attrs = {
        # -------------------------------------------------------------------------
        # Required Attributes
        # -------------------------------------------------------------------------
        
        "requirements": attr.label(
            allow_single_file = True,
            mandatory = True,
            doc = """Requirements file listing packages to install.
            
            Format: Standard pip requirements.txt format.
            Can include version constraints, hashes, etc.
            
            Example contents:
                requests==2.31.0 \\
                    --hash=sha256:abcdef...
                numpy>=1.24.0
            """,
        ),
        
        "interpreter": attr.label(
            allow_single_file = True,
            mandatory = True,
            doc = """Python interpreter executable to use for pip.
            
            This should point to python.exe from the target Python distribution.
            Using the target interpreter ensures packages are compatible.
            
            Example: "@python_portable_windows//:interpreter"
            """,
        ),
        
        "runtime": attr.label(
            mandatory = True,
            doc = """Complete Python runtime (all distribution files).
            
            Pip needs access to the full Python installation including
            standard library, DLLs, etc. to function correctly.
            
            Example: "@python_portable_windows//:runtime"
            """,
        ),
        
        # -------------------------------------------------------------------------
        # Optional Attributes
        # -------------------------------------------------------------------------
        
        "out_dir": attr.string(
            default = "site-packages",
            doc = """Name of the output directory for installed packages.
            
            This directory will be created in bazel-out and will contain
            all installed Python packages.
            
            Default: "site-packages"
            """,
        ),
        
        "require_hashes": attr.bool(
            default = True,
            doc = """Whether to require hash verification for all packages.
            
            When True, all packages in requirements.txt must include
            --hash=... entries. This ensures reproducible builds and
            protects against supply chain attacks.
            
            Default: True (recommended for production)
            """,
        ),
        
        "env": attr.string_dict(
            doc = """Environment variables to set for the pip process.
            
            Useful for configuring proxy settings, pip options, etc.
            
            Example: {"PIP_INDEX_URL": "https://pypi.example.com/simple"}
            """,
        ),
    },
    doc = """Installs Python packages using pip during the build process.
    
    This rule creates a directory containing installed Python packages
    that can be referenced by other targets (e.g., for bundling into
    installers).
    
    Unlike rules_python's pip_parse (which runs at analysis time), this
    rule runs pip at build time using the target Python interpreter.
    
    Execution Requirements:
        - Network access (to download from PyPI)
        - Local execution only (no remote build)
        - No sandbox (pip requires filesystem access)
    
    Security:
        Set require_hashes=True (default) and include hashes in
        requirements.txt for reproducible, secure builds.
    """,
)
