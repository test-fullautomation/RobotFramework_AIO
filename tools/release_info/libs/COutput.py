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
# COutput.py
#
# XC-CT/ECA3-Queckenstedt
#
# 20.10.2023
#
# --------------------------------------------------------------------------------------------------------------

import os, sys, platform, shlex, subprocess, json, argparse
import colorama as col
import pypandoc

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.File.CFile import CFile
from PythonExtensionsCollection.Utils.CUtils import *

from libs.CPattern import CPattern
from libs.CHTMLMail import CHTMLMail

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

class COutput():
   """produce the output (currently HTML and email)
   """

   def __init__(self, oConfig=None):

      sMethod = "COutput.__init__"

      if oConfig is None:
         raise Exception(CString.FormatResult(sMethod, None, "oConfig is None"))

      self.__oConfig = oConfig

      self.__oPattern = CPattern()

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GenReleaseInfo(self):

      sMethod = "GenReleaseInfo"

      bSuccess = None
      sResult  = "UNKNOWN"

      REFERENCEPATH_CONFIG = self.__oConfig.Get('REFERENCEPATH_CONFIG')
      PACKAGE_CONTEXT      = self.__oConfig.Get('PACKAGE_CONTEXT')

      bundle_name              = PACKAGE_CONTEXT['bundle_name']
      bundle_version           = PACKAGE_CONTEXT['bundle_version']
      bundle_version_date      = PACKAGE_CONTEXT['bundle_version_date']
      sReleaseInfoFileHTMLName = f"release_info_{bundle_name}_{bundle_version}.html"
      sReleaseInfoFileHTMLName = sReleaseInfoFileHTMLName.replace(" ", "_")
      sReleaseInfoFileHTML     = f"{REFERENCEPATH_CONFIG}/{sReleaseInfoFileHTMLName}"

      self.__oConfig.Set('RELEASEINFOFILEHTML', sReleaseInfoFileHTML)

      # temporary output in list; later this list will be written to file and to email
      listLinesHTML = []

      # HTML header
      listLinesHTML.append(self.__oPattern.GetHeader(bundle_name))
      listLinesHTML.append(self.__oPattern.GetHLine())

      # header table
      listLinesHTML.append(self.__oPattern.GetHeaderTable(bundle_name, bundle_version, bundle_version_date))

      listLinesHTML.append(self.__oPattern.GetHLine())

      # ---- keys from RELEASE_MAIN_INFO

      RELEASE_MAIN_INFO = self.__oConfig.Get('RELEASE_MAIN_INFO')
      listVersionNumbersAll = list(RELEASE_MAIN_INFO.keys())

      # -- find version number matches

      # PrettyPrint(listVersionNumbersAll, sPrefix="listVersionNumbersAll")

      listVersionNumbersIdentified = []
      for sVersionNumber in listVersionNumbersAll:
         if bundle_version.startswith(sVersionNumber):
            listVersionNumbersIdentified.append(sVersionNumber)

      # PrettyPrint(listVersionNumbersIdentified, sPrefix="listVersionNumbersIdentified")

      # ---- lists of items for each section over all identified version numbers

      listReleaseNotes    = []
      listHighlights      = []
      listAdditionalHints = []
      listRequirements    = []

      for sVersionNumber in listVersionNumbersIdentified:
         # -- list of sections for certain version number
         listSections = list(RELEASE_MAIN_INFO[sVersionNumber].keys())
         if "RELEASENOTES" in listSections:
            listReleaseNotes.extend(RELEASE_MAIN_INFO[sVersionNumber]['RELEASENOTES'])
         if "HIGHLIGHTS" in listSections:
            listHighlights.extend(RELEASE_MAIN_INFO[sVersionNumber]['HIGHLIGHTS'])
         if "ADDITIONALHINTS" in listSections:
            listAdditionalHints.extend(RELEASE_MAIN_INFO[sVersionNumber]['ADDITIONALHINTS'])
         if "REQUIREMENTS" in listSections:
            listRequirements.extend(RELEASE_MAIN_INFO[sVersionNumber]['REQUIREMENTS'])

      # PrettyPrint(listReleaseNotes, sPrefix="listReleaseNotes")
      # PrettyPrint(listHighlights, sPrefix="listHighlights")
      # PrettyPrint(listAdditionalHints, sPrefix="listAdditionalHints")
      # PrettyPrint(listRequirements, sPrefix="listRequirements")

      # -- 'RELEASENOTES'

      if len(listReleaseNotes) > 0:
         # found 'RELEASENOTES' => write to output
         listLinesHTML.append(self.__oPattern.GetReleaseNotesTableBegin())
         for sReleaseNote in listReleaseNotes:
            sReleaseNote_conv = pypandoc.convert_text(sReleaseNote, 'html', format='rst')
            # to open link in another explorer window:
            sReleaseNote_conv = sReleaseNote_conv.replace("a href=", "a target=\"_blank\" href=")
            listLinesHTML.append(self.__oPattern.GetReleaseNotesTableDataRow(sReleaseNote_conv))
         listLinesHTML.append(self.__oPattern.GetTableFooter())
         listLinesHTML.append(self.__oPattern.GetVDist())

      # -- 'HIGHLIGHTS'

      if len(listHighlights) > 0:
         # found 'HIGHLIGHTS' => write to output
         listLinesHTML.append(self.__oPattern.GetHighlightsTableBegin())
         for sHighlight in listHighlights:
            sHighlight_conv = pypandoc.convert_text(sHighlight, 'html', format='rst')
            # to open link in another explorer window:
            sHighlight_conv = sHighlight_conv.replace("a href=", "a target=\"_blank\" href=")
            listLinesHTML.append(self.__oPattern.GetHighlightsTableDataRow(sHighlight_conv))
         listLinesHTML.append(self.__oPattern.GetTableFooter())
         listLinesHTML.append(self.__oPattern.GetVDist())

      # -- 'ADDITIONALHINTS'

      if len(listAdditionalHints) > 0:
         # found 'ADDITIONALHINTS' => write to output
         listLinesHTML.append(self.__oPattern.GetAdditionalHintsTableBegin())
         for sAdditionalHint in listAdditionalHints:
            sAdditionalHint_conv = pypandoc.convert_text(sAdditionalHint, 'html', format='rst')
            # to open link in another explorer window:
            sAdditionalHint_conv = sAdditionalHint_conv.replace("a href=", "a target=\"_blank\" href=")
            listLinesHTML.append(self.__oPattern.GetAdditionalHintsTableDataRow(sAdditionalHint_conv))
         listLinesHTML.append(self.__oPattern.GetTableFooter())
         listLinesHTML.append(self.__oPattern.GetVDist())

      # -- 'REQUIREMENTS'

      if len(listRequirements) > 0:
         # found 'REQUIREMENTS' => write to output
         listLinesHTML.append(self.__oPattern.GetRequirementsTableBegin())
         for sRequirement in listRequirements:
            sRequirement_conv = pypandoc.convert_text(sRequirement, 'html', format='rst')
            # to open link in another explorer window:
            sRequirement_conv = sRequirement_conv.replace("a href=", "a target=\"_blank\" href=")
            listLinesHTML.append(self.__oPattern.GetRequirementsTableDataRow(sRequirement_conv))
         listLinesHTML.append(self.__oPattern.GetTableFooter())
         listLinesHTML.append(self.__oPattern.GetVDist())

      # ---- keys from RELEASEITEMS (changes) / over all components and all version numbers

      AllRELEASEITEMS = self.__oConfig.Get('AllRELEASEITEMS')
      listComponentsAll = list(AllRELEASEITEMS.keys())
      listComponentsAll.sort()

      # -- resort of data structure
      # instead of
      # <component> / <version numbers> / <changes>    (including changes for all versions) - AllRELEASEITEMS
      # we need
      # <component> / <changes>                        (changes for for current version only) - dictListOfChangesPerComponent

      dictListOfChangesPerComponent = {}
      for sComponent in listComponentsAll:
         dictListOfChangesPerComponent[sComponent] = []
         listVersionNumbersAllPerComponent = list(AllRELEASEITEMS[sComponent].keys())

         # -- find version number matches
         listVersionNumbersIdentified = []
         for sVersionNumber in listVersionNumbersAllPerComponent:
            if bundle_version.startswith(sVersionNumber):
               listVersionNumbersIdentified.append(sVersionNumber)

         for sVersion in listVersionNumbersIdentified:
            listChanges = AllRELEASEITEMS[sComponent][sVersion]
            dictListOfChangesPerComponent[sComponent].extend(listChanges)
      # eof for sComponent in listComponentsAll:

      listIdentifiedComponents = list(dictListOfChangesPerComponent.keys())
      nCnt = 0
      if len(listIdentifiedComponents) > 0:
         # someting found, therefore start a table
         listLinesHTML.append(self.__oPattern.GetChangesTableBegin())
         for sIdentifiedComponent in listIdentifiedComponents:
            listChanges = dictListOfChangesPerComponent[sIdentifiedComponent]
            for sChange in listChanges:
               nCnt = nCnt + 1
               sChange_conv = pypandoc.convert_text(sChange, 'html', format='rst')
               # to open link in another explorer window:
               sChange_conv = sChange_conv.replace("a href=", "a target=\"_blank\" href=")
               listLinesHTML.append(self.__oPattern.GetChangesTableDataRow(nCnt, sIdentifiedComponent, sChange_conv))
         listLinesHTML.append(self.__oPattern.GetTableFooter())
         listLinesHTML.append(self.__oPattern.GetVDist())
      # eof if len(listIdentifiedComponents) > 0:

      listLinesHTML.append(self.__oPattern.GetVDist())
      listLinesHTML.append(self.__oPattern.GetHLine())

      # eof HTML file
      listLinesHTML.append(self.__oPattern.GetEndOfFile())

      listResults = []

      # -- output to file

      sHTMLCode = "\n".join(listLinesHTML)

      oReleaseInfoFileHTML = CFile(sReleaseInfoFileHTML)
      oReleaseInfoFileHTML.Write(sHTMLCode)
      del oReleaseInfoFileHTML

      listResults.append(f"Release info written to '{sReleaseInfoFileHTML}'")

      # -- output to email

      oHTMLMail = None
      try:
         oHTMLMail = CHTMLMail(self.__oConfig)
      except Exception as reason:
         bSuccess = None
         sResult  = CString.FormatResult(sMethod=sMethod, bSuccess=bSuccess, sResult=str(reason))
         listResults.append(sResult)
         return bSuccess, "\n\n".join(listResults)

      bSuccess, sResult = oHTMLMail.GenHTMLMail(listLinesHTML)
      if bSuccess is not True:
         sResult = CString.FormatResult(sMethod, bSuccess, sResult)
         listResults.append(sResult)
         return bSuccess, "\n\n".join(listResults)
      listResults.append(sResult)

      bSuccess = True
      return bSuccess, "\n\n".join(listResults)

   # eof def GenReleaseInfo(self):

