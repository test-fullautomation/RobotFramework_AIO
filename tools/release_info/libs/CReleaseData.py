# **************************************************************************************************************
#
#  Copyright 2020-2024 Robert Bosch GmbH
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
# CReleaseData.py
#
# XC-HWP/ESW3-Queckenstedt
#
# 02.01.2024
#
# --------------------------------------------------------------------------------------------------------------

import os, sys, platform, shlex, subprocess, json, argparse
import colorama as col

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Utils.CUtils import *

col.init(autoreset=True)
COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN

# --------------------------------------------------------------------------------------------------------------

def printfailure(sMsg, prefix=None):
   if prefix is None:
      sMsg = COLBR + f"{sMsg}!\n\n"
   else:
      sMsg = COLBR + f"{prefix}:\n{sMsg}!\n\n"
   sys.stderr.write(sMsg)

# --------------------------------------------------------------------------------------------------------------

class CReleaseData():
   """Read release info data from JSON files
   """

   def __init__(self, oConfig=None):

      sMethod = "CReleaseData.__init__"

      if oConfig is None:
         raise Exception(CString.FormatResult(sMethod, None, "oConfig is None"))

      self.__oConfig = oConfig

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetReleaseData(self):

      sMethod = "GetReleaseData"

      bSuccess = None
      sResult  = "UNKNOWN"

      VERSION_CONFIG         = self.__oConfig.Get('VERSION_CONFIG')
      THISAPPFULLNAME        = self.__oConfig.Get('THISAPPFULLNAME')
      PACKAGE_CONTEXT_FILE   = self.__oConfig.Get('PACKAGE_CONTEXT_FILE')
      RELEASE_MAIN_INFO_FILE = self.__oConfig.Get('RELEASE_MAIN_INFO_FILE')
      RELEASE_ITEM_FILES     = self.__oConfig.Get('RELEASE_ITEM_FILES')

      print()
      print(f"{THISAPPFULLNAME} reading configuration v. {VERSION_CONFIG}")
      print()

      # -- package context file

      oPackageContextFile = CFile(PACKAGE_CONTEXT_FILE)
      listLines, bSuccess, sResult = oPackageContextFile.ReadLines(bSkipBlankLines=True)
      del oPackageContextFile
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)
      # PrettyPrint(listLines, sPrefix="listLines")

      dictPackageContext = None
      try:
         dictPackageContext = json.loads("\n".join(listLines))
      except Exception as reason:
         bSuccess = None
         sResult  = str(reason) + f" - while parsing JSON content of '{PACKAGE_CONTEXT_FILE}'"
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      if dictPackageContext is None:
         bSuccess = None
         sResult  = "dictPackageContext is None"
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # PrettyPrint(dictPackageContext, sPrefix="dictPackageContext")

      self.__oConfig.Set('PACKAGE_CONTEXT', dictPackageContext)

      # -- release main info

      oReleaseMainInfoFile = CFile(RELEASE_MAIN_INFO_FILE)
      listLines, bSuccess, sResult = oReleaseMainInfoFile.ReadLines(bSkipBlankLines=False, sComment='#') # no skip of blank lines because of RST content (blank lines are part of the RST syntax)
      del oReleaseMainInfoFile
      if bSuccess is not True:
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      dictReleaseMainInfo = None
      try:
         dictReleaseMainInfo = json.loads("\n".join(listLines), strict=False) # strict=False allows multi line content inside values defined within JSON files
      except Exception as reason:
         bSuccess = None
         sResult  = str(reason) + f" - while parsing JSON content of '{RELEASE_MAIN_INFO_FILE}'"
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      if dictReleaseMainInfo is None:
         bSuccess = None
         sResult  = "dictReleaseMainInfo is None"
         return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      # PrettyPrint(dictReleaseMainInfo, sPrefix="dictReleaseMainInfo")

      self.__oConfig.Set('RELEASE_MAIN_INFO', dictReleaseMainInfo)

      # -- RELEASE_ITEM_FILES

      dictAllReleaseItems = {}

      for sReleaseItemFile in RELEASE_ITEM_FILES:

         oReleaseItemFile = CFile(sReleaseItemFile)
         listLines, bSuccess, sResult = oReleaseItemFile.ReadLines(bSkipBlankLines=False, sComment='#') # no skip of blank lines because of RST content (blank lines are part of the RST syntax)
         del oReleaseItemFile
         if bSuccess is not True:
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

         dictReleaseItemFileContent = None
         try:
            dictReleaseItemFileContent = json.loads("\n".join(listLines), strict=False) # strict=False allows multi line content inside values defined within JSON files
         except Exception as reason:
            bSuccess = None
            sResult  = str(reason) + f" - while parsing JSON content of '{sReleaseItemFile}'"
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

         if dictReleaseItemFileContent is None:
            bSuccess = None
            sResult  = "dictReleaseItemFileContent is None"
            return bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

         # PrettyPrint(dictReleaseItemFileContent, sPrefix="dictReleaseItemFileContent")

         # TODO: separate function to synchronize keys (expected <-> got)
         sComponentName = dictReleaseItemFileContent['COMPONENT'] # TODO error handling
         dictReleases = dictReleaseItemFileContent['RELEASES'] # TODO error handling

         dictAllReleaseItems[sComponentName] = dictReleases
         self.__oConfig.Set('AllRELEASEITEMS', dictAllReleaseItems)

      # eof for sReleaseItemFile in RELEASE_ITEM_FILES:

      bSuccess = True
      sResult  = "Done"
      return bSuccess, sResult

   # eof def GetReleaseData(self):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

# eof class CReleaseData():

# --------------------------------------------------------------------------------------------------------------
