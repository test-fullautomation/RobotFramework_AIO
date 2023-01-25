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
   sys.stderr.write(COLBR + f"{sMsg}!\n")

class enVersionType:
   current_version  = "current_version"
   required_version = "required_version"

class enVersionFormatType:
   format_1 = "format_1"
   format_2 = "format_2"

def get_version_as_int(sVersion=None, oLogFile=None):
   """Converts a version number from format
   "major_number.minor_number.patch_number" (type: str)
   to
   version_number (type: int)
   with:
   version_number = (major_number*900) + (minor_number*30) + patch_number
   This format (single integer) is suitable for version number checks.
   """
   version_number = None
   if sVersion is None:
      return sVersion
   sVersion = sVersion.strip()
   if sVersion == "":
      return None

   sPattern_Versions = r"^(\d+)\.(\d+)\.(\d+)$"
   regex_Versions    = re.compile(sPattern_Versions)
   listVersions = regex_Versions.findall(sVersion)
   # debug
   # PrettyPrint(listVersions)
   # pattern has to be found once in string and has to contain three positions
   if len(listVersions) != 1:
      sResult = f"Invalid format of version string: '{sVersion}'"
      printerror(sResult)
      print()
      if oLogFile is not None:
         oLogFile.Write(sResult)
         oLogFile.Write()
      return None
   tupleVersions = listVersions[0]
   if len(tupleVersions) != 3:
      sResult = f"Invalid format of version string: '{sVersion}'"
      printerror(sResult)
      print()
      if oLogFile is not None:
         oLogFile.Write(sResult)
         oLogFile.Write()
      return None

   #                 30^2                     30^1                   30^0       
   version_number = (int(tupleVersions[0])*900) + (int(tupleVersions[1])*30) + int(tupleVersions[2])

   # debug
   # print(f"---> int(major): {int(tupleVersions[0])}")
   # print(f"---> int(minor): {int(tupleVersions[1])}")
   # print(f"---> int(patch): {int(tupleVersions[2])}")
   # print(f"---> version_number: {version_number}")
   # print()

   return version_number

# eof def get_version_as_int(sVersion=None):


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
   print()
   sys.exit(ERROR)

print()
print(f"{sThisScriptName} is running under {sPlatformSystem} ({sOSName})")
print()

# --------------------------------------------------------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------------------------------------------------------
#TM***

# -- version and date formats

# enVersionFormatType.format_1
# VERSION      = "0.2.2"
# VERSION_DATE = "18.07.2022"

sPattern_version_format_1 = r"VERSION\s*=\s*[\"'](.+?)[\"']"
regex_version_format_1    = re.compile(sPattern_version_format_1)

sPattern_version_date_format_1 = r"VERSION_DATE\s*=\s*[\"'](.+?)[\"']"
regex_version_date_format_1    = re.compile(sPattern_version_date_format_1)

# enVersionFormatType.format_2
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
dictComponent['VERSIONFILE']    = f"{sSitePackages}/RobotFramework_TestsuitesManagement/Config/CConfig.py"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_1
dictComponent['VERSIONTYPE']    = enVersionType.current_version
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "RobotFramework_TestsuitesManagement_config"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/RobotFramework_TestsuitesManagement/Config/robot_config.json"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_2
dictComponent['VERSIONTYPE']    = enVersionType.required_version
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "RobotFramework_TestsuitesManagement"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/RobotFramework_TestsuitesManagement/packageversion.py"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_1
dictComponent['VERSIONTYPE']    = None
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "GenPackageDoc"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/GenPackageDoc/version.py"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_1
dictComponent['VERSIONTYPE']    = None
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "RobotframeworkExtensions"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/RobotframeworkExtensions/version.py"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_1
dictComponent['VERSIONTYPE']    = None
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "PythonExtensionsCollection"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/PythonExtensionsCollection/version.py"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_1
dictComponent['VERSIONTYPE']    = None
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "JsonPreprocessor"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/JsonPreprocessor/version.py"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_1
dictComponent['VERSIONTYPE']    = None
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "QConnectBase"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/QConnectBase/version.py"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_1
dictComponent['VERSIONTYPE']    = None
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "QConnectionDLTLibrary"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/QConnectionDLTLibrary/version.py"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_1
dictComponent['VERSIONTYPE']    = None
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "RobotLog2RQM"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/RobotLog2RQM/version.py"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_1
dictComponent['VERSIONTYPE']    = None
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "RobotLog2DB"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/RobotLog2DB/version.py"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_1
dictComponent['VERSIONTYPE']    = None
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "PyTestLog2DB"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/PyTestLog2DB/version.py"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_1
dictComponent['VERSIONTYPE']    = None
listofdictComponents.append(dictComponent)

dictComponent = {}
dictComponent['NAME']           = "TMLLog2RobotLog"
dictComponent['VERSIONFILE']    = f"{sSitePackages}/TMLLog2RobotLog/version.py"
dictComponent['VERSIONFORMAT']  = enVersionFormatType.format_1
dictComponent['VERSIONTYPE']    = None
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

nRJust = 62
bErrorHappened = False

dictVersionControl = {}
dictVersionControl['CURRENT_VERSION']      = None
dictVersionControl['REQUIRED_MAX_VERSION'] = None
dictVersionControl['REQUIRED_MIN_VERSION'] = None

for dictComponent in listofdictComponents:
   NAME          = dictComponent['NAME']
   VERSIONFILE   = dictComponent['VERSIONFILE']
   VERSIONFORMAT = dictComponent['VERSIONFORMAT']
   VERSIONTYPE   = dictComponent['VERSIONTYPE']
   if os.path.isfile(VERSIONFILE) is False:
      bSuccess = False
      sResult = f"Version file '{VERSIONFILE}' not found (component '{NAME}')"
      printerror(CString.FormatResult(sThisScriptName, bSuccess, sResult))
      print()
      oLogFile.Write(sResult)
      oLogFile.Write()
      bErrorHappened = True
      continue # for dictComponent in listofdictComponents:

   sOut = f"* '{VERSIONFILE}'"
   print(sOut)
   oLogFile.Write(sOut)

   if VERSIONFORMAT == enVersionFormatType.format_1:
      oFile = CFile(VERSIONFILE)
      listLines, bSuccess, sResult = oFile.ReadLines(
                                                      bCaseSensitive  = True,
                                                      bSkipBlankLines = True,
                                                      sComment        = "#",
                                                      sContains       = "VERSION", # this includes 'VERSION_DATE'
                                                      bLStrip         = True,
                                                      bRStrip         = True,
                                                      bToScreen       = False
                                                     )
      del oFile
      if bSuccess is not True:
         sResult = CString.FormatResult(sThisScriptName, bSuccess, sResult)
         oLogFile.Write(sResult)
         oLogFile.Write()
         printerror(sResult)
         print()
         PrettyPrint(listLines)
         print()
         bErrorHappened = True
         continue # for dictComponent in listofdictComponents:

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
      if sVersion == "":
         sResult = "'VERSION' not defined"
      else:
         sResult = f"{sVersion}"
         if VERSIONTYPE == enVersionType.current_version:
            dictVersionControl['CURRENT_VERSION'] = sVersion
      sOut = sTopic.rjust(nRJust, ' ') + f" : {sResult}"
      oLogFile.Write(sOut)
      print(COLBY + sOut)
      sTopic = f"{NAME} > VERSION_DATE"
      if sVersionDate == "":
         sResult = "'VERSION_DATE' not defined"
      else:
         sResult = f"{sVersionDate}"
      sOut = sTopic.rjust(nRJust, ' ') + f" : {sResult}"
      oLogFile.Write(sOut)
      print(COLBY + sOut)
      oLogFile.Write()
      print()

      if ( (sVersion == "") or (sVersionDate == "") ):
         sResult = CString.FormatResult(sMethod=sThisScriptName, bSuccess=False, sResult="Not able to parse content from file")
         oLogFile.Write(sResult)
         oLogFile.Write()
         printerror(sResult)
         print()
         bErrorHappened = True
         continue # for dictComponent in listofdictComponents:

   elif VERSIONFORMAT == enVersionFormatType.format_2:
      oFile = CFile(VERSIONFILE)
      listLines, bSuccess, sResult = oFile.ReadLines(
                                                      bCaseSensitive  = True,
                                                      bSkipBlankLines = True,
                                                      sComment        = "//",
                                                      sContains       = "Maximum_version;Minimum_version",
                                                      bLStrip         = True,
                                                      bRStrip         = True,
                                                      bToScreen       = False
                                                     )
      del oFile
      if bSuccess is not True:
         sResult = CString.FormatResult(sThisScriptName, bSuccess, sResult)
         oLogFile.Write(sResult)
         oLogFile.Write()
         print()
         printerror(sResult)
         print()
         PrettyPrint(listLines)
         print()
         bErrorHappened = True
         continue # for dictComponent in listofdictComponents:

      listMaximumVersions = []
      listMinimumVersions = []
      for sLine in listLines:
         for sMaximumVersion in regex_maximum_version_format_2.findall(sLine):
            listMaximumVersions.append(sMaximumVersion)
         for sMinimumVersion in regex_minimum_version_format_2.findall(sLine):
            listMinimumVersions.append(sMinimumVersion)

      sMaximumVersion = "; ".join(listMaximumVersions)
      sMinimumVersion = "; ".join(listMinimumVersions)

      # -- both Maximum_version and Minimum_version are optional

      print()
      oLogFile.Write()
      sTopic = f"{NAME} > Maximum_version"
      if sMaximumVersion == "":
         sResult = "'Maximum_version' not defined"
      else:
         sResult = f"{sMaximumVersion}"
         if VERSIONTYPE == enVersionType.required_version:
            dictVersionControl['REQUIRED_MAX_VERSION'] = sMaximumVersion
      sOut = sTopic.rjust(nRJust, ' ') + f" : {sResult}"
      oLogFile.Write(sOut)
      print(COLBY + sOut)
      sTopic = f"{NAME} > Minimum_version"
      if sMinimumVersion == "":
         sResult = "'Minimum_version' not defined"
      else:
         sResult = f"{sMinimumVersion}"
         if VERSIONTYPE == enVersionType.required_version:
            dictVersionControl['REQUIRED_MIN_VERSION'] = sMinimumVersion
      sOut = sTopic.rjust(nRJust, ' ') + f" : {sResult}"
      oLogFile.Write(sOut)
      print(COLBY + sOut)
      print()
      oLogFile.Write()

   else:
      sResult = CString.FormatResult(sMethod=sThisScriptName, bSuccess=False, sResult=f"Version format '{VERSIONFORMAT}' not supported")
      oLogFile.Write(sResult)
      oLogFile.Write()
      printerror(sResult)
      print()
      bErrorHappened = True
      continue # for dictComponent in listofdictComponents:

   # eof else - if VERSIONFORMAT == enVersionFormatType.format_1:
# eof for dictComponent in listofdictComponents:

# -- version check (between current bundle version defined in Python code of component RobotFramework_TestsuitesManagement
#    and optional maximum and minimum version defined in JSON configuration file of component RobotFramework_TestsuitesManagement)

# debug
# print()
# PrettyPrint(dictVersionControl)
# print()

CURRENT_VERSION      = dictVersionControl['CURRENT_VERSION']
REQUIRED_MAX_VERSION = dictVersionControl['REQUIRED_MAX_VERSION']
REQUIRED_MIN_VERSION = dictVersionControl['REQUIRED_MIN_VERSION']

bVersionMismatch      = False
bVersionCheckExecuted = False

if CURRENT_VERSION is None:
   bErrorHappened = True
   print()
   print(COLBY + "Version check not possible because of missing Robot Framework AIO version")
   print()
else:
   if ( (REQUIRED_MAX_VERSION is None) and (REQUIRED_MIN_VERSION is None) ):
      print()
      print(COLBY + "Version check skipped because 'Maximum_version' and 'Minimum_version' are not defined")
      print()
   else:
      nCurrentVersion = get_version_as_int(CURRENT_VERSION, oLogFile)
      if nCurrentVersion is None:
         bErrorHappened = True
      else:
         # current version available => version check is possible in general
         nRequiredMaxVersion = None
         if REQUIRED_MAX_VERSION is not None:
            nRequiredMaxVersion = get_version_as_int(REQUIRED_MAX_VERSION, oLogFile)
            if nRequiredMaxVersion is None:
               bErrorHappened = True
         nRequiredMinVersion = None
         if REQUIRED_MIN_VERSION is not None:
            nRequiredMinVersion = get_version_as_int(REQUIRED_MIN_VERSION, oLogFile)
            if nRequiredMinVersion is None:
               bErrorHappened = True
         bVersionCheckPossible = True
         if ( (nRequiredMaxVersion is not None) and (nRequiredMinVersion is not None) ):
            if nRequiredMaxVersion < nRequiredMinVersion:
               sResult = f"Invalid version numbers: The required maximum version {REQUIRED_MAX_VERSION} is smaller than the required minimum version {REQUIRED_MIN_VERSION}."
               oLogFile.Write(sResult)
               oLogFile.Write()
               printerror(sResult)
               print()
               bErrorHappened = True
               bVersionCheckPossible = False
         if bVersionCheckPossible is True:
            if nRequiredMaxVersion is not None:
               # max version check
               if nCurrentVersion > nRequiredMaxVersion:
                  sResult = f"Version mismatch: Current Robot Framework bundle version {CURRENT_VERSION} is bigger than the allowed maximum version {REQUIRED_MAX_VERSION}."
                  oLogFile.Write(sResult)
                  oLogFile.Write()
                  printerror(sResult)
                  print()
                  bVersionMismatch = True
               bVersionCheckExecuted = True
            if nRequiredMinVersion is not None:
               # min version check
               if nCurrentVersion < nRequiredMinVersion:
                  sResult = f"Version mismatch: Current Robot Framework bundle version {CURRENT_VERSION} is smaller than the allowed minimum version {REQUIRED_MIN_VERSION}."
                  oLogFile.Write(sResult)
                  oLogFile.Write()
                  printerror(sResult)
                  print()
                  bVersionMismatch = True
               bVersionCheckExecuted = True

# eof else ... if CURRENT_VERSION is None:

if bErrorHappened is True:
   sResult = f"Done with errors (return {ERROR})"
   oLogFile.Write(sResult)
   oLogFile.Write()
   printerror(sResult)
   print()
   del oLogFile
   sys.exit(ERROR)

if bVersionMismatch is True:
   sResult = f"Done with version mismatch (return {VERSION_MISMATCH})"
   oLogFile.Write(sResult)
   oLogFile.Write()
   printerror(sResult)
   print()
   del oLogFile
   sys.exit(VERSION_MISMATCH)

if ( (bVersionCheckExecuted is True) and (bVersionMismatch is False) ):
   sResult = "Version check passed"
   oLogFile.Write(sResult)
   oLogFile.Write()
   print(COLBG + sResult)
   print()

oLogFile.Write("Done")
oLogFile.Write()
print(COLBG + "Done")
print()
del oLogFile
sys.exit(SUCCESS)

# --------------------------------------------------------------------------------------------------------------

