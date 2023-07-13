@echo off
REM NB: Removing any previous association to be sure new one will work
subst R: /D 1> NUL 2>&1
subst R: "%~dp0..\.."

if "%1"=="" (
    powershell -File "%~dp0\PowerShell\create_project_config.ps1"
) else (
    powershell -File "%~dp0\PowerShell\create_project_config.ps1" -configFile %1
)