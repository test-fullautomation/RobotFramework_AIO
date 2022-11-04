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
# selftest.py
#
# XC-CT/ECA3-Queckenstedt
#
# Test trigger self test 
#
# Calls the test trigger with a combination of several test suites and several test configuration files
# and several command lines. Counts the number of failed usecases of self test.
#
# Test Trigger selftest is standalone. No database access (mocks used as Database Executor).
# RobotFramework AIO and Python pytest module involved based on selftest test suites.
# A positive return value of selftest indicates an internal selftest error.
# Return value 0 indicates a successful selftest (all usecases passed).
# A negative return value is equivalent to the number of failed usecases.
# A usecase is passed or failed depending on the return value of the Test Trigger fits to the expected value or not.
#
# Every relative path is relative to the position of the file that contains the relative path.

# --------------------------------------------------------------------------------------------------------------
#
# 03.11.2022
#
# --------------------------------------------------------------------------------------------------------------
#TM***
# TOC:
# [USECASES]
# [EXECUTION]
# --------------------------------------------------------------------------------------------------------------


import os, sys, platform, shlex, subprocess, shutil, argparse, ctypes

import colorama as col

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.Folder.CFolder import CFolder

col.init(autoreset=True)

COLBR = col.Style.BRIGHT + col.Fore.RED
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLBG = col.Style.BRIGHT + col.Fore.GREEN

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

def printerror(sMsg):
    sys.stderr.write(COLBR + f"{sMsg}!\n")

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

sFilter = None
if sPlatformSystem == "Windows":
    sFilter = "not _Linux_"
elif sPlatformSystem == "Linux":
    sFilter = "not _Windows_"
else:
   bSuccess = False
   sResult  = f"Operating system {sPlatformSystem} ({sOSName}) not supported"
   printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
   sys.exit(ERROR)

print()
print(f"{sThisScriptName} is running under {sPlatformSystem} ({sOSName})")
print()

# SuT
sTestTrigger = CString.NormalizePath("../aio-test-trigger.py", sReferencePathAbs=sThisScriptPath)
if os.path.isfile(sTestTrigger) is False:
   bSuccess = False
   sResult  = f"Missing Test Trigger '{sTestTrigger}'"
   printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
   sys.exit(ERROR)

print(f"Testing '{sTestTrigger}'")
print()


# **************************************************************************************************************
# [USECASES]
# **************************************************************************************************************
#TM***

listofdictUsecases = []

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "001"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / good case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.001/testtrigger_selftest_config_uc_001.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 0
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "002"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / with global commandlines / good case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.002/testtrigger_selftest_config_uc_002.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = r"--variable global_cmdline_var:\"global command line test string\""
dictUsecase['PYTESTCOMMANDLINE'] = r"-k \"not _NOTME_\""
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 0
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "003"
dictUsecase['DESCRIPTION']       = "several ROBOT and PYTEST test suites / with params / with global commandlines / good case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.003/testtrigger_selftest_config_uc_003.json"
dictUsecase['PARAMS']            = "pytestexclude=not _NOTME_;local_cmdline_var=local command line test string;robot2db_param_1=robot2db_param_1_value;robot2db_param_2=robot2db_param_2_value;pytest2db_param_1=pytest2db_param_1_value;pytest2db_param_2=pytest2db_param_2_value"
dictUsecase['ROBOTCOMMANDLINE']  = r"--variable global_cmdline_var:\"global command line test string\""
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 0
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "004"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / with params / no commandlines / good case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.004/testtrigger_selftest_config_uc_004.json"
dictUsecase['PARAMS']            = "COMPONENTROOTPATH=.;FOLDERNAMEEXTENSION=TEST;EXECUTORPREFIX=execute;LOGFOLDERNAME=logfiles;USECASENUMBER=004;MOCKSFOLDER=mocks"
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 0
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "005"
dictUsecase['DESCRIPTION']       = "several ROBOT and PYTEST test suites / some tests failed / without params / without global commandlines / good case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.005/testtrigger_selftest_config_uc_005.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = -2
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "006"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / database not active / good case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.006/testtrigger_selftest_config_uc_006.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = False
dictUsecase['EXPECTEDRETURN']    = 0
listofdictUsecases.append(dictUsecase)
del dictUsecase

# **************************************************************************************************************

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "100"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / config file not found / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.100/testtrigger_selftest_config_NOTEXISTING.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "101"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / COMPONENTROOTPATH not existing / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.101/testtrigger_selftest_config_uc_101.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "102"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / TESTFOLDER not existing / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.102/testtrigger_selftest_config_uc_102.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "103"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / TESTEXECUTOR not existing / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.103/testtrigger_selftest_config_uc_103.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "104"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / invalid TESTTYPE in section 'COMPONENTS' / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.104/testtrigger_selftest_config_uc_104.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "105"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / missing TESTTYPE definition in section 'TESTTYPES' / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.105/testtrigger_selftest_config_uc_105.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "106"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / invalid TESTTYPE definition in section 'TESTTYPES' / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.106/testtrigger_selftest_config_uc_106.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "107"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / missing key DATABASEEXECUTOR / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.107/testtrigger_selftest_config_uc_107.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "108"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / DATABASEEXECUTOR not existing / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.108/testtrigger_selftest_config_uc_108.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "109"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / missing main key 'COMPONENTS' / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.109/testtrigger_selftest_config_uc_109.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "110"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / missing main key 'TESTTYPES' / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.110/testtrigger_selftest_config_uc_110.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "111"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no params / no commandlines / syntax error in configuration / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.111/testtrigger_selftest_config_uc_111.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']               = "112"
dictUsecase['DESCRIPTION']        = "ROBOT and PYTEST test suite / invalid command line parameter / bad case"
dictUsecase['CONFIGFILE']         = "./selftestfiles/UC.112/testtrigger_selftest_config_uc_112.json"
dictUsecase['PARAMS']             = None
dictUsecase['ROBOTCOMMANDLINE']   = None
dictUsecase['PYTESTCOMMANDLINE']  = None
dictUsecase['INVALIDCOMMANDLINE'] = "--invalidparam \"no matter value\""
dictUsecase['RESULTS2DB']         = True
dictUsecase['EXPECTEDRETURN']     = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "113"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no commandlines / with params, but configuration parameter not defined / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.113/testtrigger_selftest_config_uc_113.json"
dictUsecase['PARAMS']            = "param1=value1;param2=value2"
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "114"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no commandlines / no params and configuration parameter not defined / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.114/testtrigger_selftest_config_uc_114.json"
dictUsecase['PARAMS']            = None
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "115"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no commandlines / with params, but improper reference in configuration (1) / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.115/testtrigger_selftest_config_uc_115.json"
dictUsecase['PARAMS']            = "param1=value1;param2=value2"
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase

# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['NAME']              = "116"
dictUsecase['DESCRIPTION']       = "ROBOT and PYTEST test suite / no commandlines / with params, but improper reference in configuration (2) / bad case"
dictUsecase['CONFIGFILE']        = "./selftestfiles/UC.116/testtrigger_selftest_config_uc_116.json"
dictUsecase['PARAMS']            = "param1=value1;param2=value2"
dictUsecase['ROBOTCOMMANDLINE']  = None
dictUsecase['PYTESTCOMMANDLINE'] = None
dictUsecase['RESULTS2DB']        = True
dictUsecase['EXPECTEDRETURN']    = 1
listofdictUsecases.append(dictUsecase)
del dictUsecase




# **************************************************************************************************************
# [EXECUTION]
# **************************************************************************************************************
#TM***

nNrOfDefinedUsecases = len(listofdictUsecases)
nCntExecutedUsecases = 0
nCntPassedUsecases   = 0
nCntFailedUsecases   = 0

for dictUsecase in listofdictUsecases:
   nCntExecutedUsecases = nCntExecutedUsecases + 1
   NAME              = dictUsecase['NAME']
   DESCRIPTION       = dictUsecase['DESCRIPTION']
   CONFIGFILE        = dictUsecase['CONFIGFILE']
   PARAMS            = dictUsecase['PARAMS']
   ROBOTCOMMANDLINE  = dictUsecase['ROBOTCOMMANDLINE']
   PYTESTCOMMANDLINE = dictUsecase['PYTESTCOMMANDLINE']
   RESULTS2DB        = dictUsecase['RESULTS2DB']
   EXPECTEDRETURN    = dictUsecase['EXPECTEDRETURN']

   INVALIDCOMMANDLINE = None
   if "INVALIDCOMMANDLINE" in dictUsecase: # used only once; therefore not part of every dictUsecase
      INVALIDCOMMANDLINE = dictUsecase['INVALIDCOMMANDLINE']

   print(COLBY + f"* Test Trigger self test usecase {nCntExecutedUsecases}/{nNrOfDefinedUsecases} : {NAME}")
   print()
   print(COLBY + f"  {DESCRIPTION}")
   print()

   listCmdLineParts = []
   listCmdLineParts.append(f"\"{sPython}\"")
   listCmdLineParts.append(f"\"{sTestTrigger}\"")
   if CONFIGFILE is not None:
      sConfigFile = CString.NormalizePath(CONFIGFILE, sReferencePathAbs=sThisScriptPath)
      listCmdLineParts.append("--configfile")
      listCmdLineParts.append(f"\"{sConfigFile}\"")
   if INVALIDCOMMANDLINE is not None:
      listCmdLineParts.append(INVALIDCOMMANDLINE)
   if PARAMS is not None:
      listCmdLineParts.append("--params")
      listCmdLineParts.append(f"\"{PARAMS}\"")
   if ROBOTCOMMANDLINE is not None:
      listCmdLineParts.append("--robotcommandline")
      listCmdLineParts.append(f"\"{ROBOTCOMMANDLINE}\"")
   if PYTESTCOMMANDLINE is not None:
      listCmdLineParts.append("--pytestcommandline")
      listCmdLineParts.append(f"\"{PYTESTCOMMANDLINE}\"")
   if RESULTS2DB is True:
      listCmdLineParts.append("--results2db")

   sCmdLine = " ".join(listCmdLineParts)
   del listCmdLineParts
   print(f"Now executing command line:\n{sCmdLine}")
   print()
   listCmdLineParts = shlex.split(sCmdLine)
   nReturn = ERROR
   try:
      nReturn = subprocess.call(listCmdLineParts)
      # Test Trigger may return negative values; must be converted back to negative value after received here
      nReturn = ctypes.c_int32(nReturn).value
      print()
      print(f"[{sThisScriptName}] : Test Trigger returned {nReturn}")
   except Exception as ex:
      print()
      printerror(CString.FormatResult(sThisScriptName, bSuccess=None, sResult=str(ex)))
      print()
      sys.exit(ERROR)
   print()

   if nReturn == EXPECTEDRETURN:
      nCntPassedUsecases = nCntPassedUsecases + 1
   else:
      nCntFailedUsecases = nCntFailedUsecases + 1
      print(COLBR + f"Usecase '{NAME}' failed (failed up to now: {nCntFailedUsecases}) [{DESCRIPTION}]")
   print()

   # paranoia check
   if (nCntPassedUsecases + nCntFailedUsecases) != nCntExecutedUsecases:
      print()
      printerror(CString.FormatResult(sThisScriptName, bSuccess=False, sResult="Internal counter mismatch"))
      print()
      sys.exit(ERROR)

# eof for dictUsecase in listofdictUsecases:

# --------------------------------------------------------------------------------------------------------------

# Test Trigger self test result

# nReturn:
# > 0  : internal error of this script
# < 0  : failed usecases
# == 0 : no internal error of this script and no failed usecases

nReturn = ERROR

if nCntExecutedUsecases == 0:
   print(COLBR + f"No usecase executed")
elif nCntFailedUsecases > 0:
   print(COLBR + f"Test Trigger self test failed with {nCntFailedUsecases} failed usecases (with {nCntExecutedUsecases}/{nNrOfDefinedUsecases} usecases executed)")
   nReturn = -nCntFailedUsecases
else:
   print(COLBG + f"Test Trigger self test passed ({nCntExecutedUsecases}/{nNrOfDefinedUsecases} usecases executed)")
   nReturn = 0

print()

sys.exit(nReturn)

# --------------------------------------------------------------------------------------------------------------
