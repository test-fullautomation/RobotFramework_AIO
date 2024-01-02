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
# CConfig.py
#
# XC-HWP/ESW3-Queckenstedt
#
# 02.01.2024
#
# --------------------------------------------------------------------------------------------------------------

import os, sys, platform, shlex, subprocess, json, argparse
import colorama as col
import pypandoc

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

class CConfig():
   """The configuration of release info application
   """

   def __init__(self, sCalledBy=None):

      sMethod = "CConfig.__init__"

      # -- configuration init
      self.__dictConfig = {}

      if sCalledBy is None:
         raise Exception(CString.FormatResult(sMethod, None, "sCalledBy is None"))

      # -- try to access pypandoc; if pypandoc is not installed, we detect this already here as early as possible
      try:
         pypandoc.get_pandoc_path()
      except Exception as reason:
         raise Exception(CString.FormatResult(sMethod, None, str(reason)))

      # -- check platform system
      PLATFORMSYSTEM = platform.system()
      if PLATFORMSYSTEM not in ("Windows", "Linux"):
         raise Exception(CString.FormatResult(sMethod, None, f"Platform {PLATFORMSYSTEM} not supported"))

      # -- configuration: common environment

      THISAPP                                = CString.NormalizePath(sCalledBy)
      self.__dictConfig['THISAPP']           = THISAPP
      self.__dictConfig['THISAPPNAME']       = os.path.basename(THISAPP)
      REFERENCEPATH_APP                      = os.path.dirname(THISAPP) # position of main() app is reference for all relative paths
      self.__dictConfig['REFERENCEPATH_APP'] = REFERENCEPATH_APP
      OSNAME                                 = os.name
      self.__dictConfig['OSNAME']            = OSNAME
      self.__dictConfig['PLATFORMSYSTEM']    = PLATFORMSYSTEM
      PYTHON                                 = CString.NormalizePath(sys.executable)
      self.__dictConfig['PYTHON']            = PYTHON
      self.__dictConfig['PYTHONPATH']        = os.path.dirname(PYTHON)
      self.__dictConfig['PYTHONVERSION']     = sys.version
         
      # -- configuration: command line

      oCmdLineParser = argparse.ArgumentParser()
      oCmdLineParser.add_argument('--configfile', type=str, help='Path and name of release info configuration file (required)')
      oCmdLineParser.add_argument('--mailaddress', type=str, help='Mail address of initial sender and recipient (optional)')
      oCmdLineParser.add_argument('--configdump', action='store_true', help='If True, basic configuration values are dumped to console; default: False')

      oCmdLineArgs = oCmdLineParser.parse_args()

      CONFIGFILE = None
      if oCmdLineArgs.configfile != None:
         CONFIGFILE = CString.NormalizePath(oCmdLineArgs.configfile, sReferencePathAbs=REFERENCEPATH_APP)
      if CONFIGFILE is None:
         raise Exception(CString.FormatResult(sMethod, None, "Missing configuration file in command line"))

      if os.path.isfile(CONFIGFILE) is False:
         raise Exception(CString.FormatResult(sMethod, None, f"The configuration file '{CONFIGFILE}' does not exist"))

      self.__dictConfig['CONFIGFILE'] = CONFIGFILE

      MAILADDRESS = None
      if oCmdLineArgs.mailaddress != None:
         MAILADDRESS = oCmdLineArgs.mailaddress
      self.__dictConfig['MAILADDRESS'] = MAILADDRESS

      CONFIGDUMP = False
      if oCmdLineArgs.configdump != None:
         CONFIGDUMP = oCmdLineArgs.configdump
      self.__dictConfig['CONFIGDUMP'] = CONFIGDUMP

      # -- get and check content of configuration file

      oJsonConfigFile = CFile(CONFIGFILE)
      listLines, bSuccess, sResult = oJsonConfigFile.ReadLines(bSkipBlankLines=True, sComment='#')
      del oJsonConfigFile
      if bSuccess is not True:
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      dictJsonValues = None
      try:
         dictJsonValues = json.loads("\n".join(listLines))
      except Exception as reason:
         bSuccess = None
         sResult  = str(reason) + f" - while parsing JSON content of '{CONFIGFILE}'"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      if dictJsonValues is None:
         bSuccess = None
         sResult  = "dictJsonValues is None"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # -- main keys

      tupleConfigKeys = ("VERSION_CONFIG", "PACKAGE_CONTEXT_FILE", "RELEASE_MAIN_INFO_FILE", "RELEASE_ITEM_FILES")

      for sKey in dictJsonValues:
         if sKey not in tupleConfigKeys:
            raise Exception(CString.FormatResult(sMethod, False, f"Found unexpected key '{sKey}' in configuration file"))

      listConfigKeys = list(dictJsonValues.keys())
      for sKey in tupleConfigKeys:
         if sKey not in listConfigKeys:
            raise Exception(CString.FormatResult(sMethod, False, f"Missing key '{sKey}' in configuration file"))
         
      # -- update configuration with content of main keys

      # -- reference for relative paths inside the release info configuration file is the location of this file;
      #    this file also defines the position of the HTML output file
      REFERENCEPATH_CONFIG = os.path.dirname(CONFIGFILE)
      self.__dictConfig['REFERENCEPATH_CONFIG'] = REFERENCEPATH_CONFIG

      self.__dictConfig['VERSION_CONFIG'] = dictJsonValues['VERSION_CONFIG']
      PACKAGE_CONTEXT_FILE = dictJsonValues['PACKAGE_CONTEXT_FILE']
      self.__dictConfig['PACKAGE_CONTEXT_FILE'] = CString.NormalizePath(PACKAGE_CONTEXT_FILE, sReferencePathAbs=REFERENCEPATH_CONFIG)
      RELEASE_MAIN_INFO_FILE = dictJsonValues['RELEASE_MAIN_INFO_FILE']
      self.__dictConfig['RELEASE_MAIN_INFO_FILE'] = CString.NormalizePath(RELEASE_MAIN_INFO_FILE, sReferencePathAbs=REFERENCEPATH_CONFIG)
      RELEASE_ITEM_FILES = dictJsonValues['RELEASE_ITEM_FILES']
      for index, sReleaseItemFile in enumerate(RELEASE_ITEM_FILES):
         RELEASE_ITEM_FILES[index] = CString.NormalizePath(sReleaseItemFile, sReferencePathAbs=REFERENCEPATH_CONFIG)
      self.__dictConfig['RELEASE_ITEM_FILES'] = RELEASE_ITEM_FILES

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def __del__(self):
      del self.__dictConfig

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def DumpConfig(self):
      """Prints all configuration values to console."""
      listFormattedOutputLines = []
      # -- printing configuration to console
      print()
      # PrettyPrint(self.__dictConfig, sPrefix="Config")
      nJust = 32
      for key, value in self.__dictConfig.items():
         if isinstance(value, list):
            nCnt = 0
            for element in value:
               nCnt = nCnt + 1
               element_cnt = f"{key} ({nCnt})"
               sLine = element_cnt.rjust(nJust, ' ') + " : " + str(element)
               print(sLine)
               listFormattedOutputLines.append(sLine)
         else:
            sLine = key.rjust(nJust, ' ') + " : " + str(value)
            print(sLine)
            listFormattedOutputLines.append(sLine)
      print()
      return listFormattedOutputLines
   # eof def DumpConfig(self):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def Get(self, sName=None):
      """Returns the configuration value belonging to a key name."""
      if ( (sName is None) or (sName not in self.__dictConfig) ):
         print()
         printfailure(f"Configuration parameter '{sName}' not existing")
         return None # returning 'None' in case of key is not existing !!!
      else:
         return self.__dictConfig[sName]
   # eof def Get(self, sName=None):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def Set(self, sName=None, sValue=None):
      """Sets a new configuration parameter."""
      sName = f"{sName}"
      self.__dictConfig[sName] = sValue
   # eof def Set(self, sName=None, sValue=None):

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def PrettyPrint(self):
      """Makes a PrettyPrint of some main configuration values"""
      tupleExclude = ("RELEASE_MAIN_INFO", "AllRELEASEITEMS")
      listKeys = list(self.__dictConfig.keys())
      for sKey in listKeys:
         if sKey not in tupleExclude:
            PrettyPrint(self.__dictConfig[sKey], sPrefix=sKey.rjust(32, ' '))

# eof class CConfig():

# --------------------------------------------------------------------------------------------------------------
