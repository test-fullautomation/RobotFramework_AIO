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
# CTestTrigger.py
#
# XC-CT/ECA3-Queckenstedt
#
# 26.09.2022
#
# --------------------------------------------------------------------------------------------------------------

"""Python module containing all methods to execute the tests and the database applications.
"""

# --------------------------------------------------------------------------------------------------------------

import os, sys, time, json, shlex, subprocess, platform, shutil, re
import colorama as col
import pypandoc

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Folder.CFolder import CFolder
from PythonExtensionsCollection.Utils.CUtils import *

col.init(autoreset=True)
COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLBW = col.Style.BRIGHT + col.Fore.WHITE

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

def printerror(sMsg):
   sys.stderr.write(COLBR + f"Error: {sMsg}!\n")

def printexception(sMsg):
   sys.stderr.write(COLBR + f"Exception: {sMsg}!\n")

# --------------------------------------------------------------------------------------------------------------
#TM***

class CTestTrigger():
   """Test trigger main class
   """

   def __init__(self, oTestTriggerConfig=None):
      """__init__
      """

      sMethod = "CTestTrigger.__init__"

      if oTestTriggerConfig is None:
         bSuccess = None
         sResult  = "oTestTriggerConfig is None"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      self.__oTestTriggerConfig = oTestTriggerConfig

   # eof def __init__(self, oTestTriggerConfig=None):

   def __del__(self):
      pass

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def Trigger(self):
      """Trigger execution of tests and database access
      """

      sMethod = "CTestTrigger.Trigger"

      bSuccess = None
      sResult  = "UNKNOWN"

      # PrettyPrint(self.__dictTestTriggerConfig, sPrefix="(Trigger)")
      PYTHON = self.__oTestTriggerConfig.Get('PYTHON')
      listofdictComponents = self.__oTestTriggerConfig.Get('COMPONENTS')
      nNrOfComponents = len(listofdictComponents)
      nCntComponent = 0
      for dictComponent in listofdictComponents:
         nCntComponent = nCntComponent + 1

         # -- needed for test execution
         COMPONENTROOTPATH = dictComponent['COMPONENTROOTPATH']
         TESTFOLDER        = dictComponent['TESTFOLDER']
         TESTEXECUTOR      = dictComponent['TESTEXECUTOR']
         TESTTYPE          = dictComponent['TESTTYPE']
         LOGFILE           = dictComponent['LOGFILE']

         # -- needed for database access
         dictTestTypes = self.__oTestTriggerConfig.Get('TESTTYPES')
         dictTestType = dictTestTypes[TESTTYPE]
         DATABASEEXECUTOR  = dictTestType['DATABASEEXECUTOR']
         ADDITIONALCONFIG  = dictTestType['ADDITIONALCONFIG']
         ADDITIONALCMDLINE = dictTestType['ADDITIONALCMDLINE']

         # -- prepare the command line for the test execution

         listCmdLineParts = []
         listCmdLineParts.append(f"\"{PYTHON}\"")
         listCmdLineParts.append(f"\"{TESTEXECUTOR}\"")
         listCmdLineParts.append("--logfile")
         listCmdLineParts.append(f"\"{LOGFILE}\"")
         sCmdLine = " ".join(listCmdLineParts)
         del listCmdLineParts

         # -- execute the tests

         print(COLBY + "Starting test execution:")
         print()
         print(f"* ({nCntComponent}/{nNrOfComponents}) : '{TESTFOLDER}' ({TESTTYPE})")
         print()

         listCmdLineParts = shlex.split(sCmdLine)
         sCmdLine = " ".join(listCmdLineParts)
         print(f"Now executing command line:\n{sCmdLine}")
         print()
         nReturn = ERROR
         try:
            nReturn = subprocess.call(listCmdLineParts)
            # debug only:
            # print(f"[test executor] : Subprocess returned {nReturn}")
            # print()
         except Exception as ex:
            bSuccess = None
            sResult  = CString.FormatResult(sMethod, bSuccess, str(ex))
            return bSuccess, sResult
         # print()
         if nReturn != SUCCESS:
            bSuccess = False
            sResult  = CString.FormatResult(sMethod, bSuccess, f"Subprocess has not returned expected value {SUCCESS}")
            return bSuccess, sResult

         # -- prepare the command line for database access

         listCmdLineParts = []
         listCmdLineParts.append(f"\"{PYTHON}\"")
         listCmdLineParts.append(f"\"{DATABASEEXECUTOR}\"")
         listCmdLineParts.append(f"--logfile=\"{LOGFILE}\"")
         listCmdLineParts.append(f"--config=\"{ADDITIONALCONFIG}\"")
         # listCmdLineParts.append(f"--additionalparams=\"{ADDITIONALCMDLINE}\"")
         sCmdLine = " ".join(listCmdLineParts)
         del listCmdLineParts

         # -- execute the database application

         print(COLBY + "Writing testresults to database")
         print()

         listCmdLineParts = shlex.split(sCmdLine)
         sCmdLine = " ".join(listCmdLineParts)
         print(f"Now executing command line:\n{sCmdLine}")
         print()
         nReturn = ERROR
         try:
            nReturn = subprocess.call(listCmdLineParts)
            # debug only:
            # print(f"[test executor] : Subprocess returned {nReturn}")
            # print()
         except Exception as ex:
            bSuccess = None
            sResult  = CString.FormatResult(sMethod, bSuccess, str(ex))
            return bSuccess, sResult
         # print()
         if nReturn != SUCCESS:
            bSuccess = False
            sResult  = CString.FormatResult(sMethod, bSuccess, f"Subprocess has not returned expected value {SUCCESS}")
            return bSuccess, sResult

      # eof for dictComponent in listofdictComponents:

      bSuccess = True
      sResult  = "All components tested and all results saved"

      return bSuccess, sResult

   # eof def Trigger(self):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   # --------------------------------------------------------------------------------------------------------------

# eof class CTestTrigger():

# --------------------------------------------------------------------------------------------------------------
