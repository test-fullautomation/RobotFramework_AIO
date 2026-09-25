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
# Relocatable console-script wrapper generation ("Solution 1")
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
# FIX: after pip has finished installing (and its own launchers have been
# moved into scripts_dir), delete pip's non-relocatable launchers and
# regenerate our OWN launchers for the same console_scripts entry points,
# reading them via importlib.metadata against the just-installed out_dir.
# Each entry point becomes a pair of files:
#   <name>-script.py  - a tiny Python script importing the target module
#                        and invoking the entry point's callable.
#   <name>.cmd        - a batch-file wrapper that locates ITS OWN
#                        directory via "%~dp0" (always correct, no matter
#                        where the Scripts folder is finally copied to)
#                        and invokes "..\\python.exe" (one directory up,
#                        matching both the temporary pip --prefix layout
#                        used here AND the final installed layout, where
#                        Python/Scripts and Python/python.exe are siblings)
#                        against the paired *-script.py.
#
# This keeps the whole operation fully offline/hermetic (no PyPI access,
# no extra Bazel outputs) and produces launchers that work correctly
# regardless of where the final "Scripts" directory ends up on disk -
# at the cost of console scripts becoming "<name>.cmd" instead of
# "<name>.exe" (transparent for any caller that invokes them without an
# explicit extension, e.g. via PATH, since Windows' PATHEXT resolves
# ".CMD" the same way; callers hardcoding the ".exe" extension need to be
# updated to drop it, or to call "<name>" without an extension instead).
# =============================================================================

_WRAPPER_GENERATION_SNIPPET = """\
# --- BEGIN relocatable console-script wrapper generation (Solution 1) ---
try:
    from importlib.metadata import entry_points as _entry_points
except ImportError:
    from importlib_metadata import entry_points as _entry_points

sys.path.insert(0, out_dir)
try:
    _eps = _entry_points(group="console_scripts")
except TypeError:
    # Python < 3.10: entry_points() returns a SelectableGroups-like mapping
    # instead of accepting a group= keyword argument directly.
    _eps = _entry_points().get("console_scripts", [])

# Wipe whatever pip itself generated into scripts_dir (non-relocatable
# .exe/-script.py/.exe.manifest launchers with a hardcoded, build-time-only
# shebang path) - fully replaced below with our own relocatable .cmd +
# *-script.py pair per console_scripts entry point.
shutil.rmtree(scripts_dir, ignore_errors=True)
os.makedirs(scripts_dir, exist_ok=True)

for _ep in _eps:
    _name = _ep.name
    _module, _, _attr = _ep.value.partition(":")
    _attr_chain = _attr.split(".") if _attr else []

    _py_path = os.path.join(scripts_dir, _name + "-script.py")
    with open(_py_path, "w", encoding="utf-8") as _f:
        _f.write("import sys\\n")
        _f.write("import " + _module + " as _mod\\n")
        _f.write("_obj = _mod\\n")
        for _part in _attr_chain:
            _f.write("_obj = getattr(_obj, " + repr(_part) + ")\\n")
        _f.write("sys.exit(_obj())\\n")

    _cmd_path = os.path.join(scripts_dir, _name + ".cmd")
    with open(_cmd_path, "w", encoding="utf-8") as _f:
        _f.write("@echo off\\r\\n")
        _f.write('"%~dp0..\\\\python.exe" "%~dp0' + _name + '-script.py" %*\\r\\n')
# --- END relocatable console-script wrapper generation (Solution 1) ---
"""

def _pip_install_impl(ctx):
    """Implementation function for the pip_install_dir rule.

    Executes pip install with the specified requirements file and target
    Python interpreter. Outputs packages to a directory that can be
    referenced by other targets, AND a second directory containing the
    console-script launchers (e.g. robotlog2rqm.exe) that pip generates
    for any package declaring console_scripts entry points.

    Args:
        ctx: The rule context providing access to attributes and actions.

    Returns:
        DefaultInfo provider with the output directories containing
        installed packages (out_dir) and their console-script launchers
        (scripts_dir).

    Note:
        This action requires network access and must run without sandboxing
        to allow pip to download packages from PyPI.
    """
    # Declare output directories: one for the installed packages
    # (site-packages), one for the console-script launchers pip generates
    # for any package with console_scripts entry points (e.g. robotlog2rqm,
    # robotlog2db, genpackagedoc's CLI, ...). See the "--target vs --prefix"
    # note below for why a second directory is needed at all.
    out = ctx.actions.declare_directory(ctx.attr.out_dir)
    scripts_out = ctx.actions.declare_directory(ctx.attr.scripts_dir)

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
    ctx.actions.write(
        output = launcher,
        content = """\
import os
import shutil
import subprocess
import sys

out_dir = r"{out_path}"
scripts_dir = r"{scripts_path}"
prefix_dir = r"{prefix_path}"

shutil.rmtree(out_dir, ignore_errors=True)
shutil.rmtree(scripts_dir, ignore_errors=True)
shutil.rmtree(prefix_dir, ignore_errors=True)

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

{wrapper_generation_snippet}

shutil.rmtree(prefix_dir, ignore_errors=True)
""".format(
            out_path = out.path,
            scripts_path = scripts_out.path,
            prefix_path = tmp_prefix,
            pip_args_literal = pip_args_literal,
            wrapper_generation_snippet = _WRAPPER_GENERATION_SNIPPET,
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
        outputs = [out, scripts_out],
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

    return [DefaultInfo(files = depset([out, scripts_out]))]


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

            Default: "py-scripts". Must be changed (like out_dir) if two
            pip_install_dir/pip_install_from_source targets exist in the
            SAME Bazel package (e.g. python-extensions-collection's
            "..._deps" target), to avoid a "conflicting actions" error.
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
        installed package (out_dir) and its console-script launchers
        (scripts_dir), if any.
    """
    out = ctx.actions.declare_directory(ctx.attr.out_dir)
    scripts_out = ctx.actions.declare_directory(ctx.attr.scripts_dir)

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
prefix_dir = r"{prefix_path}"
shutil.rmtree(out_dir, ignore_errors=True)
shutil.rmtree(scripts_dir, ignore_errors=True)
shutil.rmtree(prefix_dir, ignore_errors=True)

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

{wrapper_generation_snippet}

shutil.rmtree(prefix_dir, ignore_errors=True)
""".format(
                out_path = out.path,
                scripts_path = scripts_out.path,
                prefix_path = tmp_prefix,
                deps_path_rel = deps_path_rel,
                pip_args_literal = pip_args_literal,
                wrapper_generation_snippet = _WRAPPER_GENERATION_SNIPPET,
            ),
        )

        ctx.actions.run(
            executable = interpreter,
            arguments = [launcher.path],
            inputs = depset([launcher], transitive = [inputs]),
            outputs = [out, scripts_out],
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
        ctx.actions.write(
            output = launcher,
            content = """\
import os
import shutil
import subprocess
import sys

out_dir = r"{out_path}"
scripts_dir = r"{scripts_path}"
prefix_dir = r"{prefix_path}"
shutil.rmtree(out_dir, ignore_errors=True)
shutil.rmtree(scripts_dir, ignore_errors=True)
shutil.rmtree(prefix_dir, ignore_errors=True)

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

{wrapper_generation_snippet}

shutil.rmtree(prefix_dir, ignore_errors=True)
""".format(
                out_path = out.path,
                scripts_path = scripts_out.path,
                prefix_path = tmp_prefix,
                pip_args_literal = pip_args_literal,
                wrapper_generation_snippet = _WRAPPER_GENERATION_SNIPPET,
            ),
        )

        ctx.actions.run(
            executable = interpreter,
            arguments = [launcher.path],
            inputs = depset([launcher], transitive = [inputs]),
            outputs = [out, scripts_out],
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

    return [DefaultInfo(files = depset([out, scripts_out]))]


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
