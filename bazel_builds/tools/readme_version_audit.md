# version_audit.py - Static Version-Consistency Audit for Bazel Workspaces

`version_audit.py` is a standalone Python script that statically scans a
directory tree for component/package version declarations and reports every
finding in a single, tabular overview - flagging components for which more
than one distinct version was found anywhere in the scanned tree.

It was created to catch exactly the kind of problem described in
[`Bazel_PyPI_zu_GitHub_Source_Umstellung.md`](Bazel_PyPI_zu_GitHub_Source_Umstellung.md):
a component (`PythonExtensionsCollection`) was pinned to one version via a
Git tag in `MODULE.bazel`, while a completely separate, PyPI-based
transitive dependency elsewhere in the workspace silently pulled in a
*different* version of the same component - both copies then got merged
into the same final `site-packages` directory by the installer's staging
step, with the "last one staged" silently winning.

## Location

```
C:\BZL\tools\version_audit.py
```

## What It Scans

The script recursively walks a root directory and inspects three kinds of
files:

| File type | Examples | What is parsed |
|---|---|---|
| Bazel/Starlark files | `MODULE.bazel`, `BUILD.bazel`, `*.bzl`, `WORKSPACE` | `module(name=..., version=...)`, `bazel_dep(name=..., version=...)`, `git_repository(name=..., tag=...)` |
| pip requirements files | `requirements.txt`, `requirements_lock.txt`, `requirements_*.txt` | Lines of the form `package==1.2.3` |
| TOML files | `pyproject.toml`, any `*.toml` | `[project]` table (`name`/`version`), and dependency specifier strings like `"package==1.2.3"` inside dependency lists |

Directories that are generated, vendored, or otherwise irrelevant noise are
skipped by default: `.git`, `__pycache__`, `node_modules`, `bazel-out`,
`bazel-bin`, `bazel-testlogs`, `bazel-genfiles`, `bazel-build`, `external`,
`site-packages`, `site-packages-deps`, `.vscode-test`, `bzl_cache`.
Additional directory names can be excluded via `--exclude-dir`.

### Git tag version extraction

For `git_repository(tag = "...")`, the script strips common release-tag
prefixes to obtain a bare version number, matching the tag naming
conventions observed in this project's components:

| Tag | Extracted version |
|---|---|
| `rel/0.17.0` | `0.17.0` |
| `rel/aio/1.0.1.9` | `1.0.1.9` |
| `v2.3.4` | `2.3.4` |
| `main` / `master` / `develop` / `head` | *(skipped - not a version tag)* |

## Component Name Normalization

Findings are grouped using a PEP 503-style normalized name (lower-cased,
runs of `-`, `_`, `.` collapsed to a single `-`), so that different spelling
conventions for the same component are recognized as one:

```
PythonExtensionsCollection  ─┐
python-extensions-collection ├─►  python-extensions-collection
pythonextensionscollection  ─┘
```

## Filtering Bazel `bazel_dep` Placeholder Versions

This workspace consistently uses the pattern of referencing every local
(in-repo) Bzlmod module via:

```python
bazel_dep(name = "some_component", version = "0.1.0")

local_path_override(
    module_name = "some_component",
    path = "../some_component",
)
```

Bzlmod does **not** actually validate the `bazel_dep` `version` attribute
against the real module's own `module(version = ...)` declaration when a
`local_path_override` is in effect for that module in the same file - it is
merely a required-but-unchecked registry-compatibility placeholder,
conventionally left at `"0.1.0"` for every local module regardless of that
module's real, independently evolving version.

To avoid reporting dozens of false-positive "mismatches" purely from this
convention, `version_audit.py` first collects every `module_name` that has a
`local_path_override` in the same file, then **skips** `bazel_dep` entries
referencing those same module names when collecting findings. Only the
authoritative `module(version = ...)` declaration (inside that component's
own `MODULE.bazel`) is kept.

## Output

The script produces the **same** report in two places:

1. **Console** (stdout)
2. **Text file** - default: `<root>/version_audit_report.txt`, overridable
   via `--output`

The written/printed content actually consists of **two** report sections,
concatenated one after another.

### Section 1: Main audit table (one row per finding)

### Report structure

```
====================================================================================================
Version Audit Report
Scanned root: C:\BZL
Total findings: 294  |  Distinct components: 99  |  Components with version MISMATCH: 4
====================================================================================================

Component        Version   Status     Source         File                                    Line
---------------  --------  ---------  -------------  --------------------------------------  ----
   colorama         0.4.6              requirements   python-extensions-collection\...          7
   ...
>> pythonextensionscollection  0.17.0  MISMATCH  requirements  python-genpackagedoc\...          29
>> pythonextensionscollection  0.17.1  MISMATCH  requirements  robotframework-dbus\...           33
   ...

----------------------------------------------------------------------------------------------------
4 component(s) with INCONSISTENT versions detected:
  - docutils: 0.22.4, 0.23
  - pythonextensionscollection: 0.17.0, 0.17.1
  - robotframework: 6.1, 7.5
  - setuptools: 82.0.1, 84.0.0
----------------------------------------------------------------------------------------------------
```

- Every individual finding (one row per file/line where a component/version
  pair was declared) is listed, grouped by normalized component name.
- Rows belonging to a component with more than one distinct version are
  prefixed with `>>` and marked `MISMATCH` in the **Status** column.
- A summary block at the end lists every mismatched component together with
  all distinct versions found for it, for quick scanning without reading
  the full table.

### Section 2: Dedicated `bazel_dep()` dependency overview (one row per name)

A second, dedicated table specifically for Bazel `bazel_dep(name = "...",
version = "...")` declarations is appended after the main table. Unlike the
main table (one row per finding), this section produces **one row per
dependency name**, listing every distinct version found for it directly in
the "Versions Found" column:

```
====================================================================================================
Bazel bazel_dep() Dependency Overview
Distinct dependency names: 25  |  Names with version MISMATCH: 1
(One row per dependency name; ALL bazel_dep() declarations are included
here, even those superseded by a local_path_override - see the main table
above for the noise-filtered view.)
====================================================================================================

Dependency Name    Versions Found  Status
-----------------  --------------  --------
   bazel_skylib       1.8.2           ok
   inno_setup         0.1.0           ok
>> py_modules_set_2   0.1.0, 9.9.9    MISMATCH
        - 0.1.0 @ build\MODULE.bazel:38
        - 0.1.0 @ installer\MODULE.bazel:19
        - 9.9.9 @ python\MODULE.bazel:24
   rules_pkg          1.0.1           ok
   ...

----------------------------------------------------------------------------------------------------
1 bazel_dep() name(s) with INCONSISTENT versions detected:
  - py_modules_set_2: 0.1.0, 9.9.9
----------------------------------------------------------------------------------------------------
```

Key differences from Section 1:

- **Granularity**: one row per dependency **name**, not one row per
  finding. All versions found for that name are shown together in the
  "Versions Found" column (comma-separated).
- **Unfiltered**: this section deliberately includes **every** `bazel_dep()`
  call found anywhere in the scanned tree, even for module names that also
  have a `local_path_override` in the same file (which Section 1 excludes
  as noise - see
  [Filtering Bazel `bazel_dep` Placeholder Versions](#filtering-bazel-bazel_dep-placeholder-versions)
  below). This was an explicit requirement: `bazel_dep()` declarations
  should always be extracted and reported, independent of whether an
  override exists.
- **File breakdown for mismatches**: whenever more than one distinct
  version is found for a name, every contributing file (with line number)
  is listed directly below that row, indented and prefixed with `-`, so the
  exact source of the inconsistency is immediately visible without cross-
  referencing Section 1.



## Usage

```powershell
python C:\BZL\tools\version_audit.py --root C:\BZL --output C:\BZL\version_audit_report.txt
```

### Arguments

| Argument | Default | Description |
|---|---|---|
| `--root DIR` | current directory | Root directory to scan recursively |
| `--output FILE` | `<root>/version_audit_report.txt` | Path of the report text file to write |
| `--exclude-dir NAME` (repeatable) | *(none)* | Additional directory name(s) to exclude, merged with the built-in defaults |

### Exit code

The script returns a **non-zero exit code (`1`) if at least one version
mismatch was detected**, and `0` if all components are consistent. This
makes it straightforward to wire the script into a CI pipeline or a
pre-build check:

```powershell
python C:\BZL\tools\version_audit.py --root C:\BZL
if ($LASTEXITCODE -ne 0) {
    Write-Host "Version mismatches detected - review version_audit_report.txt"
}
```

## Known Limitations

- **Not a full Starlark/TOML parser.** Parsing is done via targeted regular
  expressions and simple paren-balance scanning, tuned to the conventional,
  single-purpose call style used throughout this project's `.bazel`/`.bzl`
  files (each `module()`/`bazel_dep()`/`git_repository()` call is expected
  to be a single, non-nested, balanced-parenthesis block with
  double-quoted string attributes). Unusual formatting (e.g. deeply nested
  macro calls with the same name, or dynamically constructed
  version strings) may not be detected.
- **No semantic/PEP 440 version comparison.** Two version strings are only
  compared for exact textual equality - the tool does not know that `1.0`
  and `1.0.0` are semantically identical, nor does it detect
  `>=`/`~=`-style ranges that would still allow full compatibility.
- **`bazel_dep` version placeholders are only filtered within the SAME
  file** as their matching `local_path_override`. If a workspace ever
  references a module via `bazel_dep` in one file while its
  `local_path_override` lives in a different file, that `bazel_dep` entry
  will currently still be reported (this does not occur anywhere in the
  current `C:\BZL` layout, where every `bazel_dep`/`local_path_override`
  pair is co-located).
- **Only `==` pins are recognized** in `requirements*.txt` and TOML
  dependency specifiers (plus `>=`/`<=`/`~=` for TOML). Unpinned
  dependencies (bare package names, e.g. `setuptools` without a version)
  are intentionally not reported, since there is no version to compare.

## Related Documents

- `Bazel_PyPI_zu_GitHub_Source_Umstellung.md` - describes the specific
  version-mismatch incident (`PythonExtensionsCollection` 0.17.0 vs. 0.17.1)
  that motivated writing this tool.
- `Bazel_Requirements_Lock_Files.md`
- `Bazel_Dependency_Management.md`
