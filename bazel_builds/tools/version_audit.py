# =============================================================================
# version_audit.py - Static Version-Consistency Audit for Bazel Workspaces
# =============================================================================
#
# Recursively scans a directory tree for files that declare component/package
# names together with version numbers:
#
#   - MODULE.bazel (and *.bazel, *.bzl files in general):
#       * module(name = "...", version = "...")
#       * bazel_dep(name = "...", version = "...")
#       * git_repository(name = "...", tag = "...")   (version extracted from
#         the tag, stripping common prefixes like "rel/", "v", "rel/aio/")
#
#   - requirements*.txt (pip requirements files):
#       * lines of the form "package==1.2.3" (optionally continued with a
#         trailing backslash + --hash=... lines, which are ignored)
#
#   - *.toml files (e.g. pyproject.toml):
#       * [project] name = "..." / version = "..."
#       * dependency version specifiers in dependency lists
#         (package==1.2.3, package>=1.2.3, etc.)
#
# All findings are grouped by a NORMALIZED component name (PEP 503 style:
# lower-cased, runs of "-", "_", "." collapsed to a single "-") so that e.g.
# "PythonExtensionsCollection", "python-extensions-collection" and
# "pythonextensionscollection" are recognized as the same component.
#
# Output:
#   - A tabular report is printed to the console.
#   - The SAME report is written to a text file (default:
#     version_audit_report.txt in the scanned root, override via --output).
#   - Components for which more than one DISTINCT version was found across
#     all scanned files are marked as "MISMATCH" and highlighted.
#   - A SECOND, dedicated table specifically for Bazel
#     "bazel_dep(name=..., version=...)" dependency declarations is
#     appended: one row PER DEPENDENCY NAME, listing every distinct version
#     found for it and (for mismatches) every file that declares a
#     differing version. Unlike the main table, this section deliberately
#     does NOT filter out bazel_dep entries whose module_name has a
#     local_path_override in the same file - it reports the raw bazel_dep()
#     declarations exactly as written, since that is what was explicitly
#     requested.
#
# Usage:
#   python version_audit.py [--root DIR] [--output FILE]
#                            [--exclude-dir NAME [--exclude-dir NAME ...]]
#
# Example:
#   python version_audit.py --root C:\BZL --output C:\BZL\version_audit_report.txt
#
# =============================================================================

"""Static version-consistency audit tool for Bazel workspaces.

Scans MODULE.bazel/BUILD.bazel/*.bzl, requirements*.txt, and *.toml files for
component name + version declarations, then reports every finding in a single
table and flags components that show more than one distinct version.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# -----------------------------------------------------------------------------
# Data model
# -----------------------------------------------------------------------------


@dataclass
class Finding:
    """A single (component name, version) declaration found in a file."""

    raw_name: str
    version: str
    file: Path
    line: int
    source_kind: str  # e.g. "module", "bazel_dep", "git_repository(tag)",
    # "requirements", "toml[project]", "toml[dependency]"


# -----------------------------------------------------------------------------
# Default directory excludes
# -----------------------------------------------------------------------------
# These are Bazel-generated / vendored / cache directories that either
# duplicate the same information many times over (external/, bazel-out/,
# disk_cache/) or are irrelevant noise (.git/, __pycache__/, node_modules/).
# Matched against the directory NAME (not the full path), so they are
# skipped no matter how deep they occur.
DEFAULT_EXCLUDE_DIRS = {
    ".git",
    "__pycache__",
    "node_modules",
    "bazel-out",
    "bazel-bin",
    "bazel-testlogs",
    "bazel-genfiles",
    "bazel-build",
    "external",
    "site-packages",
    "site-packages-deps",
    ".vscode-test",
    "bzl_cache",
}

# File names that must be scanned even though their suffix alone would not
# select them (e.g. "MODULE.bazel", "BUILD.bazel" have no ".bazel"-only stem
# match via suffix alone since Path.suffix would be ".bazel" for MODULE.bazel
# - actually it does match, but WORKSPACE has no suffix at all).
EXTRA_EXACT_FILENAMES = {"WORKSPACE", "WORKSPACE.bazel", "BUILD", "BUILD.bazel"}


def iter_candidate_files(root: Path, exclude_dirs: set[str]):
    """Yields all files under root that could plausibly declare versions.

    Matches:
      - *.bazel, *.bzl              (Bazel/Starlark files)
      - WORKSPACE / BUILD (no suffix)
      - requirements*.txt
      - *.toml
    """
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in exclude_dirs for part in path.parts):
            continue
        name = path.name
        suffix = path.suffix.lower()
        if suffix in (".bazel", ".bzl"):
            yield path
        elif name in EXTRA_EXACT_FILENAMES:
            yield path
        elif name.lower().startswith("requirements") and suffix == ".txt":
            yield path
        elif suffix == ".toml":
            yield path


# -----------------------------------------------------------------------------
# Starlark (.bazel / .bzl) parsing
# -----------------------------------------------------------------------------


def _find_call_blocks(content: str, call_name: str):
    """Finds all `call_name(...)` invocations in Starlark source and returns
    (block_text, start_line) for each, using simple paren-balance scanning.

    This is intentionally not a full Starlark parser - it is robust enough
    for the conventional, single-purpose attribute-call style used
    throughout this project's MODULE.bazel/BUILD.bazel files (each
    call spans one balanced set of parentheses, string values are always
    double-quoted, no nested calls of the SAME name inside one another).
    """
    pattern = re.compile(r"\b" + re.escape(call_name) + r"\s*\(")
    for match in pattern.finditer(content):
        start = match.end()  # position right after the opening "("
        depth = 1
        i = start
        while i < len(content) and depth > 0:
            ch = content[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            i += 1
        block = content[start : i - 1]
        line_no = content.count("\n", 0, match.start()) + 1
        yield block, line_no


_ATTR_STRING_RE_TEMPLATE = r'{attr}\s*=\s*"([^"]*)"'


def _attr(block: str, attr: str) -> str | None:
    m = re.search(_ATTR_STRING_RE_TEMPLATE.format(attr=re.escape(attr)), block)
    return m.group(1) if m else None


_TAG_PREFIX_RE = re.compile(r"^(rel/aio/|rel/|v)", re.IGNORECASE)


def _version_from_tag(tag: str) -> str:
    """Strips common release-tag prefixes to obtain a bare version number.

    Examples:
        "rel/0.17.0"      -> "0.17.0"
        "rel/aio/1.0.1.9" -> "1.0.1.9"
        "v2.3.4"          -> "2.3.4"
        "main"            -> "main" (not a version tag - caller should check)
    """
    return _TAG_PREFIX_RE.sub("", tag)


def parse_bazel_file(path: Path) -> tuple[list[Finding], list[Finding]]:
    """Parses a single Bazel/Starlark file.

    Returns a tuple (findings, bazel_dep_raw_findings):
      - findings: module()/bazel_dep()/git_repository() declarations, with
        bazel_dep() entries FILTERED to exclude module_names that have a
        local_path_override in the same file (see comment below for why -
        used for the main, noise-reduced audit table).
      - bazel_dep_raw_findings: EVERY bazel_dep(name=..., version=...)
        declaration found in this file, completely UNFILTERED. Used for the
        dedicated "Bazel bazel_dep() Dependency Overview" report section.
    """
    findings: list[Finding] = []
    bazel_dep_raw_findings: list[Finding] = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings, bazel_dep_raw_findings

    # module(name = "...", version = "...")
    for block, line_no in _find_call_blocks(content, "module"):
        name = _attr(block, "name")
        version = _attr(block, "version")
        if name and version:
            findings.append(Finding(name, version, path, line_no, "module()"))

    # local_path_override(module_name = "...", path = "...") - collected
    # FIRST so that bazel_dep() entries for the same module_name can be
    # recognized as version-check-irrelevant (see comment below).
    overridden_modules: set[str] = set()
    for block, _line_no in _find_call_blocks(content, "local_path_override"):
        module_name = _attr(block, "module_name")
        if module_name:
            overridden_modules.add(module_name)

    # bazel_dep(name = "...", version = "...")
    #
    # IMPORTANT: In this project, every LOCAL (in-repo) component is
    # referenced via "bazel_dep(name=X, version='0.1.0') +
    # local_path_override(module_name=X, path='../X')". Bzlmod does NOT
    # actually verify the bazel_dep "version" attribute against the real
    # module's own module(version=...) declaration when a
    # local_path_override is in effect for that same module_name in this
    # file - it is merely a required-but-unchecked registry compatibility
    # placeholder, conventionally left at "0.1.0" for every local module
    # regardless of that module's real, independently evolving version
    # (e.g. robotframework-testsuitesmanagement's actual version is
    # "0.11.0", but every consumer's bazel_dep says "0.1.0"). Comparing
    # these placeholder versions against the real module() version would
    # produce a MISMATCH finding for essentially every single local
    # component in the repo - pure noise, not an actual inconsistency.
    # Such bazel_dep entries are therefore EXCLUDED from `findings` (the
    # main audit table) - but they are ALWAYS included, unfiltered, in
    # `bazel_dep_raw_findings` (the dedicated bazel_dep report section),
    # since that section's whole purpose is to show bazel_dep()
    # declarations exactly as they appear across the codebase.
    for block, line_no in _find_call_blocks(content, "bazel_dep"):
        name = _attr(block, "name")
        version = _attr(block, "version")
        if name and version:
            bazel_dep_raw_findings.append(
                Finding(name, version, path, line_no, "bazel_dep()")
            )
            if name not in overridden_modules:
                findings.append(Finding(name, version, path, line_no, "bazel_dep()"))

    # git_repository(name = "...", tag = "...")
    for block, line_no in _find_call_blocks(content, "git_repository"):
        name = _attr(block, "name")
        tag = _attr(block, "tag")
        if name and tag:
            version = _version_from_tag(tag)
            if version.lower() not in ("main", "master", "develop", "head"):
                findings.append(
                    Finding(name, version, path, line_no, "git_repository(tag)")
                )

    return findings, bazel_dep_raw_findings


# -----------------------------------------------------------------------------
# requirements*.txt parsing
# -----------------------------------------------------------------------------

# Matches "package==1.2.3" (optionally followed by a trailing backslash for
# --hash continuation lines, extras like "package[extra]==1.2.3", and
# arbitrary surrounding whitespace). Comment-only and blank lines, and
# continuation lines (starting with whitespace, e.g. "    --hash=..."), are
# skipped because they don't match this pattern at column 0.
_REQ_LINE_RE = re.compile(
    r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(?:\[[^\]]*\])?\s*==\s*"
    r"([A-Za-z0-9][A-Za-z0-9._+-]*)"
)


def parse_requirements_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return findings

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = _REQ_LINE_RE.match(line)
        if m:
            name, version = m.group(1), m.group(2)
            findings.append(Finding(name, version, path, line_no, "requirements"))
    return findings


# -----------------------------------------------------------------------------
# *.toml parsing
# -----------------------------------------------------------------------------

# Matches a PEP 508-ish dependency specifier string, e.g.:
#   "requests==2.31.0"
#   "click>=8.0,<9"
#   'genpackagedoc == 0.44.0'
_TOML_DEP_STRING_RE = re.compile(
    r'"([A-Za-z0-9][A-Za-z0-9._-]*)\s*(==|>=|<=|~=)\s*'
    r'([A-Za-z0-9][A-Za-z0-9._+-]*)[^"]*"'
)


def parse_toml_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings
    lines = content.splitlines()

    # --- [project] table: name = "..." / version = "..." -------------------
    project_name = None
    project_version = None
    project_name_line = None
    project_version_line = None
    in_project_table = False
    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if re.match(r"^\[project\]\s*(#.*)?$", stripped):
            in_project_table = True
            continue
        if stripped.startswith("[") and stripped != "[project]":
            in_project_table = False
            continue
        if not in_project_table:
            continue
        m_name = re.match(r'^name\s*=\s*"([^"]+)"', stripped)
        if m_name:
            project_name = m_name.group(1)
            project_name_line = line_no
            continue
        m_version = re.match(r'^version\s*=\s*"([^"]+)"', stripped)
        if m_version:
            project_version = m_version.group(1)
            project_version_line = line_no

    if project_name and project_version:
        findings.append(
            Finding(
                project_name,
                project_version,
                path,
                project_version_line or project_name_line or 1,
                "toml[project]",
            )
        )

    # --- Dependency specifiers anywhere in the file (dependencies = [...],
    #     [project.optional-dependencies], [tool.poetry.dependencies], etc.)
    for line_no, line in enumerate(lines, start=1):
        for m in _TOML_DEP_STRING_RE.finditer(line):
            name, _op, version = m.group(1), m.group(2), m.group(3)
            findings.append(Finding(name, version, path, line_no, "toml[dependency]"))

    return findings


# -----------------------------------------------------------------------------
# Dispatch
# -----------------------------------------------------------------------------


def parse_file(path: Path) -> tuple[list[Finding], list[Finding]]:
    """Parses a single file, returning (findings, bazel_dep_raw_findings).

    bazel_dep_raw_findings is only ever non-empty for Bazel/Starlark files -
    see parse_bazel_file() for details. Other file types return an empty
    list as their second tuple element.
    """
    suffix = path.suffix.lower()
    name = path.name
    if suffix in (".bazel", ".bzl") or name in ("WORKSPACE", "WORKSPACE.bazel"):
        return parse_bazel_file(path)
    if name.lower().startswith("requirements") and suffix == ".txt":
        return parse_requirements_file(path), []
    if suffix == ".toml":
        return parse_toml_file(path), []
    return [], []


# -----------------------------------------------------------------------------
# Component name normalization (PEP 503 style)
# -----------------------------------------------------------------------------

_NORMALIZE_RE = re.compile(r"[-_.]+")


def normalize_name(name: str) -> str:
    return _NORMALIZE_RE.sub("-", name.lower()).strip("-")


# -----------------------------------------------------------------------------
# Report generation
# -----------------------------------------------------------------------------


def build_report(findings: list[Finding], root: Path) -> str:
    # Group findings by normalized component name.
    groups: dict[str, list[Finding]] = {}
    for f in findings:
        groups.setdefault(normalize_name(f.raw_name), []).append(f)

    # Determine which groups have more than one DISTINCT version.
    mismatched: set[str] = set()
    for key, group_findings in groups.items():
        versions = {f.version for f in group_findings}
        if len(versions) > 1:
            mismatched.add(key)

    # Build table rows: one row per finding, sorted by normalized name, then
    # by version, then by file path - mismatched components' rows are all
    # grouped together and flagged.
    rows = []
    for key in sorted(groups.keys()):
        group_findings = sorted(
            groups[key], key=lambda f: (f.version, str(f.file), f.line)
        )
        status = "MISMATCH" if key in mismatched else "ok"
        for f in group_findings:
            try:
                rel_file = f.file.relative_to(root)
            except ValueError:
                rel_file = f.file
            rows.append(
                (
                    f.raw_name,
                    f.version,
                    status if key in mismatched else "",
                    f.source_kind,
                    str(rel_file),
                    str(f.line),
                )
            )

    headers = ("Component", "Version", "Status", "Source", "File", "Line")
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    def fmt_row(row) -> str:
        return "  ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))

    lines = []
    lines.append("=" * 100)
    lines.append("Version Audit Report")
    lines.append("Scanned root: %s" % root)
    lines.append(
        "Total findings: %d  |  Distinct components: %d  |  Components with "
        "version MISMATCH: %d" % (len(findings), len(groups), len(mismatched))
    )
    lines.append("=" * 100)
    lines.append("")
    lines.append(fmt_row(headers))
    lines.append("  ".join("-" * w for w in col_widths))

    last_key = None
    for row, key in zip(
        rows,
        (
            k
            for k in sorted(groups.keys())
            for _ in sorted(
                groups[k], key=lambda f: (f.version, str(f.file), f.line)
            )
        ),
    ):
        if last_key is not None and key != last_key:
            lines.append("")  # blank line between different components
        marker = ">> " if row[2] == "MISMATCH" else "   "
        lines.append(marker + fmt_row(row))
        last_key = key

    lines.append("")
    lines.append("-" * 100)
    if mismatched:
        lines.append(
            "%d component(s) with INCONSISTENT versions detected:" % len(mismatched)
        )
        for key in sorted(mismatched):
            versions = sorted({f.version for f in groups[key]})
            display_name = groups[key][0].raw_name
            lines.append("  - %s: %s" % (display_name, ", ".join(versions)))
    else:
        lines.append("No version mismatches detected.")
    lines.append("-" * 100)

    return "\n".join(lines) + "\n"


# -----------------------------------------------------------------------------
# Dedicated report: bazel_dep() dependency overview
# -----------------------------------------------------------------------------


def build_bazel_dep_report(bazel_dep_findings: list[Finding], root: Path) -> str:
    """Builds the dedicated "Bazel bazel_dep() Dependency Overview" report.

    Unlike build_report() (one row per finding), this produces ONE ROW PER
    DEPENDENCY NAME, listing every distinct version found for it. If more
    than one distinct version was found for a name, the row is flagged
    "MISMATCH" and a breakdown of exactly which file declares which
    (differing) version is appended below that row.

    This report is deliberately based on the UNFILTERED bazel_dep()
    collection (see parse_bazel_file()) - i.e. it includes every bazel_dep()
    call found anywhere in the scanned tree, even those whose module_name
    also has a local_path_override in the same file (which the main
    build_report() table excludes as noise). This gives a complete, raw
    view of every bazel_dep() declaration exactly as written.
    """
    groups: dict[str, list[Finding]] = {}
    for f in bazel_dep_findings:
        groups.setdefault(normalize_name(f.raw_name), []).append(f)

    def rel(path: Path) -> str:
        try:
            return str(path.relative_to(root))
        except ValueError:
            return str(path)

    mismatched_keys = sorted(
        key for key, gf in groups.items() if len({f.version for f in gf}) > 1
    )

    headers = ("Dependency Name", "Versions Found", "Status")
    row_by_key: dict[str, tuple] = {}
    for key, group_findings in groups.items():
        versions = sorted({f.version for f in group_findings})
        display_name = group_findings[0].raw_name
        status = "MISMATCH" if key in mismatched_keys else "ok"
        row_by_key[key] = (display_name, ", ".join(versions), status)

    col_widths = [len(h) for h in headers]
    for row in row_by_key.values():
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    def fmt_row(row) -> str:
        return "  ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(row))

    lines = []
    lines.append("=" * 100)
    lines.append("Bazel bazel_dep() Dependency Overview")
    lines.append(
        "Distinct dependency names: %d  |  Names with version MISMATCH: %d"
        % (len(groups), len(mismatched_keys))
    )
    lines.append(
        "(One row per dependency name; ALL bazel_dep() declarations are "
        "included here, even those superseded by a local_path_override - "
        "see the main table above for the noise-filtered view.)"
    )
    lines.append("=" * 100)
    lines.append("")
    lines.append(fmt_row(headers))
    lines.append("  ".join("-" * w for w in col_widths))

    for key in sorted(groups.keys()):
        row = row_by_key[key]
        marker = ">> " if key in mismatched_keys else "   "
        lines.append(marker + fmt_row(row))
        if key in mismatched_keys:
            # Breakdown: which file declares which (differing) version.
            group_findings = sorted(
                groups[key], key=lambda f: (f.version, str(f.file), f.line)
            )
            for f in group_findings:
                lines.append(
                    "        - %s @ %s:%d" % (f.version, rel(f.file), f.line)
                )
            lines.append("")

    lines.append("-" * 100)
    if mismatched_keys:
        lines.append(
            "%d bazel_dep() name(s) with INCONSISTENT versions detected:"
            % len(mismatched_keys)
        )
        for key in mismatched_keys:
            versions = sorted({f.version for f in groups[key]})
            display_name = groups[key][0].raw_name
            lines.append("  - %s: %s" % (display_name, ", ".join(versions)))
    else:
        lines.append("No bazel_dep() version mismatches detected.")
    lines.append("-" * 100)

    return "\n".join(lines) + "\n"


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Static version-consistency audit for Bazel workspaces.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Scans MODULE.bazel/BUILD.bazel/*.bzl (module()/bazel_dep()/git_repository()
tag=...), requirements*.txt (package==version), and *.toml (pyproject.toml
[project] table + dependency specifiers) for component name/version pairs,
then prints and writes a report table. Components for which more than one
distinct version was found anywhere in the scanned tree are marked
"MISMATCH".
        """,
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory to scan recursively (default: current directory).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output text file for the report "
        "(default: <root>/version_audit_report.txt).",
    )
    parser.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        metavar="NAME",
        help="Additional directory name to exclude (repeatable). Merged "
        "with the built-in default excludes (.git, bazel-out, external, "
        "site-packages, node_modules, __pycache__, ...).",
    )
    args = parser.parse_args()

    root: Path = args.root.resolve()
    if not root.is_dir():
        print("ERROR: --root is not a directory: %s" % root, file=sys.stderr)
        return 1

    output_path: Path = args.output or (root / "version_audit_report.txt")
    exclude_dirs = set(DEFAULT_EXCLUDE_DIRS) | set(args.exclude_dir)

    all_findings: list[Finding] = []
    all_bazel_dep_findings: list[Finding] = []
    for path in iter_candidate_files(root, exclude_dirs):
        findings, bazel_dep_findings = parse_file(path)
        all_findings.extend(findings)
        all_bazel_dep_findings.extend(bazel_dep_findings)

    report = build_report(all_findings, root)
    bazel_dep_report = build_bazel_dep_report(all_bazel_dep_findings, root)
    combined_report = report + "\n" + bazel_dep_report

    print(combined_report)
    output_path.write_text(combined_report, encoding="utf-8")
    print("Report written to: %s" % output_path)

    # Non-zero exit code if mismatches were found, so this can be wired into
    # a CI/pre-build check if desired.
    has_mismatch = "MISMATCH" in combined_report
    return 1 if has_mismatch else 0


if __name__ == "__main__":
    sys.exit(main())
