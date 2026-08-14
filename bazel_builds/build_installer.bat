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

REM %BAZEL_EXEC% build //components/installer:installer_set_1
REM %BAZEL_EXEC% build //components/installer:installer_set_2
%BAZEL_EXEC% build //components/installer:all


echo ========================================
echo Batch file returns : %ERRORLEVEL%
echo ========================================

exit /b %ERRORLEVEL%

