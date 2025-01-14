@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
  set "directory=%cd%"
) else (
  set "directory=%~1"
)

echo The directory is set to: %directory%

set "app="
for /f "tokens=*" %%a in ('dir /b !directory!\*.exe') do (
    if not defined app (
        set "app=%%~na"
        start /wait "" "!directory!\%%a" /SILENT /NORESTART /SUPPRESSMSGBOXES /LOG=install-windows.log
        if !errorlevel! equ 0 (
            echo !app! installation successful.
        ) else (
            echo !app! installation failed.
            exit 1
        )
    )
)

if not defined app (
    echo No executable file found in current directory.
)
