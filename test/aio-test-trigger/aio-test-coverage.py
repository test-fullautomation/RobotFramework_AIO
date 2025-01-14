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
# aio-test-coverage.py
#
# XC-CT/EMC51-Mai Minh Tri
#
# --------------------------------------------------------------------------------------------------------------
#
# 06.10.2024
#
# --------------------------------------------------------------------------------------------------------------

import os, sys, shlex, subprocess, ctypes
import colorama as col
from libs.CTestTriggerConfig import CTestTriggerConfig
from PythonExtensionsCollection.String.CString import CString

col.init(autoreset=True)
COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN
COLBY = col.Style.BRIGHT + col.Fore.YELLOW

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

def printerror(sMsg):
   sys.stderr.write(COLBR + f"{sMsg}!\n")

def printexception(sMsg):
   sys.stderr.write(COLBR + f"Exception: {sMsg}!\n")

# --------------------------------------------------------------------------------------------------------------

from libs.CTestTriggerConfig import CTestTriggerConfig

nReturn  = ERROR
bSuccess = None
sResult  = "UNKNOWN"
nCntSubProcessErrors = 0
nCntComponent = 0
# -- setting up the test trigger configuration (relative to the path of this script)
try:
   oTestTriggerConfig = CTestTriggerConfig(os.path.abspath(sys.argv[0]))
except Exception as ex:
   print()
   printerror(str(ex))
   print()
   sys.exit(ERROR)

# -- setting up the test trigger
try:
   listofdictComponents = oTestTriggerConfig.Get('COMPONENTS')
   PLATFORMSYSTEM = oTestTriggerConfig.Get('PLATFORMSYSTEM')
   nNrOfComponents = len(listofdictComponents)
   PYTHON = oTestTriggerConfig.Get('PYTHON')

   for dictComponent in listofdictComponents:
      if "robotframework-robotlog2rqm" in dictComponent['COMPONENTROOTPATH'].lower():
         continue
      nCntComponent = nCntComponent + 1
      # -- get data for test execution
      TESTTYPE          = dictComponent['TESTTYPE']
      TESTFOLDER        = dictComponent['TESTFOLDER']
      COMPONENTROOTPATH = dictComponent['COMPONENTROOTPATH']

      sCoverageFile = CString.NormalizePath(f"\"{TESTFOLDER}/coverage/coverage.py\"")

      # -- Handle repositories that cannot run coverage. These will be removed after coverage is completed.
      from pathlib import Path
      try:
         file_path = Path(sCoverageFile)
         if file_path.exists():
            pass
         else:
            continue
      except:
         pass  # The file does not exist, but we are ignoring this case

      # --------------------------------------------------

      # -- prepare the command line for the test execution

      listCmdLineParts = []
      listCmdLineParts.append(f"\"{PYTHON}\"")
      listCmdLineParts.append(f"\"{sCoverageFile}\"")
      listCmdLineParts.append(f"\"{COMPONENTROOTPATH}\"")
      sCmdLine = " ".join(listCmdLineParts)

      print(COLBY + "Starting test coverage:")
      print()
      print(f"* ({nCntComponent}/{nNrOfComponents}) : '{TESTFOLDER}' ({TESTTYPE})")
      print()

      print(f"Now executing command line:\n{sCmdLine}")
      listCmdLineParts = shlex.split(sCmdLine)

      try:
         nReturn = subprocess.call(listCmdLineParts)
         nReturn = ctypes.c_int32(nReturn).value
         print()
      except Exception as ex:
         nReturn  = ERROR
         bSuccess = None
         sResult  = CString.FormatResult(bSuccess, str(ex))

      if nReturn != SUCCESS:
         nCntSubProcessErrors = nCntSubProcessErrors + 1
         bSuccess = False
         sResult  = CString.FormatResult(bSuccess, f"Subprocess {TESTTYPE} executor has not returned expected value {SUCCESS}")
         print()
         print(COLBR + sResult)
         print()

      if nCntSubProcessErrors == 0:
         nReturn  = SUCCESS
         bSuccess = True
         sResult = "COMPLETE"
      else:
         nReturn  = -nCntSubProcessErrors
         bSuccess = False
         sResult  = f"[coverage trigger] : {nCntSubProcessErrors} errors occurred during the execution of subprocesses"

except Exception as ex:
   print()
   printerror(str(ex))
   print()
   sys.exit(ERROR)

if bSuccess is None:
   print()
   printerror(sResult)
   nReturn = ERROR
elif bSuccess is False:
   print()
   printerror(sResult)
elif bSuccess is True:
   print()
   print(COLBG + sResult)
else:
   print()
   printerror("Internal aio-test-coverage error")
   nReturn = ERROR

print()
sys.exit(nReturn)

# # --------------------------------------------------------------------------------------------------------------

