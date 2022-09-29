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
# aio-analyzer.py
#
# XC-CT/ECA3-Queckenstedt
#
# --------------------------------------------------------------------------------------------------------------
#
# Application to parse (and partially check) the version numbers from installed components
# of the RobotFramework AIO.
#
# Return values:
# 0 : all fine
# 1 : error, e.g. missing file or not able to parse content
# 2 : version mismatch
#
# --------------------------------------------------------------------------------------------------------------

import os, sys, platform, re, time, itertools

import colorama as col

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Folder.CFolder import CFolder
from PythonExtensionsCollection.Utils.CUtils import *

col.init(autoreset=True)

COLBR = col.Style.BRIGHT + col.Fore.RED
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLBG = col.Style.BRIGHT + col.Fore.GREEN

SUCCESS          = 0
ERROR            = 1
VERSION_MISMATCH = 2

# --------------------------------------------------------------------------------------------------------------

def printerror(sMsg):
   sys.stderr.write(COLBR + f"Error: {sMsg}!\n")

def printexception(sMsg):
   sys.stderr.write(COLBR + f"Exception: {sMsg}!\n")

# --------------------------------------------------------------------------------------------------------------
# ENVIRONMENT
# --------------------------------------------------------------------------------------------------------------
#TM***

sThisScript     = sys.argv[0]
sThisScript     = CString.NormalizePath(sThisScript)
sThisScriptPath = os.path.dirname(sThisScript)
sThisScriptName = os.path.basename(sThisScript)

sOSName         = os.name
sPlatformSystem = platform.system()
sPythonPath     = CString.NormalizePath(os.path.dirname(sys.executable))
sPython         = CString.NormalizePath(sys.executable)
sPythonVersion  = sys.version

sSitePackages = None
if sPlatformSystem == "Windows":
    sSitePackages = CString.NormalizePath(f"{sPythonPath}/Lib/site-packages")
elif sPlatformSystem == "Linux":
    sSitePackages = CString.NormalizePath(f"{sPythonPath}/../lib/python3.9/site-packages")
else:
   bSuccess = False
   sResult  = f"Operating system {sPlatformSystem} ({sOSName}) not supported"
   printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
   sys.exit(ERROR)

print()
print(f"{sThisScriptName} is running under {sPlatformSystem} ({sOSName})")
print()

# --------------------------------------------------------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------------------------------------------------------
#TM***

# -- version and date formats

# "FORMAT-1"
# VERSION      = "0.2.2"
# VERSION_DATE = "18.07.2022"

sPattern_version_format_1 = r"VERSION\s*=\s*[\"'](.+?)[\"']"
regex_version_format_1    = re.compile(sPattern_version_format_1)

sPattern_version_date_format_1 = r"VERSION_DATE\s*=\s*[\"'](.+?)[\"']"
regex_version_date_format_1    = re.compile(sPattern_version_date_format_1)

# "FORMAT-2"
# "Maximum_version": "0.5.1",
# "Minimum_version": "0.4.10",

sPattern_maximum_version_format_2 = r"\"Maximum_version\"\s*:\s*\"(.+?)\""
regex_maximum_version_format_2    = re.compile(sPattern_maximum_version_format_2)

sPattern_minimum_version_format_2 = r"\"Minimum_version\"\s*:\s*\"(.+?)\""
regex_minimum_version_format_2    = re.compile(sPattern_minimum_version_format_2)

# -- list of components version information (location and format)

listofdictComponents = []

dictComponent = {}
dictComponent['NAME']           = "RobotFramework_AIO"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/RobotFramework_Testsuites/Config/CConfig.py"
dictComponent['VERSIONFORMAT']  = "FORMAT-1"
dictComponent['COMPAREVERSION'] = True
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "RobotFramework_Testsuites_config"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/RobotFramework_Testsuites/Config/robot_config.json"
dictComponent['VERSIONFORMAT']  = "FORMAT-2"
dictComponent['COMPAREVERSION'] = True
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "RobotFramework_Testsuites"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/RobotFramework_Testsuites/packageversion.py"
dictComponent['VERSIONFORMAT']  = "FORMAT-1"
dictComponent['COMPAREVERSION'] = False
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "GenPackageDoc"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/GenPackageDoc/version.py"
dictComponent['VERSIONFORMAT']  = "FORMAT-1"
dictComponent['COMPAREVERSION'] = False
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "RobotframeworkExtensions"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/RobotframeworkExtensions/version.py"
dictComponent['VERSIONFORMAT']  = "FORMAT-1"
dictComponent['COMPAREVERSION'] = False
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "PythonExtensionsCollection"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/PythonExtensionsCollection/version.py"
dictComponent['VERSIONFORMAT']  = "FORMAT-1"
dictComponent['COMPAREVERSION'] = False
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "JsonPreprocessor"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/JsonPreprocessor/version.py"
dictComponent['VERSIONFORMAT']  = "FORMAT-1"
dictComponent['COMPAREVERSION'] = False
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "QConnectBase"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/QConnectBase/version.py"
dictComponent['VERSIONFORMAT']  = "FORMAT-1"
dictComponent['COMPAREVERSION'] = False
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "QConnectionDLTLibrary"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/QConnectionDLTLibrary/version.py"
dictComponent['VERSIONFORMAT']  = "FORMAT-1"
dictComponent['COMPAREVERSION'] = False
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "RobotResults2RQM"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/RobotResults2RQM/version.py"
dictComponent['VERSIONFORMAT']  = "FORMAT-1"
dictComponent['COMPAREVERSION'] = False
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "RobotResults2DB"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/RobotResults2DB/version.py"
dictComponent['VERSIONFORMAT']  = "FORMAT-1"
dictComponent['COMPAREVERSION'] = False
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "TMLLog2RobotLog"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/TMLLog2RobotLog/version.py"
dictComponent['VERSIONFORMAT']  = "FORMAT-1"
dictComponent['COMPAREVERSION'] = False
listofdictComponents.append(dictComponent)

# Debug:
# PrettyPrint(listofdictComponents)
# print()

# --------------------------------------------------------------------------------------------------------------
# EXECUTION
# --------------------------------------------------------------------------------------------------------------
#TM***

sLogFile = f"{sThisScript}.log"
oLogFile = CFile(sLogFile)
oLogFile.Write(120*"*")
oLogFile.Write()
oLogFile.Write(f"{sThisScriptName} executed at " + time.strftime('%Y.%m.%d - %H:%M:%S'))
oLogFile.Write()
oLogFile.Write(120*"-")
oLogFile.Write()

nRJust = 55
bErrorHappened = False

listofdictVersions = [] # used vor version mistmatch detection

for dictComponent in listofdictComponents:
   NAME          = dictComponent['NAME']
   VERSIONFILE   = dictComponent['VERSIONFILE']
   VERSIONFORMAT = dictComponent['VERSIONFORMAT']
   if os.path.isfile(VERSIONFILE) is False:
      bSuccess = False
      sResult = f"Version file '{VERSIONFILE}' not found (component '{NAME}')"
      print(COLBR + CString.FormatResult(sThisScriptName, bSuccess, sResult))
      print()
      bErrorHappened = True
      continue

   sOut = f"* '{VERSIONFILE}'"
   print(sOut)
   oLogFile.Write(sOut)

   if VERSIONFORMAT == "FORMAT-1":
      oFile = CFile(VERSIONFILE)
      listLines, bSuccess, sResult = oFile.ReadLines(
                                                      bCaseSensitive  = True,
                                                      bSkipBlankLines = True,
                                                      sContains       = "VERSION",
                                                      bLStrip         = True,
                                                      bRStrip         = True,
                                                      bToScreen       = False
                                                     )
      del oFile
      if bSuccess is not True:
         sResult = CString.FormatResult(sThisScriptName, bSuccess, sResult)
         oLogFile.Write(sResult)
         print()
         print(COLBR + sResult)
         print()
         PrettyPrint(listLines)
         print()
         bErrorHappened = True
         continue

      listVersions = []
      listVersionDates = []
      for sLine in listLines:
         for sVersion in regex_version_format_1.findall(sLine):
            listVersions.append(sVersion)
         for sVersionDate in regex_version_date_format_1.findall(sLine):
            listVersionDates.append(sVersionDate)
      sVersion     = "; ".join(listVersions)
      sVersionDate = "; ".join(listVersionDates)

      print()
      oLogFile.Write()
      sTopic = f"{NAME} > VERSION"
      sOut = sTopic.rjust(nRJust, ' ') + " : " + sVersion
      oLogFile.Write(sOut)
      print(COLBY + sOut)
      sTopic = f"{NAME} > VERSION_DATE"
      sOut = sTopic.rjust(nRJust, ' ') + " : " + sVersionDate
      oLogFile.Write(sOut)
      print(COLBY + sOut)
      oLogFile.Write()
      print()

      if ( (sVersion == "") or (sVersionDate == "") ):
         sResult = CString.FormatResult(sMethod=sThisScriptName, bSuccess=False, sResult="Not able to parse content from file")
         oLogFile.Write(sResult)
         print(COLBR + sResult)
         print()
         bErrorHappened = True
         continue

      if dictComponent['COMPAREVERSION'] is True:
         dictComponent['VERSION'] = sVersion
         listofdictVersions.append(dictComponent)

   elif VERSIONFORMAT == "FORMAT-2":
      oFile = CFile(VERSIONFILE)
      listLines, bSuccess, sResult = oFile.ReadLines(
                                                      bCaseSensitive  = True,
                                                      bSkipBlankLines = True,
                                                      sContains       = "Maximum_version;Minimum_version",
                                                      bLStrip         = True,
                                                      bRStrip         = True,
                                                      bToScreen       = False
                                                     )
      del oFile
      if bSuccess is not True:
         sResult = CString.FormatResult(sThisScriptName, bSuccess, sResult)
         oLogFile.Write(sResult)
         print()
         print(COLBR + sResult)
         print()
         PrettyPrint(listLines)
         print()
         bErrorHappened = True
         continue

      listMaximumVersions = []
      listMinimumVersions = []
      for sLine in listLines:
         for sMaximumVersion in regex_maximum_version_format_2.findall(sLine):
            listMaximumVersions.append(sMaximumVersion)
         for sMinimumVersion in regex_minimum_version_format_2.findall(sLine):
            listMinimumVersions.append(sMinimumVersion)

      sMaximumVersion = "; ".join(listMaximumVersions)
      sMinimumVersion = "; ".join(listMinimumVersions)

      print()
      oLogFile.Write()
      sTopic = f"{NAME} > Maximum_version"
      sOut = sTopic.rjust(nRJust, ' ') + " : " + sMaximumVersion
      oLogFile.Write(sOut)
      print(COLBY + sOut)
      sTopic = f"{NAME} > Minimum_version"
      sOut = sTopic.rjust(nRJust, ' ') + " : " + sMinimumVersion
      oLogFile.Write(sOut)
      print(COLBY + sOut)
      print()
      oLogFile.Write()

      if ( (sMaximumVersion == "") or (sMinimumVersion == "") ):
         sResult = CString.FormatResult(sMethod=sThisScriptName, bSuccess=False, sResult="Not able to parse content from file")
         oLogFile.Write(sResult)
         print(COLBR + sResult)
         print()
         bErrorHappened = True
         continue

      if dictComponent['COMPAREVERSION'] is True:
         dictComponent['VERSION'] = sMaximumVersion
         listofdictVersions.append(dictComponent)

   else:
      sResult = CString.FormatResult(sMethod=sThisScriptName, bSuccess=False, sResult=f"Version format '{VERSIONFORMAT}' not supported")
      oLogFile.Write(sResult)
      print()
      print(COLBR + sResult)
      print()
      bErrorHappened = True
      continue

# eof for dictComponent in listofdictComponents:

# debug
# print()
# PrettyPrint(listofdictVersions)
# print()

# -- version control
bVersionMismatchHappened = False
for tupleCombinations in itertools.combinations(listofdictVersions, 2):
   dictVersion_1 = tupleCombinations[0]
   dictVersion_2 = tupleCombinations[1]
   sVersion_1 = dictVersion_1['VERSION']
   sVersion_2 = dictVersion_2['VERSION']
   if sVersion_1 != sVersion_2:
      sName_1 = dictVersion_1['NAME']
      sName_2 = dictVersion_2['NAME']
      sOut = f"version mismatch between version '{sVersion_1}' of '{sName_1}' and version '{sVersion_2}' of '{sName_2}'"
      sResult = CString.FormatResult(sMethod=sThisScriptName, bSuccess=False, sResult=sOut)
      oLogFile.Write(sResult)
      oLogFile.Write()
      print(COLBR + sResult)
      print()
      bVersionMismatchHappened = True
      continue
   # eof if sVersion_1 != sVersion_2:
# eof for tupleCombinations in itertools.combinations(listofdictVersions, 2):

if bErrorHappened is True:
   sOut = f"done with errors (return {ERROR})"
   sResult = CString.FormatResult(sMethod=sThisScriptName, bSuccess=False, sResult=sOut)
   oLogFile.Write(sResult)
   oLogFile.Write()
   print(COLBR + sResult)
   print()
   del oLogFile
   sys.exit(ERROR)
elif bVersionMismatchHappened is True:
   sOut = f"done with version mismatch (return {VERSION_MISMATCH})"
   sResult = CString.FormatResult(sMethod=sThisScriptName, bSuccess=False, sResult=sOut)
   oLogFile.Write(sResult)
   oLogFile.Write()
   print(COLBR + sResult)
   print()
   del oLogFile
   sys.exit(VERSION_MISMATCH)
else:
   oLogFile.Write("done")
   oLogFile.Write()
   print(COLBG + "done")
   print()
   del oLogFile
   sys.exit(SUCCESS)

# --------------------------------------------------------------------------------------------------------------

