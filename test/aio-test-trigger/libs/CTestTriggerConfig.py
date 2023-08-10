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
# CTestTriggerConfig.py
#
# XC-CT/ECA3-Queckenstedt
#
# 10.08.2023
#
# --------------------------------------------------------------------------------------------------------------

"""Python module containing the configuration for the RobotFramework AIO test trigger.
"""

# --------------------------------------------------------------------------------------------------------------

import os, sys, time, platform, json, argparse, re
import uuid

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
   sys.stderr.write(COLBR + f"{sMsg}!\n")

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
      sExecutionLogFile = f"{sReferencePath}/ExecutionLogFile.log"
      # update config
      self.__dictTestTriggerConfig['WHOAMI']           = sWhoAmI
      self.__dictTestTriggerConfig['REFERENCEPATH']    = sReferencePath
      self.__dictTestTriggerConfig['EXECUTIONLOGFILE'] = sExecutionLogFile
      self.__dictTestTriggerConfig['NAME']             = NAME
      self.__dictTestTriggerConfig['VERSION']          = VERSION
      self.__dictTestTriggerConfig['VERSION_DATE']     = VERSION_DATE
      self.__dictTestTriggerConfig['UUID']             = str(uuid.uuid4()) # Test Trigger defines this, not the database application

      bSuccess, sResult = self.__GetCommandLine()
      if bSuccess is not True:
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      sTestTriggerConfigFile = self.__dictTestTriggerConfig['TESTTRIGGERCONFIGFILE']
      if sTestTriggerConfigFile is None:
         # no config file given in command line, therefore using default config file (within subfolder 'config')
         sConfigPath = f"{sReferencePath}/config"
         sTestTriggerConfigFileName = "testtrigger_config.json"
         sTestTriggerConfigFile = f"{sConfigPath}/{sTestTriggerConfigFileName}"
         self.__dictTestTriggerConfig['TESTTRIGGERCONFIGFILE'] = sTestTriggerConfigFile + " (default config file)"

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

      # precompile regular expression needed for parsing the parameters in configuration file
      sPattern_Parameters = r"\${(\w+?)}"  # version 1: only alphanumerical characters (including the underline) are allowed within names
      # sPattern_Parameters = r"\${(.+?)}" # version 2: all characters are allowed within names
      self.__dictTestTriggerConfig['regex_Parameters'] = re.compile(sPattern_Parameters)

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

      dictExternalConfigValues = None
      try:
         dictExternalConfigValues = json.loads("\n".join(listLines))
      except Exception as reason:
         bSuccess = None
         sResult  = str(reason) + f" - while parsing JSON content of '{sTestTriggerConfigFile}'"
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

      if self.__dictTestTriggerConfig['VERSION_CONFIG'] is None:
         bSuccess = None
         sResult  = f"Missing key 'VERSION_CONFIG' in file {sTestTriggerConfigFile}"
         raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

      # print()
      # PrettyPrint(self.__dictTestTriggerConfig, sPrefix="TestTriggerConfig")
      # print()

      self.PrintConfig() # (all values that shall be printed to console, are available now)

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
         #
         if "COMPONENTROOTPATH" not in dictComponent:
            bSuccess = None
            sResult  = f"Missing key 'COMPONENTROOTPATH' in file {sTestTriggerConfigFile}"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         COMPONENTROOTPATH, bSuccess, sResult = self.__ResolveParameters(dictComponent['COMPONENTROOTPATH'])
         if bSuccess is False:
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         COMPONENTROOTPATH = CString.NormalizePath(COMPONENTROOTPATH, sReferencePathAbs=sConfigPath)
         dictComponent['COMPONENTROOTPATH'] = COMPONENTROOTPATH
         if os.path.isdir(COMPONENTROOTPATH) is False:
            bSuccess = None
            sResult  = f"Component root path '{COMPONENTROOTPATH}' does not exist"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         #
         if "TESTFOLDER" not in dictComponent:
            bSuccess = None
            sResult  = f"Missing key 'TESTFOLDER' in file {sTestTriggerConfigFile}, component '{COMPONENTROOTPATH}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         TESTFOLDER = f"{COMPONENTROOTPATH}/{dictComponent['TESTFOLDER']}"
         TESTFOLDER, bSuccess, sResult = self.__ResolveParameters(TESTFOLDER)
         if bSuccess is False:
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         TESTFOLDER = CString.NormalizePath(TESTFOLDER, sReferencePathAbs=sConfigPath)
         dictComponent['TESTFOLDER'] = TESTFOLDER
         if os.path.isdir(TESTFOLDER) is False:
            bSuccess = None
            sResult  = f"Test folder '{TESTFOLDER}' does not exist"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         #
         if "TESTEXECUTOR" not in dictComponent:
            bSuccess = None
            sResult  = f"Missing key 'TESTEXECUTOR' in file {sTestTriggerConfigFile}, component '{COMPONENTROOTPATH}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         TESTEXECUTOR = f"{TESTFOLDER}/{dictComponent['TESTEXECUTOR']}"
         TESTEXECUTOR, bSuccess, sResult = self.__ResolveParameters(TESTEXECUTOR)
         if bSuccess is False:
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         TESTEXECUTOR = CString.NormalizePath(TESTEXECUTOR, sReferencePathAbs=sConfigPath)
         dictComponent['TESTEXECUTOR'] = TESTEXECUTOR
         if os.path.isfile(TESTEXECUTOR) is False:
            bSuccess = None
            sResult  = f"Test Executor '{TESTEXECUTOR}' does not exist"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         #
         if "TESTTYPE" not in dictComponent:
            bSuccess = None
            sResult  = f"Missing key 'TESTTYPE' in file {sTestTriggerConfigFile}, component '{COMPONENTROOTPATH}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         TESTTYPE = dictComponent['TESTTYPE']
         if TESTTYPE not in tupleSupportedTestTypes:
            bSuccess = None
            sResult  = f"TESTTYPE '{TESTTYPE}' not supported; file {sTestTriggerConfigFile}, component '{COMPONENTROOTPATH}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         #
         if "LOGFILE" not in dictComponent:
            bSuccess = None
            sResult  = f"Missing key 'LOGFILE' in file {sTestTriggerConfigFile}, component '{COMPONENTROOTPATH}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         LOGFILE, bSuccess, sResult = self.__ResolveParameters(dictComponent['LOGFILE'])
         if bSuccess is False:
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         LOGFILE = CString.NormalizePath(LOGFILE, sReferencePathAbs=sConfigPath)
         dictComponent['LOGFILE'] = LOGFILE
         # LOGFILE will be created, therefore existence is not checked here

         # optional
         LOCALCOMMANDLINE = None # caution: same name like in section "TESTTYPES"
         if "LOCALCOMMANDLINE" in dictComponent:
            LOCALCOMMANDLINE = dictComponent['LOCALCOMMANDLINE']
            # In this section 'LOCALCOMMANDLINE' is a list. Every element of the list is a single command line parameter.
            # These parameters can be required or optional. Now we convert the list to a command line string containing
            # only the parameters that are given in command line of the Test Trigger (--params).
            # With this command line string (together with the global command line) the Test Executor is called.
            # In case of a parameter used in the command line list LOCALCOMMANDLINE, is not defined in the command line
            # of the test Trigger, it is assumed that this parameter is an optional one - and therefore the missing parameter
            # is not handled as error (like in other parts of the Test Trigger configuration (by __ResolveParameters()).
            # It is under the reponsibility of the one who calls the Test Trigger, to provide all required parameters, and it is
            # under the responsibility of the Test Executor to react on missing parameters properly.
            # But in the following code no valuation of command line parameters will happen.
            LOCALCOMMANDLINE, bSuccess, sResult = self.__ResolveCommandLine(LOCALCOMMANDLINE)
            if bSuccess is not True:
               raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         # eof if "LOCALCOMMANDLINE" in dictComponent:
         dictComponent['LOCALCOMMANDLINE'] = LOCALCOMMANDLINE

         # optional
         if "EXECUTION" not in dictComponent:
            dictComponent['EXECUTION'] = None

         # short summary
         dictTestExecution = {}
         dictTestExecution['TESTFOLDER']       = dictComponent['TESTFOLDER']
         dictTestExecution['TESTTYPE']         = dictComponent['TESTTYPE']
         dictTestExecution['TESTEXECUTOR']     = dictComponent['TESTEXECUTOR']
         dictTestExecution['LOCALCOMMANDLINE'] = dictComponent['LOCALCOMMANDLINE']
         dictTestExecution['LOGFILE']          = dictComponent['LOGFILE']
         dictTestExecution['EXECUTION']        = dictComponent['EXECUTION']
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
            sResult  = f"TESTTYPE '{TESTTYPE}' not supported; file {sTestTriggerConfigFile}, section 'TESTTYPES'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         dictTestType = self.__dictTestTriggerConfig['TESTTYPES'][TESTTYPE]
         if "DATABASEEXECUTOR" not in dictTestType:
            bSuccess = None
            sResult  = f"Missing key 'DATABASEEXECUTOR' in file {sTestTriggerConfigFile}, section 'TESTTYPES', test type '{TESTTYPE}'"
            raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))

         # optional
         LOCALCOMMANDLINE = None # caution: same name like in section "COMPONENTS"
         if "LOCALCOMMANDLINE" in dictTestType:
            LOCALCOMMANDLINE = dictTestType['LOCALCOMMANDLINE']
            # In this section 'LOCALCOMMANDLINE' is a list. Every element of the list is a single command line parameter.
            # These parameters can be required or optional. Now we convert the list to a command line string containing
            # only the parameters that are given in command line of the Test Trigger (--params).
            # With this command line string (together with the global command line) the Database Executor is called.
            # In case of a parameter used in the command line list LOCALCOMMANDLINE, is not defined in the command line
            # of the test Trigger, it is assumed that this parameter is an optional one - and therefore the missing parameter
            # is not handled as error (like in other parts of the Test Trigger configuration (by __ResolveParameters()).
            # It is under the reponsibility of the one who calls the Test Trigger, to provide all required parameters, and it is
            # under the responsibility of the Database Executor to react on missing parameters properly.
            # But in the following code no valuation of command line parameters will happen.
            LOCALCOMMANDLINE, bSuccess, sResult = self.__ResolveCommandLine(LOCALCOMMANDLINE)
            if bSuccess is False:
               raise Exception(CString.FormatResult(sMethod, bSuccess, sResult))
         # eof if "LOCALCOMMANDLINE" in dictTestType:
         self.__dictTestTriggerConfig['TESTTYPES'][TESTTYPE]['LOCALCOMMANDLINE'] = LOCALCOMMANDLINE

      # eof for dictComponent in listofdictComponents:

      # final debug
      # PrettyPrint(self.__dictTestTriggerConfig, sPrefix="final TestTriggerConfig")

      # overview about planned test executions
      self.PrintConfiguredTestExecutions()

   # eof def __init__(self, sWhoAmI=None):


   def __del__(self):
      del self.__dictTestTriggerConfig

   # --------------------------------------------------------------------------------------------------------------

   def __ResolveParameters(self, sString=""):
      sMethod  = "CTestTriggerConfig.__ResolveParameters"
      bSuccess = None
      sResult  = "unknown"
      regex_Parameters = self.__dictTestTriggerConfig['regex_Parameters']
      dictParams = self.__dictTestTriggerConfig['PARAMS']
      if dictParams is not None:
         # replace all possible parameters
         for sName, sValue in dictParams.items():
            # TODO: not nice exception here: we assume that 'config' is a path that must be normalized; find better solution
            if sName == "config":
               sValue = CString.NormalizePath(sValue, sReferencePathAbs=self.__dictTestTriggerConfig['REFERENCEPATH'])
            sPlaceholder = "${" + sName + "}"
            sString = sString.replace(sPlaceholder, sValue)

      # check if there are undefined parameters left
      bSuccess = False
      sResult  = "UNKNOWN"
      listUndefinedParameters = regex_Parameters.findall(sString)
      if len(listUndefinedParameters) > 0:
         bSuccess = False
         sResult  = "The following parameters are not defined : [" + ",".join(listUndefinedParameters) + "], (in '" + sString + "'). Please add them to the test trigger command line."
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
      else:
         bSuccess = True
         sResult  = "Done"
         # check for further issues caused by failed regular expressions or incomplete parameter syntax
         if ( ('$' in sString) or ('{' in sString) or ('}' in sString) ):
            bSuccess = False
            sResult  = f"After resolving the parameters still issues found in configuration (probably caused by a not matching regular expression or incomplete parameter syntax. Line:'{sString}'"
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)

      return sString, bSuccess, sResult

   # --------------------------------------------------------------------------------------------------------------

   def __ResolveCommandLine(self, LOCALCOMMANDLINE=[]):
      # similar to __ResolveParameters but designed for command lines with possible optional parameters;
      # therefore no error handling in case of missing parameters

      sMethod = "CTestTriggerConfig.__ResolveCommandLine"

      if not isinstance(LOCALCOMMANDLINE, (tuple, list)):
         bSuccess = None
         sResult  = "Invalid type of LOCALCOMMANDLINE. Expected 'tuple' or 'list'."
         return LOCALCOMMANDLINE, bSuccess, CString.FormatResult(sMethod, bSuccess, sResult)

      sLocalCommandLine = None
      bSuccess = None
      sResult  = "unknown"

      listLocalCommandLineParts = []

      regex_Parameters = self.__dictTestTriggerConfig['regex_Parameters']
      dictParams = self.__dictTestTriggerConfig['PARAMS']
      if dictParams is not None:
         # resolve all possible parameters:
         # 1. parameter in LOCALCOMMANDLINE may contain ${...} or not (it's an option only)
         # 2. Test Trigger command line may contain value for ${...} or not (if not: parameter is not required)
         for sParameter in LOCALCOMMANDLINE:
            # anything ${...} to resolve ?
            listParameters = regex_Parameters.findall(sParameter)
            if len(listParameters) == 0:
               # nothing to resolve; take over content unchanged
               listLocalCommandLineParts.append(sParameter)
            else:
               # found ${...}, but resolving depends on corresponding content of --params of test Trigger command line (because LOCALCOMMANDLINE are handled as optional)
               bSomethingResolved = False
               for sName, sValue in dictParams.items():
                  # TODO: not nice exception here: we assume that 'config' is a path that must be normalized; find better solution
                  if sName == "config":
                     sValue = CString.NormalizePath(sValue, sReferencePathAbs=self.__dictTestTriggerConfig['REFERENCEPATH'])
                  sPlaceholder = "${" + sName + "}"
                  if sPlaceholder in sParameter:
                     sValue = "\"" + sValue + "\"" # assuming that all command line parameters can contain blanks
                     sParameter = sParameter.replace(sPlaceholder, sValue)
                     bSomethingResolved = True
               # eof for sName, sValue in dictParams.items():
               if bSomethingResolved is True:
                  listLocalCommandLineParts.append(sParameter)
            # eof else - if len(listParameters) == 0:
         # eof for sParameter in LOCALCOMMANDLINE:
      # eof if dictParams is not None:
      if len(listLocalCommandLineParts) > 0:
         sLocalCommandLine = " ".join(listLocalCommandLineParts)
      else:
         sLocalCommandLine = " ".join(LOCALCOMMANDLINE)

      bSuccess = True
      sResult  = "Done"

      return sLocalCommandLine, bSuccess, sResult

   # --------------------------------------------------------------------------------------------------------------

   def __GetCommandLine(self):

      sMethod = "CTestTriggerConfig.__GetCommandLine"

      bSuccess = None
      sResult  = "UNKNOWN"

      oCmdLineParser = argparse.ArgumentParser()
      oCmdLineParser.add_argument('--robotcommandline', type=str, help='Command line for RobotFramework AIO (optional).')
      oCmdLineParser.add_argument('--pytestcommandline', type=str, help='Command line for Python pytest module (optional).')
      oCmdLineParser.add_argument('--configfile', type=str, help='Path and name of Test Trigger configuration file (optional).')
      oCmdLineParser.add_argument('--params', type=str, help='List of values for parameters used in Test Trigger configuration file (optional).')
      oCmdLineParser.add_argument('--results2db', action='store_true', help='Activates the database access and test results will be written to database (boolean switch).')

      try:
         oCmdLineArgs = oCmdLineParser.parse_args()
      except SystemExit as reason:
         bSuccess = None
         sResult  = "Error in command line: " + str(reason) + "\n\n" + oCmdLineParser.format_help()
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      sRobotCommandLine = None
      if oCmdLineArgs.robotcommandline is not None:
         sRobotCommandLine = oCmdLineArgs.robotcommandline
      self.__dictTestTriggerConfig['ROBOTCOMMANDLINE'] = sRobotCommandLine

      sPytestCommandLine = None
      if oCmdLineArgs.pytestcommandline is not None:
         sPytestCommandLine = oCmdLineArgs.pytestcommandline
      self.__dictTestTriggerConfig['PYTESTCOMMANDLINE'] = sPytestCommandLine

      sConfigFile = None
      if oCmdLineArgs.configfile is not None:
         sConfigFile = oCmdLineArgs.configfile
         sConfigFile = CString.NormalizePath(sConfigFile, sReferencePathAbs=self.__dictTestTriggerConfig['REFERENCEPATH'])
         if os.path.isfile(sConfigFile) is False:
            bSuccess = False
            sResult  = f"Configuration file does not exist: '{sConfigFile}'"
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
            return bSuccess, sResult
      self.__dictTestTriggerConfig['TESTTRIGGERCONFIGFILE'] = sConfigFile
      self.__dictTestTriggerConfig['VERSION_CONFIG']        = None # will be overwritten when content is read, but we preserve this position in dict to have both informations printed nearby in console

      dictParams = None
      if oCmdLineArgs.params is not None:
         dictParams = {}
         sParams = oCmdLineArgs.params
         sParams = sParams.strip()
         if sParams == "":
            bSuccess = False
            sResult  = f"Empty parameter list (--params)"
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
            return bSuccess, sResult

         listAssignments = sParams.split(';')
         for sAssignment in listAssignments:
            sAssignment = sAssignment.strip()
            if sAssignment == "":
               bSuccess = False
               sResult  = f"Empty parameter assignment found in parameter list '{sParams}'"
               sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
               return bSuccess, sResult

            listParts = sAssignment.split('=')
            if len(listParts) != 2:
               bSuccess = False
               sResult  = f"Invalid parameter assignment: '{sAssignment}' found in parameter list '{sParams}'"
               sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
               return bSuccess, sResult

            sName  = listParts[0].strip()
            sValue = listParts[1].strip()
            if sName == "":
               bSuccess = False
               sResult  = f"Missing parameter name in parameter assignment '{sAssignment}' of parameter list '{sParams}'"
               sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
               return bSuccess, sResult

            if sValue == "":
               bSuccess = False
               sResult  = f"Missing parameter value in parameter assignment '{sAssignment}' of parameter list '{sParams}'"
               sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
               return bSuccess, sResult

            dictParams[sName] = sValue

         # eof for sAssignment in listAssignments:

         if len(dictParams) == 0:
            bSuccess = False
            sResult  = f"Parsing of parameter list '{sParams}' failed"
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
            return bSuccess, sResult

      # eof if oCmdLineArgs.params is not None:

      self.__dictTestTriggerConfig['PARAMS'] = dictParams

      bResults2DB = False
      # database access only in case of the user explicitely order this
      if oCmdLineArgs.results2db is not None:
         bResults2DB = oCmdLineArgs.results2db
      self.__dictTestTriggerConfig['RESULTS2DB'] = bResults2DB

      bSuccess = True
      sResult  = "Done"
      return bSuccess, sResult

   # eof def __GetCommandLine(self):

   # --------------------------------------------------------------------------------------------------------------

   def PrintConfig(self):
      # -- print assorted configuration values to console
      tupleSupportedValues = ('WHOAMI',
                              'REFERENCEPATH',
                              'EXECUTIONLOGFILE',
                              'NAME',
                              'VERSION',
                              'VERSION_DATE',
                              'UUID',
                              'ROBOTCOMMANDLINE',
                              'PYTESTCOMMANDLINE',
                              'TESTTRIGGERCONFIGFILE',
                              'VERSION_CONFIG',
                              'RESULTS2DB',
                              'CONFIGPATH',
                              'PYTHON',
                              'PYTHONVERSION',
                              'PLATFORMSYSTEM',
                              'OSNAME',
                              'TMPPATH')
      nJust = 25
      print()
      for sValue in tupleSupportedValues:
         print(sValue.rjust(nJust, ' ') + " : " + str(self.__dictTestTriggerConfig[sValue]))
      print()
   # eof def PrintConfig(self):

   # --------------------------------------------------------------------------------------------------------------

   def PrintConfiguredTestExecutions(self):
      # -- print configured test executions to console
      nJust = 25
      print()
      print("Configured tests:")
      print()
      for dictTestExecution in self.__listofdictTestExecutions:
         print("TESTFOLDER".rjust(nJust, ' ')       + " : " + str(dictTestExecution['TESTFOLDER']))
         print("TESTTYPE".rjust(nJust, ' ')         + " : " + str(dictTestExecution['TESTTYPE']))
         print("TESTEXECUTOR".rjust(nJust, ' ')     + " : " + str(dictTestExecution['TESTEXECUTOR']))
         print("LOCALCOMMANDLINE".rjust(nJust, ' ') + " : " + str(dictTestExecution['LOCALCOMMANDLINE']))
         print("LOGFILE".rjust(nJust, ' ')          + " : " + str(dictTestExecution['LOGFILE']))
         EXECUTION = dictTestExecution['EXECUTION']
         if EXECUTION is not None:
            print("EXECUTION".rjust(nJust, ' ') + " : " + str(EXECUTION))
         print()
   # eof def PrintConfig(self):

   # --------------------------------------------------------------------------------------------------------------

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

   # --------------------------------------------------------------------------------------------------------------

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

   # --------------------------------------------------------------------------------------------------------------

   def GetConfig(self):
      """Returns the complete configuration dictionary.
      """
      return self.__dictTestTriggerConfig
   # eof def GetConfig(self):

# eof class CTestTriggerConfig():

# **************************************************************************************************************


