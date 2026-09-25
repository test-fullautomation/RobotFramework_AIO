@echo off
echo.
echo ========================================
echo Install Framework
echo ========================================
echo.

REM Workspace configuration
set BAZEL_EXEC=C:\TAF\tools\bazelisk\bazel.exe

REM Proxy settings
set HTTP_PROXY=...
set HTTPS_PROXY=...
set NO_PROXY=...

REM Git Token
set GIT_TOKEN=...

REM ----------------------------------------------------------------------
REM GitHub authentication via _netrc (see components/python-extensions-
REM collection/MODULE.bazel, option 4: "Alternative for CI/automation").
REM ----------------------------------------------------------------------
REM git_repository() has no token/credential attribute of its own - it just
REM shells out to `git fetch`/`git checkout`. For a private GitHub repo
REM (like python-extensions-collection now uses), Git itself must already
REM be configured to authenticate. The _netrc file is the standard way to
REM do this non-interactively: Git for Windows reads "%HOME%\_netrc" (note:
REM underscore, not a leading dot, on Windows) for HTTPS credentials.
REM
REM A pre-existing _netrc is backed up first and restored afterwards (in
REM the "Cleanup" section near the end of this script), so this script
REM never permanently overwrites a file that may already contain unrelated
REM credentials for other hosts.
REM
REM SECURITY NOTE: GIT_TOKEN is currently hardcoded above for convenience.
REM Since this file may be version-controlled, treat it as SENSITIVE -
REM do not commit real tokens; prefer sourcing GIT_TOKEN from an external,
REM untracked file or the calling CI system's secret store instead.
set NETRC_FILE=%USERPROFILE%\_netrc
set NETRC_BACKUP=%USERPROFILE%\_netrc.bak_build_installer
set NETRC_DID_BACKUP=0

if exist "%NETRC_FILE%" (
    set NETRC_DID_BACKUP=1
    move /Y "%NETRC_FILE%" "%NETRC_BACKUP%" >nul
)

(
    echo machine github.com
    echo login x-access-token
    echo password %GIT_TOKEN%
) > "%NETRC_FILE%"

echo _netrc written to: %NETRC_FILE%
echo.

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

REM set
REM %BAZEL_EXEC% info --show_make_env
REM %BAZEL_EXEC% info client-env


REM start from scratch
%BAZEL_EXEC% clean --expunge


REM BASIC CALLS:

REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% build @installer//:test_framework_tng
REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% build @installer//:rf_testsuitesmanagement
REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% build @installer//:installer_set_2
REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% build @installer//:all

REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% build @inno_setup//:iscc

REM DEBUGGING:
REM - test run without disk cache, to detect hidden cache dependencies:
REM     %BAZEL_EXEC% ... build --disk_cache= ...
REM - or with new output_base (simulating a new computer)
REM     %BAZEL_EXEC% ... --output_base=C:/bazel_out_fresh_test build ...

REM EXTENDED CALLS:
REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% build --disk_cache= @installer//:test_framework_tng
REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% build --disk_cache= @installer//:installer_set_2
REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% build --disk_cache= @installer//:all


REM (1) daily build based on latest commit in develop branch (default, no further command line extension)
REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% --output_base=C:/B16 build --disk_cache= @installer//:test_framework_tng

REM (2) build based on tag
REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% --output_base=C:/B13 build --config=tagged --repo_env=RELEASE_TAG_OVERRIDE=rel/0.17.0 --disk_cache= @installer//:test_framework_tng

REM (2b) daily build based on a different branch than daily_branch's MODULE.bazel default
%BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% --output_base=C:/B18 build --repo_env=RELEASE_BRANCH_OVERRIDE=develop --disk_cache= @installer//:test_framework_tng

REM another target
REM %BAZEL_EXEC% --bazelrc=.bazelrc --bazelrc=%BAZEL_PLATFORM_RC% --output_base=C:/BO8 build --disk_cache= @installer//:rf_testsuitesmanagement

REM Capture the build's exit code immediately - it would otherwise be
REM overwritten by the "bazel shutdown" call below before we get to check it.
set BUILD_EXITCODE=%ERRORLEVEL%


REM Bazel shutdown to remove file handles to enable to delete previus output in Windows explorer
%BAZEL_EXEC% shutdown

REM ----------------------------------------------------------------------
REM Cleanup: remove the temporary _netrc / restore the previous one
REM ----------------------------------------------------------------------
REM Always runs, regardless of whether the build succeeded or failed, so
REM the GitHub token never lingers on disk longer than this script's
REM execution, and any pre-existing _netrc (with unrelated credentials for
REM other hosts) is put back exactly as it was found.
del /F /Q "%NETRC_FILE%" >nul 2>&1
if "%NETRC_DID_BACKUP%"=="1" (
    move /Y "%NETRC_BACKUP%" "%NETRC_FILE%" >nul
    echo Restored previous _netrc: %NETRC_FILE%
) else (
    echo Removed temporary _netrc: %NETRC_FILE%
)
echo.

echo ========================================
echo Batch file returns : %BUILD_EXITCODE%
echo ========================================

exit /b %BUILD_EXITCODE%
