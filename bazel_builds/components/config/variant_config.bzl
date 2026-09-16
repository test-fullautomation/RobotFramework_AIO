# =============================================================================
# variant_config.bzl - Central Installer Variant Configuration
# =============================================================================
#
# *** THIS IS THE FILE TO EDIT WHEN ADDING/CHANGING INSTALLER VARIANTS. ***
#
# Everything else needed to actually BUILD an installer (the inno_setup_installer
# rule, the create_installer()/create_all_installers() macros, staging logic,
# etc.) lives in components/installer/ (inno_setup.bzl, installer_variants.bzl,
# stage_files.py, build_installer.py). None of that needs to be touched to
# add a new installer variant or to change which components go into an
# existing one - only the two definitions in this file matter for that.
#
# =============================================================================

"""
Central, user-facing configuration for installer variants.

This file intentionally contains ONLY declarative data (which components go
into which installer variant) - no rule/macro logic. It is loaded by
components/installer/installer_variants.bzl via:

    load("@config//:variant_config.bzl", "BASE_COMPONENTS", "INSTALLER_VARIANTS")

Keeping this in its own Bzlmod module ("config", see MODULE.bazel in this
directory) means these two definitions are no longer surrounded by - and
easy to lose track of within - the generic macro/rule plumbing code in
installer_variants.bzl.
"""

# -----------------------------------------------------------------------------
# Base Components
# -----------------------------------------------------------------------------
# Components included in EVERY installer variant.
# These are the core dependencies that all installers share.
#
# NOTE: Public (no leading underscore) so it can be load()-ed from other
# modules - Starlark's load() statement can only import public symbols.
BASE_COMPONENTS = [
    "@python//:python_runtime",  # Python interpreter distribution
    "@inno_setup//:iscc",  # InnoSetup distribution
    # "@robotframework_testsuitesmanagement//:robotframework_testsuitesmanagement",  # RFTSM PyPI package
]

# -----------------------------------------------------------------------------
# Installer Variants
# -----------------------------------------------------------------------------
# Central definition of all installer variants.
# Each key is the target name, each value is a configuration dictionary.
#
# Configuration options:
#   - components: List of component targets (required)
#   - version: Installer version string (optional, default: "1.0.0")
#   - installer_name: Output filename without .exe (optional, default: target name)
#
# To add a new variant:
#   "installer_new_variant": {
#       "components": BASE_COMPONENTS + [
#           "//components/new_module:new_module",
#       ],
#       "version": "1.0.0",
#       "installer_name": "install_python_new_variant",
#   },
#
# No changes to installer_variants.bzl or BUILD.bazel are required - just add
# an entry here.

INSTALLER_VARIANTS = {
    # Installer with Python runtime + Module Set 1
    # Output: install_python_set_1.exe
    "installer_set_1": {
        "components": BASE_COMPONENTS + [
            "@py_modules_set_1//:py_modules_set_1",
            "@robotframework_testsuitesmanagement//:robotframework_testsuitesmanagement",  # RFTSM PyPI package
        ],
        "version": "3.12.11",
        "installer_name": "install_python_set_1",
    },

    # Installer with Python runtime + Module Set 2
    # Output: install_python_set_2.exe
    "installer_set_2": {
        "components": BASE_COMPONENTS + [
            "@py_modules_set_2//:py_modules_set_2",
        ],
        "version": "3.12.11",
        "installer_name": "install_python_set_2",
    },
}
