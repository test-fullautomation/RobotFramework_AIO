@echo off

echo.
echo =================
echo Bazel Test Runner
echo =================
echo.

REM Workspace configuration
set WORKSPACE_ROOT=C:\workplace\ROBFW\components\bazel_aio
set BAZEL_EXEC=C:\TAF\tools\bazelisk\bazel.exe

REM Proxy settings
set HTTP_PROXY=
set HTTPS_PROXY=
set NO_PROXY=

REM Bazel shell (required for 'bazel test'; select any Bazel compatible bash)
set BAZEL_SH="C:\Program Files\Git\usr\bin\bash.exe"

echo Workspace Root  : %WORKSPACE_ROOT%
echo.

%BAZEL_EXEC% test --build_event_json_file=bep_2.json //python-jsonpreprocessor/...

echo ---------------------------------------
echo Batch returned ERRORLEVEL : %ERRORLEVEL%
echo ---------------------------------------

exit /b %ERRORLEVEL%
