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
# 21.10.2022
#
# --------------------------------------------------------------------------------------------------------------

"""Python module containing all methods to execute the tests and the database applications.
"""

# --------------------------------------------------------------------------------------------------------------

import os, sys, time, json, shlex, subprocess, platform, shutil, re, ctypes
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

      nReturn  = ERROR
      bSuccess = None
      sResult  = "UNKNOWN"

      nCntSubProcessErrors = 0

      PYTHON = self.__oTestTriggerConfig.Get('PYTHON')
      ROBOTCOMMANDLINE  = self.__oTestTriggerConfig.Get('ROBOTCOMMANDLINE')
      PYTESTCOMMANDLINE = self.__oTestTriggerConfig.Get('PYTESTCOMMANDLINE')

      # recover the masking of nested quotes
      if ROBOTCOMMANDLINE is not None:
         ROBOTCOMMANDLINE = ROBOTCOMMANDLINE.replace("\"", r"\"")
         ROBOTCOMMANDLINE = ROBOTCOMMANDLINE.replace("'", r"\"")
      if PYTESTCOMMANDLINE is not None:
         PYTESTCOMMANDLINE = PYTESTCOMMANDLINE.replace("\"", r"\"")
         PYTESTCOMMANDLINE = PYTESTCOMMANDLINE.replace("'", r"\"")

      listofdictComponents = self.__oTestTriggerConfig.Get('COMPONENTS')
      nNrOfComponents = len(listofdictComponents)
      nCntComponent = 0
      for dictComponent in listofdictComponents:
         nCntComponent = nCntComponent + 1

         # -- get data for test execution
         COMPONENTROOTPATH = dictComponent['COMPONENTROOTPATH']
         TESTFOLDER        = dictComponent['TESTFOLDER']
         TESTTYPE          = dictComponent['TESTTYPE']
         TESTEXECUTOR      = dictComponent['TESTEXECUTOR']
         LOCALCOMMANDLINE  = dictComponent['LOCALCOMMANDLINE']
         LOGFILE           = dictComponent['LOGFILE']

         # -- prepare the command line for the test execution

         listCmdLineParts = []
         listCmdLineParts.append(f"\"{PYTHON}\"")
         listCmdLineParts.append(f"\"{TESTEXECUTOR}\"")
         listCmdLineParts.append("--logfile")
         listCmdLineParts.append(f"\"{LOGFILE}\"")

         if LOCALCOMMANDLINE is not None:
            # recover the masking of nested quotes
            LOCALCOMMANDLINE = LOCALCOMMANDLINE.replace("\"", r"\"")
            LOCALCOMMANDLINE = LOCALCOMMANDLINE.replace("'", r"\"")

         if TESTTYPE == "ROBOT":
            if ( (ROBOTCOMMANDLINE is not None) or (LOCALCOMMANDLINE is not None) ):
               listCmdLineParts.append(f"--robotcommandline")
               if ( (ROBOTCOMMANDLINE is not None) and (LOCALCOMMANDLINE is None) ):
                  listCmdLineParts.append(f"\"{ROBOTCOMMANDLINE}\"")
               elif ( (ROBOTCOMMANDLINE is None) and (LOCALCOMMANDLINE is not None) ):
                  listCmdLineParts.append(f"\"{LOCALCOMMANDLINE}\"")
               elif ( (ROBOTCOMMANDLINE is not None) and (LOCALCOMMANDLINE is not None) ):
                  listCmdLineParts.append(f"\"{ROBOTCOMMANDLINE} {LOCALCOMMANDLINE}\"")

         if TESTTYPE == "PYTEST":
            if ( (PYTESTCOMMANDLINE is not None) or (LOCALCOMMANDLINE is not None) ):
               listCmdLineParts.append(f"--pytestcommandline")
               if ( (PYTESTCOMMANDLINE is not None) and (LOCALCOMMANDLINE is None) ):
                  listCmdLineParts.append(f"\"{PYTESTCOMMANDLINE}\"")
               elif ( (PYTESTCOMMANDLINE is None) and (LOCALCOMMANDLINE is not None) ):
                  listCmdLineParts.append(f"\"{LOCALCOMMANDLINE}\"")
               elif ( (PYTESTCOMMANDLINE is not None) and (LOCALCOMMANDLINE is not None) ):
                  listCmdLineParts.append(f"\"{PYTESTCOMMANDLINE} {LOCALCOMMANDLINE}\"")

         sCmdLine = " ".join(listCmdLineParts)
         del listCmdLineParts

         # -- execute the tests

         print(COLBY + "Starting test execution:")
         print()
         print(f"* ({nCntComponent}/{nNrOfComponents}) : '{TESTFOLDER}' ({TESTTYPE})")
         print()

         print(f"Now executing command line:\n{sCmdLine}")
         print()

         listCmdLineParts = shlex.split(sCmdLine)

         nReturn = ERROR
         try:
            nReturn = subprocess.call(listCmdLineParts)
            # Executor may return negative values; must be converted back to negative value after received here
            nReturn = ctypes.c_int32(nReturn).value
            print()
            print(f"[test trigger] : Subprocess {TESTTYPE} executor returned {nReturn}")
         except Exception as ex:
            nReturn  = ERROR
            bSuccess = None
            sResult  = CString.FormatResult(sMethod, bSuccess, str(ex))
            return nReturn, bSuccess, sResult
         print()
         if nReturn != SUCCESS:
            nCntSubProcessErrors = nCntSubProcessErrors + 1
            bSuccess = False
            sResult  = CString.FormatResult(sMethod, bSuccess, f"Subprocess {TESTTYPE} executor has not returned expected value {SUCCESS}")
            print()
            print(COLBR + sResult)
            print()

         # -- get data for database access
         dictTestTypes = self.__oTestTriggerConfig.Get('TESTTYPES')
         if TESTTYPE not in dictTestTypes:
            # missing testttype definition
            nReturn  = ERROR
            bSuccess = None
            sResult  = f"Missing defintion of TESTTYPE '{TESTTYPE}' in configuration"
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
            return nReturn, bSuccess, sResult

         dictTestType  = dictTestTypes[TESTTYPE] # TESTTYPE got from data for test execution above
         DATABASEEXECUTOR = dictTestType['DATABASEEXECUTOR']
         LOCALCOMMANDLINE = dictTestType['LOCALCOMMANDLINE']

         # -- prepare the command line for database access

         listCmdLineParts = []
         listCmdLineParts.append(f"\"{PYTHON}\"")
         listCmdLineParts.append(f"\"{DATABASEEXECUTOR}\"")
         listCmdLineParts.append(f"\"{LOGFILE}\"")

         if LOCALCOMMANDLINE is not None:
            # recover the masking of nested quotes
            LOCALCOMMANDLINE = LOCALCOMMANDLINE.replace("\"", r"\"")
            LOCALCOMMANDLINE = LOCALCOMMANDLINE.replace("'", r"\"")
            listCmdLineParts.append(LOCALCOMMANDLINE)
         sCmdLine = " ".join(listCmdLineParts)
         del listCmdLineParts

         # -- execute the database application

         print(COLBY + "Writing testresults to database")
         print()
         print(f"Now executing command line:\n{sCmdLine}")
         print()

         listCmdLineParts = shlex.split(sCmdLine)

         nReturn = ERROR
         try:
            nReturn = subprocess.call(listCmdLineParts)
            # Executor may return negative values; must be converted back to negative value after received here
            nReturn = ctypes.c_int32(nReturn).value
            print()
            print(f"[test trigger] : Subprocess database executor returned {nReturn}")
         except Exception as ex:
            nReturn  = ERROR
            bSuccess = None
            sResult  = CString.FormatResult(sMethod, bSuccess, str(ex))
            return nReturn, bSuccess, sResult
         print()
         if nReturn != SUCCESS:
            nCntSubProcessErrors = nCntSubProcessErrors + 1
            bSuccess = False
            sResult  = CString.FormatResult(sMethod, bSuccess, f"Subprocess database executor has not returned expected value {SUCCESS}")
            print()
            print(COLBR + sResult)
            print()
            continue

      # eof for dictComponent in listofdictComponents:

      if nCntSubProcessErrors == 0:
         nReturn  = SUCCESS
         bSuccess = True
         sResult  = "All components tested and all results saved"
      else:
         nReturn  = -nCntSubProcessErrors
         bSuccess = False
         sResult  = f"[test trigger] : {nCntSubProcessErrors} errors occurred during the execution of subprocesses"

      return nReturn, bSuccess, sResult

   # eof def Trigger(self):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   # --------------------------------------------------------------------------------------------------------------

# eof class CTestTrigger():

# --------------------------------------------------------------------------------------------------------------
