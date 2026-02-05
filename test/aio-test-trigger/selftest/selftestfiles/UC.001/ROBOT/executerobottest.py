# **************************************************************************************************************
#
#  Copyright 2020-2023 Robert Bosch GmbH
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
# executerobottest.py
#
# XC-CT/ECA3-Queckenstedt
#
# Executes robot tests recursively in current folder.
# Log file can be set in command line. If not, default log is written.
# Additional command line for involved framework can also be set in command line (of this script).
#
# --------------------------------------------------------------------------------------------------------------
#
# 09.11.2022
#
# --------------------------------------------------------------------------------------------------------------

import os, sys, platform, shlex, subprocess, shutil, argparse

import colorama as col

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Folder.CFolder import CFolder

col.init(autoreset=True)

COLBR = col.Style.BRIGHT + col.Fore.RED
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
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
sThisScript     = CString.NormalizePath(sThisScript)
sThisScriptPath = os.path.dirname(sThisScript)
sThisScriptName = os.path.basename(sThisScript)

sOSName         = os.name
sPlatformSystem = platform.system()
sPythonPath     = CString.NormalizePath(os.path.dirname(sys.executable))
sPython         = CString.NormalizePath(sys.executable)
sPythonVersion  = sys.version

if sPlatformSystem == "Windows":
    # nothing specific to do
    pass
elif sPlatformSystem == "Linux":
    # nothing specific to do
    pass
else:
   bSuccess = False
   sResult  = f"Operating system {sPlatformSystem} ({sOSName}) not supported"
   printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
   sys.exit(ERROR)

print()
print(f"{sThisScriptName} is running under {sPlatformSystem} ({sOSName})")
print()

# -- parse the command line of this script (optional path and name of robot xml log file)

oCmdLineParser = argparse.ArgumentParser()
oCmdLineParser.add_argument('--logfile', type=str, help='Path and name of XML log file (optional).')
oCmdLineParser.add_argument('--robotcommandline', type=str, help='Command line for RobotFramework AIO (optional).')
oCmdLineArgs = oCmdLineParser.parse_args()

sLogFile = None
if oCmdLineArgs.logfile is not None:
   sLogFile = CString.NormalizePath(oCmdLineArgs.logfile, sReferencePathAbs=sThisScriptPath)
else:
   # default log
   sLogFile = f"{sThisScriptPath}/logfiles/RobotTestLog.xml"

sRobotCommandLine = None
if oCmdLineArgs.robotcommandline is not None:
   sRobotCommandLine = oCmdLineArgs.robotcommandline

# -- create the log file folder

oLogFile = CFile(sLogFile)
dLogFileInfo     = oLogFile.GetFileInfo()
sLogFilePath     = dLogFileInfo['sFilePath']
sLogFileName     = dLogFileInfo['sFileName']
sLogFileNameOnly = dLogFileInfo['sFileNameOnly']

oLogFilePath = CFolder(sLogFilePath)
bSuccess, sResult = oLogFilePath.Create(bOverwrite=False, bRecursive=True)
del oLogFilePath
if bSuccess is not True:
   printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
   sys.exit(ERROR)
print(sResult)
print()

# -- prepare the command line for the test execution

listCmdLineParts = []
listCmdLineParts.append(f"\"{sPython}\"")
listCmdLineParts.append("-m robot")
if sRobotCommandLine is not None:
   listCmdLineParts.append(f"{sRobotCommandLine}")
listCmdLineParts.append(f"-d \"{sLogFilePath}\"")
listCmdLineParts.append(f"-o \"{sLogFileName}\"")
listCmdLineParts.append(f"-l \"{sLogFileNameOnly}_log.html\"")
listCmdLineParts.append(f"-r \"{sLogFileNameOnly}_report.html\"")
listCmdLineParts.append(f"-b \"{sLogFileNameOnly}.log\"")
listCmdLineParts.append(f"\"{sThisScriptPath}\"")
sCmdLine = " ".join(listCmdLineParts)
del listCmdLineParts

# -- execute the tests

print(f"Now executing command line:\n{sCmdLine}")
print()

listCmdLineParts = shlex.split(sCmdLine)

nReturn = ERROR
try:
   nReturn = subprocess.call(listCmdLineParts)
   print()
   print(f"[{sThisScriptName}] : Subprocess ROBOT returned {nReturn}")
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
   printerror(f"[{sThisScriptName}] : Subprocess ROBOT has not returned expected value {SUCCESS}")
   nReturn = -nReturn

print()

# nReturn:
# > 0  : internal error of this script
# < 0  : return value (!= 0) from subprocess
# == 0 : no internal error of this script and no error from subprocess

sys.exit(nReturn)

# --------------------------------------------------------------------------------------------------------------
