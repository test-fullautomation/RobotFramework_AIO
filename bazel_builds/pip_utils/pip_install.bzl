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

# =============================================================================
# Relocatable console scripts via bundled wheels ("Solution 2b")
# =============================================================================
#
# BUG BACKGROUND: pip (via distlib) generates console-script launchers
# (e.g. "rst2latex.exe") as PE executables with an embedded, ABSOLUTE
# shebang path pointing at the interpreter used AT BUILD TIME - i.e. the
# python.exe under this action's Bazel execroot
# (".../external/python++http_archive+python_portable_windows/python.exe").
# That build-time interpreter's own site-packages is always the pristine,
# empty root distribution; the actually-installed packages produced by
# THIS action live in a separate declared output (out_dir) that only gets
# merged into the final installation tree later, during Inno Setup
# staging. Consequently, once these launchers are copied to their real
# installed location (e.g. "...\\Python\\Scripts\\rst2latex.exe"), they
# either fail outright (build execroot no longer exists on the target
# machine) or - if run on the build machine itself - fail with
# "ModuleNotFoundError" (interpreter found, but its site-packages is
# empty).
#
# FIX ("Solution 2b" - see documentation/docs/Bazel_Installer_Python_Scripts_Ordner.md
# for the full comparison against the previously implemented "Solution 1",
# custom relocatable wrapper-script generation, which this replaces):
# instead of trying to construct our own relocatable launcher scripts at
# BUILD time (where the real, final installation path is not yet known),
# this rule additionally builds a pre-compiled .whl file for every package
# it installs (via "pip wheel", into a THIRD declared output directory,
# wheels_dir) and bundles those wheels into the installer as plain data
# files (see installer/stage_files.py's "py-wheels" mapping ->
# "Python/_wheels"). A tiny helper script
# (installer/reinstall_console_scripts.py, staged to
# "Python/_wheels/reinstall_console_scripts.py") is then invoked ONCE, at
# the very END of installation, via Inno Setup's [Run] section (see
# installer/installer.iss) - using the REAL, now-installed python.exe at
# its REAL, final location. It reinstalls every bundled wheel with
# "--force-reinstall --no-deps --no-index --find-links=<its own directory>"
# (fully offline, no PyPI access), which makes pip itself regenerate every
# console-script launcher - but this time pip embeds the shebang of the
# ACTUAL, final sys.executable, since that is genuinely the interpreter
# now running pip. This works regardless of where the installer was run,
# with no further build-time knowledge of the eventual installation path
# required.
#
# The package files themselves (out_dir/site-packages) are still installed
# and staged the normal way at BUILD time as before - only the
# console-script launchers get regenerated at INSTALL time; the wheels
# used for that reinstall step are otherwise redundant with out_dir's
# content and are only there to let pip regenerate scripts fully offline
# without needing the original source/sdist again.
# =============================================================================

def _pip_wheel_args_literal(wheel_args):
    """Renders a Python argument list (for `sys.executable -m pip wheel ...`)
    as a Starlark string containing a literal Python list expression, for
    embedding into a generated launcher script's `.format()` template -
    mirrors the pattern already used for the "install" pip_args lists in
    both _pip_install_impl and _pip_install_from_source_impl.
    """
    return "[" + ", ".join([repr(a) for a in wheel_args]) + "]"

def _pip_install_impl(ctx):
    """Implementation function for the pip_install_dir rule.

    Executes pip install with the specified requirements file and target
    Python interpreter. Outputs packages to a directory that can be
    referenced by other targets, a second directory containing the
    console-script launchers (e.g. robotlog2rqm.exe) that pip generates
    for any package declaring console_scripts entry points, and a third
    directory containing pre-built .whl files for every installed package
    (see the "Solution 2b" note above for why - installed via
    installer/reinstall_console_scripts.py at the END of installation, to
    regenerate the console-script launchers with a correct, relocatable
    shebang path).

    Args:
        ctx: The rule context providing access to attributes and actions.

    Returns:
        DefaultInfo provider with the output directories containing
        installed packages (out_dir), their console-script launchers
        (scripts_dir), and their pre-built wheels (wheels_dir).

    Note:
        This action requires network access and must run without sandboxing
        to allow pip to download packages from PyPI.
    """
    # Declare output directories: one for the installed packages
    # (site-packages), one for the console-script launchers pip generates
    # for any package with console_scripts entry points (e.g. robotlog2rqm,
    # robotlog2db, genpackagedoc's CLI, ...), and one for pre-built .whl
    # files (used to regenerate those launchers at install time - see the
    # "Solution 2b" note above). See the "--target vs --prefix" note below
    # for why a second directory is needed at all.
    out = ctx.actions.declare_directory(ctx.attr.out_dir)
    scripts_out = ctx.actions.declare_directory(ctx.attr.scripts_dir)
    wheels_out = ctx.actions.declare_directory(ctx.attr.wheels_dir)


    # Get Python interpreter and runtime files from the external repository
    interpreter = ctx.file.interpreter    # python.exe from portable distribution
    runtime = ctx.files.runtime           # All files from the Python distribution

    # --target vs --prefix:
    # "pip install --target <dir>" installs package FILES into <dir> but
    # deliberately does NOT generate console-script launchers (the .exe/
    # -script.py wrappers for any package's console_scripts entry points) -
    # this is documented, intentional pip behavior, since --target does not
    # simulate a full installation prefix. "pip install --prefix <dir>"
    # instead simulates a complete installation prefix (like a venv's
    # sys.prefix) and DOES generate these launchers, using the standard
    # Windows prefix layout:
    #   <prefix>/Lib/site-packages/...   (equivalent to --target's output)
    #   <prefix>/Scripts/...             (console-script launchers)
    #
    # We install into a temporary prefix directory (not itself a declared
    # Bazel output - just scratch space alongside the two real outputs),
    # then move its two subdirectories into the actual declared outputs.
    # This gives us both pieces (packages AND scripts) from a single pip
    # invocation, instead of needing a second, redundant install pass.
    tmp_prefix = out.path + "__pip_prefix_tmp"

    pip_args = ["-m", "pip", "install"]
    pip_args += ["--requirement", ctx.file.requirements.path]
    pip_args += ["--prefix", tmp_prefix]
    pip_args += ["--no-compile"]
    pip_args += ["--disable-pip-version-check"]
    pip_args += ["--no-input"]

    # Optional: Require hash verification for security
    if ctx.attr.require_hashes:
        pip_args += ["--require-hashes"]

    # Companion "pip wheel" invocation (see the "Solution 2b" note above):
    # builds a pre-compiled .whl file for every package in requirements
    # into wheels_out, WITHOUT installing them anywhere. --no-deps is
    # correct here (not a limitation): "pip wheel -r requirements.txt"
    # already builds a wheel for every entry in the file, including
    # transitive dependencies (they are all explicit, hash-verified
    # entries in a compiled requirements_lock.txt) - so no further
    # dependency resolution is needed or wanted.
    pip_wheel_args = ["-m", "pip", "wheel"]
    pip_wheel_args += ["--requirement", ctx.file.requirements.path]
    pip_wheel_args += ["--wheel-dir", wheels_out.path]
    pip_wheel_args += ["--no-deps"]
    pip_wheel_args += ["--disable-pip-version-check"]
    pip_wheel_args += ["--no-input"]
    if ctx.attr.require_hashes:
        pip_wheel_args += ["--require-hashes"]


    # IMPORTANT - stale output directory content:
    # This action runs with "no-sandbox" (see execution_requirements below),
    # which means Bazel does NOT necessarily delete a pre-existing
    # declare_directory() output directory before re-running this action
    # (unlike sandboxed actions, where every output starts from a guaranteed
    # empty directory each time). If a PREVIOUS build already populated
    # `out.path` with an OLDER resolution of requirements.txt/lock file
    # (e.g. a different pinned version of some package), pip's install mode
    # does NOT perform an uninstall-then-install of the previous version
    # the way a normal site-packages install would - it just extracts the
    # new wheel's files over whatever is already there. Depending on
    # file-name/case overlaps between old and new versions, this can leave
    # a mix of old and new files/dist-info directories behind, causing
    # tools that read package metadata (e.g. importlib.metadata, `pip
    # show`) to report a STALE version even though the requirements file
    # was correctly updated and re-resolved.
    #
    # Fix: explicitly wipe `out.path`, `scripts_out.path`, AND the
    # temporary prefix directory before invoking pip, so every build of
    # this target always starts from guaranteed-empty directories,
    # regardless of whether Bazel happened to reuse stale ones.
    launcher = ctx.actions.declare_file(ctx.attr.name + "_pip_install_launcher.py")
    pip_args_literal = "[" + ", ".join([repr(a) for a in pip_args]) + "]"
    pip_wheel_args_literal = _pip_wheel_args_literal(pip_wheel_args)
    ctx.actions.write(
        output = launcher,
        content = """\
import os
import shutil
import subprocess
import sys

out_dir = r"{out_path}"
scripts_dir = r"{scripts_path}"
wheels_dir = r"{wheels_path}"
prefix_dir = r"{prefix_path}"

shutil.rmtree(out_dir, ignore_errors=True)
shutil.rmtree(scripts_dir, ignore_errors=True)
shutil.rmtree(wheels_dir, ignore_errors=True)
shutil.rmtree(prefix_dir, ignore_errors=True)
os.makedirs(wheels_dir, exist_ok=True)

# Bootstrap pip if this interpreter doesn't have it yet. The
# python-build-standalone "install_only" distribution used by this
# project does NOT bundle pip (unlike a typical desktop CPython install),
# but its stdlib DOES include the "ensurepip" module with a bundled pip
# wheel (Lib/ensurepip/_bundled/*.whl) - so this works fully offline, with
# no PyPI/network access needed, and is a cheap no-op if pip is already
# present (e.g. a previously-bootstrapped, reused output_base).
try:
    import pip  # noqa: F401
except ImportError:
    subprocess.check_call([sys.executable, "-m", "ensurepip", "--default-pip"])

cmd = [sys.executable] + {pip_args_literal}
rc = subprocess.call(cmd)
if rc != 0:
    raise SystemExit(rc)

# See the "Solution 2b" note above pip_install.bzl's top: build a
# pre-compiled .whl for every installed package into wheels_dir, bundled
# into the installer and reinstalled at the END of installation (see
# installer/reinstall_console_scripts.py) to regenerate console-script
# launchers with a correct, relocatable shebang path.
#
# Re-check pip's importability here: if requirements(_lock).txt pins its
# own "pip==..." entry (as e.g. py_modules_set_1's requirements do), the
# install step above can end up UNINSTALLING the base interpreter's own
# ensurepip-provided pip (pip sees a newer/different pinned version and
# replaces the "existing installation" it finds via sys.path - which is
# the base interpreter's real site-packages, NOT just tmp_prefix) - and
# since this happens WHILE that very pip process is still running (pip
# uninstalling itself mid-execution), the result can be a broken-but-
# still-importable state on disk (some files removed, others not) that a
# simple "try: import pip" check does NOT reliably detect (a bare
# "import pip" can still succeed even though "python -m pip" itself then
# fails with "No module named pip", since "-m" exercises more of pip's
# internals than a bare top-level import does). Fix: force ensurepip to
# unconditionally reinstall pip here ("--upgrade", not "--default-pip" -
# the latter is a no-op if pip already appears present, which is exactly
# the unreliable state being worked around), fully offline, regardless of
# whether pip already looks importable.
subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])

cmd = [sys.executable] + {pip_wheel_args_literal}
rc = subprocess.call(cmd)
if rc != 0:
    raise SystemExit(rc)

# Move the two subdirectories pip created under the temporary prefix into
# the two REAL declared outputs. Both declare_directory() outputs must
# exist (even if empty) after this action runs, so fall back to an empty
# mkdir if pip happened not to produce one (e.g. no console_scripts
# entry points anywhere in this requirements file -> no Scripts dir).
site_packages_src = os.path.join(prefix_dir, "Lib", "site-packages")
if os.path.isdir(site_packages_src):
    shutil.move(site_packages_src, out_dir)
else:
    os.makedirs(out_dir, exist_ok=True)

scripts_src = os.path.join(prefix_dir, "Scripts")
if os.path.isdir(scripts_src):
    shutil.move(scripts_src, scripts_dir)
else:
    os.makedirs(scripts_dir, exist_ok=True)

shutil.rmtree(prefix_dir, ignore_errors=True)
""".format(
            out_path = out.path,
            scripts_path = scripts_out.path,
            wheels_path = wheels_out.path,
            prefix_path = tmp_prefix,
            pip_args_literal = pip_args_literal,
            pip_wheel_args_literal = pip_wheel_args_literal,
        ),
    )


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
        arguments = [launcher.path],
        inputs = depset([launcher, ctx.file.requirements] + runtime),
        outputs = [out, scripts_out, wheels_out],
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

    return [DefaultInfo(files = depset([out, scripts_out, wheels_out]))]


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
        "scripts_dir": attr.string(
            default = "py-scripts",
            doc = """Name of the output directory for console-script launchers.

            pip generates these (e.g. robotlog2rqm.exe, robotlog2rqm-script.py)
            for any installed package declaring console_scripts entry points,
            when installed via "pip install --prefix" (used internally by
            this rule instead of "--target", specifically to obtain these
            launchers - see _pip_install_impl for details).

            NOTE: These launchers have a build-time-only, non-relocatable
            shebang path (see the "Solution 2b" note near the top of this
            file) and are effectively superseded by an install-time
            reinstall from wheels_dir's bundled wheels - they are still
            produced/staged (harmless) but should not be relied upon
            directly.

            Default: "py-scripts". Must be changed (like out_dir) if two
            pip_install_dir/pip_install_from_source targets exist in the
            SAME Bazel package (e.g. python-extensions-collection's
            "..._deps" target), to avoid a "conflicting actions" error.
            """,
        ),
        "wheels_dir": attr.string(
            default = "py-wheels",
            doc = """Name of the output directory for pre-built .whl files.

            One .whl is built (via "pip wheel", --no-deps) for every
            package in requirements/requirements_lock.txt, WITHOUT
            installing it anywhere. These wheels are bundled into the
            installer (see installer/stage_files.py's "py-wheels" mapping)
            and reinstalled once, at the END of installation, by
            installer/reinstall_console_scripts.py - see the "Solution 2b"
            note near the top of this file for the full rationale (fixes
            console-script launchers' non-relocatable, build-time-only
            shebang path).

            Default: "py-wheels". Must be changed (like out_dir/scripts_dir)
            if two pip_install_dir/pip_install_from_source targets exist in
            the SAME Bazel package, to avoid a "conflicting actions" error.
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
        DefaultInfo provider with the output directories containing the
        installed package (out_dir), its console-script launchers
        (scripts_dir), and its pre-built wheel (wheels_dir), if any.
    """
    out = ctx.actions.declare_directory(ctx.attr.out_dir)
    scripts_out = ctx.actions.declare_directory(ctx.attr.scripts_dir)
    wheels_out = ctx.actions.declare_directory(ctx.attr.wheels_dir)

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

    # See _pip_install_impl for the rationale of using "--prefix" instead of
    # "--target": only --prefix makes pip generate console-script launchers
    # (e.g. genpackagedoc.exe) for the source tree's console_scripts entry
    # points, into a standard <prefix>/Lib/site-packages + <prefix>/Scripts
    # layout, which we then split into our two REAL declared outputs below.
    tmp_prefix = out.path + "__pip_prefix_tmp"

    pip_args = ["-m", "pip", "install"]
    pip_args += ["--prefix", tmp_prefix]
    pip_args += ["--no-compile"]
    pip_args += ["--disable-pip-version-check"]
    pip_args += ["--no-input"]
    pip_args += ["--no-deps"]               # transitive deps come from deps_dir instead
    pip_args += ["--no-build-isolation"]    # use the interpreter's own env, no fresh venv
    pip_args += [source_dir]                # install FROM this local directory, not PyPI

    # Companion "pip wheel" invocation (see the "Solution 2b" note near the
    # top of this file): builds a pre-compiled .whl for this source tree
    # into wheels_out, WITHOUT installing it anywhere. Same --no-deps/
    # --no-build-isolation reasoning as pip_args above.
    pip_wheel_args = ["-m", "pip", "wheel"]
    pip_wheel_args += ["--wheel-dir", wheels_out.path]
    pip_wheel_args += ["--no-deps"]
    pip_wheel_args += ["--disable-pip-version-check"]
    pip_wheel_args += ["--no-input"]
    pip_wheel_args += ["--no-build-isolation"]
    pip_wheel_args += [source_dir]

    # inputs: full source tree + runtime + (optionally) the pre-installed
    # transitive dependency directory, so the build backend can import them
    # (e.g. setuptools itself, or a build-time dependency of the package).
    inputs = depset(source_files + runtime + ctx.files.deps_dir)

    env = dict(ctx.attr.env)

    deps_path_rel = None
    if ctx.files.deps_dir:
        deps_path_rel = ctx.files.deps_dir[0].path

    if deps_path_rel:
        # IMPORTANT: We do NOT set PYTHONPATH directly here to
        # ctx.files.deps_dir[0].path (a path RELATIVE to the Bazel
        # execution root). That relative path only resolves correctly as
        # long as the process importing from it has the execution root as
        # its current working directory - which is true for THIS action's
        # own process, but NOT for the pip-internal subprocess that
        # actually needs it:
        #
        # pip's build-backend metadata/wheel hooks (prepare_metadata_for_
        # build_wheel / build_wheel, invoked even with --no-build-isolation)
        # are executed by pyproject_hooks in a SEPARATE subprocess whose
        # working directory pip explicitly sets to the unpacked SOURCE
        # directory (not the execution root) - while still inheriting our
        # PYTHONPATH value as a plain string. Since Python resolves
        # relative sys.path/PYTHONPATH entries against the process's
        # CURRENT working directory at import time, a relative PYTHONPATH
        # that was valid from the execution root silently resolves to a
        # nonexistent path from within the source directory - causing
        # e.g. "ModuleNotFoundError: No module named 'setuptools'" even
        # though setuptools is physically present in deps_dir's output.
        # (Confirmed by reproducing the exact same pip invocation manually
        # outside Bazel: it only succeeds when PYTHONPATH is an ABSOLUTE
        # path - a relative one reproduces the identical import error.)
        #
        # Fix: generate a tiny Python launcher script that converts the
        # relative deps_dir path to an ABSOLUTE one via os.path.abspath()
        # while the launcher's own cwd is STILL the execution root (i.e.
        # before pip gets a chance to spawn its cwd-changed subprocess),
        # then re-execs "python -m pip install ..." with that now-absolute
        # PYTHONPATH. This makes the fix robust regardless of whatever
        # working directory pip's internal hook subprocess happens to use.
        launcher = ctx.actions.declare_file(ctx.attr.name + "_pip_install_from_source_launcher.py")

        # Starlark's string.format() has no Python "!r"/repr() equivalent,
        # so the pip argument list is rendered into a Python list-literal
        # string manually here (each argument individually quoted).
        pip_args_literal = "[" + ", ".join([repr(a) for a in pip_args]) + "]"
        pip_wheel_args_literal = _pip_wheel_args_literal(pip_wheel_args)

        ctx.actions.write(
            output = launcher,
            content = """\
import os
import shutil
import subprocess
import sys

# See _pip_install_impl for why this cleanup is necessary: this action
# runs with "no-sandbox", so Bazel does not guarantee out.path starts
# empty on every re-execution. Without this, a package version bump
# (e.g. a new git tag) can leave stale files/dist-info from a PREVIOUS
# build's different version behind, causing tools that read package
# metadata to report a stale version despite a successful, "correct"
# build.
out_dir = r"{out_path}"
scripts_dir = r"{scripts_path}"
wheels_dir = r"{wheels_path}"
prefix_dir = r"{prefix_path}"
shutil.rmtree(out_dir, ignore_errors=True)
shutil.rmtree(scripts_dir, ignore_errors=True)
shutil.rmtree(wheels_dir, ignore_errors=True)
shutil.rmtree(prefix_dir, ignore_errors=True)
os.makedirs(wheels_dir, exist_ok=True)

# Resolved while cwd is still the Bazel execution root (see pip_install.bzl
# _pip_install_from_source_impl for why this must be absolute).
deps_dir_abs = os.path.abspath(r"{deps_path_rel}")

env = dict(os.environ)
existing = env.get("PYTHONPATH")
env["PYTHONPATH"] = deps_dir_abs if not existing else (deps_dir_abs + os.pathsep + existing)

# See _pip_install_impl's launcher for why this bootstrap is necessary and
# safe to run unconditionally (offline, idempotent).
try:
    import pip  # noqa: F401
except ImportError:
    subprocess.check_call([sys.executable, "-m", "ensurepip", "--default-pip"])

cmd = [sys.executable] + {pip_args_literal}
rc = subprocess.call(cmd, env=env)
if rc != 0:
    raise SystemExit(rc)

# See the "Solution 2b" note near the top of pip_install.bzl: build a
# pre-compiled .whl for this source tree into wheels_dir, bundled into the
# installer and reinstalled at the END of installation (see
# installer/reinstall_console_scripts.py) to regenerate console-script
# launchers with a correct, relocatable shebang path. Same PYTHONPATH as
# the install step above (--no-build-isolation needs setuptools importable).
#
# Re-check pip's importability here - see the equivalent comment in
# _pip_install_impl's launcher for why an unconditional "ensurepip
# --upgrade" (not a "try: import pip" check) is necessary here (the
# install step above can leave the base interpreter's own pip in a
# broken-but-still-importable state even though it succeeded).
subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])

cmd = [sys.executable] + {pip_wheel_args_literal}
rc = subprocess.call(cmd, env=env)
if rc != 0:
    raise SystemExit(rc)

# Move the two subdirectories pip created under the temporary prefix into
# the two REAL declared outputs (see _pip_install_impl for the same
# pattern/rationale).
site_packages_src = os.path.join(prefix_dir, "Lib", "site-packages")
if os.path.isdir(site_packages_src):
    shutil.move(site_packages_src, out_dir)
else:
    os.makedirs(out_dir, exist_ok=True)

scripts_src = os.path.join(prefix_dir, "Scripts")
if os.path.isdir(scripts_src):
    shutil.move(scripts_src, scripts_dir)
else:
    os.makedirs(scripts_dir, exist_ok=True)

shutil.rmtree(prefix_dir, ignore_errors=True)
""".format(
                out_path = out.path,
                scripts_path = scripts_out.path,
                wheels_path = wheels_out.path,
                prefix_path = tmp_prefix,
                deps_path_rel = deps_path_rel,
                pip_args_literal = pip_args_literal,
                pip_wheel_args_literal = pip_wheel_args_literal,
            ),
        )

        ctx.actions.run(
            executable = interpreter,
            arguments = [launcher.path],
            inputs = depset([launcher], transitive = [inputs]),
            outputs = [out, scripts_out, wheels_out],
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
    else:
        # No deps_dir given - no PYTHONPATH/cwd concerns, but still need the
        # same stale-output-directory cleanup as the branch above (see the
        # comment there and in _pip_install_impl for why this is necessary
        # with "no-sandbox" actions).
        launcher = ctx.actions.declare_file(ctx.attr.name + "_pip_install_from_source_launcher.py")
        pip_args_literal = "[" + ", ".join([repr(a) for a in pip_args]) + "]"
        pip_wheel_args_literal = _pip_wheel_args_literal(pip_wheel_args)
        ctx.actions.write(
            output = launcher,
            content = """\
import os
import shutil
import subprocess
import sys

out_dir = r"{out_path}"
scripts_dir = r"{scripts_path}"
wheels_dir = r"{wheels_path}"
prefix_dir = r"{prefix_path}"
shutil.rmtree(out_dir, ignore_errors=True)
shutil.rmtree(scripts_dir, ignore_errors=True)
shutil.rmtree(wheels_dir, ignore_errors=True)
shutil.rmtree(prefix_dir, ignore_errors=True)
os.makedirs(wheels_dir, exist_ok=True)

# See _pip_install_impl's launcher for why this bootstrap is necessary and
# safe to run unconditionally (offline, idempotent).
try:
    import pip  # noqa: F401
except ImportError:
    subprocess.check_call([sys.executable, "-m", "ensurepip", "--default-pip"])

cmd = [sys.executable] + {pip_args_literal}
rc = subprocess.call(cmd)
if rc != 0:
    raise SystemExit(rc)

# See the "Solution 2b" note near the top of pip_install.bzl: build a
# pre-compiled .whl for this source tree into wheels_dir - see the
# deps_dir branch above for the full rationale.
#
# Re-check pip's importability here - see the equivalent comment in
# _pip_install_impl's launcher for why this second, unconditional
# bootstrap is necessary.
subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])

cmd = [sys.executable] + {pip_wheel_args_literal}
rc = subprocess.call(cmd)
if rc != 0:
    raise SystemExit(rc)

site_packages_src = os.path.join(prefix_dir, "Lib", "site-packages")
if os.path.isdir(site_packages_src):
    shutil.move(site_packages_src, out_dir)
else:
    os.makedirs(out_dir, exist_ok=True)

scripts_src = os.path.join(prefix_dir, "Scripts")
if os.path.isdir(scripts_src):
    shutil.move(scripts_src, scripts_dir)
else:
    os.makedirs(scripts_dir, exist_ok=True)

shutil.rmtree(prefix_dir, ignore_errors=True)
""".format(
                out_path = out.path,
                scripts_path = scripts_out.path,
                wheels_path = wheels_out.path,
                prefix_path = tmp_prefix,
                pip_args_literal = pip_args_literal,
                pip_wheel_args_literal = pip_wheel_args_literal,
            ),
        )

        ctx.actions.run(
            executable = interpreter,
            arguments = [launcher.path],
            inputs = depset([launcher], transitive = [inputs]),
            outputs = [out, scripts_out, wheels_out],
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

    return [DefaultInfo(files = depset([out, scripts_out, wheels_out]))]


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
        "scripts_dir": attr.string(
            default = "py-scripts",
            doc = """Name of the output directory for console-script launchers.

            Same rationale/mechanism as pip_install_dir's "scripts_dir" -
            see pip_install_dir's doc and _pip_install_from_source_impl for
            details. Must be changed if two targets exist in the SAME
            Bazel package (see out_dir's doc for the same requirement).
            """,
        ),
        "wheels_dir": attr.string(
            default = "py-wheels",
            doc = """Name of the output directory for the pre-built .whl file.

            Same rationale/mechanism as pip_install_dir's "wheels_dir" -
            see pip_install_dir's doc and the "Solution 2b" note near the
            top of this file for details. Must be changed if two targets
            exist in the SAME Bazel package (see out_dir's doc for the
            same requirement).
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

