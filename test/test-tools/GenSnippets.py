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
# GenSnippets.py
#
# XC-HWP/ESW3-Queckenstedt
#
# **************************************************************************************************************
#
VERSION      = "0.1.0"
VERSION_DATE = "12.02.2024"
#
# **************************************************************************************************************

# History

# **************************************************************************************************************
# TM***
#
# -- TOC
#[DEFCONFIG]
#[DEFCOUNTER]
#[DEFCLISTVALUES]
#[DEFLOGGER]
#[DEFEXECUTOR]
#[HTMLPATTERN]
#[CSNIPPETS]
#[INITCONFIG]
#[INITLOGGER]
#[INITCOUNTER]
#[INITJPP]
#[INITEXECUTOR]
#[STARTOFEXECUTION]
#[ENDOFEXECUTION]
#
# TM***
# **************************************************************************************************************


# -- import standard Python modules
import os, sys, shlex, subprocess, ctypes, time, platform, json, pprint, itertools
import colorama as col

# -- import own Python modules
from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.Folder.CFolder import CFolder
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Utils.CUtils import *

# -- import module under test
from JsonPreprocessor.CJsonPreprocessor import CJsonPreprocessor

col.init(autoreset=True)

COLBR = col.Style.BRIGHT + col.Fore.RED
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLBG = col.Style.BRIGHT + col.Fore.GREEN
COLBB = col.Style.BRIGHT + col.Fore.BLUE

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

def printfailure(sMsg, prefix=None):
   if prefix is None:
      sMsg = COLBR + f"{sMsg}!\n\n"
   else:
      sMsg = COLBR + f"{prefix}:\n{sMsg}!\n\n"
   sys.stderr.write(sMsg)


# --------------------------------------------------------------------------------------------------------------
#[DEFCONFIG]
# --------------------------------------------------------------------------------------------------------------
#TM***

class CConfig():

   def __init__(self, sCalledBy=None):

      sMethod = "CConfig.__init__"

      # -- configuration init
      self.__dictConfig = {}

      if sCalledBy is None:
         raise Exception(CString.FormatResult(sMethod, None, "sCalledBy is None"))

      THISAPP                             = CString.NormalizePath(sCalledBy)
      self.__dictConfig['THISAPP']        = THISAPP
      self.__dictConfig['THISAPPNAME']    = os.path.basename(THISAPP)
      REFERENCEPATH                       = os.path.dirname(THISAPP) # position of main() app is reference for all relative paths
      self.__dictConfig['REFERENCEPATH']  = REFERENCEPATH
      self.__dictConfig['TMPFILESPATH']   = f"{REFERENCEPATH}/tmp_files"
      self.__dictConfig['OUTPUTPATH']     = f"{REFERENCEPATH}" # /output
      self.__dictConfig['LOGFILE']        = f"{self.__dictConfig['OUTPUTPATH']}/GenSnippetLog.log"
      self.__dictConfig['REPORTFILE']     = f"{self.__dictConfig['OUTPUTPATH']}/GenSnippetReport.html"
      self.__dictConfig['JPPJSONFILE']    = f"{self.__dictConfig['TMPFILESPATH']}/JPPSnippetFile.jsonp"
      OSNAME                              = os.name
      self.__dictConfig['OSNAME']         = OSNAME
      self.__dictConfig['PLATFORMSYSTEM'] = platform.system()
      PYTHON                              = CString.NormalizePath(sys.executable)
      self.__dictConfig['PYTHON']         = PYTHON
      self.__dictConfig['PYTHONPATH']     = os.path.dirname(PYTHON)
      self.__dictConfig['PYTHONVERSION']  = sys.version
      self.__dictConfig['NOW']            = time.strftime('%d.%m.%Y - %H:%M:%S')

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

# eof class CConfig():


# --------------------------------------------------------------------------------------------------------------
#[DEFCOUNTER]
# --------------------------------------------------------------------------------------------------------------
#TM***

class CCounter():

   def __init__(self, nCntSection=0,nCntSubSection=0,nCntGlobal=0):
      self.__nCntSection    = nCntSection
      self.__nCntSubSection = nCntSubSection
      self.__nCntGlobal     = nCntGlobal

   def IncSection(self):
      self.__nCntSection = self.__nCntSection + 1
      self.__nCntSubSection = 0 # => 'IncSection' requires a separate 'IncSubSection'; advantage: 'IncSubSection' can run separately in loop
      return f"[ {self.__nCntSection}.{self.__nCntSubSection} ]"

   def IncSubSection(self):
      self.__nCntSubSection = self.__nCntSubSection + 1
      self.__nCntGlobal = self.__nCntGlobal + 1
      return f"( {self.__nCntGlobal} ) - [ {self.__nCntSection}.{self.__nCntSubSection} ]"

   def GetCntString(self):
      return f"( {self.__nCntGlobal} ) - [ {self.__nCntSection}.{self.__nCntSubSection} ]"

   def GetCntSection(self):
      return self.__nCntSection

   def GetCntClobal(self):
      return self.__nCntGlobal

# eof class CCounter():


# --------------------------------------------------------------------------------------------------------------
#[DEFCLISTVALUES]
# --------------------------------------------------------------------------------------------------------------
#TM***

class CListElements():

   def __init__(self, listElements=[]):
      self.listElements  = listElements
      self.nNrOfElements = len(self.listElements)
      self.nCurrentIndex = 0

   def GetElement(self):
      oElement = self.listElements[self.nCurrentIndex]
      self.nCurrentIndex = self.nCurrentIndex + 1
      if self.nCurrentIndex >= self.nNrOfElements:
         self.nCurrentIndex = 0
      return oElement

# eof class CListElements():


# --------------------------------------------------------------------------------------------------------------
#[DEFLOGGER]
# --------------------------------------------------------------------------------------------------------------
#TM***

class CLogger():

   def __init__(self, oConfig=None):

      sMethod = "CLogger.__init__"

      self.__oLogfile    = None
      self.__oReportfile = None
      self.__oConfig     = None

      if oConfig is None:
         raise Exception(CString.FormatResult(sMethod, None, "oConfig is None"))
      self.__oConfig = oConfig

      LOGFILE    = self.__oConfig.Get('LOGFILE')
      REPORTFILE = self.__oConfig.Get('REPORTFILE')

      self.__oLogfile    = CFile(LOGFILE)
      self.__oReportfile = CFile(REPORTFILE)

   def __del__(self):
      del self.__oConfig
      del self.__oLogfile
      del self.__oReportfile

   def WriteLog(self, content=None):
      if type(content) == list:
         for element in content:
            self.__oLogfile.Write(element)
      else:
         self.__oLogfile.Write(f"{content}")

   def WriteReport(self, content=None):
      if type(content) == list:
         for element in content:
            self.__oReportfile.Write(element)
      else:
         self.__oReportfile.Write(f"{content}")

# eof class CLogger(oConfig):


# --------------------------------------------------------------------------------------------------------------
#[DEFEXECUTOR]
# --------------------------------------------------------------------------------------------------------------
#TM***

class CExecutor():

   def __init__(self, oConfig=None, oCounter=None, oLogger=None, oJsonPreprocessor=None):

      sMethod = "CExecutor.__init__"

      self.__oConfig           = None
      self.__oCounter          = None
      self.__oLogger           = None
      self.__oJsonPreprocessor = None
      self.__oSnippets         = None
      self.__oHTMLPattern      = None

      if oConfig is None:
         raise Exception(CString.FormatResult(sMethod, None, "oConfig is None"))
      self.__oConfig = oConfig

      if oCounter is None:
         raise Exception(CString.FormatResult(sMethod, None, "oCounter is None"))
      self.__oCounter = oCounter

      if oLogger is None:
         raise Exception(CString.FormatResult(sMethod, None, "oLogger is None"))
      self.__oLogger = oLogger

      # if defined outside CExecutor(), every JPP snippet execution works with the same oJsonPreprocessor object;
      # otherwise every JPP snippet execution works with his own oJsonPreprocessor object
      self.__oJsonPreprocessor = oJsonPreprocessor

      # access to code snippets (required for HTML report file)
      self.__oSnippets = CSnippets()

      # access to HTML pattern (required for HTML report file)
      self.__oHTMLPattern = CHTMLPattern()

      # create the tmp files folder
      TMPFILESPATH  = oConfig.Get('TMPFILESPATH')
      oTMPFILESPATH = CFolder(TMPFILESPATH)
      oTMPFILESPATH.Create(bOverwrite=False, bRecursive=True)
      del oTMPFILESPATH

   #eof def __init__(self, oConfig=None, oCounter=None, oJsonPreprocessor=None):


   def __del__(self):
      del self.__oConfig
      del self.__oCounter
      del self.__oLogger
      del self.__oJsonPreprocessor
      del self.__oSnippets
      del self.__oHTMLPattern

   # --------------------------------------------------------------------------------------------------------------

   def Execute(self, sHeadline=None, listCodeSnippets=None, sType="JPP"):

      sMethod = "Execute"

      bSuccess = None
      sResult  = "UNKNOWN"

      if sHeadline is None:
         bSuccess = None
         sResult  = "sHeadline is None"
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      if listCodeSnippets is None:
         bSuccess = None
         sResult  = "listCodeSnippets is None"
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      if len(listCodeSnippets) == 0:
         bSuccess = None
         sResult  = "List of code snippets is empty"
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      tupleSupportedTypes = ("JPP") # , "TSM"   >> TODO: enumeration type
      if sType not in tupleSupportedTypes:
         bSuccess = None
         sResult  = f"Unexpected application type '{sType}'. Expected is one of '{tupleSupportedTypes}'"
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
         return bSuccess, sResult

      if sType == "JPP":
         bSuccess, sResult = self.__ExecuteJPPSnippets(sHeadline, listCodeSnippets)
         if bSuccess is not True:
            sResult  = CString.FormatResult(sMethod, bSuccess, sResult)
      else:
         bSuccess = False
         sResult  = f"Types other than 'JPP' are currently not supported"
         sResult  = CString.FormatResult(sMethod, bSuccess, sResult)

      return bSuccess, sResult

   # eof def Execute(self, listCodeSnippets=None, sType="JPP"):

   # --------------------------------------------------------------------------------------------------------------

   def __ExecuteJPPSnippets(self, sHeadline="UNKNOWN", listCodeSnippets=[]):

      sMethod = "__ExecuteJPPSnippets"

      bSuccess     = None
      sResult      = "UNKNOWN"

      # increment section counter and write headline to log file and to report file
      self.__oCounter.IncSection()
      nSectionNumber = self.__oCounter.GetCntSection()
      print(COLBY + f"{nSectionNumber}. {sHeadline}\n")
      self.__oLogger.WriteLog(120*"-")
      self.__oLogger.WriteLog(f"{nSectionNumber}. {sHeadline}")
      self.__oLogger.WriteReport(self.__oHTMLPattern.GetHTMLHeadline1(f"{nSectionNumber}. {sHeadline}"))
      self.__oLogger.WriteLog(120*"-" + "\n")
      self.__oLogger.WriteReport(self.__oHTMLPattern.GetHTMLHLine())

      for sCodeSnippet in listCodeSnippets:
         # for every code snippet increment subsection counter and write current counter string to log file and to report file
         self.__oCounter.IncSubSection()
         print(COLBY + self.__oCounter.GetCntString() + "\n")
         self.__oLogger.WriteLog(self.__oCounter.GetCntString() + "\n")
         self.__oLogger.WriteReport(self.__oHTMLPattern.GetHTMLCounter(self.__oCounter.GetCntString()))
         # write code snippet to log file and to report file
         print(COLBG + sCodeSnippet)
         self.__oLogger.WriteLog(sCodeSnippet)
         self.__oLogger.WriteReport(self.__oHTMLPattern.GetHTMLSnippetCode(self.__oHTMLPattern.Txt2HTML(sCodeSnippet)))
         # write code snippet to temporary JSON file for execution
         NOW = self.__oConfig.Get('NOW')
         JPPJSONFILE = self.__oConfig.Get('JPPJSONFILE')
         oJPPJSONFILE = CFile(JPPJSONFILE)
         oJPPJSONFILE.Write(f"// created at {NOW}")
         oJPPJSONFILE.Write(sCodeSnippet)
         del oJPPJSONFILE
         # execute temporary JSON file
         dictReturned, sException, bSuccess, sResult = self.__ExecuteJPPFile(JPPJSONFILE)
         # PrettyPrint(bSuccess, sPrefix="(bSuccess)")
         # PrettyPrint(sResult, sPrefix="(sResult)")
         # PrettyPrint(dictReturned, sPrefix="(dictReturned)")
         # PrettyPrint(sException, sPrefix="(sException)")

         # if available write returned value to log file and to report file
         if dictReturned is not None:
            listValuesReturned = PrettyPrint(dictReturned, bToConsole=True) #, sPrefix="(dictReturned)")
            print()
            self.__oLogger.WriteLog(listValuesReturned)
            self.__oLogger.WriteLog("")
            self.__oLogger.WriteReport(self.__oHTMLPattern.GetHTMLValuesReturned(self.__oHTMLPattern.Txt2HTML("\n".join(listValuesReturned))))

         # if available write exception to log file and to report file
         if sException is not None:
            printfailure(sException)
            self.__oLogger.WriteLog(sException)
            self.__oLogger.WriteLog("")
            self.__oLogger.WriteReport(self.__oHTMLPattern.GetHTMLException(sException))

         self.__oLogger.WriteLog(120*"-" + "\n")
         self.__oLogger.WriteReport(self.__oHTMLPattern.GetHTMLHLine())

      # eof for sCodeSnippet in listCodeSnippets:

      bSuccess = True
      sResult  = "done"

      return bSuccess, sResult

   # --------------------------------------------------------------------------------------------------------------

   def __ExecuteJPPFile(self, sJSONFile=None):

      sMethod = "__ExecuteJPPFile"

      bSuccess     = None
      sResult      = "UNKNOWN"
      dictReturned = None
      sException   = None

      if sJSONFile is None:
         sResult = CString.FormatResult(sMethod, None, "sJSONFile is None")
         return dictReturned, sException, bSuccess, sResult

      if not os.path.isfile(sJSONFile):
         sResult = f"Input JSON file does not exist: '{sJSONFile}'"
         sResult = CString.FormatResult(sMethod, None, sResult)
         return dictReturned, sException, bSuccess, sResult

      # print(f"* '{sJSONFile}'")

      # use either own or common JsonPreprocessor object
      oJsonPreprocessor = None
      if self.__oJsonPreprocessor is None:
         oJsonPreprocessor = CJsonPreprocessor()
      else:
         oJsonPreprocessor = self.__oJsonPreprocessor

      # execute JsonPreprocessor
      dictReturned = None
      sException   = None
      try:
         dictReturned = oJsonPreprocessor.jsonLoad(sJSONFile)
      except Exception as reason:
         sException = f"'{reason}'"

      del oJsonPreprocessor

      bSuccess = True
      sResult  = "done"
      return dictReturned, sException, bSuccess, sResult

   # eof def __ExecuteJPPFile(self, sJSONFile=None):

   # --------------------------------------------------------------------------------------------------------------

# eof class CExecutor():


# --------------------------------------------------------------------------------------------------------------
#[HTMLPATTERN]
# --------------------------------------------------------------------------------------------------------------
#TM***

class CHTMLPattern():

   sHTMLHeader = """
<html>
<head>
   <meta name="Code Snippets" content="Release">
   <title>Code Snippets</title>
</head>
<body bgcolor="#FFFFFF" text="#000000" link="#0000FF" vlink="#0000FF" alink="#0000FF">

   <hr width="100%" align="center" color="#d0d0d0"/>
"""

   sHTMLFooter = """
   <div align="center"><font size="2" color="#27408B">###NOW###</font></div>
</body>
</html>
"""

   sHTMLHLine = """
<hr width="100%" align="center" color="#d0d0d0"/>
"""

   sHTMLHeadline1 = """
<h1>###HTMLHEADLINE1###</h1>
"""

   sHTMLHeadline2 = """
<h2>###HTMLHEADLINE2###</h2>
"""

   sHTMLText = """
<p><font face="Arial" color="black" size="-1">###HTMLTEXT###</font></p>
"""

   sHTMLCounter = """
<p><font face="Arial" color="black" size="-1">###HTMLCOUNTER###</font></p>
"""

   sHTMLSnippetCode = """
<p><code><font font-family="courier new" color="mediumblue" size="">###HTMLSNIPPETCODE###</font></code></p>
"""

   sHTMLValuesReturned = """
<p><code><font font-family="courier new" color="green" size="">###HTMLVALUESRETURNED###</font></code></p>
"""

   sHTMLException = """
<p><font face="Arial" color="red" size="-1">###HTMLEXCEPTION###</font></p>
"""


   def Txt2HTML(self, sText=None):
      listHTML = sText.splitlines()
      listLinesHTMLindent = []
      for sLine in listHTML:
         sLine = sLine.rstrip() # remove unnecessary trailing blanks
         sLine = sLine.replace(" ", "&nbsp;") # replace spaces by non breaking HTML spaces
         listLinesHTMLindent.append(sLine)
      # eof for sLine in listHTML:
      print()
      sHTML = "</br>\n".join(listLinesHTMLindent)
      return sHTML

   def GetHTMLHeader(self):
      return CHTMLPattern.sHTMLHeader

   def GetHTMLFooter(self, NOW=None):
      sHTML = CHTMLPattern.sHTMLFooter.replace("###NOW###", f"{NOW}")
      return sHTML

   def GetHTMLHLine(self):
      return CHTMLPattern.sHTMLHLine

   def GetHTMLHeadline1(self, sHTML=None):
      sHTML = CHTMLPattern.sHTMLHeadline1.replace("###HTMLHEADLINE1###", f"{sHTML}")
      return sHTML

   def GetHTMLHeadline2(self, sHTML=None):
      sHTML = CHTMLPattern.sHTMLHeadline2.replace("###HTMLHEADLINE2###", f"{sHTML}")
      return sHTML

   def GetHTMLText(self, sHTML=None):
      sHTML = CHTMLPattern.sHTMLText.replace("###HTMLTEXT###", f"{sHTML}")
      return sHTML

   def GetHTMLCounter(self, sHTML=None):
      sHTML = CHTMLPattern.sHTMLCounter.replace("###HTMLCOUNTER###", f"{sHTML}")
      return sHTML

   def GetHTMLSnippetCode(self, sHTML=None):
      sHTML = CHTMLPattern.sHTMLSnippetCode.replace("###HTMLSNIPPETCODE###", f"{sHTML}")
      return sHTML

   def GetHTMLValuesReturned(self, sHTML=None):
      sHTML = CHTMLPattern.sHTMLValuesReturned.replace("###HTMLVALUESRETURNED###", f"{sHTML}")
      return sHTML

   def GetHTMLException(self, sHTML=None):
      sHTML = CHTMLPattern.sHTMLException.replace("###HTMLEXCEPTION###", f"{sHTML}")
      return sHTML

# eof class CHTMLPattern():


# --------------------------------------------------------------------------------------------------------------
#[CSNIPPETS]
# --------------------------------------------------------------------------------------------------------------
#TM***

class CSnippets():

   def GetSeveralParticularSnippets(self):
      """Several particular snippets covering different topics
      """

      sHeadline = "Several particular snippets covering different topics"

      listCodeSnippets = []

      listCodeSnippets.append("""{
   ${testdict1.subKey1.subKey2.subKey3} : {"subKey4" : 1},
   ${testdict2.subKey1.subKey2} : {"subKey3" : {"subKey4" : 2}},
   ${testdict3.subKey1} : {"subKey2" : {"subKey3" : {"subKey4" : 3}}},
   ${testdict4} : {"subKey1" : {"subKey2" : {"subKey3" : {"subKey4" : 4}}}}
}
""")

      listCodeSnippets.append("""{
   ${testdict1.subKey1.subKey2.subKey3} : {"subKey4" : 1}
}
""")

      listCodeSnippets.append("""{
   ${testdict5.subKey1.subKey2.subKey3} : {"subKey4" : 1},
   ${testdict5.subKey1} : 2
}
""")

      listCodeSnippets.append("""{
   "par${1}am2" : "123"
}
""")

      listCodeSnippets.append("""{
   "par${...}am2" : "123"
}
""")

      listCodeSnippets.append("""{
   "testlist" : [1,2,3],
   "value"    : ${testlist}[]
}
""")

      listCodeSnippets.append("""{
   "testlist" : [1,2,3],
   "value"    : ${testlist}[${}]
}
""")

      listCodeSnippets.append("""{
   "param1" : {},
   ${param1}['subkey']['subkey']['subkey'] : "subkey value",
   "param1" : {},
   ${param1}['subkey2']['subkey2']['subkey2'] : "subkey value 2"
}
""")

      listCodeSnippets.append("""{
   "key1"     : "keyA",
   "testdict" : {"keyA" : "A", "keyB" : "B"},
   "param1"   : ${testdict}['keyA'],
   "param2"   : ${testdict}[${key1}],
   "param3"   : ${testdict}['${key1}'],
   ${testdict}[${key1}]   : "C",
   ${testdict}['${key1}'] : "D"
}
""")

      listCodeSnippets.append("""{
   "intparam"    : 0,
   "stringparam" : "A",
   "listparam"   : ["A", "B"],
   "dictparam"   : {"0" : 0, "A" : 1, "B" : 2},
   //
   "val01" : ${listparam}[${intparam}],
   "val02" : ${listparam}[1],
   "val03" : ${dictparam}['${intparam}'],
   "val04" : ${dictparam}[${stringparam}],
   "val05" : ${dictparam}['${stringparam}'],
   "val06" : ${dictparam}['A'],
   //
   "val07" : "${listparam}[${intparam}]",
   "val08" : "${listparam}[1]",
   "val09" : "${dictparam}['${intparam}']",
   "val10" : "${dictparam}[${stringparam}]",
   "val11" : "${dictparam}['${stringparam}']",
   "val12" : "${dictparam}['A']"
}
""")

      listCodeSnippets.append("""{
   ${testdict9.subKey1.subKey2.subKey3} : "ABC",
   "param1" : "subKey1",
   "param2" : "subKey2",
   "param3" : "subKey3",
   ${testdict9.${param1}.subKey2.subKey3} : "123",
   ${testdict9.subKey1.${param2}.subKey3} : "456",
   ${testdict9.subKey1.subKey2.${param3}} : "789"
}
""")

      listCodeSnippets.append("""{
   "dict_param" : {"A" : 1 , "B" : 2}
   "list_param" : ["A", "B", "C"]
   "val1"       : "${list_param[1]}"
}
""")

      listCodeSnippets.append("""{
   "dict_param" : {"A" : 1 , "B" : 2}
   "list_param" : ["A", "B", "C"]
   "val3"       : "${list_param[${dict_param}['A']]}"
}
""")

      listCodeSnippets.append("""{
   "dict_param" : {"A" : 1 , "B" : 2},
   "list_param" : ["A", "B", "C"],
   "val3"       : "${list_param[${dict_param}['A']]}"
}
""")

      listCodeSnippets.append("""{
   "dict_param" : {"A" : 1 , "B" : 2},
   "list_param" : ["A", "B", "C"],
   "val4"       : "${list_param[${dict_param}[${list_param}[0]]]}"
}
""")

      listCodeSnippets.append("""{
   "dict_param" : {"A" : 1 , "B" : 2},
   "list_param" : ["A", "B", "C"],
   "val4"       : "${list_param[${dict_param}['${list_param}[0]']]}"
}
""")

      listCodeSnippets.append("""{
   "intval"   : 1,
   "testlist" : ["B", 2],
   "param_${testlist}['${intval}']}" : 3
}
""")

      listCodeSnippets.append("""{
   "intval"   : 1,
   "testlist" : ["B", 2],
   ${testlist}[${intval}] : 4
}
""")

      listCodeSnippets.append("""{
   "testdict_1" : {},
   ${testdict_1.subKey.subKey.paramA} : {"A" : 1},
   ${testdict_2.subKey.subKey.paramA} : {"B" : 2},
   ${testdict_2.subKey.subKey.paramA.paramB} : {"C" : 3},
   ${testdict_2.subKey.subKey.paramA}['paramC'] : {"D" : 4},
   "paramD" : "D",
   "paramE" : "E",
   ${testdict_3.paramD.paramE.paramD} : {"E" : 5},
   ${testdict_3.paramD.paramE.paramD}[${paramE}] : {"F" : 6}
}
""")

      listCodeSnippets.append("""{
   ${testdict1.subKey1.subKey2.subKey3.subKey4} : 1,
   ${testdict1.subKey1.subKey2.subKey3} : {"subKey4" : 2},
   "testdict2" : ${testdict1},
   "param1" : "subKey1",
   "param2" : "subKey2",
   "param3" : "subKey3",
   "param4" : "subKey4",
   ${testdict1}[${param1}]['${param2}']['subKey3'][${param4}] : 3,
   ${testdict2.${param1}.subKey2.${param3}.subKey4} : 4,
   ${testdict2.subKey1.${param2}.subKey3.${param4}} : 5,
   "param5" : ${testdict1}[${param1}]['${param2}']['subKey3'][${param4}],
   "param6" : ${testdict2.${param1}.subKey2.${param3}.subKey4}
}
""")

      listCodeSnippets.append("""{
   ${testdict1.subKey1.subKey2} : 1,
   "testdict2" : ${testdict1}
   ${testdict1.subKey1.subKey2} : 2
}
""")

      listCodeSnippets.append("""{
   ${testdict1.subKey1.subKey2} : 1,
   "testdict2" : ${testdict1},
   ${testdict2.subKey1.subKey2} : 2
}
""")

      listCodeSnippets.append("""{
   "intval"   : 1,
   "testlist" : ["B", 2],
   ${testlist[${intval}]} : 4
}
""")

      listCodeSnippets.append("""{
   "intval" : 1,
   "testlist" : ["B", 2],
   ${testlist}['${intval}'] : 4
}
""")

      listCodeSnippets.append("""{
   "teststring" : "ABC",
   "${teststring}___${teststring}" : "DEF"
}
""")

      listCodeSnippets.append("""{
   "param1" : "prefix",
   "param2" : [1,2,3],
   "param3" : {"${param1}_${param2}_suffix" : "value"}
}
""")

# >> slicing:
# TODO: make autogenerated code in separate section

      listCodeSnippets.append("""{
   "testlist" : ["A", "B", "C", "D"],
   "index1"   : 1,
   "index2"   : 3,
   "param3"   : ${testlist}[${index1}:${index2}]
}
""")

      listCodeSnippets.append("""{
   "testlist" : ["A", "B", "C", "D"],
   "param1"   : ${testlist}[1:3]
}
""")

      listCodeSnippets.append("""{
   "testlist" : ["A", "B", "C", "D"],
   "param2"   : ${testlist}[:-1]
}
""")

      listCodeSnippets.append("""{
   "testlist" : ["A", "B", "C", "D"],
   "param2"  : ${testlist}[-1]
}
""")

      listCodeSnippets.append("""{
   "testlist" : ["A", "B", "C", "D"],
   "param2"  : ${testlist}[+1]
}
""")

      listCodeSnippets.append("""{
   "testlist" : ["A", "B", "C", "D"],
   "param2"  : ${testlist}[1:]
}
""")

      listCodeSnippets.append("""{
   "testlist" : ["A", "B", "C", "D"],
   "param2"  : ${testlist}[50]
}
""")

      listCodeSnippets.append("""{
   "testlist" : ["A", "B", "C", "D"],
   "param2"  : ${testlist}[X]
}
""")

      listCodeSnippets.append("""{
   "param1" : "string",
   "param2"  : ${param1}[50]
}
""")

      listCodeSnippets.append("""{
   "param"  : "value",
   ${param} : ${param}
}
""")

      listCodeSnippets.append("""{
   "param"  : {"A" : 1},
   ${param} : ${param}
}
""")

      listCodeSnippets.append("""{
   "param"  : ["A" , 1],
   ${param} : ${param}
}
""")

      listCodeSnippets.append("""{
   ${testdict1.subKey1.subKey2_1} : 1,
   ${testdict1.subKey1} : {"subKey2_2" : 2}
}
""")

      listCodeSnippets.append("""{
   ${testdict1.subKey1.subKey2_1} : 1,
   ${testdict1.subKey1} : 2
}
""")

      listCodeSnippets.append("""{
   "ara"   : "ara",
   "param" : 123,
   "val1"  : ${p${ara}m}
}
""")

      listCodeSnippets.append("""{
   "ara"   : "ara",
   "param" : 123,
   "val1"  : "${p${ara}m}"
}
""")

      listCodeSnippets.append("""{
   "teststring-1"  : "teststring-1 value",
   ${teststring-1} : "${teststring-1} extended"
}
""")

      listCodeSnippets.append("""{
   "intval"   : 1,
   "testlist" : ["B", 2],
   ${testlist}['${intval}'] : 4
}
""")

      listCodeSnippets.append("""{
   "intparam"    : 0,
   "stringparam" : "A",
   "listparam"   : ["A", "B"],
   "dictparam"   : {"0" : 0, "A" : 1, "B" : 2},
   "val01" : ${listparam}[${intparam}],
   "val02" : ${listparam}[1],
   "val03" : ${dictparam}['${intparam}'],
   "val04" : ${dictparam}[${stringparam}],
   "val05" : ${dictparam}['${stringparam}'],
   "val06" : ${dictparam}['A']
}
""")

      listCodeSnippets.append("""{
   "intparam"    : 0,
   "stringparam" : "A",
   "listparam"   : ["A", "B"],
   "dictparam"   : {"0" : 0, "A" : 1, "B" : 2},
   "val07" : "${listparam}[${intparam}]",
   "val08" : "${listparam}[1]",
   "val09" : "${dictparam}['${intparam}']",
   "val10" : "${dictparam}[${stringparam}]",
   "val11" : "${dictparam}['${stringparam}']",
   "val12" : "${dictparam}['A']"
}
""")

      listCodeSnippets.append("""{
   "dictparam" : {"A" : 1},
   "listparam" : ["A", "B"],
   ${IAMNOTEXISTING.${dictparam}}['${listparam}'] : 2
}
""")

      listCodeSnippets.append("""{
   "listparam"   : ["A", "B"],
   "stringparam" : "string",
   ${IAMNOTEXISTING.${stringparam}}['${listparam}'] : 2
}
""")

      listCodeSnippets.append("""{
   "stringparam" : "string",
   "intparam"    : 0,
   ${IAMNOTEXISTING.${stringparam}}['${intparam}'] : 2
}
""")

      listCodeSnippets.append("""{
   "stringparam" : "string",
   "intparam"    : 0,
   ${IAMNOTEXISTING.${stringparam}}[${intparam}] : 2
}
""")

      listCodeSnippets.append("""{
   "intval" : 1,
   "testlist" : ["B", 2],
   ${testlist}[${intval}] : 4
}
""")

      listCodeSnippets.append("""{
${testdict.subKey.subKey.subKey} : {"A" : 1},
"testdict": {"subKey": {"subKey": {"subKey": {"A": 2}}}}
}
""")

      listCodeSnippets.append("""{
   ${testdict.subKey.subKey.subKey} : {"A" : 1},
   "subKey" : "A",
   ${testdict.subKey.subKey.subKey}[${subKey}] : 2
}
""")

      listCodeSnippets.append("""{
   ${testdict.subKey.subKey.subKey} : {"A" : 1},
   "subKey" : "B",
   ${testdict.subKey.subKey.subKey}[${subKey}] : "2"
}
""")


      # --------------------------------------------------------------------------------------------------------------
      # TODO: check: several different expressions in square brackets inside curly brackets
      # TODO: check: invalid bracket content
      # TODO: check: usage of single quotes
      # TODO: check: substitutiomn with not supported (composite) data types
      # TODO: automate: several combinations with not existing parameters
      # TODO: ${dict} : ${dict} -> by value or by reference?

      # --------------------------------------------------------------------------------------------------------------

      return sHeadline, listCodeSnippets

   # eof def GetSeveralParticularSnippets(self):

   # --------------------------------------------------------------------------------------------------------------

   def GetBracketMismatch(self):
      """Assignments with missing brackets
      """

      sHeadline = "Assignments with missing brackets"

      listCodeSnippets = []

      listCodeSnippets.append("""{
   "param1" : "value1",
   "param2" : ${param1}
}
""")

      listCodeSnippets.append("""{
   "param1" : "value1",
   "param2" : ${param1
}
""")

      listCodeSnippets.append("""{
   "param1" : "value1",
   "param2" : "${param1"
}
""")

      listCodeSnippets.append("""{
   "param1" : "value1",
   "param2" : param1"
}
""")

      listCodeSnippets.append("""{
   "param1" : "value1",
   "param2" : "param1}"
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   "param" : ${listparam[0]
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   "param" : "${listparam[0]"
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   "param" : ${listparam}0]
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   "param" : "${listparam}0]"
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   "param" : ${listparam}[0
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   "param" : "${listparam}[0"
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   "param" : ${${listparam}[0]
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   "param" : "${${listparam}[0]"
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   "param" : $}${listparam}[0]
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   "param" : "$}${listparam}[0]"
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   ${listparam}[0] : "value"
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   ${listparam[0] : "value"
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   ${listparam}0] : "value"
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   ${{listparam}[0] : "value"
}
""")

      listCodeSnippets.append("""{
   "listparam" : ["A","B","C"],
   ${listparam}[}0] : "value"
}
""")

      return sHeadline, listCodeSnippets

   # eof def GetBracketMismatch(self):

   # --------------------------------------------------------------------------------------------------------------

   def GetDatatypePermutations(self):
      """Data type permutations in a fix pattern. Paremeter types: int, str, list, dict.
      """

      sHeadline = "Data type permutations in a fix pattern. Paremeter types: int, str, list, dict."

      sDefinitions = """   "indexP" : 0,
   "keyP"   : "A",
   "dictP"  : {"A" : 1, "B" : 2},
   "listP"  : ["A", "B"],
"""

      sCodeSnippetPattern = """{
####DEFINITIONS####
####ASSIGNMENT####
}
"""

      listofDataTypeTuples = []
      listofDataTypeTuples.append(("indexP", "indexP"))
      listofDataTypeTuples.append(("indexP", "keyP"))
      listofDataTypeTuples.append(("indexP", "dictP"))
      listofDataTypeTuples.append(("indexP", "listP"))
      listofDataTypeTuples.append(("keyP", "indexP"))
      listofDataTypeTuples.append(("keyP", "keyP"))
      listofDataTypeTuples.append(("keyP", "dictP"))
      listofDataTypeTuples.append(("keyP", "listP"))
      listofDataTypeTuples.append(("dictP", "indexP"))
      listofDataTypeTuples.append(("dictP", "keyP"))
      listofDataTypeTuples.append(("dictP", "dictP"))
      listofDataTypeTuples.append(("dictP", "listP"))
      listofDataTypeTuples.append(("listP", "indexP"))
      listofDataTypeTuples.append(("listP", "keyP"))
      listofDataTypeTuples.append(("listP", "dictP"))
      listofDataTypeTuples.append(("listP", "listP"))

      listAssignments = []

      listAssignments.append("   \"newparam\" : ${XXXX}[${YYYY}]")
      listAssignments.append("   \"newparam\" : \"${XXXX}[${YYYY}]\"")
      listAssignments.append("   \"newparam\" : ${XXXX}['${YYYY}']")
      listAssignments.append("   \"newparam\" : \"${XXXX}['${YYYY}']\"")

      listAssignments.append("   \"newparam\" : ${XXXX[${YYYY}]}")
      listAssignments.append("   \"newparam\" : \"${XXXX[${YYYY}]}\"")
      listAssignments.append("   \"newparam\" : ${XXXX['${YYYY}']}")
      listAssignments.append("   \"newparam\" : \"${XXXX['${YYYY}']}\"")

      listAssignments.append("   \"newparam\" : ${XXXX[${YYYY}]}")
      listAssignments.append("   \"newparam\" : \"${XXXX[${YYYY}]}\"")
      listAssignments.append("   \"newparam\" : ${XXXX['${YYYY}']}")
      listAssignments.append("   \"newparam\" : \"${XXXX['${YYYY}']}\"")

      listAssignments.append("   \"newparam\" : ${XXXX.${YYYY}}")
      listAssignments.append("   \"newparam\" : \"${XXXX.${YYYY}}\"")

      listAssignments.append("   ${XXXX}[${YYYY}] : \"newvalue\"")
      listAssignments.append("   \"${XXXX}[${YYYY}]\" : \"newvalue\"")
      listAssignments.append("   ${XXXX}['${YYYY}'] : \"newvalue\"")
      listAssignments.append("   \"${XXXX}['${YYYY}']\" : \"newvalue\"")

      listAssignments.append("   ${XXXX[${YYYY}]} : \"newvalue\"")
      listAssignments.append("   \"${XXXX[${YYYY}]}\" : \"newvalue\"")
      listAssignments.append("   ${XXXX['${YYYY}']} : \"newvalue\"")
      listAssignments.append("   \"${XXXX['${YYYY}']}\" : \"newvalue\"")

      listAssignments.append("   ${XXXX[${YYYY}]} : \"newvalue\"")
      listAssignments.append("   \"${XXXX[${YYYY}]}\" : \"newvalue\"")
      listAssignments.append("   ${XXXX['${YYYY}']} : \"newvalue\"")
      listAssignments.append("   \"${XXXX['${YYYY}']}\" : \"newvalue\"")

      listAssignments.append("   ${XXXX.${YYYY}} : \"newvalue\"")
      listAssignments.append("   \"${XXXX.${YYYY}}\" : \"newvalue\"")

      # put all things together

      listCodeSnippets = []

      for sAssignment in listAssignments:
         for tupleDataTypes in listofDataTypeTuples:
            sAssignment_repl = sAssignment.replace("XXXX", tupleDataTypes[0])
            sAssignment_repl = sAssignment_repl.replace("YYYY", tupleDataTypes[1])

            sCodeSnippet = sCodeSnippetPattern.replace("####DEFINITIONS####", sDefinitions)
            sCodeSnippet = sCodeSnippet.replace("####ASSIGNMENT####", sAssignment_repl)
            listCodeSnippets.append(sCodeSnippet)

      return sHeadline, listCodeSnippets

   # eof def GetDatatypePermutations(self):

   # --------------------------------------------------------------------------------------------------------------

   def GetNestedDataTypes(self):
      """Combinations of several expressions within a data structure of multiple nested dictionaries and lists
      """

      sHeadline = "Combinations of several expressions within a data structure of multiple nested dictionaries and lists"

      # 1. data structure without additional blanks around brackets, sub elements at end of parent elements
      sDataStructure1 = """   "params" : {*01* : *02*,
               *03* : [*04*, {*05* : *06*,
                              *07* : [*08*, [*09*, *10*]],
                              *11* : [*12*, {*13* : *14*}],
                              *15* : {*16* : [*17*, *18*]},
                              *19* : {*20* : {*21* : *22*}}
                             }
                       ]
              }"""

      # 2. data structure containing additional blanks around brackets, sub elements at end of parent elements
      sDataStructure2 = """   "params" : { *01* : *02*,
                *03* : [ *04*, { *05* : *06*,
                                 *07* : [ *08*, [ *09*, *10* ]],
                                 *11* : [ *12*, { *13* : *14* }],
                                 *15* : { *16* : [ *17*, *18* ]},
                                 *19* : { *20* : { *21* : *22* }}
                               }
                       ]
              }"""

      sDefinitions = """   "indexP" : 0,
   "keyP"   : "A",
   "dictP"  : {"A" : 0, "B" : 1},
   "listP"  : ["A", "B"],
"""

      sCodeSnippetPattern = """{
####DEFINITIONS####
####DATASTRUCTURE####
}
"""

      # We have a list of expressions and we have a list of placeholders like used in sDataStructure1 and sDataStructure2.
      # The followig code runs in a nested loop: Every expression is placed at every placeholder position. Only one single
      # expression and placeholder per iteration. All remaining placeholders in current iteration are replaced by elements
      # from a list of filler expressions (simple letters) that are only used to complete the code snippet, but are not in focus.
      # The expressions are of different complexity.
      # The impact on several expressions at several positions within the entire JSON code is to have successive brackets
      # in several combinations: [[, [{, {[, {{, }}, ]}, }], ]]

      listExpressions = ["${indexP}", "${keyP}", "${dictP}", "${listP}", "\"${indexP}\"", "\"${keyP}\"", "\"${dictP}\"", "\"${listP}\"", "123", "\"ABC\"",
                         "${listP}[${indexP}]", "${dictP}[${keyP}]", "${listP}[${dictP}[${keyP}]]", "${dictP}[${listP}[${indexP}]]",
                         "\"${listP}[${indexP}]\"", "\"${dictP}[${keyP}]\"", "\"${listP}[${dictP}[${keyP}]]\"", "\"${dictP}[${listP}[${indexP}]]\""]

      listPlaceholders = ["*01*", "*02*", "*03*", "*04*", "*05*", "*06*", "*07*", "*08*", "*09*", "*10*", "*11*",
                          "*12*", "*13*", "*14*", "*15*", "*16*", "*17*", "*18*", "*19*", "*20*", "*21*", "*22*"]

      listPositions = listPlaceholders[:] # to support a nested iteration of the same list; better readibility of code because of different names

      listFiller = ["001","002","003","004","005","006","007","008","009","010",
                    "011","012","013","014","015","016","017","018","019","020","021","022"] # as much elements as in listPlaceholders

      # put all things together

      listCodeSnippets = []

      # 1. data structure without additional blanks around brackets, sub elements at end of parent elements

      # sDataStructure1

      for sExpression in listExpressions:
         for sPosition in listPositions:
            sDataStructure = sDataStructure1      # init a new data structure from pattern sDataStructure1
            sCodeSnippet   = sCodeSnippetPattern  # init a new code snippet from code snippet pattern
            oFiller = CListElements(listFiller)   # init a new filler object (= content for remaining placeholders)
            for sPlaceholder in listPlaceholders:
               sFiller = oFiller.GetElement()
               if sPosition == sPlaceholder:
                  sDataStructure = sDataStructure.replace(sPlaceholder, sExpression)
               else:
                  sDataStructure = sDataStructure.replace(sPlaceholder, f"\"{sFiller}\"")
            # eof for sPlaceholder in listPlaceholders:
            sCodeSnippet = sCodeSnippet.replace("####DEFINITIONS####", sDefinitions)
            sCodeSnippet = sCodeSnippet.replace("####DATASTRUCTURE####", sDataStructure)
            listCodeSnippets.append(sCodeSnippet)
         # eof for sPosition in listPositions:
      # eof for sExpression in listExpressions:

      # 2. data structure containing additional blanks around brackets, sub elements at end of parent elements

      # sDataStructure2

      for sExpression in listExpressions:
         for sPosition in listPositions:
            sDataStructure = sDataStructure2      # init a new data structure from pattern sDataStructure2
            sCodeSnippet   = sCodeSnippetPattern  # init a new code snippet from code snippet pattern
            oFiller = CListElements(listFiller)   # init a new filler object (= content for remaining placeholders)
            for sPlaceholder in listPlaceholders:
               sFiller = oFiller.GetElement()
               if sPosition == sPlaceholder:
                  sDataStructure = sDataStructure.replace(sPlaceholder, sExpression)
               else:
                  sDataStructure = sDataStructure.replace(sPlaceholder, f"\"{sFiller}\"")
            # eof for sPlaceholder in listPlaceholders:
            sCodeSnippet = sCodeSnippet.replace("####DEFINITIONS####", sDefinitions)
            sCodeSnippet = sCodeSnippet.replace("####DATASTRUCTURE####", sDataStructure)
            listCodeSnippets.append(sCodeSnippet)
         # eof for sPosition in listPositions:
      # eof for sExpression in listExpressions:

      return sHeadline, listCodeSnippets

   # eof def GetNestedDataTypes(self):

   # --------------------------------------------------------------------------------------------------------------

   def GetNotExistingParams(self):
      """Not existing params at several positions within a complex data structure
      """

      sHeadline = "Not existing params at several positions within a complex data structure"

      # data structure 1
      sDataStructure1 = """   "params" : {*01* : *02*,
               *03* : [*04*, {*05* : *06*,
                              *07* : [*08*, [*09*, *10*]],
                              *11* : [*12*, {*13* : *14*}],
                              *15* : {*16* : [*17*, *18*]},
                              *19* : {*20* : {*21* : *22*}}
                             }
                       ]
              }"""

      sDefinitions = """   "indexP" : 0,
   "keyP"   : "A",
   "dictP"  : {"A" : 0, "B" : 1},
   "listP"  : ["A", "B"],
"""

      sCodeSnippetPattern = """{
####DEFINITIONS####
####DATASTRUCTURE####
}
"""

      # We have a list of expressions and we have a list of placeholders like used in sDataStructure1.
      # The followig code runs in a nested loop: Every expression is placed at every placeholder position. Only one single
      # expression and placeholder per iteration. All remaining placeholders in current iteration are replaced by elements
      # from a list of filler expressions (simple letters) that are only used to complete the code snippet, but are not in focus.

      listExpressions = ["${IAMNOTEXISTING}", "${dictP}[${IAMNOTEXISTING}]", "${listP}[${IAMNOTEXISTING}]"]

      listPlaceholders = ["*01*", "*02*", "*03*", "*04*", "*05*", "*06*", "*07*", "*08*", "*09*", "*10*", "*11*",
                          "*12*", "*13*", "*14*", "*15*", "*16*", "*17*", "*18*", "*19*", "*20*", "*21*", "*22*"]

      listPositions = listPlaceholders[:] # to support a nested iteration of the same list; better readibility of code because of different names

      listFiller = ["001","002","003","004","005","006","007","008","009","010",
                    "011","012","013","014","015","016","017","018","019","020","021","022"] # as much elements as in listPlaceholders

      # put all things together

      listCodeSnippets = []

      # sDataStructure1

      for sExpression in listExpressions:
         for sPosition in listPositions:
            sDataStructure = sDataStructure1      # init a new data structure from pattern sDataStructure1
            sCodeSnippet   = sCodeSnippetPattern  # init a new code snippet from code snippet pattern
            oFiller = CListElements(listFiller)   # init a new filler object (= content for remaining placeholders)
            for sPlaceholder in listPlaceholders:
               sFiller = oFiller.GetElement()
               if sPosition == sPlaceholder:
                  sDataStructure = sDataStructure.replace(sPlaceholder, sExpression)
               else:
                  sDataStructure = sDataStructure.replace(sPlaceholder, f"\"{sFiller}\"")
            # eof for sPlaceholder in listPlaceholders:
            sCodeSnippet = sCodeSnippet.replace("####DEFINITIONS####", sDefinitions)
            sCodeSnippet = sCodeSnippet.replace("####DATASTRUCTURE####", sDataStructure)
            listCodeSnippets.append(sCodeSnippet)
         # eof for sPosition in listPositions:
      # eof for sExpression in listExpressions:

      return sHeadline, listCodeSnippets

   # eof def GetNotExistingParams(self):

# eof class CSnippets():


# --------------------------------------------------------------------------------------------------------------
# eof class definitions
# --------------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------
#[INITCONFIG]
# --------------------------------------------------------------------------------------------------------------
#TM***

# -- configuration setup (relative to the path of this app)
oConfig = None
try:
   oConfig = CConfig(os.path.abspath(sys.argv[0]))
except Exception as reason:
   sResult = CString.FormatResult(sMethod="(main)", bSuccess=None, sResult=str(reason))
   print()
   printfailure(sResult)
   print()
   sys.exit(ERROR)

# update version and date of this app
oConfig.Set("APP_VERSION", VERSION)
oConfig.Set("APP_VERSION_DATE", VERSION_DATE)
THISAPPNAME     = oConfig.Get('THISAPPNAME')
THISAPPFULLNAME = f"{THISAPPNAME} v. {VERSION} / {VERSION_DATE}"
oConfig.Set("THISAPPFULLNAME", THISAPPFULLNAME)


# --------------------------------------------------------------------------------------------------------------
#[INITLOGGER]
# --------------------------------------------------------------------------------------------------------------
#TM***

oLogger = None
try:
   oLogger = CLogger(oConfig)
except Exception as reason:
   sResult = CString.FormatResult(sMethod="(main)", bSuccess=None, sResult=str(reason))
   print()
   printfailure(sResult)
   print()
   sys.exit(ERROR)


# --------------------------------------------------------------------------------------------------------------

# ---- prepare initial output

# dump configuration values to log file
listFormattedOutputLines = oConfig.DumpConfig()
oLogger.WriteLog(120*"*")
oLogger.WriteLog(listFormattedOutputLines)
oLogger.WriteLog(120*"*" + "\n")

# write HTML header to report file
oHTMLPattern = CHTMLPattern()
oLogger.WriteReport(oHTMLPattern.GetHTMLHeader())
del oHTMLPattern

# --------------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------------
#[INITCOUNTER]
# --------------------------------------------------------------------------------------------------------------
#TM***

oCounter = CCounter()


# --------------------------------------------------------------------------------------------------------------
#[INITJPP]
# --------------------------------------------------------------------------------------------------------------
#TM***

# If oJsonPreprocessor is created here, all JSON snippets will be executed with the same JsonPreprocessor object.
# If oJsonPreprocessor is set to None, every JSON snippet is executed with an own object (that is createed within CExecutor).
# oJsonPreprocessor = None
oJsonPreprocessor = CJsonPreprocessor()


# --------------------------------------------------------------------------------------------------------------
#[INITEXECUTOR]
# --------------------------------------------------------------------------------------------------------------
#TM***

oExecutor = None
try:
   oExecutor = CExecutor(oConfig, oCounter, oLogger, oJsonPreprocessor)
except Exception as reason:
   sResult = CString.FormatResult(sMethod="(main)", bSuccess=None, sResult=str(reason))
   print()
   printfailure(sResult)
   print()
   sys.exit(ERROR)


# --------------------------------------------------------------------------------------------------------------
#[STARTOFEXECUTION]
# --------------------------------------------------------------------------------------------------------------
#TM***

oSnippets = CSnippets()

sHeadline, listCodeSnippets = oSnippets.GetSeveralParticularSnippets()
bSuccess, sResult = oExecutor.Execute(sHeadline, listCodeSnippets, "JPP")

sHeadline, listCodeSnippets = oSnippets.GetBracketMismatch()
bSuccess, sResult = oExecutor.Execute(sHeadline, listCodeSnippets, "JPP")

sHeadline, listCodeSnippets = oSnippets.GetDatatypePermutations()
bSuccess, sResult = oExecutor.Execute(sHeadline, listCodeSnippets, "JPP")

sHeadline, listCodeSnippets = oSnippets.GetNestedDataTypes()
bSuccess, sResult = oExecutor.Execute(sHeadline, listCodeSnippets, "JPP")

sHeadline, listCodeSnippets = oSnippets.GetNotExistingParams()
bSuccess, sResult = oExecutor.Execute(sHeadline, listCodeSnippets, "JPP")

print()
print(COLBG + "done")
print()


# --------------------------------------------------------------------------------------------------------------

# PrettyPrint(sHeadline, sPrefix="(sHeadline)")
# PrettyPrint(listCodeSnippets, sPrefix="(listCodeSnippets)")

# --------------------------------------------------------------------------------------------------------------
#[ENDOFEXECUTION]
# --------------------------------------------------------------------------------------------------------------
#TM***


# write HTML footer to report file
oHTMLPattern = CHTMLPattern()
oLogger.WriteReport(oHTMLPattern.GetHTMLFooter(oConfig.Get('NOW')))
del oHTMLPattern

del oConfig
del oLogger
del oCounter
del oExecutor

sys.exit(SUCCESS)

# --------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------

