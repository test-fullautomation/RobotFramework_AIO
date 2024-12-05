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
# release_info.py
#
# XC-HWP/ESW3-Queckenstedt
#
# **************************************************************************************************************
#
VERSION      = "0.10.0"
VERSION_DATE = "26.11.2024"
#
# **************************************************************************************************************

# History

# **************************************************************************************************************
# TM***
#
# -- TOC
#[CONFIG]
#[RELEASEDATA]
#[OUTPUT]

# -- import standard Python modules
import sys, string, re, time, os, argparse, pypandoc
from lxml import etree
import colorama as col

# -- import own Python modules
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.Utils.CUtils import *

from libs.CConfig import CConfig
from libs.CReleaseData import CReleaseData
from libs.COutput import COutput

col.init(autoreset=True)

COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN
COLNG = col.Style.NORMAL + col.Fore.GREEN
COLBY = col.Style.BRIGHT + col.Fore.YELLOW

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
#[CONFIG]
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

# dump configuration values to screen
oConfig.DumpConfig()

CONFIGDUMP = oConfig.Get('CONFIGDUMP')
if CONFIGDUMP is True:
   # if that's all, we have nothing more to do
   print(COLNG + "done.")
   sys.exit(SUCCESS)

# --------------------------------------------------------------------------------------------------------------
#[RELEASEDATA]
# --------------------------------------------------------------------------------------------------------------
#TM***

# -- read all release data from JSON files
oReleaseData = None
try:
   oReleaseData = CReleaseData(oConfig)
except Exception as reason:
   sResult = CString.FormatResult(sMethod="(main)", bSuccess=None, sResult=str(reason))
   print()
   printfailure(sResult)
   print()
   sys.exit(ERROR)

bSuccess, sResult = oReleaseData.GetReleaseData()
if bSuccess is not True:
   sResult = CString.FormatResult(sMethod="(main)", bSuccess=bSuccess, sResult=sResult)
   print()
   printfailure(sResult)
   print()
   sys.exit(ERROR)

# debug
# oConfig.PrettyPrint()

# --------------------------------------------------------------------------------------------------------------
#[OUTPUT]
# --------------------------------------------------------------------------------------------------------------
#TM***

oOutput = None
try:
   oOutput = COutput(oConfig)
except Exception as reason:
   sResult = CString.FormatResult(sMethod="(main)", bSuccess=None, sResult=str(reason))
   print()
   printfailure(sResult)
   print()
   sys.exit(ERROR)

bSuccess, sResult = oOutput.GenReleaseInfo()
if bSuccess is not True:
   sResult = CString.FormatResult(sMethod="(main)", bSuccess=bSuccess, sResult=sResult)
   print()
   printfailure(sResult)
   print()
   sys.exit(ERROR)

print(COLBY + sResult)
print()

print(COLNG + "done.")

sys.exit(SUCCESS)

# --------------------------------------------------------------------------------------------------------------


