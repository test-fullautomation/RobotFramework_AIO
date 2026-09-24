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
    # Installer with Python runtime + Module Set 1 + bunch of own components (test_framework_tng)
    # Output: <installer_name>.exe
    "test_framework_tng": {
        "components": BASE_COMPONENTS + [            # Python interpreter distribution
            "@py_modules_set_1//:py_modules_set_1",  # certain set of additional Python modules (site-packages)
            #
            # own components
            "@robotframework_testsuitesmanagement//:robotframework_testsuitesmanagement",  # PyPI package
            "@python_genpackagedoc//:python_genpackagedoc",  # PyPI package
            "@python_extensions_collection//:python_extensions_collection",  # PyPI package
            "@python_jsonpreprocessor//:python_jsonpreprocessor",  # PyPI package
            "@robotframework_qconnect_base//:robotframework_qconnect_base",  # PyPI package
            "@robotframework_extensions_collection//:robotframework_extensions_collection",  # PyPI package
            "@robotframework_dbus//:robotframework_dbus",  # PyPI package
            "@robotframework_doip//:robotframework_doip",  # PyPI package
            # "@robotframework_uds//:robotframework_uds",  # PyPI package     >>>>>>>>>>>>>>>>>>>>>>>> causes Bazel errors / to be investigated
            "@robotframework_qconnect_winapp//:robotframework_qconnect_winapp",  # PyPI package
            "@robotframework_robotlog2rqm//:robotframework_robotlog2rqm",  # PyPI package
            "@robotframework_robotlog2db//:robotframework_robotlog2db",  # PyPI package
            # "@robotframework_qconnect_dlt//:robotframework_qconnect_dlt",  # Internal Git source (Bosch Bitbucket) - TODO: real git tag/deps still pending
            #
            # further extensions
            "@inno_setup//:iscc", # InnoSetup distribution
            "@vscode//:vscode",   # VS Code portable distribution (Windows x64)
        ],
        "version": "3.12.11",
        "installer_name": "test_framework_tng_setup",
    },

    # Robot Framework and TestsuitesManagement installation
    # Output: <installer_name>.exe
    "rf_testsuitesmanagement": {
        "components": BASE_COMPONENTS + [            # Python interpreter distribution
            "@py_modules_set_1//:py_modules_set_1",  # certain set of additional Python modules (site-packages)
            #
            # own components
            "@robotframework_testsuitesmanagement//:robotframework_testsuitesmanagement",
            #
            # further extensions
            "@inno_setup//:iscc", # InnoSetup distribution
            "@vscode//:vscode",   # VS Code portable distribution (Windows x64)
        ],
        "version": "3.12.11",
        "installer_name": "rf_testsuitesmanagement_setup",
    },

    # Installer with Python runtime + Module Set 2
    # Output: <installer_name>.exe
    "installer_set_2": {
        "components": BASE_COMPONENTS + [            # Python interpreter distribution
            "@py_modules_set_2//:py_modules_set_2",  # certain set of additional Python modules (site-packages)
            "@inno_setup//:iscc",                    # InnoSetup distribution
        ],
        "version": "3.12.11",
        "installer_name": "install_python_set_2",
    },
}
