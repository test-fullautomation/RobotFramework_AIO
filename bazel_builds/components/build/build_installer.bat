@echo off
echo.
echo ========================================
echo Install Python
echo ========================================
echo.

REM Workspace configuration
set BAZEL_EXEC=C:\TAF\tools\bazelisk\bazel.exe

REM Proxy settings
set HTTP_PROXY=...
set HTTPS_PROXY=...
set NO_PROXY=...

REM ----------------------------------------------------------------------
REM Platform selection
REM ----------------------------------------------------------------------
REM The platform can be passed as the first command line argument, e.g.:
REM   build_installer.bat windows
REM   build_installer.bat linux
REM Defaults to "windows" if not specified.
REM
REM "startup" options (--output_base, --output_user_root) cannot use the
REM "startup:windows"/"startup:linux" syntax in .bazelrc - Bazel does not
REM support :config selectors for the startup phase at all. Instead of
REM maintaining these paths here in the batch file, they live in separate
REM platform-specific rc files (.bazelrc.windows / .bazelrc.linux). This
REM script only selects WHICH file to load via --bazelrc=<file>. Note that
REM specifying --bazelrc disables Bazel's automatic workspace .bazelrc
REM lookup, so the main .bazelrc must be passed explicitly as well; both
REM --bazelrc flags are merged (later ones do not replace earlier ones,
REM they add to/override individual options).
REM
REM Note: --config=%PLATFORM% is NOT needed for the build-specific flags
REM (build:windows/build:linux in .bazelrc) - since .bazelrc already sets
REM "build --enable_platform_specific_config", Bazel automatically expands
REM "build" to "build:windows"/"build:linux"/... based on the OS it actually
REM detects at runtime. The PLATFORM variable here is used ONLY to select
REM which startup rc file to load (see --bazelrc=%BAZEL_PLATFORM_RC% below).
set PLATFORM=%1
if "%PLATFORM%"=="" set PLATFORM=windows

if /I "%PLATFORM%"=="windows" (
    set BAZEL_PLATFORM_RC=.bazelrc.windows
) else if /I "%PLATFORM%"=="linux" (
    set BAZEL_PLATFORM_RC=.bazelrc.linux
) else (
    echo ERROR: Unknown platform "%PLATFORM%". Expected "windows" or "linux".
    exit /b 1
)

echo Platform: %PLATFORM%
echo Platform rc file: %BAZEL_PLATFORM_RC%
echo.

%BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% build @installer//:installer_set_1
REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% build @installer//:installer_set_2
REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% build @installer//:all


echo ========================================
echo Batch file returns : %ERRORLEVEL%
echo ========================================

exit /b %ERRORLEVEL%
