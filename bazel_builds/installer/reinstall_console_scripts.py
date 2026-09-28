# =============================================================================
# reinstall_console_scripts.py - Regenerate relocatable console-script launchers
# =============================================================================
#
# WHAT / WHY (see pip_utils/pip_install.bzl's "Solution 2b" note for the
# full background):
#
# pip (via distlib) generates console-script launchers (e.g.
# "rst2latex.exe") as PE executables with an embedded, ABSOLUTE shebang
# path pointing at whatever python.exe was used to run pip AT THE TIME the
# launcher was generated. When those launchers are generated during the
# Bazel BUILD (as pip_install_dir/pip_install_from_source normally do,
# using "pip install --prefix"), the shebang ends up pointing at the
# BUILD-time interpreter under the Bazel execroot - not at wherever this
# installer eventually gets installed on an end-user's machine. Running
# such a launcher from its real, installed location then either fails
# outright (the build execroot no longer exists) or - on the build machine
# itself - fails with "ModuleNotFoundError" (the build-time interpreter's
# own site-packages is the pristine, empty root distribution; the actually
# installed packages live in a completely separate location).
#
# FIX: pip_install.bzl additionally builds a pre-compiled .whl file for
# every installed package (see its "wheels_dir" output), which is bundled
# into this installer as a plain data file under "Python/_wheels/" (see
# installer/stage_files.py's "py-wheels" mapping). THIS script is bundled
# alongside those wheels (same directory) and run EXACTLY ONCE, at the
# very END of installation, via Inno Setup's [Run] section (see
# installer.iss) - using the python.exe that was JUST installed, at its
# REAL, final location. It reinstalls every bundled wheel with
# "--force-reinstall --no-deps --no-index --find-links=<this script's own
# directory>" (fully offline, no PyPI/network access whatsoever), which
# makes pip itself regenerate every console-script launcher - but this
# time pip embeds the shebang of the ACTUAL, final sys.executable, since
# that is genuinely the interpreter now running pip. This works correctly
# regardless of where the installer was run, with zero build-time
# knowledge of the eventual installation path required.
#
# --no-deps is safe (not a limitation): every wheel needed - including
# every transitive dependency - is already present in this same directory
# (pip_install_dir/pip_install_from_source builds one for every package in
# requirements_lock.txt / every source tree, respectively), so no further
# dependency resolution against any index is required or even possible
# (--no-index).
#
# --force-reinstall is necessary because the package FILES themselves
# (site-packages) were already staged directly from the Bazel build
# (unrelated to this script) and would otherwise look "already installed,
# same version" to pip, causing it to skip regenerating the launchers
# entirely.
#
# This script deliberately has NO command-line arguments: it locates the
# directory it itself lives in (Path(__file__).parent) to find both the
# wheels AND the correct --find-links location, and relies on
# sys.executable to be the CORRECT, final python.exe (guaranteed by how
# installer.iss's [Run] section invokes it - see that file).
# =============================================================================

import glob
import os
import stat
import subprocess
import sys


def _clear_readonly(root):
    """Recursively clears the read-only attribute under `root`.

    Background: Bazel marks build outputs read-only on Windows.
    installer/stage_files.py already calls its own _make_writable() after
    every file/directory copy, so the STAGED tree (the actual source Inno
    Setup's [Files] section extracts from) should already be writable.
    However, this has been observed to NOT always hold in practice - e.g.
    a genpackagedoc*.dist-info/direct_url.json file was found read-only in
    a real staged build despite that safeguard (root cause not fully
    pinned down: plausibly a Bazel action-cache situation where an older,
    pre-fix staging output was never re-copied because none of that
    action's declared inputs changed). Whatever the exact cause on the
    BUILD side, a stray read-only bit here would break this script with
    "OSError: [WinError 5] Zugriff verweigert" while pip's uninstall/
    rollback logic tries to move its own temp files into place (observed
    concretely for genpackagedoc's dist-info during end-to-end testing).
    Clearing it defensively, unconditionally, right before doing any pip
    installs makes this script robust regardless of the staged tree's
    actual attribute state, with no downside (chmod on an already-writable
    file/dir is a harmless no-op).
    """
    if not os.path.isdir(root):
        return
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames:
            try:
                os.chmod(os.path.join(dirpath, name), stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
        for name in filenames:
            try:
                os.chmod(os.path.join(dirpath, name), stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass


def main():
    wheels_dir = os.path.dirname(os.path.abspath(__file__))
    wheels = sorted(glob.glob(os.path.join(wheels_dir, "*.whl")))

    if not wheels:
        print(
            "reinstall_console_scripts.py: no *.whl files found in %s - "
            "nothing to do (installer variant without console_scripts?)."
            % wheels_dir
        )
        return 0

    # Bootstrap pip if this interpreter doesn't have it yet. Should
    # normally already be present (part of the staged site-packages
    # produced by the Bazel build - see pip_install.bzl's own ensurepip
    # bootstrap), but repeating it here is a cheap, safe, fully offline
    # no-op if pip is already importable, and a useful safety net in case
    # some future installer variant ships without any pip_install_dir/
    # pip_install_from_source component at all.
    try:
        import pip  # noqa: F401
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--default-pip"])

    # Defensively clear any stray read-only attributes under the installed
    # Python/Lib and Python/Scripts trees before touching anything with
    # pip - see _clear_readonly()'s docstring for why this is needed.
    # wheels_dir is ".../Python/_wheels", so its parent is "Python".
    python_root = os.path.dirname(wheels_dir)
    _clear_readonly(os.path.join(python_root, "Lib"))
    _clear_readonly(os.path.join(python_root, "Scripts"))

    print(
        "reinstall_console_scripts.py: regenerating console-script "
        "launchers for %d bundled wheel(s)..." % len(wheels)
    )

    # IMPORTANT: install each wheel with its OWN "pip install" invocation,
    # not all of them together in a single command. Some components
    # deliberately bundle two DIFFERENT versions of the SAME package as an
    # accepted, harmless duplicate - e.g. "pythonextensionscollection" is
    # built both from its git source (python-extensions-collection, the
    # "real"/authoritative copy) AND pulled in transitively via PyPI by
    # genpackagedoc's own requirements_lock.txt (see that component's
    # requirements.txt for the full rationale). stage_files.py's directory
    # merge already accepts "whichever copy is staged last wins" for the
    # site-packages content itself; installing one wheel file at a time
    # here reproduces the exact same "last one wins" semantics for the
    # regenerated console-script launchers. Passing BOTH wheel files to a
    # single "pip install a.whl b.whl" command instead would make pip
    # treat them as two conflicting, simultaneously "user requested"
    # versions of the same package and hard-fail with
    # "ResolutionImpossible" - even though installing them one after
    # another is perfectly fine.
    for wheel in wheels:
        cmd = [
            sys.executable, "-m", "pip", "install",
            "--disable-pip-version-check",
            "--no-input",
            "--no-index",
            "--find-links", wheels_dir,
            "--force-reinstall",
            "--no-deps",
            wheel,
        ]
        rc = subprocess.call(cmd)
        if rc != 0:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
