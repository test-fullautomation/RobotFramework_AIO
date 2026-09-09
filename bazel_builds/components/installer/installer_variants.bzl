# =============================================================================
# installer_variants.bzl - Macro-Based Installer Variant Generation
# =============================================================================
#
# This module provides macros for generating multiple installer variants from
# a central configuration. It implements the DRY (Don't Repeat Yourself)
# principle by defining installer variants in a single dictionary and
# generating the corresponding Bazel targets automatically.
#
# Architecture:
#   - INSTALLER_VARIANTS: Central dictionary defining all variants
#   - _BASE_COMPONENTS: Components included in every installer
#   - create_installer(): Macro to create a single installer target
#   - create_all_installers(): Macro to generate all defined variants
#
# Usage in BUILD.bazel:
#   load(":installer_variants.bzl", "create_all_installers")
#   create_all_installers()
#
# Adding a new variant:
#   Simply add an entry to INSTALLER_VARIANTS dictionary below.
#   No changes to BUILD.bazel required.
#
# =============================================================================

"""
Macros for generating installer variants.

This module defines Starlark macros that create multiple installer combinations
from the available components. Each variant is defined declaratively in the
INSTALLER_VARIANTS dictionary, and the macros generate the corresponding
Bazel targets during the analysis phase.
"""

load(":inno_setup.bzl", "inno_setup_installer")


def create_installer(
        name,
        components,
        version = "1.0.0",
        installer_name = None,
        iscc_path = "C:/workplace/Programme/InnoSetup/ISCC.exe",
        iss_template = "installer.iss",
        visibility = None):
    """Creates an installer target with the specified components.
    
    This macro generates two targets:
      1. {name}_bundle: A filegroup aggregating all component files
      2. {name}: The actual installer target (inno_setup_installer rule)
    
    The macro wraps the low-level inno_setup_installer rule and provides
    a simpler interface for defining installer variants.
    
    Args:
        name: Name of the installer target.
              Also used as prefix for the bundle filegroup ({name}_bundle).
        
        components: List of component targets to include in the installer.
                    Example: ["//components/python:python_runtime",
                              "//components/py_modules_set_1:py_modules_set_1"]
        
        version: Installer version string (default: "1.0.0").
                 Passed to ISCC.exe and available in ISS script.
        
        installer_name: Base name for the output .exe file (default: same as name).
                        The final output will be {installer_name}.exe
        
        iscc_path: Absolute path to ISCC.exe on the build machine.
        
        iss_template: Path to the Inno Setup script template (.iss file).
        
        visibility: Bazel visibility for the generated targets.
    
    Generated Targets:
        //{package}:{name}_bundle  - Filegroup containing all component files
        //{package}:{name}         - Installer target producing {installer_name}.exe
    """
    bundle_name = name + "_bundle"
    
    # Use target name as installer name if not specified
    if installer_name == None:
        installer_name = name
    
    # Create a filegroup that aggregates all component files for this variant.
    # This bundle is marked private since it's an implementation detail;
    # users should reference the installer target, not the bundle.
    native.filegroup(
        name = bundle_name,
        srcs = components,
        visibility = ["//visibility:private"],
    )
    
    # Create the actual installer target using the inno_setup_installer rule.
    # This target depends on the bundle and produces the final .exe file.
    inno_setup_installer(
        name = name,
        bundle = [":" + bundle_name],
        iss_template = iss_template,
        iscc_path = iscc_path,
        version = version,
        installer_name = installer_name,
        visibility = visibility,
    )


# =============================================================================
# Installer Variant Configuration
# =============================================================================
# This section defines all available installer variants in a declarative way.
# To add a new variant, simply add an entry to INSTALLER_VARIANTS.

# Base components included in EVERY installer variant.
# These are the core dependencies that all installers share.
# Using a private variable (underscore prefix) to indicate this is
# an internal implementation detail, not meant for external use.
_BASE_COMPONENTS = [
    "@python//:python_runtime",  # Python interpreter distribution
]

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
#       "components": _BASE_COMPONENTS + [
#           "//components/new_module:new_module",
#       ],
#       "version": "1.0.0",
#       "installer_name": "install_python_new_variant",
#   },

INSTALLER_VARIANTS = {
    # Installer with Python runtime + Module Set 1
    # Output: install_python_set_1.exe
    "installer_set_1": {
        "components": _BASE_COMPONENTS + [
            "@py_modules_set_1//:py_modules_set_1",
        ],
        "version": "3.12.11",
        "installer_name": "install_python_set_1",
    },
    
    # Installer with Python runtime + Module Set 2
    # Output: install_python_set_2.exe
    "installer_set_2": {
        "components": _BASE_COMPONENTS + [
            "@py_modules_set_2//:py_modules_set_2",
        ],
        "version": "3.12.11",
        "installer_name": "install_python_set_2",
    },
}


def create_all_installers(
        iscc_path = "C:/workplace/Programme/InnoSetup/ISCC.exe",
        iss_template = "installer.iss",
        visibility = None):
    """Creates all installer variants defined in INSTALLER_VARIANTS.
    
    This macro iterates over the INSTALLER_VARIANTS dictionary and calls
    create_installer() for each entry. It is typically called once in the
    BUILD.bazel file to generate all standard installer targets.
    
    Args:
        iscc_path: Absolute path to ISCC.exe (shared by all variants).
        
        iss_template: Path to ISS template file (shared by all variants).
        
        visibility: Bazel visibility for all generated targets.
    
    Generated Targets (based on current INSTALLER_VARIANTS):
        //components/installer:installer_set_1         -> install_python_set_1.exe
        //components/installer:installer_set_1_bundle  -> (internal filegroup)
        //components/installer:installer_set_2         -> install_python_set_2.exe
        //components/installer:installer_set_2_bundle  -> (internal filegroup)
    
    Usage:
        # In BUILD.bazel:
        load(":installer_variants.bzl", "create_all_installers")
        
        create_all_installers(
            visibility = ["//visibility:public"],
        )
    """
    for variant_name, config in INSTALLER_VARIANTS.items():
        create_installer(
            name = variant_name,
            components = config["components"],
            version = config.get("version", "1.0.0"),
            installer_name = config.get("installer_name", variant_name),
            iscc_path = iscc_path,
            iss_template = iss_template,
            visibility = visibility,
        )

