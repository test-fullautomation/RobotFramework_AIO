# =============================================================================
# pip_install.bzl - Custom Bazel Rules for pip Package Installation
# =============================================================================
#
# SINGLE SOURCE OF TRUTH for these rules (module "pip_utils"). Every other
# component in this repository loads this file via:
#
#   load("@pip_utils//:pip_install.bzl", "pip_install_dir")
#   # or, when needed:
#   load("@pip_utils//:pip_install.bzl", "pip_install_dir", "pip_install_from_source")
#
# and declares in its own MODULE.bazel:
#
#   bazel_dep(name = "pip_utils", version = "0.1.0")
#   local_path_override(module_name = "pip_utils", path = "../pip_utils")
#
# This replaces the previous approach of keeping a verbatim COPY of this file
# in every single component directory (required because Bzlmod isolates each
# module's dependency graph and does not support loading a plain .bzl file
# across module boundaries without an explicit bazel_dep). Centralizing the
# file here means bugfixes/changes to these rules now only need to be made
# ONCE.
#
# This file defines TWO custom Bazel rules that install Python packages
# during the build process (at action-execution time, not analysis time),
# using the target Python interpreter (from python_portable_windows):
#
#   1. pip_install_dir          - installs packages FROM PyPI, using a
#                                  requirements_lock.txt with --require-hashes.
#                                  Used by every PyPI-based component in
#                                  this repo.
#
#   2. pip_install_from_source   - installs a package FROM A LOCAL SOURCE TREE
#                                  (e.g. fetched via git_repository from an
#                                  internal, non-PyPI Git server) instead of
#                                  from PyPI. Used by
#                                  robotframework-qconnect-dlt, whose source
#                                  is only available on Bosch's internal
#                                  Bitbucket server, not on PyPI.
#
# Usage (PyPI):
#   load("@pip_utils//:pip_install.bzl", "pip_install_dir")
#
#   pip_install_dir(
#       name = "...",
#       requirements = "requirements_lock.txt",
#       interpreter = "@python//:python_interpreter",
#       runtime = "@python//:python_runtime",
#   )
#
# Usage (internal Git source):
#   load("@pip_utils//:pip_install.bzl", "pip_install_from_source")
#
#   pip_install_from_source(
#       name = "...",
#       source = "@some_git_repo//:src",
#       interpreter = "@python//:python_interpreter",
#       runtime = "@python//:python_runtime",
#       deps_dir = ":some_pip_install_dir_target",  # optional
#   )
#
# =============================================================================

"""
Custom Bazel rules for installing Python packages via pip.

These rules run pip install during the build action phase, allowing packages
to be installed using the target Python interpreter and bundled into
installers. One rule installs from PyPI (requirements_lock.txt), the other
installs a local source tree (e.g. fetched from an internal Git server).
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
    # pip subprocess runs with an empty/minimal environment.
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
# Rule Definition: pip_install_dir (PyPI, hash-verified)
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
            """,
        ),
        "interpreter": attr.label(
            allow_single_file = True,
            mandatory = True,
            doc = """Python interpreter executable to use for pip.

            This should point to python.exe from the target Python distribution.
            Using the target interpreter ensures packages are compatible.

            Example: "@python//:python_interpreter"
            """,
        ),
        "runtime": attr.label(
            mandatory = True,
            doc = """Complete Python runtime (all distribution files).

            Pip needs access to the full Python installation including
            standard library, DLLs, etc. to function correctly.

            Example: "@python//:python_runtime"
            """,
        ),

        # -------------------------------------------------------------------------
        # Optional Attributes
        # -------------------------------------------------------------------------
        "out_dir": attr.string(
            default = "site-packages",
            doc = """Name of the output directory for installed packages.

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
            """,
        ),
    },
    doc = """Installs Python packages FROM PyPI using pip during the build process.

    This rule creates a directory containing installed Python packages
    that can be referenced by other targets (e.g., for bundling into
    installers). Requires a requirements_lock.txt with --hash=... entries
    for every package (see require_hashes).
    """,
)


def _pip_install_from_source_impl(ctx):
    """Implementation function for the pip_install_from_source rule.

    Installs a Python package directly from a local source tree (typically
    fetched via git_repository from an internal, non-PyPI server) instead
    of from a PyPI index. Unlike pip_install_dir, this does NOT use
    --require-hashes (source trees have no PyPI-style hash to verify
    against) and passes --no-deps + --no-build-isolation so that:

      - transitive PyPI dependencies are NOT re-resolved/re-downloaded here
        (they are expected to already be installed separately via a normal
        pip_install_dir target and merged in via PYTHONPATH, see deps_dir);
      - the build backend (setuptools/wheel/etc.) does not attempt to
        create a fresh, network-isolated build environment and fetch its
        own build-time requirements from PyPI, which would defeat the
        purpose of building from an internal-only source tree in an
        environment where broad PyPI access may be restricted.

    Args:
        ctx: The rule context providing access to attributes and actions.

    Returns:
        DefaultInfo provider with the output directory containing the
        installed package.
    """
    out = ctx.actions.declare_directory(ctx.attr.out_dir)

    interpreter = ctx.file.interpreter
    runtime = ctx.files.runtime
    source_files = ctx.files.source

    # The source files are a filegroup (e.g. "@robotframework_qconnect_dlt_src//:src").
    # pip install accepts a directory containing setup.py/pyproject.toml as
    # its "package" argument - derive that directory from any one of the
    # source files' paths (they all share the same root).
    if not source_files:
        fail("pip_install_from_source: 'source' attribute produced no files.")
    source_dir = source_files[0].dirname

    args = ctx.actions.args()
    args.add("-m").add("pip").add("install")
    args.add("--target", out.path)
    args.add("--no-compile")
    args.add("--disable-pip-version-check")
    args.add("--no-input")
    args.add("--no-deps")               # transitive deps come from deps_dir instead
    args.add("--no-build-isolation")    # use the interpreter's own env, no fresh venv
    args.add(source_dir)                # install FROM this local directory, not PyPI

    # inputs: full source tree + runtime + (optionally) the pre-installed
    # transitive dependency directory, so the build backend can import them
    # (e.g. setuptools itself, or a build-time dependency of the package).
    inputs = depset(source_files + runtime + ctx.files.deps_dir)

    env = dict(ctx.attr.env)
    if ctx.files.deps_dir:
        # Make transitively-installed PyPI packages (from a sibling
        # pip_install_dir target) importable during the build/install step,
        # e.g. for packages whose setup.py imports a helper dependency.
        deps_path = ctx.files.deps_dir[0].path
        env["PYTHONPATH"] = deps_path

    ctx.actions.run(
        executable = interpreter,
        arguments = [args],
        inputs = inputs,
        outputs = [out],
        env = env,
        use_default_shell_env = True,
        execution_requirements = {
            "requires-network": "",  # pip still needs network for its own bookkeeping
            "no-sandbox": "",
            "no-remote": "",
        },
        mnemonic = "PipInstallFromSource",
        progress_message = "pip install (from source) -> %s" % out.short_path,
    )

    return [DefaultInfo(files = depset([out]))]


# =============================================================================
# Rule Definition: pip_install_from_source (internal Git source, no hashes)
# =============================================================================

pip_install_from_source = rule(
    implementation = _pip_install_from_source_impl,
    attrs = {
        "source": attr.label(
            mandatory = True,
            doc = """Filegroup (or similar) containing the package's source tree.

            The source tree must contain a setup.py or pyproject.toml at its
            root. Typically points at a filegroup exposed by a git_repository
            fetching an internal (non-PyPI) repository, e.g.:

                "@robotframework_qconnect_dlt_src//:src"
            """,
        ),
        "interpreter": attr.label(
            allow_single_file = True,
            mandatory = True,
            doc = """Python interpreter executable to use for pip.

            Example: "@python//:python_interpreter"
            """,
        ),
        "runtime": attr.label(
            mandatory = True,
            doc = """Complete Python runtime (all distribution files).

            Example: "@python//:python_runtime"
            """,
        ),
        "deps_dir": attr.label(
            allow_files = True,
            doc = """Optional: a pip_install_dir target providing this
            package's transitive PyPI dependencies (installed separately,
            WITH hash verification, from requirements_lock.txt).

            Passed to pip via --no-deps + PYTHONPATH instead of letting pip
            resolve dependencies itself from the source tree's metadata,
            since PyPI dependency resolution should stay confined to the
            hash-verified pip_install_dir path used by every other
            component in this repository.
            """,
        ),
        "out_dir": attr.string(
            default = "site-packages",
            doc = """Name of the output directory for the installed package.

            Deliberately defaults to "site-packages" (same as pip_install_dir)
            so that components/installer/stage_files.py's existing
            site-packages merge logic (dirs_exist_ok=True copytree) applies
            here without any changes.
            """,
        ),
        "env": attr.string_dict(
            doc = """Additional environment variables to set for the pip process.""",
        ),
    },
    doc = """Installs a Python package FROM A LOCAL SOURCE TREE using pip.

    Unlike pip_install_dir (which installs hash-verified packages from a
    PyPI requirements_lock.txt), this rule builds/installs a package
    directly from source - typically source fetched via git_repository
    from an internal, non-PyPI Git server (e.g. Bosch's internal Bitbucket).

    No hash verification is performed (source trees have no PyPI-style
    hashes to check). Transitive PyPI dependencies should instead be
    declared in a normal requirements.txt/requirements_lock.txt and
    installed via a sibling pip_install_dir target, referenced here via
    deps_dir.
    """,
)
