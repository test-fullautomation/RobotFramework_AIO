@echo off
echo.
echo ========================================
echo Install Python
echo ========================================
echo.

REM Workspace configuration
set BAZEL_EXEC=C:\TAF\tools\bazelisk\bazel.exe

%BAZEL_EXEC% build //components/python:python_runtime

%BAZEL_EXEC% build //components/py_modules:site_packages

%BAZEL_EXEC% build //components/installer:python_installer

echo ========================================
echo Batch file returns : %ERRORLEVEL%
echo ========================================

exit /b %ERRORLEVEL%

