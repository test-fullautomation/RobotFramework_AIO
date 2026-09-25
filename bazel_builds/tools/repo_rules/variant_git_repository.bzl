# =============================================================================
# variant_git_repository.bzl - Git source checkout with Tag/Branch selection
# =============================================================================
#
# This module defines a custom repository_rule that fetches a Git source
# tree, choosing between a fixed, hermetic release tag ("tagged" variant -
# the default, used for reproducible, production/installer builds) and a
# moving branch HEAD ("daily" variant, used for Daily Build / Daily Test
# pipelines that intentionally want "always the latest commit").
#
# Rationale / background:
#   See documentation/docs/Bazel_Git_Repository_Tag_vs_Branch.md for the
#   full discussion of why a plain git_repository(tag=...) should never be
#   switched to git_repository(branch=...) for production builds, and why a
#   dedicated mechanism is needed to support BOTH modes side by side without
#   duplicating MODULE.bazel per component.
#
# Selection mechanism:
#   The variant is selected via the BUILD_VARIANT environment variable,
#   passed through Bazel's --repo_env flag (NOT a plain OS environment
#   variable - Bazel repository rules only see environment variables that
#   are explicitly declared in "environ" AND forwarded via --repo_env or
#   --action_env, to keep the build's dependency on the environment
#   explicit and cacheable).
#
#     BUILD_VARIANT=daily  (project default, set in .bazelrc) -> uses "daily_branch"
#     BUILD_VARIANT=tagged (explicit opt-in via --config=tagged) -> uses "release_tag"
#
#   Note: the implementation's own rctx.getenv(..., "tagged") fallback only
#   applies if BUILD_VARIANT is not set at all (e.g. .bazelrc were removed
#   or bypassed) - in normal usage .bazelrc's "common --repo_env=..." line
#   always sets it explicitly, so the effective project-wide default is
#   "daily", not this code-level fallback.
#
#   Because "BUILD_VARIANT" is declared in the "environ" attribute below,
#   Bazel automatically includes its value in the repository rule's cache
#   key - switching between `bazel build --config=tagged` and a normal
#   `bazel build` correctly triggers a re-fetch, unlike a plain
#   git_repository(branch=...) whose attribute value never changes and
#   therefore never invalidates Bazel's repository cache on its own.
#
#   Additionally, in "tagged" mode, the RELEASE_TAG_OVERRIDE environment
#   variable (also passed via --repo_env, also declared in "environ") lets
#   the caller pin a DIFFERENT tag than the one hardcoded in MODULE.bazel's
#   "release_tag" attribute, without editing that file - see the dedicated
#   section below.
#
# Usage (see python-extensions-collection/MODULE.bazel for the real example):
#
#   bazel_dep(name = "repo_rules", version = "0.1.0")
#   local_path_override(module_name = "repo_rules", path = "../tools/repo_rules")
#
#   variant_git_repository = use_repo_rule(
#       "@repo_rules//:variant_git_repository.bzl",
#       "variant_git_repository",
#   )
#
#   variant_git_repository(
#       name = "python_extensions_collection_src",
#       remote = "https://github.com/test-fullautomation/python-extensions-collection.git",
#       release_tag = "rel/0.17.0",
#       daily_branch = "develop",
#       build_file_content = """filegroup(name = "src", srcs = glob(["**"], exclude = [".git/**"]), visibility = ["//visibility:public"])""",
#   )
#
# .bazelrc:
#
#   common --repo_env=BUILD_VARIANT=daily         # project default: Daily Build/Test
#   common:tagged --repo_env=BUILD_VARIANT=tagged # explicit reproducible/hermetic build
#
# Invocation:
#
#   bazel build //...                   # daily build (tracks branch HEAD, project default)
#   bazel build --config=tagged //...   # tagged (reproducible) build
#
# Overriding the release tag from the command line:
#   By default, "tagged" mode uses the "release_tag" attribute hardcoded in
#   MODULE.bazel (e.g. release_tag = "rel/0.17.1"). To pin a DIFFERENT tag
#   for a one-off build/test WITHOUT editing MODULE.bazel, pass the
#   RELEASE_TAG_OVERRIDE environment variable via --repo_env, e.g.:
#
#     bazel build --config=tagged --repo_env=RELEASE_TAG_OVERRIDE=rel/0.17.0 //...
#
#   Like BUILD_VARIANT, this is declared in "environ" below, so Bazel
#   correctly re-fetches the repository whenever this value changes. If
#   RELEASE_TAG_OVERRIDE is unset (the normal case), the hardcoded
#   "release_tag" attribute value is used unchanged. This override has NO
#   effect in "daily" mode (which always uses "daily_branch").
#
# Overriding the daily branch from the command line:
#   Analogous to RELEASE_TAG_OVERRIDE above, "daily" mode uses the
#   "daily_branch" attribute hardcoded in MODULE.bazel (e.g.
#   daily_branch = "develop") by default. To build/test against a
#   DIFFERENT branch for a one-off run WITHOUT editing MODULE.bazel, pass
#   the RELEASE_BRANCH_OVERRIDE environment variable via --repo_env, e.g.:
#
#     bazel build --repo_env=RELEASE_BRANCH_OVERRIDE=feature/my-branch //...
#
#   Like RELEASE_TAG_OVERRIDE, this is declared in "environ" below, so
#   Bazel correctly re-fetches the repository whenever this value changes.
#   If RELEASE_BRANCH_OVERRIDE is unset (the normal case), the hardcoded
#   "daily_branch" attribute value is used unchanged. This override has NO
#   effect in "tagged" mode (which always uses "release_tag"/
#   RELEASE_TAG_OVERRIDE).
#
# =============================================================================

def _variant_git_repository_impl(rctx):
    variant = rctx.getenv("BUILD_VARIANT", "tagged")

    if variant == "daily":
        branch_override = rctx.getenv("RELEASE_BRANCH_OVERRIDE", "")
        ref = branch_override if branch_override else rctx.attr.daily_branch
        ref_kind = "branch (overridden via RELEASE_BRANCH_OVERRIDE)" if branch_override else "branch"
    elif variant == "tagged":
        ref_override = rctx.getenv("RELEASE_TAG_OVERRIDE", "")
        ref = ref_override if ref_override else rctx.attr.release_tag
        ref_kind = "tag (overridden via RELEASE_TAG_OVERRIDE)" if ref_override else "tag"
    else:
        fail(
            "Unknown BUILD_VARIANT '{}' for repository '{}'. ".format(variant, rctx.attr.name) +
            "Expected 'tagged' (default) or 'daily'. Check --repo_env=BUILD_VARIANT=... " +
            "in .bazelrc / on the command line.",
        )

    rctx.report_progress(
        "Cloning {} at {} '{}' (BUILD_VARIANT={})".format(rctx.attr.remote, ref_kind, ref, variant),
    )

    # Shallow, single-ref clone. `git clone --branch <ref>` works for both
    # tags and branch names - Git resolves whichever kind of ref matches.
    # A shallow clone (--depth=1) keeps the fetch fast and avoids pulling
    # the entire repository history, which is not needed for a source
    # checkout that is only ever used as a filegroup input.
    clone_result = rctx.execute(
        [
            "git",
            "clone",
            "--quiet",
            "--depth=1",
            "--branch",
            ref,
            rctx.attr.remote,
            ".",
        ],
        timeout = rctx.attr.timeout,
        environment = rctx.attr.git_env,
    )
    if clone_result.return_code != 0:
        fail(
            ("variant_git_repository '{}': failed to clone '{}' at {} '{}' " +
             "(BUILD_VARIANT={}).\nstdout:\n{}\nstderr:\n{}").format(
                rctx.attr.name,
                rctx.attr.remote,
                ref_kind,
                ref,
                variant,
                clone_result.stdout,
                clone_result.stderr,
            ),
        )

    # Record the exact commit that was actually checked out, so that a
    # "daily" (branch-tracking) build remains traceable after the fact even
    # though the MODULE.bazel source itself does not pin a specific commit.
    # This directly implements the "log the resolved commit hash" guidance
    # from Bazel_Git_Repository_Tag_vs_Branch.md.
    rev_parse_result = rctx.execute(["git", "rev-parse", "HEAD"], timeout = 60)
    resolved_commit = rev_parse_result.stdout.strip() if rev_parse_result.return_code == 0 else "<unknown>"

    rctx.file(
        "RESOLVED_REF.txt",
        content = (
            "remote: {}\n".format(rctx.attr.remote) +
            "variant: {}\n".format(variant) +
            "ref_kind: {}\n".format(ref_kind) +
            "ref: {}\n".format(ref) +
            "resolved_commit: {}\n".format(resolved_commit)
        ),
        executable = False,
    )

    # Remove the .git directory - only the working tree contents are
    # needed as build input, and excluding .git keeps the resulting
    # filegroup (see build_file_content's glob(..., exclude=[".git/**"])
    # in callers) both smaller and free of Bazel-unfriendly file types
    # (e.g. symlinks/hooks) that a full .git directory can contain.
    rctx.delete(".git")

    if rctx.attr.build_file_content:
        rctx.file("BUILD.bazel", rctx.attr.build_file_content, executable = False)

variant_git_repository = repository_rule(
    implementation = _variant_git_repository_impl,
    attrs = {
        "remote": attr.string(
            mandatory = True,
            doc = "Git remote URL (e.g. https://github.com/<org>/<repo>.git).",
        ),
        "release_tag": attr.string(
            mandatory = True,
            doc = """Fixed tag used when BUILD_VARIANT is 'tagged'.
            Must reference an existing tag in the remote repository, e.g. "rel/0.17.0".
            This is the hermetic, reproducible reference used for production/
            installer builds - see Bazel_Git_Repository_Tag_vs_Branch.md.

            Can be overridden without editing MODULE.bazel by passing the
            RELEASE_TAG_OVERRIDE environment variable via --repo_env, e.g.:
              bazel build --config=tagged --repo_env=RELEASE_TAG_OVERRIDE=rel/0.17.0 //...
            If set, RELEASE_TAG_OVERRIDE takes precedence over this attribute.""",
        ),
        "daily_branch": attr.string(
            default = "develop",
            doc = """Branch name used when BUILD_VARIANT is 'daily'. Always resolves
            to the branch's current HEAD commit at fetch time - intentionally
            NON-hermetic, for Daily Build / Daily Test pipelines only.

            Can be overridden without editing MODULE.bazel by passing the
            RELEASE_BRANCH_OVERRIDE environment variable via --repo_env, e.g.:
              bazel build --repo_env=RELEASE_BRANCH_OVERRIDE=feature/my-branch //...
            If set, RELEASE_BRANCH_OVERRIDE takes precedence over this attribute.""",
        ),
        "build_file_content": attr.string(
            default = "",
            doc = "Optional BUILD.bazel file content to write into the fetched repository root.",
        ),
        "git_env": attr.string_dict(
            default = {},
            doc = "Optional extra environment variables to pass to the git subprocess (e.g. proxy settings).",
        ),
        "timeout": attr.int(
            default = 600,
            doc = "Timeout in seconds for the git clone operation.",
        ),
    },
    environ = ["BUILD_VARIANT", "RELEASE_TAG_OVERRIDE", "RELEASE_BRANCH_OVERRIDE"],
    doc = """Fetches a Git source tree, selecting between a fixed release tag
    (hermetic) and a tracked branch HEAD (non-hermetic, for Daily
    Build/Test, project default) based on the BUILD_VARIANT environment
    variable, forwarded via `--repo_env=BUILD_VARIANT=tagged|daily`.

    In 'tagged' mode, the tag itself can additionally be overridden without
    editing MODULE.bazel via `--repo_env=RELEASE_TAG_OVERRIDE=<tag>`.

    In 'daily' mode, the branch itself can additionally be overridden
    without editing MODULE.bazel via
    `--repo_env=RELEASE_BRANCH_OVERRIDE=<branch>`.

    See documentation/docs/Bazel_Git_Repository_Tag_vs_Branch.md for the
    full rationale and usage guide.""",
)
