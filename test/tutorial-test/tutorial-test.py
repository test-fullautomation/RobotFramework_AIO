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
# tutorial-test.py
#
# XC-CT/ECA3-Queckenstedt
#

# --------------------------------------------------------------------------------------------------------------
#
# 21.02.2023
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

sTutorialRootPath = None
if sPlatformSystem == "Windows":
   sTutorialRootPath = CString.NormalizePath("%RobotTutorialPath%")
elif sPlatformSystem == "Linux":
   sTutorialRootPath = CString.NormalizePath("${RobotTutorialPath}")
else:
   bSuccess = False
   sResult  = f"Operating system {sPlatformSystem} ({sOSName}) not supported"
   printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
   sys.exit(ERROR)

print()
print(f"{sThisScriptName} is running under {sPlatformSystem} ({sOSName})")
print()

if os.path.isdir(sTutorialRootPath) is False:
   bSuccess = False
   sResult  = f"Tutorial not found: '{sTutorialRootPath}'"
   printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
   sys.exit(ERROR)

print(f"Identified tutorial in '{sTutorialRootPath}'")
print()

PATTERNFILE = f"{sThisScriptPath}/config/tutorial-test_pattern.txt"
if os.path.isfile(PATTERNFILE) is False:
   print()
   bSuccess = False
   sResult  = f"Missing pattern file '{PATTERNFILE}'"
   printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
   print()
   sys.exit(ERROR)


# **************************************************************************************************************
# [USECASES]
# **************************************************************************************************************
#TM***

listofdictUsecases = []

# --------------------------------------------------------------------------------------------------------------
#TM***
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E01-01"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-01"
dictUsecase['DESCRIPTION']      = "Using default configuration"
dictUsecase['TESTFILENAME']     = "exercise-01.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = None
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E02-01"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-02"
dictUsecase['DESCRIPTION']      = "Variant specific parameter configuration file directly in command line"
dictUsecase['TESTFILENAME']     = "exercise-02.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = f"--variable config_file:\"./config/exercise-02_config_variant1.json\"" # path relative to position of robot file
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E02-02"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-02"
dictUsecase['DESCRIPTION']      = "Test execution without any variant specific command line extensions"
dictUsecase['TESTFILENAME']     = "exercise-02-B.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = None
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E02-03"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-02"
dictUsecase['DESCRIPTION']      = "Name of a variant in command line"
dictUsecase['TESTFILENAME']     = "exercise-02-B.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = f"--variable variant:\"variant2\""
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E03-01"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-03"
dictUsecase['DESCRIPTION']      = "Configuration from config folder (1)"
dictUsecase['TESTFILENAME']     = "exercise-03.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = None
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E03-02"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-03"
dictUsecase['DESCRIPTION']      = "Configuration from config folder (2)"
dictUsecase['TESTFILENAME']     = "exercise-03-A.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = None
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E03-03"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-03"
dictUsecase['DESCRIPTION']      = "Configuration from config folder (3)"
dictUsecase['TESTFILENAME']     = "exercise-03-B.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = None
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E04-01"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-04"
dictUsecase['DESCRIPTION']      = "Computation of folder containing several robot files"
dictUsecase['TESTFILENAME']     = None
dictUsecase['TESTFOLDERNAME']   = "testsuites"
dictUsecase['ADDITIONALPARAMS'] = f"--variable variant:\"variant2\""
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E05-01"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-05"
dictUsecase['DESCRIPTION']      = "Nested parameter in configuration file (default variant)"
dictUsecase['TESTFILENAME']     = "exercise-05.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = None
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E05-02"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-05"
dictUsecase['DESCRIPTION']      = "Nested parameter in configuration file (variant 1)"
dictUsecase['TESTFILENAME']     = "exercise-05.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = f"--variable variant:\"variant1\""
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E06-01"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-06"
dictUsecase['DESCRIPTION']      = "Local parameter configuration (default)"
dictUsecase['TESTFILENAME']     = "exercise-06.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = None
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E06-02"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-06"
dictUsecase['DESCRIPTION']      = "Local parameter configuration (variant 1)"
dictUsecase['TESTFILENAME']     = "exercise-06.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = f"--variable variant:\"variant1\""
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E06-03"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-06"
dictUsecase['DESCRIPTION']      = "Local parameter configuration in command line"
dictUsecase['TESTFILENAME']     = "exercise-06.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = f"--variable local_config:\"./localconfig/exercise-06_localconfig_bench1.json\"" # path relative to position of robot file
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E06-04"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-06"
dictUsecase['DESCRIPTION']      = "Local parameter configuration with variant 2 in command line"
dictUsecase['TESTFILENAME']     = "exercise-06.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = f"--variable variant:\"variant2\" --variable local_config:\"./localconfig/exercise-06_localconfig_bench1.json\"" # path relative to position of robot file
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E06-05"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-06"
dictUsecase['DESCRIPTION']      = "Local parameter configuration by ROBOT_LOCAL_CONFIG (bench1) with variant 2 in command line"
dictUsecase['TESTFILENAME']     = "exercise-06.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = f"--variable variant:\"variant2\""
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------
dictUsecase = {}
dictUsecase['TESTNAME']         = "testsuites-E07-01"
dictUsecase['TUTORIALNAME']     = "900_building_testsuites"
dictUsecase['EXERCISENAME']     = "exercise-07"
dictUsecase['DESCRIPTION']      = "Priority of configuration parameters"
dictUsecase['TESTFILENAME']     = "exercise-07.robot"
dictUsecase['TESTFOLDERNAME']   = None
dictUsecase['ADDITIONALPARAMS'] = f"--variable teststring:\"command line test string\" --variable local_config:\"./localconfig/exercise-07_localconfig_bench1.json\" --variable config_file:\"./config/exercise-07_config_variant1.json\"" # path relative to position of robot file
listofdictUsecases.append(dictUsecase)
del dictUsecase
# --------------------------------------------------------------------------------------------------------------


# **************************************************************************************************************
# [EXECUTION]
# **************************************************************************************************************
#TM***

print("Executing tutorial files")
print()

nNrOfDefinedUsecases = len(listofdictUsecases)
nCntExecutedUsecases = 0
nCntPassedUsecases   = 0
nCntFailedUsecases   = 0

oComparison = CComparison()

for dictUsecase in listofdictUsecases:
   nCntExecutedUsecases = nCntExecutedUsecases + 1

   TESTNAME         = dictUsecase['TESTNAME']
   TUTORIALNAME     = dictUsecase['TUTORIALNAME']
   EXERCISENAME     = dictUsecase['EXERCISENAME']
   DESCRIPTION      = dictUsecase['DESCRIPTION']
   TESTFILENAME     = dictUsecase['TESTFILENAME']
   TESTFOLDERNAME   = dictUsecase['TESTFOLDERNAME']
   ADDITIONALPARAMS = dictUsecase['ADDITIONALPARAMS']

   TESTLOGFILE      = f"{sThisScriptPath}/tutoriallogfiles/{TESTNAME}/{EXERCISENAME}.log"  # ! without quotes !
   REFERENCELOGFILE = f"{sThisScriptPath}/referencelogfiles/{TESTNAME}/{EXERCISENAME}.log" # ! without quotes !

   print(COLBY + f"* Execution of test '{TESTNAME}' / exercise '{EXERCISENAME}' / tutorial '{TUTORIALNAME}' / ({nCntExecutedUsecases}/{nNrOfDefinedUsecases})")
   print()
   print(COLBY + f"  {DESCRIPTION}")
   print()

   listCmdLineParts = []
   listCmdLineParts.append(f"\"{sPython}\"")
   listCmdLineParts.append(f"-m robot")
   listCmdLineParts.append(f"-d")
   listCmdLineParts.append(f"\"{sThisScriptPath}/tutoriallogfiles/{TESTNAME}\"")
   listCmdLineParts.append(f"-o")
   listCmdLineParts.append(f"\"{sThisScriptPath}/tutoriallogfiles/{TESTNAME}/{EXERCISENAME}.xml\"")
   listCmdLineParts.append(f"-l")
   listCmdLineParts.append(f"\"{sThisScriptPath}/tutoriallogfiles/{TESTNAME}/{EXERCISENAME}_log.html\"")
   listCmdLineParts.append(f"-r")
   listCmdLineParts.append(f"\"{sThisScriptPath}/tutoriallogfiles/{TESTNAME}/{EXERCISENAME}_report.html\"")
   listCmdLineParts.append(f"-b")
   listCmdLineParts.append("\"" + TESTLOGFILE + "\"")
   if ADDITIONALPARAMS is not None:
      listCmdLineParts.append(f"{ADDITIONALPARAMS}")
   # (distinguishing between TESTFILENAME and TESTFOLDERNAME maybe not really required)
   if TESTFILENAME is not None:
      listCmdLineParts.append(f"\"{sTutorialRootPath}/{TUTORIALNAME}/{EXERCISENAME}/{TESTFILENAME}\"")
   elif TESTFOLDERNAME is not None:
      listCmdLineParts.append(f"\"{sTutorialRootPath}/{dictUsecase['TUTORIALNAME']}/{dictUsecase['EXERCISENAME']}/{TESTFOLDERNAME}\"")
   else:
      # invalid
      pass

   # --------------------------------------------------------------------------------------------------------------
   # !!! exception in test execution !!!
   if TESTNAME == "testsuites-E06-05":
      os.environ['ROBOT_LOCAL_CONFIG'] = f"{sTutorialRootPath}/{dictUsecase['TUTORIALNAME']}/{dictUsecase['EXERCISENAME']}/localconfig/exercise-06_localconfig_bench1.json"
   else:
      if 'ROBOT_LOCAL_CONFIG' in os.environ:
         del os.environ['ROBOT_LOCAL_CONFIG']
   # --------------------------------------------------------------------------------------------------------------

   EXPECTEDRETURN = SUCCESS # not yet config parameter; currently valid for all use cases (bad case tests not part of tutorial)

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
      nCntFailedUsecases = nCntFailedUsecases + 1
      printerror(f"Usecase '{TESTNAME}' failed (failed up to now: {nCntFailedUsecases}) [{DESCRIPTION}]")
      continue # for dictUsecase in listofdictUsecases:
   print()

   if nReturn != EXPECTEDRETURN:
      print()
      bSuccess = False
      sResult  = f"Robot Framework returned not expected value {nReturn}"
      printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
      nCntFailedUsecases = nCntFailedUsecases + 1
      printerror(f"Usecase '{TESTNAME}' failed (failed up to now: {nCntFailedUsecases}) [{DESCRIPTION}]")
      continue # for dictUsecase in listofdictUsecases:

   # -- log file check

   if os.path.isfile(TESTLOGFILE) is False:
      print()
      bSuccess = False
      sResult  = f"Missing log file of test '{TESTNAME}': '{TESTLOGFILE}'"
      printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
      nCntFailedUsecases = nCntFailedUsecases + 1
      printerror(f"Usecase '{TESTNAME}' failed (failed up to now: {nCntFailedUsecases}) [{DESCRIPTION}]")
      continue # for dictUsecase in listofdictUsecases:
   if os.path.isfile(REFERENCELOGFILE) is False:
      print()
      bSuccess = False
      sResult  = f"Missing reference log file of test '{TESTNAME}': '{REFERENCELOGFILE}'"
      printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
      nCntFailedUsecases = nCntFailedUsecases + 1
      printerror(f"Usecase '{TESTNAME}' failed (failed up to now: {nCntFailedUsecases}) [{DESCRIPTION}]")
      continue # for dictUsecase in listofdictUsecases:

   bIdentical, bSuccess, sResult = oComparison.Compare(TESTLOGFILE, REFERENCELOGFILE, sPatternFile=PATTERNFILE)

   print(f"(1) Test log file      : {TESTLOGFILE}")
   print(f"(2) Reference log file : {REFERENCELOGFILE}")
   print(f"(3) Pattern file       : {PATTERNFILE}")

   if bSuccess is True:
      if bIdentical is True:
         nCntPassedUsecases = nCntPassedUsecases + 1
         print()
         print(f"            ({TESTNAME}) : log file check passed")
         print()
      else:
         print()
         printerror(sResult) # without FormatResult!
         nCntFailedUsecases = nCntFailedUsecases + 1
         printerror(f"Usecase '{TESTNAME}' failed (failed up to now: {nCntFailedUsecases}) [{DESCRIPTION}]")
         continue # for dictUsecase in listofdictUsecases:
   else:
      print()
      printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
      nCntFailedUsecases = nCntFailedUsecases + 1
      printerror(f"Usecase '{TESTNAME}' failed (failed up to now: {nCntFailedUsecases}) [{DESCRIPTION}]")
      continue # for dictUsecase in listofdictUsecases:

# eof for dictUsecase in listofdictUsecases:

# --------------------------------------------------------------------------------------------------------------

# paranoia check
if (nCntPassedUsecases + nCntFailedUsecases) != nCntExecutedUsecases:
   print()
   printerror(CString.FormatResult(sThisScriptName, bSuccess=False, sResult="Internal counter mismatch"))
   print()
   sys.exit(ERROR)

# --------------------------------------------------------------------------------------------------------------

# -- tutorial test result

nReturn = ERROR

if nCntExecutedUsecases == 0:
   printerror(f"No usecase executed")
   nReturn = ERROR # should not happen; makes no sense
elif nCntFailedUsecases > 0:
   printerror(f"Tutorial test failed with {nCntFailedUsecases} failed usecases (with {nCntExecutedUsecases}/{nNrOfDefinedUsecases} usecases executed)")
   nReturn = ERROR
else:
   print(COLBG + f"Tutorial test passed ({nCntExecutedUsecases}/{nNrOfDefinedUsecases} usecases executed)")
   nReturn = SUCCESS

print()

sys.exit(nReturn)

# --------------------------------------------------------------------------------------------------------------
