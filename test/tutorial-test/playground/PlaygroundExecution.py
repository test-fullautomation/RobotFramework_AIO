# **************************************************************************************************************
#
#  Copyright 2020-2022 Robert Bosch GmbH
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
# PlaygroundExecution.py
#
# XC-CT/ECA3-Queckenstedt
#

# --------------------------------------------------------------------------------------------------------------
#
# 15.02.2023
#
# --------------------------------------------------------------------------------------------------------------
# TM***
# TOC:
# [CONFIG]
# [EXECUTION]
# --------------------------------------------------------------------------------------------------------------

import os, sys, platform, shlex, subprocess, shutil, argparse, ctypes

import colorama as col

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.Folder.CFolder import CFolder
from PythonExtensionsCollection.Utils.CUtils import *
from PythonExtensionsCollection.Comparison.CComparison import CComparison

col.init(autoreset=True)

COLBR = col.Style.BRIGHT + col.Fore.RED
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLBG = col.Style.BRIGHT + col.Fore.GREEN

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

def printerror(sMsg):
    sys.stderr.write(COLBR + f"{sMsg}!\n\n")

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

# --------------------------------------------------------------------------------------------------------------

sReferencePath = sThisScriptPath

print()
print(COLBY + f"* Reference path: '{sReferencePath}'")

# --------------------------------------------------------------------------------------------------------------
# TM***
# [CONFIG]

LOGNAME = "PlaygroundLog"

# without variant configuration
sRobotFile_1    = CString.NormalizePath("./exercise-pg-1.robot", sReferencePathAbs=sReferencePath)
# with variant configuration
sRobotFile_2    = CString.NormalizePath("./exercise-pg-2.robot", sReferencePathAbs=sReferencePath)
# with variant configuration
sRobotFile_3    = CString.NormalizePath("./testsuites/exercise-pg-ts.robot", sReferencePathAbs=sReferencePath)
sTestsuitesPath = CString.NormalizePath("./testsuites", sReferencePathAbs=sReferencePath)

sSource = sRobotFile_2

# local config
# os.environ['ROBOT_LOCAL_CONFIG'] = f"..."

print(COLBY + f"* Source........: '{sSource}'")
print()

listCmdLineParts = []
listCmdLineParts.append(f"\"{sPython}\"")
listCmdLineParts.append(f"-m robot")
listCmdLineParts.append(f"-d")
listCmdLineParts.append(f"\"{sThisScriptPath}/playgroundlogfiles\"")
listCmdLineParts.append(f"-o")
listCmdLineParts.append(f"\"{sThisScriptPath}/playgroundlogfiles/{LOGNAME}.xml\"")
listCmdLineParts.append(f"-l")
listCmdLineParts.append(f"\"{sThisScriptPath}/playgroundlogfiles/{LOGNAME}_log.html\"")
listCmdLineParts.append(f"-r")
listCmdLineParts.append(f"\"{sThisScriptPath}/playgroundlogfiles/{LOGNAME}_report.html\"")
listCmdLineParts.append(f"-b")
listCmdLineParts.append(f"\"{sThisScriptPath}/playgroundlogfiles/{LOGNAME}.log\"")
#
# TM***
#
METADATA     = None
VARIABLE     = None
VARIANT      = None
CONFIG_FILE  = None
LOCAL_CONFIG = None
#
# METADATA    = "--metadata version_sw:1.2.3"
# METADATA    = "--metadata version_Hw:2.3.4"
# METADATA    = "--metadata version_test:3.4.5"
# METADATA    = "--metadata version_sw:1.2.3 --metadata version_Hw:2.3.4 --metadata version_test:3.4.5"
# METADATA    = "--metadata my_cmdline_metadata:my_cmdline_metadata_value"
# METADATA    = "--metadata my_test_local_metadata:my_test_local_metadata_cmdline_value"
# VARIABLE     = "--variable teststring:\"command line test string\""
# VARIABLE     = "--variable teststring_common:\"command line test string common\""
# VARIABLE     = "--variable teststring_variant:\"command line test string variant\""
# VARIABLE     = "--variable teststring_bench:\"command line test string bench\""
# VARIABLE     = "--variable teststring_common:\"command line test string common\" --variable teststring_variant:\"command line test string variant\" --variable teststring_bench:\"command line test string bench\""
# VARIANT      = "--variable variant:\"variant1\""
# VARIANT      = "--variable variant:\"variant2\""
# VARIANT      = "--variable variant:\"inv/alid\""
# VARIANT      = "--variable variant:\"    \""
# VARIANT      = "--variable variant:\"SälfTest.ß.€.考.𠼭.𠼭\""
# VARIANT      = "--variable variant:\".\localconfig\exercise-pg_localconfig_bench1.json\""
# CONFIG_FILE  = "--variable config_file:\"./config/exercise-pg_config_variant1.json\""          # path relative to position of robot file
# CONFIG_FILE  = "--variable config_file:\"./config/exercise-pg_config_variant2.json\""          # path relative to position of robot file
# CONFIG_FILE  = "--variable config_file:\"./config/not_existing.json\""                         # path relative to position of robot file
# CONFIG_FILE  = "--variable config_file:\"./localconfig/exercise-pg_localconfig_bench1.json\""  # path relative to position of robot file
# LOCAL_CONFIG = "--variable local_config:\"./localconfig/exercise-pg_localconfig_bench1.json\"" # path relative to position of robot file
# LOCAL_CONFIG = "--variable local_config:\"./localconfig/exercise-pg_localconfig_bench2.json\"" # path relative to position of robot file
# LOCAL_CONFIG = "--variable local_config:\"./localconfig/not_existing.json\""                   # path relative to position of robot file
#
# TM***
#
if METADATA is not None:
   listCmdLineParts.append(METADATA)
if VARIABLE is not None:
   listCmdLineParts.append(VARIABLE)
if VARIANT is not None:
   listCmdLineParts.append(VARIANT)
if CONFIG_FILE is not None:
   listCmdLineParts.append(CONFIG_FILE)
if LOCAL_CONFIG is not None:
   listCmdLineParts.append(LOCAL_CONFIG)
#
listCmdLineParts.append(f"\"{sSource}\"")

# --------------------------------------------------------------------------------------------------------------
# TM***
# [EXECUTION]

sCmdLine = " ".join(listCmdLineParts)
del listCmdLineParts
print(f"Now executing command line:\n{sCmdLine}")
print()
listCmdLineParts = shlex.split(sCmdLine)
nReturn = ERROR
try:
   nReturn = subprocess.call(listCmdLineParts)
   print()
   bSuccess = True
   sResult  = f"Robot Framework returned {nReturn}"
   print(CString.FormatResult(sThisScriptName, bSuccess, sResult))
except Exception as ex:
   print()
   printerror(CString.FormatResult(sThisScriptName, bSuccess=None, sResult=str(ex)))
print()

if 'ROBOT_LOCAL_CONFIG' in os.environ:
   del os.environ['ROBOT_LOCAL_CONFIG']

sys.exit(nReturn)

# --------------------------------------------------------------------------------------------------------------
