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

import os, sys

import colorama as col

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

# add the directory containing the CTestTriggerConfig module to sys.path
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../aio-test-trigger/libs'))
sys.path.append(module_path)

from CTestTriggerConfig import CTestTriggerConfig
from CTestTrigger import CTestTrigger

# -- setting up the test trigger configuration (relative to the path of this script)
oRepositoryConfig = None
try:
   oTestTriggerConfig = CTestTriggerConfig(os.path.abspath(sys.argv[0]))
except Exception as ex:
   print()
   printerror(str(ex))
   print()
   sys.exit(ERROR)

# -- setting up the test trigger
try:
   listofdictComponents = self.__oTestTriggerConfig.Get('COMPONENTS')
   nNrOfComponents = len(listofdictComponents)
   nCntComponent = 0

   for dictComponent in listofdictComponents:
      nCntComponent = nCntComponent + 1

      # -- get data for test execution
      COMPONENTROOTPATH = dictComponent['COMPONENTROOTPATH']
      TESTFOLDER        = dictComponent['TESTFOLDER']
      TESTTYPE          = dictComponent['TESTTYPE']
      COVERAGE          = dictComponent['COVERAGE']
      # -- prepare the command line for the test execution

      listCmdLineParts = []
      listCmdLineParts.append(f"\"{PYTHON}\"")
      listCmdLineParts.append(f"\"{TESTFOLDER}/coverage/coverage.py\"")

   if TESTTYPE == "PYTEST":
      PLATFORMSYSTEM = self.__oTestTriggerConfig.Get('PLATFORMSYSTEM')
      if PLATFORMSYSTEM == "Windows" and COVERAGE is not None:
         sCmdLine = " ".join(listCmdLineParts)
         del listCmdLineParts
         print(f"Now executing command line:\n{sCmdLine}")
         listCmdLineParts = shlex.split(sCmdLine)
         try:
            nReturn = subprocess.call(listCmdLineParts)
            nReturn = ctypes.c_int32(nReturn).value
            print()
         except Exception as ex:
            nReturn  = ERROR
            bSuccess = None
            bSuccess = None
            sResult  = CString.FormatResult(sMethod, bSuccess, str(ex))

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

# --------------------------------------------------------------------------------------------------------------

