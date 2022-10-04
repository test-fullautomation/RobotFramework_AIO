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
# CTestTriggerConfig.py
#
# XC-CT/ECA3-Queckenstedt
#
# 04.10.2022
#
# --------------------------------------------------------------------------------------------------------------

"""Python module containing the configuration for the RobotFramework AIO test trigger.
"""

# --------------------------------------------------------------------------------------------------------------

import os, sys, time, platform, json, argparse
import colorama as col

from version import NAME
from version import VERSION
from version import VERSION_DATE

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Utils.CUtils import *

col.init(autoreset=True)
COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLNY = col.Style.NORMAL + col.Fore.YELLOW
COLBW = col.Style.BRIGHT + col.Fore.WHITE

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

def printerror(sMsg):
   sys.stderr.write(COLBR + f"Error: {sMsg}!\n")

def printexception(sMsg):
   sys.stderr.write(COLBR + f"Exception: {sMsg}!\n")

# --------------------------------------------------------------------------------------------------------------

class CTestTriggerConfig():

   def __init__(self, sWhoAmI=None):
      """Constructor of class ``CTestTriggerConfig``.
      """

      sMethod = "CTestTriggerConfig.__init__"

      self.__dictTestTriggerConfig = {}
      self.__listofdictTestExecutions = [] # subset only, mostly for debug purposes

      if sWhoAmI is None:
         bSuccess = None
         sResult  = f"sWhoAmI is None"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      sWhoAmI = CString.NormalizePath(sWhoAmI)
      sReferencePath = os.path.dirname(sWhoAmI)
      # update config
      self.__dictTestTriggerConfig['WHOAMI']        = sWhoAmI
      self.__dictTestTriggerConfig['REFERENCEPATH'] = sReferencePath
      self.__dictTestTriggerConfig['NAME']          = NAME
      self.__dictTestTriggerConfig['VERSION']       = VERSION
      self.__dictTestTriggerConfig['VERSION_DATE']  = VERSION_DATE

      self.__GetCommandLine()

      sTestTriggerConfigFile = self.__dictTestTriggerConfig['TESTTRIGGERCONFIGFILE']
      if sTestTriggerConfigFile is None:
         # no config file given in command line, therefore using default config file (within subfolder 'config')
         sConfigPath = f"{sReferencePath}/config"
         sTestTriggerConfigFileName = "testtrigger_config.json"
         sTestTriggerConfigFile = f"{sConfigPath}/{sTestTriggerConfigFileName}"
         self.__dictTestTriggerConfig['TESTTRIGGERCONFIGFILE'] = sTestTriggerConfigFile

      if os.path.isfile(sTestTriggerConfigFile) is False:
         bSuccess = None
         sResult  = f"Configuration file not found: '{sTestTriggerConfigFile}'."
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      sConfigPath = os.path.dirname(sTestTriggerConfigFile)
      self.__dictTestTriggerConfig['CONFIGPATH'] = sConfigPath # absolute path that is the reference for all relative paths within the config file

      # operating system and temporary path
      sOSName = os.name
      sTmpPath = None
      sPlatformSystem = platform.system()
      if sPlatformSystem == "Windows":
         sTmpPath = CString.NormalizePath("%TMP%")
      elif sPlatformSystem == "Linux":
         sTmpPath = "/tmp"
      else:
         bSuccess = None
         sResult  = f"Platform system {sPlatformSystem} ({sOSName}) not supported"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # update config
      self.__dictTestTriggerConfig['PYTHON']         = CString.NormalizePath(sys.executable)
      self.__dictTestTriggerConfig['PYTHONVERSION']  = sys.version
      self.__dictTestTriggerConfig['PLATFORMSYSTEM'] = sPlatformSystem
      self.__dictTestTriggerConfig['OSNAME']         = sOSName
      self.__dictTestTriggerConfig['TMPPATH']        = sTmpPath

      self.PrintConfig()

      # Read the test trigger configuration from separate json file.
      #
      # The json file may contain lines that are commented out by a '#' at the beginning of the line.
      # Therefore we read in this file in text format, remove the comments and save the cleaned file within the temp folder.
      # Now it's a valid json file and we read the file from there.

      sTestTriggerConfigFileName = os.path.basename(sTestTriggerConfigFile)
      sTestTriggerConfigFileCleaned = f"{sTmpPath}/{sTestTriggerConfigFileName}"

      oTestTriggerConfigFile = CFile(sTestTriggerConfigFile)
      listLines, bSuccess, sResult = oTestTriggerConfigFile.ReadLines(bSkipBlankLines=True, sComment='#')
      del oTestTriggerConfigFile
      if bSuccess is not True:
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      oTestTriggerConfigFileCleaned = CFile(sTestTriggerConfigFileCleaned)
      bSuccess, sResult = oTestTriggerConfigFileCleaned.Write(listLines)
      del oTestTriggerConfigFileCleaned
      if bSuccess is not True:
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # access to json file (external configuration values)
      dictExternalConfigValues = None
      try:
         hTestTriggerConfigFileCleaned = open(sTestTriggerConfigFileCleaned)
         dictExternalConfigValues = json.load(hTestTriggerConfigFileCleaned)
         hTestTriggerConfigFileCleaned.close()
         del hTestTriggerConfigFileCleaned
      except Exception as reason:
         bSuccess = None
         sResult  = str(reason)
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      if dictExternalConfigValues is None:
         bSuccess = None
         sResult  = "dictExternalConfigValues is None"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # PrettyPrint(dictExternalConfigValues, sPrefix="from json file")
      # print()

      # take over keys and values from external configuration values (json file)
      for key, value in dictExternalConfigValues.items():
         self.__dictTestTriggerConfig[key] = value

      # print()
      # PrettyPrint(self.__dictTestTriggerConfig, sPrefix="TestTriggerConfig")
      # print()

      # Prepare and check all paths from external json configuration file.
      # The absolute path that is the reference for all possible relative paths inside the json file, is 'sConfigPath'.

      tupleSupportedTestTypes = ('ROBOT', 'PYTEST')

      # -- 1. section 'COMPONENTS'
      if "COMPONENTS" not in self.__dictTestTriggerConfig:
         bSuccess = None
         sResult  = f"Missing key 'COMPONENTS' in file {sTestTriggerConfigFile}"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
      listofdictComponents = self.__dictTestTriggerConfig['COMPONENTS']
      for dictComponent in listofdictComponents:
         COMPONENTROOTPATH = CString.NormalizePath(dictComponent['COMPONENTROOTPATH'], sReferencePathAbs=sConfigPath)
         dictComponent['COMPONENTROOTPATH'] = COMPONENTROOTPATH
         if os.path.isdir(COMPONENTROOTPATH) is False:
            bSuccess = None
            sResult  = f"Folder '{COMPONENTROOTPATH}' does not exist"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         if "TESTFOLDER" not in dictComponent:
            bSuccess = None
            sResult  = f"Missing key 'TESTFOLDER' in file {sTestTriggerConfigFile}, component '{COMPONENTROOTPATH}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         TESTFOLDER = f"{COMPONENTROOTPATH}/{dictComponent['TESTFOLDER']}"
         dictComponent['TESTFOLDER'] = TESTFOLDER
         if os.path.isdir(TESTFOLDER) is False:
            bSuccess = None
            sResult  = f"Folder '{TESTFOLDER}' does not exist"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         if "TESTEXECUTOR" not in dictComponent:
            bSuccess = None
            sResult  = f"Missing key 'TESTEXECUTOR' in file {sTestTriggerConfigFile}, component '{COMPONENTROOTPATH}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         TESTEXECUTOR = f"{TESTFOLDER}/{dictComponent['TESTEXECUTOR']}"
         dictComponent['TESTEXECUTOR'] = TESTEXECUTOR
         if os.path.isfile(TESTEXECUTOR) is False:
            bSuccess = None
            sResult  = f"File '{TESTEXECUTOR}' does not exist"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         if "TESTTYPE" not in dictComponent:
            bSuccess = None
            sResult  = f"Missing key 'TESTTYPE' in file {sTestTriggerConfigFile}, component '{COMPONENTROOTPATH}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         TESTTYPE = dictComponent['TESTTYPE']
         if TESTTYPE not in tupleSupportedTestTypes:
            bSuccess = None
            sResult  = f"TESTTYPE '{TESTTYPE}' not supported in file {sTestTriggerConfigFile}, component '{COMPONENTROOTPATH}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         dictComponent['LOGFILE'] = CString.NormalizePath(dictComponent['LOGFILE'], sReferencePathAbs=sConfigPath) # will be created, therefore existence is not checked here

         # short summary
         dictTestExecution = {}
         dictTestExecution['TESTFOLDER'] = dictComponent['TESTFOLDER']
         dictTestExecution['TESTTYPE']   = dictComponent['TESTTYPE']
         self.__listofdictTestExecutions.append(dictTestExecution)

      # eof for dictComponent in listofdictComponents:
      # PrettyPrint(listofdictComponents, sPrefix="listofdictComponents")
      # print()

      # -- 2. section 'TESTTYPES'
      if "TESTTYPES" not in self.__dictTestTriggerConfig:
         bSuccess = None
         sResult  = f"Missing key 'TESTTYPES' in file {sTestTriggerConfigFile}"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
      for TESTTYPE in self.__dictTestTriggerConfig['TESTTYPES'].keys():
         if TESTTYPE not in tupleSupportedTestTypes:
            bSuccess = None
            sResult  = f"TESTTYPE '{TESTTYPE}' not supported in file {sTestTriggerConfigFile}, section 'TESTTYPES'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         dictTestType = self.__dictTestTriggerConfig['TESTTYPES'][TESTTYPE]
         if "DATABASEEXECUTOR" not in dictTestType:
            bSuccess = None
            sResult  = f"Missing key 'DATABASEEXECUTOR' in file {sTestTriggerConfigFile}, section 'TESTTYPES', test type '{TESTTYPE}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         DATABASEEXECUTOR = CString.NormalizePath(self.__dictTestTriggerConfig['TESTTYPES'][TESTTYPE]['DATABASEEXECUTOR'], sReferencePathAbs=sConfigPath)
         if os.path.isfile(DATABASEEXECUTOR) is False:
            bSuccess = None
            sResult  = f"File '{DATABASEEXECUTOR}' does not exist"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         self.__dictTestTriggerConfig['TESTTYPES'][TESTTYPE]['DATABASEEXECUTOR'] = DATABASEEXECUTOR
         if "ADDITIONALCONFIG" not in dictTestType:
            bSuccess = None
            sResult  = f"Missing key 'ADDITIONALCONFIG' in file {sTestTriggerConfigFile}, section 'TESTTYPES', test type '{TESTTYPE}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         ADDITIONALCONFIG = CString.NormalizePath(self.__dictTestTriggerConfig['TESTTYPES'][TESTTYPE]['ADDITIONALCONFIG'], sReferencePathAbs=sConfigPath)
         if os.path.isfile(ADDITIONALCONFIG) is False:
            bSuccess = None
            sResult  = f"File '{ADDITIONALCONFIG}' does not exist"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         self.__dictTestTriggerConfig['TESTTYPES'][TESTTYPE]['ADDITIONALCONFIG'] = ADDITIONALCONFIG
         # TODO: needs more clarification
         # if "ADDITIONALCMDLINE" not in dictTestType:
            # bSuccess = None
            # sResult  = f"Missing key 'ADDITIONALCMDLINE' in file {sTestTriggerConfigFile}, section 'TESTTYPES', test type '{TESTTYPE}'"
            # raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))


      # final debug
      # PrettyPrint(self.__dictTestTriggerConfig, sPrefix="final TestTriggerConfig")

      # overview about planned test executions
      self.PrintConfiguredTestExecutions()

   # eof def __init__(self, sWhoAmI=None):


   def __del__(self):
      del self.__dictTestTriggerConfig

   def __GetCommandLine(self):
      oCmdLineParser = argparse.ArgumentParser()
      oCmdLineParser.add_argument('--robotcommandline', type=str, help='Command line for RobotFramework AIO (optional).')
      oCmdLineParser.add_argument('--pytestcommandline', type=str, help='Command line for Python pytest module (optional).')
      oCmdLineParser.add_argument('--configfile', type=str, help='Path and name of configuration file (optional).')
      oCmdLineArgs = oCmdLineParser.parse_args()

      sRobotCommandLine = None
      if oCmdLineArgs.robotcommandline is not None:
         sRobotCommandLine = oCmdLineArgs.robotcommandline
         # recover the masking of nested quotes
         sRobotCommandLine = sRobotCommandLine.replace("\"", r"\"")
         sRobotCommandLine = sRobotCommandLine.replace("'", r"\"")
      self.__dictTestTriggerConfig['ROBOTCOMMANDLINE'] = sRobotCommandLine

      sPytestCommandLine = None
      if oCmdLineArgs.pytestcommandline is not None:
         sPytestCommandLine = oCmdLineArgs.pytestcommandline
         # recover the masking of nested quotes
         sPytestCommandLine = sPytestCommandLine.replace("\"", r"\"")
         sPytestCommandLine = sPytestCommandLine.replace("'", r"\"")
      self.__dictTestTriggerConfig['PYTESTCOMMANDLINE'] = sPytestCommandLine

      sConfigFile = None
      if oCmdLineArgs.configfile is not None:
         sConfigFile = oCmdLineArgs.configfile
         sConfigFile = CString.NormalizePath(sConfigFile, sReferencePathAbs=self.__dictTestTriggerConfig['REFERENCEPATH'])
      self.__dictTestTriggerConfig['TESTTRIGGERCONFIGFILE'] = sConfigFile

   # eof def __GetCommandLine(self):

   def PrintConfig(self):
      # -- print configuration to console
      nJust = 25
      print()
      for sKey in self.__dictTestTriggerConfig:
         print(sKey.rjust(nJust, ' ') + " : " + str(self.__dictTestTriggerConfig[sKey]))
      print()
   # eof def PrintConfig(self):

   def PrintConfiguredTestExecutions(self):
      # -- print configured test executions to console
      nJust = 8
      print()
      print("Configured test folders together with their test types:")
      print()
      for dictTestExecution in self.__listofdictTestExecutions:
         print(dictTestExecution['TESTTYPE'].rjust(nJust, ' ') + " : " + str(dictTestExecution['TESTFOLDER']))
      print()
   # eof def PrintConfig(self):

   def PrintConfigKeys(self):
      """Prints all configuration key names to console.
      """
      # -- print configuration keys to console
      print()
      listKeys = self.__dictTestTriggerConfig.keys()
      sKeys = "[" + ", ".join(listKeys) + "]"
      print(sKeys)
      print()
   # eof def PrintConfigKeys(self):


   def Get(self, sName=None):
      """Returns the configuration value belonging to a key name.
      """
      if ( (sName is None) or (sName not in self.__dictTestTriggerConfig) ):
         print()
         sError = f"Configuration parameter '{sName}' not existing!"
         printerror(CString.FormatResult("Get", False, sError))
         # from here it's standard output:
         print()
         print("Use instead one of:")
         self.PrintConfigKeys()
         return None # returning 'None' in case of key is not existing !!!
      else:
         return self.__dictTestTriggerConfig[sName]
   # eof def Get(self, sName=None):


   def GetConfig(self):
      """Returns the complete configuration dictionary.
      """
      return self.__dictTestTriggerConfig
   # eof def GetConfig(self):

# eof class CTestTriggerConfig():

# **************************************************************************************************************


