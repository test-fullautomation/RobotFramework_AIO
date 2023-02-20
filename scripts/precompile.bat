@echo off
REM NB: Removing any previous association to be sure new one will work
subst A: /D 1> NUL 2>&1
subst A: "%~dp0..\.."

if "%1"=="" (
    powershell -File "%~dp0\scripts\PowerShell\create_project_config.ps1"
) else (
    powershell -File "%~dp0\scripts\PowerShell\create_project_config.ps1 %1"
)