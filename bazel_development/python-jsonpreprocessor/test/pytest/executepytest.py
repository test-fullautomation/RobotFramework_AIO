# **************************************************************************************************************
#
#  Copyright 2020-2026 Robert Bosch GmbH
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# **************************************************************************************************************
#
# executepytest.py
#
# XC-HWP/ESW3-Queckenstedt
#
# Executes pytest recursively in current folder.
# Log file can be set in command line. If not, default log is written.
# Additional command line for involved framework can also be set in command line (of this script).
#
# --------------------------------------------------------------------------------------------------------------
#
# 04.08.2026
#
# --------------------------------------------------------------------------------------------------------------

import os, sys, platform, shlex, subprocess, argparse, ntpath

import colorama as col

col.init(autoreset=True)

COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

def printerror(sMsg):
    sys.stderr.write(COLBR + f"Error: {sMsg}!\n")

def printexception(sMsg):
    sys.stderr.write(COLBR + f"Exception: {sMsg}!\n")

# --------------------------------------------------------------------------------------------------------------

# -- some informations about the environment of this script

sThisScript     = sys.argv[0]
sThisScript     = ntpath.normpath(sThisScript)
sThisScriptPath = os.path.dirname(sThisScript)
sThisScriptName = os.path.basename(sThisScript)

sOSName         = os.name
sPlatformSystem = platform.system()
sPythonPath     = ntpath.normpath(os.path.dirname(sys.executable))
sPython         = ntpath.normpath(sys.executable)
sPythonVersion  = sys.version

print()
print(f"{sThisScriptName} is running under {sPlatformSystem} ({sOSName})")
print()

# -- parse the command line of this script (optional path and name of pytest xml log file)

oCmdLineParser = argparse.ArgumentParser()
oCmdLineParser.add_argument('--logfile', type=str, help='Path and name of XML log file (optional).')
oCmdLineParser.add_argument('--pytestcommandline', type=str, help='Command line for Python pytest module (optional).')
oCmdLineArgs = oCmdLineParser.parse_args()

# Determine log file location
# Priority: 1. XML_OUTPUT_FILE (Bazel), 2. Command line, 3. TEST_UNDECLARED_OUTPUTS_DIR (Bazel), 4. TEST_LOGFILE (external), 5. Default
xml_log_file = None

# Check for Bazel's XML_OUTPUT_FILE environment variable (highest priority)
xml_output_file_env = os.environ.get("XML_OUTPUT_FILE")
if xml_output_file_env:
   # Bazel test: Use the path provided by Bazel
   xml_log_file = ntpath.normpath(xml_output_file_env)
elif oCmdLineArgs.logfile is not None:
   # Command line argument has second priority
   xml_log_file = ntpath.normpath(oCmdLineArgs.logfile)
else:
   # Check if running in Bazel test environment
   sTestUndeclaredOutputsDir = os.environ.get("TEST_UNDECLARED_OUTPUTS_DIR")
   if sTestUndeclaredOutputsDir:
      # Bazel test: Write to undeclared outputs (will be copied to bazel-testlogs)
      xml_log_file = ntpath.normpath(os.path.join(sTestUndeclaredOutputsDir, "pytest_results.xml"))
   else:
      # Direct execution or bazel run: Use TEST_LOGFILE if available
      xml_log_file = os.environ.get("TEST_LOGFILE")
      if xml_log_file:
         xml_log_file = ntpath.normpath(xml_log_file)
      else:
         # Fallback
         xml_log_file = f"{sThisScriptPath}/logfiles/PyTestLog.xml"

# -- create the log file folder
xml_log_file_path = os.path.dirname(xml_log_file)
if not os.path.isdir(xml_log_file_path):
   try:
      os.makedirs(xml_log_file_path)
   except Exception as ex:
      print()
      printexception(str(ex))
      print()
      sys.exit(ERROR)

print(f"Test log file '{xml_log_file}'")
print()

sPytestCommandLine = None
if oCmdLineArgs.pytestcommandline is not None:
   sPytestCommandLine = oCmdLineArgs.pytestcommandline

# -- prepare the command line for the test execution

# pytest.ini
# The complete absolute path deactivates the pytest internal automatic search for this file.
# This enables to use a specific pytest.ini file individually by every component - even in case
# of a common target call like '//...' (because in this case the Bazel root folder would be used
# as starting point for the search for pytest.ini files - and this would go wrong).
pytest_ini = ntpath.normpath(os.path.join(os.path.dirname(__file__), "pytest.ini"))
listCmdLineParts = []
listCmdLineParts.append(f"\"{sPython}\"")
listCmdLineParts.append("-m pytest")
if sPytestCommandLine:
   listCmdLineParts.append(f"{sPytestCommandLine}")
listCmdLineParts.append(f"-c \"{pytest_ini}\"")
listCmdLineParts.append("--show-capture=all")
listCmdLineParts.append(f"--junitxml=\"{xml_log_file}\"")
listCmdLineParts.append(f"\"{sThisScriptPath}\"")
sCmdLine = " ".join(listCmdLineParts)
del listCmdLineParts

# -- execute the tests

print(f"Now executing command line:\n{sCmdLine}")
print()

listCmdLineParts = shlex.split(sCmdLine)

# Pass the current environment to subprocess to inherit PYTHONPATH set by Bazel
env = os.environ.copy()
# Set PYTHONPATH from sys.path so subprocess can find pytest and other modules
env['PYTHONPATH'] = os.pathsep.join(sys.path)

nReturn = ERROR
try:
   nReturn = subprocess.call(listCmdLineParts, env=env)
   print()
   print(f"[{sThisScriptName}] : Subprocess PYTEST returned {nReturn}")
except Exception as ex:
   print()
   printexception(str(ex))
   print()
   sys.exit(ERROR)
print()

if nReturn == SUCCESS:
   print(f"Test results in '{xml_log_file}'")
   print()
   print(COLBG + f"{sThisScriptName} done")
else:
   printerror(f"[{sThisScriptName}] : Subprocess PYTEST has not returned expected value {SUCCESS}")
   nReturn = -nReturn

print()

# nReturn:
# > 0  : internal error of this script
# < 0  : return value (!= 0) from subprocess
# == 0 : no internal error of this script and no error from subprocess

sys.exit(nReturn)

# --------------------------------------------------------------------------------------------------------------
