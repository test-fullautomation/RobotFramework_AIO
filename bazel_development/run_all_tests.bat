@echo off
REM ================================================================
REM run_all_tests.bat - Wrapper für run_all_tests.py
REM 
REM Runs all Bazel test targets separately for pytest.ini isolation.
REM JUnit XML log files are automatically derived from target names.
REM ================================================================

echo.
echo ========================================
echo Bazel Test Runner - pytest.ini Isolation
echo ========================================
echo.

REM Workspace configuration
set WORKSPACE_ROOT=C:\workplace\ROBFW\components\bazel_aio
set LOGFILE_BASE_DIR=%WORKSPACE_ROOT%\test_logfiles
set BAZEL_EXEC=C:\TAF\tools\bazelisk\bazel.exe

REM Proxy settings
set HTTP_PROXY=
set HTTPS_PROXY=
set NO_PROXY=

REM Bazel shell (required for 'bazel test'; select any Bazel compatible bash)
set BAZEL_SH="C:\Program Files\Git\usr\bin\bash.exe"

echo Workspace Root  : %WORKSPACE_ROOT%
echo Logfile Base Dir: %LOGFILE_BASE_DIR%
echo.

REM -- Filter by folder name
REM "%RobotPythonPath%/python.exe" run_all_tests.py --workspace-root "%WORKSPACE_ROOT%" --logfile-base-dir "%LOGFILE_BASE_DIR%" --no-cache %*
REM "%RobotPythonPath%/python.exe" run_all_tests.py --workspace-root "%WORKSPACE_ROOT%" --logfile-base-dir "%LOGFILE_BASE_DIR%" --pattern //test_trigger/components/py_test_module_2/... %*
REM "%RobotPythonPath%/python.exe" run_all_tests.py --workspace-root "%WORKSPACE_ROOT%" --logfile-base-dir "%LOGFILE_BASE_DIR%" --pattern //test_trigger/components/py_test_module_2/... --no-cache %*

REM -- Filter by target name
REM "%RobotPythonPath%/python.exe" run_all_tests.py --workspace-root "%WORKSPACE_ROOT%" --logfile-base-dir "%LOGFILE_BASE_DIR%" --pattern "attr('name', 'execute_.*', //test_trigger/components/...)" --no-cache %*
REM "%RobotPythonPath%/python.exe" run_all_tests.py --workspace-root "%WORKSPACE_ROOT%" --logfile-base-dir "%LOGFILE_BASE_DIR%" --pattern "attr('name', 'execute_robot_.*', //test_trigger/components/...)" --no-cache %*
REM "%RobotPythonPath%/python.exe" run_all_tests.py --workspace-root "%WORKSPACE_ROOT%" --logfile-base-dir "%LOGFILE_BASE_DIR%" --pattern "attr('name', 'execute_py_test_.*', //test_trigger/components/...)" --no-cache %*

REM with --verbose und --continue-on-error
REM "%RobotPythonPath%/python.exe" run_all_tests.py --workspace-root "%WORKSPACE_ROOT%" --logfile-base-dir "%LOGFILE_BASE_DIR%" --verbose --continue-on-error %*


REM Python independend
REM C:\TAF\tools\bazelisk\bazel.exe run //:run_all_tests  --check_direct_dependencies=off

echo ---------------------------------------
echo Batch returned ERRORLEVEL : %ERRORLEVEL%
echo ---------------------------------------

exit /b %ERRORLEVEL%
