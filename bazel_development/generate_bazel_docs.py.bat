@echo off
"%RobotPythonPath%/python.exe" "./tools/generate_bazel_docs.py" . -o bazel_docs
REM "%RobotPythonPath%/python.exe" "./tools/generate_bazel_docs.py" ./python-jsonpreprocessor -o bazel_docs
echo ==============================================================================================================
echo generate_bazel_docs.py returns : %ERRORLEVEL%
echo ==============================================================================================================
