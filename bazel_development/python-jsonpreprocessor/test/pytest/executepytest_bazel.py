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
# 14.07.2026
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
# Priority: 1. Command line, 2. TEST_UNDECLARED_OUTPUTS_DIR (Bazel), 3. TEST_LOGFILE (external), 4. Default
sLogFile = None

if oCmdLineArgs.logfile is not None:
   # Command line argument has highest priority
   sLogFile = ntpath.normpath(oCmdLineArgs.logfile)
else:
   # Check if running in Bazel test environment
   sTestUndeclaredOutputsDir = os.environ.get("TEST_UNDECLARED_OUTPUTS_DIR")
   if sTestUndeclaredOutputsDir:
      # Bazel test: Write to undeclared outputs (will be copied to bazel-testlogs)
      sLogFile = os.path.join(sTestUndeclaredOutputsDir, "pytest_results.xml")
      # Store target logfile path for later reference
      sTargetLogFile = os.environ.get("TEST_LOGFILE")
      if sTargetLogFile:
         print(f"Running in Bazel test environment")
         print(f"XML will be written to: {sLogFile}")
         print(f"Target logfile location: {sTargetLogFile}")
   else:
      # Direct execution or bazel run: Use TEST_LOGFILE if available
      sLogFile = os.environ.get("TEST_LOGFILE")
      if sLogFile:
         sLogFile = ntpath.normpath(sLogFile)
      else:
         # Fallback default
         sLogFile = f"{sThisScriptPath}/logfiles/PyTestLog.xml"

sPytestCommandLine = None
if oCmdLineArgs.pytestcommandline is not None:
   sPytestCommandLine = oCmdLineArgs.pytestcommandline

# -- create the log file folder

sLogFilePath = os.path.dirname(sLogFile)
if not os.path.isdir(sLogFilePath):
   try:
      os.makedirs(sLogFilePath)
   except Exception as ex:
      print()
      printexception(str(ex))
      print()
      sys.exit(ERROR)

# -- prepare the command line for the test execution

listCmdLineParts = []
listCmdLineParts.append(f"\"{sPython}\"")
listCmdLineParts.append("-m pytest")
if sPytestCommandLine:
   listCmdLineParts.append(f"{sPytestCommandLine}")
listCmdLineParts.append("--show-capture=all")
listCmdLineParts.append(f"--junitxml=\"{sLogFile}\"")
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
   print(f"Test results in '{sLogFile}'")
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
