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
# COutput.py
#
# XC-HWP/ESW3-Queckenstedt
#
# 26.11.2024
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

def IsVersionMatch(bundle_version, release_info_version):
   """Little helper to identify version numbers (match between bundle version number and version number string in release info file)
   """
   is_version_match = False
   splitparts = release_info_version.split(';')
   for part in splitparts:
      part = part.strip()
      if part != "":
         if ( (part == "*") or (bundle_version.startswith(part)) ):
            is_version_match = True
            break
   return is_version_match

# --------------------------------------------------------------------------------------------------------------

def resolveVariable(sContent, dVarMapping):
   """Helps to resolve variable (define with ###VAR### syntax) by its value in given content
   """
   sResolvedLine = sContent
   for var, value in dVarMapping.items():
      sResolvedLine = sResolvedLine.replace(f"###{var}###", value)
   
   return sResolvedLine

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
      sReleaseInfoFileHTMLName = sReleaseInfoFileHTMLName.replace("(", "")
      sReleaseInfoFileHTMLName = sReleaseInfoFileHTMLName.replace(")", "")
      sReleaseInfoFileHTML     = f"{REFERENCEPATH_CONFIG}/{sReleaseInfoFileHTMLName}"
      sReleaseChangelogFileHTML= f"{REFERENCEPATH_CONFIG}/release_changelog.html"

      self.__oConfig.Set('RELEASEINFOFILEHTML', sReleaseInfoFileHTML)

      # temporary output in list; later this list will be written to file and to email
      listLinesHTML = []

      # HTML header
      listLinesHTML.append(self.__oPattern.GetHeader(bundle_name))
      listLinesHTML.append(self.__oPattern.GetHLine())

      # header table
      # (!!! temporary hack !!!)
      framework_name = "RobotFramework AIO"
      bundle_name_fixed = bundle_name.replace("AIO ", "")
      listLinesHTML.append(self.__oPattern.GetHeaderTable(framework_name, bundle_name_fixed, bundle_version, bundle_version_date))

      listLinesHTML.append(self.__oPattern.GetHLine())

      # ---- keys from RELEASE_MAIN_INFO

      RELEASE_MAIN_INFO = self.__oConfig.Get('RELEASE_MAIN_INFO')
      listVersionNumbersAll = list(RELEASE_MAIN_INFO.keys())

      # prepare variable mapping for replacement in release main info 
      lBundleVersion = bundle_version.split('.')
      lIntermediateLabels = []
      if (len(lBundleVersion) > 2) and (int(lBundleVersion[2]) == 0):
         # check list of version from release_main_info to get intermediate release labels
         # intermediate release labels are only required for major release (patch version is 0)
         for versionNo in listVersionNumbersAll:
            lVersionInfo = versionNo.split('.')
            if (len(lVersionInfo) > 2) and (lVersionInfo[0] == lBundleVersion[0]) \
                and (int(lVersionInfo[1]) == int(lBundleVersion[1])-1) and (int(lVersionInfo[2]) != 0):
               lIntermediateLabels.append('.'.join(lVersionInfo[:3]))
      sIntermediateLabels = ','.join(lIntermediateLabels) if len(lIntermediateLabels) > 0 else ""
         
      dVariableMapping = {
         "VERSION": '.'.join(lBundleVersion[:4]),
         "INTERMEDIATE_LABELS": sIntermediateLabels,
         "LABEL": '.'.join(lBundleVersion[:3])
      }

      # -- find version number matches

      # PrettyPrint(listVersionNumbersAll, sPrefix="listVersionNumbersAll")

      listVersionNumbersIdentified = []
      for sVersionNumber in listVersionNumbersAll:
         if IsVersionMatch(bundle_version, sVersionNumber):
            listVersionNumbersIdentified.append(sVersionNumber)

      # PrettyPrint(listVersionNumbersIdentified, sPrefix="listVersionNumbersIdentified")

      # ---- lists of items for each section over all identified version numbers

      listReleaseNotes          = []
      listWarnings              = []
      listHighlights            = []
      listAdditionalInformation = []
      listRequirements          = []
      listRestrictions          = []
      listLinksRaw              = []

      for sVersionNumber in listVersionNumbersIdentified:
         # -- list of sections for certain version number
         listSections = list(RELEASE_MAIN_INFO[sVersionNumber].keys())
         if "RELEASENOTES" in listSections:
            listReleaseNotes.extend(RELEASE_MAIN_INFO[sVersionNumber]['RELEASENOTES'])
         if "WARNINGS" in listSections:
            listWarnings.extend(RELEASE_MAIN_INFO[sVersionNumber]['WARNINGS'])
         if "HIGHLIGHTS" in listSections:
            listHighlights.extend(RELEASE_MAIN_INFO[sVersionNumber]['HIGHLIGHTS'])
         if "ADDITIONALINFORMATION" in listSections:
            listAdditionalInformation.extend(RELEASE_MAIN_INFO[sVersionNumber]['ADDITIONALINFORMATION'])
         if "REQUIREMENTS" in listSections:
            listRequirements.extend(RELEASE_MAIN_INFO[sVersionNumber]['REQUIREMENTS'])
         if "RESTRICTIONS" in listSections:
            listRestrictions.extend(RELEASE_MAIN_INFO[sVersionNumber]['RESTRICTIONS'])
         if "VERSIONEDLINKS" in listSections:
            listLinksRaw.extend(RELEASE_MAIN_INFO[sVersionNumber]['VERSIONEDLINKS'])
      # eof for sVersionNumber in listVersionNumbersIdentified:

      if "COMMONLINKS" in RELEASE_MAIN_INFO:
         # we assume here that no version number is "COMMONLINKS"
         listLinksRaw.extend(RELEASE_MAIN_INFO['COMMONLINKS'])

      # generate a list of all links, at first the version specific ones, at second the common ones,
      # with link information separated by link address and link name

      listofdictLinks = []
      for sLink in listLinksRaw:
         sResolvedLink = resolveVariable(sLink, dVariableMapping)
         listLinkParts = sResolvedLink.split(';')
         # PrettyPrint(listLinkParts, sPrefix="listLinkParts")
         nNrOfParts = len(listLinkParts)
         dictLink = {}
         if nNrOfParts == 1:
            dictLink['LINKADDRESS']  = listLinkParts[0].strip()
            dictLink['LINKNAME']     = dictLink['LINKADDRESS']
            dictLink['LINKHEADLINE'] = None
         elif nNrOfParts == 2:
            dictLink['LINKADDRESS']  = listLinkParts[0].strip()
            dictLink['LINKNAME']     = listLinkParts[1].strip()
            dictLink['LINKHEADLINE'] = None
         elif nNrOfParts == 3:
            dictLink['LINKADDRESS']  = listLinkParts[0].strip()
            dictLink['LINKNAME']     = listLinkParts[1].strip()
            dictLink['LINKHEADLINE'] = listLinkParts[2].strip()
         else:
            bSuccess = False
            sResult  = f"Invalid link: '{sLink}'. Reason: Too much ';' separators found; expected two separator at most"
            sResult  = CString.FormatResult(sMethod=sMethod, bSuccess=bSuccess, sResult=sResult)
            return bSuccess, sResult
         listofdictLinks.append(dictLink)
         del dictLink
      # eof for sLink in listLinksRaw:

      # debug:
      # PrettyPrint(listReleaseNotes, sPrefix="listReleaseNotes")
      # PrettyPrint(listWarnings, sPrefix="listReleaseNotes")
      # PrettyPrint(listHighlights, sPrefix="listHighlights")
      # PrettyPrint(listAdditionalInformation, sPrefix="listAdditionalInformation")
      # PrettyPrint(listRequirements, sPrefix="listRequirements")
      # PrettyPrint(listRestrictions, sPrefix="listRestrictions")
      # PrettyPrint(listLinksRaw, sPrefix="listLinksRaw")
      # PrettyPrint(listofdictLinks, sPrefix="listofdictLinks")

      # -- 'RELEASENOTES'

      if len(listReleaseNotes) > 0:
         # found 'RELEASENOTES' => write to output
         listLinesHTML.append(self.__oPattern.GetReleaseNotesTableBegin())
         for sReleaseNote in listReleaseNotes:
            sReleaseNote_resolve = resolveVariable(sReleaseNote, dVariableMapping)
            sReleaseNote_conv = pypandoc.convert_text(sReleaseNote_resolve, 'html', format='rst')
            # to open link in another explorer window:
            sReleaseNote_conv = sReleaseNote_conv.replace("a href=", "a target=\"_blank\" href=")
            # <code> tag fix: size and color
            sReleaseNote_conv = sReleaseNote_conv.replace("<code>", "<code><font font-family=\"courier new\" color=\"navy\" size=\"+1\">")
            sReleaseNote_conv = sReleaseNote_conv.replace("</code>", "</font></code>")
            listLinesHTML.append(self.__oPattern.GetReleaseNotesTableDataRow(sReleaseNote_conv))
         listLinesHTML.append(self.__oPattern.GetTableFooter())
         listLinesHTML.append(self.__oPattern.GetVDist())

      # -- 'WARNINGS'

      if len(listWarnings) > 0:
         # found 'WARNINGS' => write to output
         listLinesHTML.append(self.__oPattern.GetWarningsTableBegin())
         for sWarning in listWarnings:
            sWarning_resolve = resolveVariable(sWarning, dVariableMapping)
            sWarning_conv = pypandoc.convert_text(sWarning_resolve, 'html', format='rst')
            # to open link in another explorer window:
            sWarning_conv = sWarning_conv.replace("a href=", "a target=\"_blank\" href=")
            # <code> tag fix: size and color
            sWarning_conv = sWarning_conv.replace("<code>", "<code><font font-family=\"courier new\" color=\"navy\" size=\"+1\">")
            sWarning_conv = sWarning_conv.replace("</code>", "</font></code>")
            listLinesHTML.append(self.__oPattern.GetWarningsTableDataRow(sWarning_conv))
         listLinesHTML.append(self.__oPattern.GetTableFooter())
         listLinesHTML.append(self.__oPattern.GetVDist())

      # -- 'HIGHLIGHTS'

      if len(listHighlights) > 0:
         # found 'HIGHLIGHTS' => write to output
         listLinesHTML.append(self.__oPattern.GetHighlightsTableBegin())
         for sHighlight in listHighlights:
            sHighlight_resolve = resolveVariable(sHighlight, dVariableMapping)
            sHighlight_conv = pypandoc.convert_text(sHighlight_resolve, 'html', format='rst')
            # to open link in another explorer window:
            sHighlight_conv = sHighlight_conv.replace("a href=", "a target=\"_blank\" href=")
            # <code> tag fix: size and color
            sHighlight_conv = sHighlight_conv.replace("<code>", "<code><font font-family=\"courier new\" color=\"navy\" size=\"+1\">")
            sHighlight_conv = sHighlight_conv.replace("</code>", "</font></code>")
            listLinesHTML.append(self.__oPattern.GetHighlightsTableDataRow(sHighlight_conv))
         listLinesHTML.append(self.__oPattern.GetTableFooter())
         listLinesHTML.append(self.__oPattern.GetVDist())

      # -- 'ADDITIONALINFORMATION'

      if len(listAdditionalInformation) > 0:
         # found 'ADDITIONALINFORMATION' => write to output
         listLinesHTML.append(self.__oPattern.GetAdditionalInformationTableBegin())
         for sAdditionalInformation in listAdditionalInformation:
            sAdditionalInformation_resolved = resolveVariable(sAdditionalInformation, dVariableMapping)
            sAdditionalInformation_conv = pypandoc.convert_text(sAdditionalInformation_resolved, 'html', format='rst')
            # to open link in another explorer window:
            sAdditionalInformation_conv = sAdditionalInformation_conv.replace("a href=", "a target=\"_blank\" href=")
            # <code> tag fix: size and color
            sAdditionalInformation_conv = sAdditionalInformation_conv.replace("<code>", "<code><font font-family=\"courier new\" color=\"navy\" size=\"+1\">")
            sAdditionalInformation_conv = sAdditionalInformation_conv.replace("</code>", "</font></code>")
            listLinesHTML.append(self.__oPattern.GetAdditionalInformationTableDataRow(sAdditionalInformation_conv))
         listLinesHTML.append(self.__oPattern.GetTableFooter())
         listLinesHTML.append(self.__oPattern.GetVDist())

      # -- 'REQUIREMENTS'

      if len(listRequirements) > 0:
         # found 'REQUIREMENTS' => write to output
         listLinesHTML.append(self.__oPattern.GetRequirementsTableBegin())
         for sRequirement in listRequirements:
            sRequirement_resolve = resolveVariable(sRequirement, dVariableMapping)
            sRequirement_conv = pypandoc.convert_text(sRequirement_resolve, 'html', format='rst')
            # to open link in another explorer window:
            sRequirement_conv = sRequirement_conv.replace("a href=", "a target=\"_blank\" href=")
            # <code> tag fix: size and color
            sRequirement_conv = sRequirement_conv.replace("<code>", "<code><font font-family=\"courier new\" color=\"navy\" size=\"+1\">")
            sRequirement_conv = sRequirement_conv.replace("</code>", "</font></code>")
            listLinesHTML.append(self.__oPattern.GetRequirementsTableDataRow(sRequirement_conv))
         listLinesHTML.append(self.__oPattern.GetTableFooter())
         listLinesHTML.append(self.__oPattern.GetVDist())

      # -- 'RESTRICTIONS'

      if len(listRestrictions) > 0:
         # found 'RESTRICTIONS' => write to output
         listLinesHTML.append(self.__oPattern.GetRestrictionsTableBegin())
         for sRestriction in listRestrictions:
            sRestriction_resolve = resolveVariable(sRestriction, dVariableMapping)
            sRestriction_conv = pypandoc.convert_text(sRestriction_resolve, 'html', format='rst')
            # to open link in another explorer window:
            sRestriction_conv = sRestriction_conv.replace("a href=", "a target=\"_blank\" href=")
            # <code> tag fix: size and color
            sRestriction_conv = sRestriction_conv.replace("<code>", "<code><font font-family=\"courier new\" color=\"navy\" size=\"+1\">")
            sRestriction_conv = sRestriction_conv.replace("</code>", "</font></code>")
            listLinesHTML.append(self.__oPattern.GetRestrictionsTableDataRow(sRestriction_conv))
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
            if IsVersionMatch(bundle_version, sVersionNumber):
               listVersionNumbersIdentified.append(sVersionNumber)

         for sVersion in listVersionNumbersIdentified:
            listChanges = AllRELEASEITEMS[sComponent][sVersion]
            dictListOfChangesPerComponent[sComponent].extend(listChanges)
      # eof for sComponent in listComponentsAll:

      listHTMLChangelog = []
      listIdentifiedComponents = list(dictListOfChangesPerComponent.keys())
      nCnt = 0
      nCntCmpt = 1
      if len(listIdentifiedComponents) > 0:
         # someting found, therefore start a table
         listLinesHTML.append(self.__oPattern.GetChangesTableBegin())
         listHTMLChangelog.append(self.__oPattern.GetChangeLogTableBegin())
         for sIdentifiedComponent in listIdentifiedComponents:
            listChanges = dictListOfChangesPerComponent[sIdentifiedComponent]
            sHTMLChangelogCmpt = ''
            if listChanges:
               nCntCmpt = nCntCmpt + 1
               sHTMLChangelogCmpt = sHTMLChangelogCmpt + f"<h3>{sIdentifiedComponent}</h3>"
            for sChange in listChanges:
               nCnt = nCnt + 1
               sChange_conv = pypandoc.convert_text(sChange, 'html', format='rst')
               # to open link in another explorer window:
               sChange_conv = sChange_conv.replace("a href=", "a target=\"_blank\" href=")
               # <code> tag fix: size and color
               sChange_conv = sChange_conv.replace("<code>", "<code><font font-family=\"courier new\" color=\"navy\" size=\"+1\">")
               sChange_conv = sChange_conv.replace("</code>", "</font></code>")
               listLinesHTML.append(self.__oPattern.GetChangesTableDataRow(nCnt, sIdentifiedComponent, sChange_conv))
               sHTMLChangelogCmpt = sHTMLChangelogCmpt + sChange_conv
            
            if sHTMLChangelogCmpt:
               listHTMLChangelog.append(self.__oPattern.GetChangeLogTableDataRow(sHTMLChangelogCmpt))

         listLinesHTML.append(self.__oPattern.GetTableFooter())
         listLinesHTML.append(self.__oPattern.GetVDist())
      # eof if len(listIdentifiedComponents) > 0:

      # -- 'LINKS'

      if len(listofdictLinks) > 0:
         # found 'LINKS' => write to output
         listLinesHTML.append(self.__oPattern.GetLinksTableBegin())
         for dictLink in listofdictLinks:
            listLinesHTML.append(self.__oPattern.GetLinksTableDataRow(dictLink['LINKADDRESS'], dictLink['LINKNAME'], dictLink['LINKHEADLINE']))
         listLinesHTML.append(self.__oPattern.GetTableFooter())
         listLinesHTML.append(self.__oPattern.GetVDist())
      # eof if len(listofdictLinks) > 0:

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

      # write changelog html file
      oReleaseChangelogFileHTML = CFile(sReleaseChangelogFileHTML)
      sChangelogContent = "\n".join(listHTMLChangelog).replace("\r\n", " ")
      oReleaseChangelogFileHTML.Write(sChangelogContent)
      del oReleaseChangelogFileHTML

      listResults.append(f"Release changelog written to '{sReleaseChangelogFileHTML}'")

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

