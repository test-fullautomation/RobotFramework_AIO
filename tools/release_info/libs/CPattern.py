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
# CPattern.py
#
# XC-HWP/ESW3-Queckenstedt
#
# 05.09.2024
#
# --------------------------------------------------------------------------------------------------------------

import os, sys, platform, shlex, subprocess, json, argparse, time
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

class CPattern():
   """All text pattern to produce the output format (currently HTML)
   """

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetHeader(self, sFrameworkName=None):
      sHeader = """<html>
<head>
   <meta name="###FRAMEWORKNAME###" content="Release" charset="UTF-8"/>
   <title>###FRAMEWORKNAME###</title>
</head>
<body bgcolor="#FFFFFF" text="#000000" link="#0000FF" vlink="#0000FF" alink="#0000FF">
"""
      sHeader = sHeader.replace("###FRAMEWORKNAME###", f"{sFrameworkName}")
      return sHeader

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetEndOfFile(self):
      sEndOfFile = """<font face="Arial" color="#000000" size="-2">Created at ###DATEOFCREATION###</font>
</body>
</html>
"""
      sDateOfCreation = time.strftime('%d.%m.%Y - %H:%M:%S')
      sEndOfFile = sEndOfFile.replace("###DATEOFCREATION###", f"{sDateOfCreation}")
      return sEndOfFile

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetHLine(self):
      sHLine = """<hr width=\"100%\" align=\"center\" color=\"#d0d0d0\"/>
"""
      return sHLine

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetVDist(self):
      sVDist = """<par><font size=\"-3\">&nbsp;</font></par>
"""
      return sVDist

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetTableHeader(self):
      sTableHeader = """<table border="0" width="100%" cellspacing="0" cellpadding="5" rules="none">
   <colgroup>
      <col width="100%" span="1"/>
   </colgroup>
"""
      return sTableHeader

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetTableFooter(self):
      sTableFooter = """</table>
"""
      return sTableFooter

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetHeaderTable(self, sFrameworkName=None, sBundleName=None, sReleaseVersion=None, sReleaseDate=None):
      sHeaderTable = """<table border="0" width="100%" cellspacing="0" cellpadding="5" rules="none">
<colgroup>
   <col width="100%" span="1"/>
</colgroup>
<tr border="0" cellspacing="0" colspan="2">
   <td bgcolor="#FFFFFF" align="center" valign="top" border="0" cellspacing="0" style="padding:9pt 6pt 9pt 6pt">
      <font face="Arial" color="#242424" size="+4"><b>###FRAMEWORKNAME###</b></font>
   </td>
</tr>
<tr border="0" cellspacing="0" colspan="2">
   <td bgcolor="#FFFFFF" align="center" valign="top" border="0" cellspacing="0" style="padding:9pt 6pt 9pt 6pt">
      <font face="Arial" color="#242424" size="+3"><i>&quot;<b>A</b>ll <b>I</b>n <b>O</b>ne&quot; bundle, based on ###BUNDLENAME###</i></font>
   </td>
</tr>
<tr border="0" cellspacing="0" colspan="2">
   <td bgcolor="#FFFFFF" align="center" valign="top" border="0" cellspacing="0">
      <font face="Arial" color="#242424" size="+1"></font>
   </td>
</tr>
<tr border="0" cellspacing="0" colspan="2">
   <td bgcolor="#FFFFFF" width="100%" align="center" valign="middle" border="0" cellspacing="0">
      <table width="40%" border="1" cellspacing="0" cellpadding="0" frame="box" rules="all">
         <colgroup>
            <col width="50%" span="1"/>
            <col width="50%" span="1"/>
         </colgroup>
         <tr>
            <td bgcolor="#F5F5F5" width="50%" align="left" style="padding:9pt 6pt 9pt 6pt"><font face="Arial" color="#000000" size="2">Release version</font></td>
            <td bgcolor="#F5F5F5" width="50%" align="left" style="padding:9pt 6pt 9pt 6pt"><font face="Arial" color="#FF0000" size="2">###RELEASEVERSION###</font></td>
         </tr>
         <tr>
            <td bgcolor="#F5F5F5" width="50%" align="left" style="padding:9pt 6pt 9pt 6pt"><font face="Arial" color="#000000" size="2">Release date</font></td>
            <td bgcolor="#F5F5F5" width="50%" align="left" style="padding:9pt 6pt 9pt 6pt"><font face="Arial" color="#FF0000" size="2">###RELEASEDATE###</font></td>
         </tr>
      </table>
   </td>
</tr>
</table>
"""
      sHeaderTable = sHeaderTable.replace("###FRAMEWORKNAME###",  f"{sFrameworkName}")
      sHeaderTable = sHeaderTable.replace("###BUNDLENAME###",     f"{sBundleName}")
      sHeaderTable = sHeaderTable.replace("###RELEASEVERSION###", f"{sReleaseVersion}")
      sHeaderTable = sHeaderTable.replace("###RELEASEDATE###",    f"{sReleaseDate}")
      return sHeaderTable

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetReleaseNotesTableBegin(self):
      sReleaseNotesTableBegin = """<h3><font face="Arial" color="#242424">Release notes</font></h3>
<table width="100%" border="1" cellspacing="0" cellpadding="0" frame="box" rules="all" align="left">
"""
      return sReleaseNotesTableBegin

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetReleaseNotesTableDataRow(self, sReleaseNote=None):
      sReleaseNotesTableDataRow = """<tr>
   <td bgcolor="#F5F5F5" width="100%" align="left" style="padding:6pt 6pt 6pt 6pt"><font face="Arial" color="#000000" size="-1">###RELEASENOTE###</font></td>
</tr>
"""
      sReleaseNotesTableDataRow = sReleaseNotesTableDataRow.replace("###RELEASENOTE###", f"{sReleaseNote}")
      return sReleaseNotesTableDataRow

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetWarningsTableBegin(self):
      sWarningsTableBegin = """<h3><font face="Arial" color="#242424">Warnings</font></h3>
<table width="100%" border="1" cellspacing="0" cellpadding="0" frame="box" rules="all" align="left">
"""
      return sWarningsTableBegin

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetWarningsTableDataRow(self, sWarning=None):
      sWarningsTableDataRow = """<tr>
   <td bgcolor="#FFC1C1" width="100%" align="left" style="padding:6pt 6pt 6pt 6pt"><font face="Arial" color="#000000" size="-1">###WARNING###</font></td>
</tr>
"""
      sWarningsTableDataRow = sWarningsTableDataRow.replace("###WARNING###", f"{sWarning}")
      return sWarningsTableDataRow

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetHighlightsTableBegin(self):
      sHighlightsTableBegin = """<h3><font face="Arial" color="#242424">Highlights</font></h3>
<table width="100%" border="1" cellspacing="0" cellpadding="0" frame="box" rules="all" align="left">
"""
      return sHighlightsTableBegin

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetHighlightsTableDataRow(self, sHighlight=None):
      sHighlightsTableDataRow = """<tr>
   <td bgcolor="#F5F5F5" width="100%" align="left" style="padding:6pt 6pt 6pt 6pt"><font face="Arial" color="#000000" size="-1">###HIGHLIGHT###</font></td>
</tr>
"""
      sHighlightsTableDataRow = sHighlightsTableDataRow.replace("###HIGHLIGHT###", f"{sHighlight}")
      return sHighlightsTableDataRow

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetAdditionalInformationTableBegin(self):
      sAdditionalInformationTableBegin = """<h3><font face="Arial" color="#242424">Additional information</font></h3>
<table width="100%" border="1" cellspacing="0" cellpadding="0" frame="box" rules="all" align="left">
"""
      return sAdditionalInformationTableBegin

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetAdditionalInformationTableDataRow(self, sHint=None):
      sAdditionalInformationTableDataRow = """<tr>
   <td bgcolor="#F5F5F5" width="100%" align="left" style="padding:6pt 6pt 6pt 6pt"><font face="Arial" color="#000000" size="-1">###HINT###</font></td>
</tr>
"""
      sAdditionalInformationTableDataRow = sAdditionalInformationTableDataRow.replace("###HINT###", f"{sHint}")
      return sAdditionalInformationTableDataRow

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetRequirementsTableBegin(self):
      sRequirementsTableBegin = """<h3><font face="Arial" color="#242424">Requirements</font></h3>
<table width="100%" border="1" cellspacing="0" cellpadding="0" frame="box" rules="all" align="left">
"""
      return sRequirementsTableBegin

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetRequirementsTableDataRow(self, sRequirement=None):
      sRequirementsTableDataRow = """<tr>
   <td bgcolor="#F5F5F5" width="100%" align="left" style="padding:6pt 6pt 6pt 6pt"><font face="Arial" color="#000000" size="-1">###REQUIREMENT###</font></td>
</tr>
"""
      sRequirementsTableDataRow = sRequirementsTableDataRow.replace("###REQUIREMENT###", f"{sRequirement}")
      return sRequirementsTableDataRow

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetRestrictionsTableBegin(self):
      sRestrictionsTableBegin = """<h3><font face="Arial" color="#242424">Restrictions</font></h3>
<table width="100%" border="1" cellspacing="0" cellpadding="0" frame="box" rules="all" align="left">
"""
      return sRestrictionsTableBegin

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetRestrictionsTableDataRow(self, sRestriction=None):
      sRestrictionsTableDataRow = """<tr>
   <td bgcolor="#FFEFD5" width="100%" align="left" style="padding:6pt 6pt 6pt 6pt"><font face="Arial" color="#000000" size="-1">###RESTRICTION###</font></td>
</tr>
"""
      sRestrictionsTableDataRow = sRestrictionsTableDataRow.replace("###RESTRICTION###", f"{sRestriction}")
      return sRestrictionsTableDataRow

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetChangesTableBegin(self):
      sChangesTableBegin = """<h3><font face="Arial" color="#242424">Changes</font></h3>
<table width="100%" border="1" cellspacing="0" cellpadding="0" frame="box" rules="all" align="left">
<colgroup>
   <col width="3%" span="1"/>
   <col width="16%" span="1"/>
   <col width="81%" span="1"/>
</colgroup>
"""
      return sChangesTableBegin

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetChangesTableDataRow(self, nCnt=0, sComponent=None, sChange=None):
      # padding: oben rechts unten links
      sChangesTableDataRow = """<tr>
   <td bgcolor="#F5F5F5" width="3%" valign="middle" align="center" style="padding:6pt 6pt 6pt 6pt"><font face="Arial" color="#FF0000" size="-1"><b>###CNT###</b></font></td>
   <td bgcolor="#F5F5F5" width="16%" valign="middle" align="left" style="padding:6pt 6pt 6pt 6pt"><font face="Arial" color="#000000" size="-1"><i>###COMPONENT###</i></font></td>
   <td bgcolor="#F5F5F5" width="81%" valign="middle" align="left" style="padding:6pt 6pt 6pt 6pt"><font face="Arial" color="#000000" size="-1">###CHANGE###</font></td>
</tr>
"""
      sChangesTableDataRow = sChangesTableDataRow.replace("###CNT###", f"{nCnt}")
      sChangesTableDataRow = sChangesTableDataRow.replace("###COMPONENT###", f"{sComponent}")
      sChangesTableDataRow = sChangesTableDataRow.replace("###CHANGE###", f"{sChange}")
      return sChangesTableDataRow

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetLinksTableBegin(self):
      sLinksTableBegin = """<h3><font face="Arial" color="#242424">Links</font></h3>
<table width="100%" border="1" cellspacing="0" cellpadding="0" frame="box" rules="all" align="left">
"""
      return sLinksTableBegin

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetLinksTableDataRow(self, sLinkAddress=None, sLinkName=None, sLinkHeadline=None):
      sLinksTableDataRow = """<tr>
   <td bgcolor="#F5F5F5" width="100%" align="left" style="padding:6pt 6pt 6pt 6pt"><font face="Arial" color="#000000" size="-1">###LINKHEADLINE###<a target="_blank" href="###LINKADDRESS###">###LINKNAME###</a></font></td>
</tr>
"""
      sLinksTableDataRow = sLinksTableDataRow.replace("###LINKADDRESS###", f"{sLinkAddress}")
      sLinksTableDataRow = sLinksTableDataRow.replace("###LINKNAME###", f"{sLinkName}")
      if sLinkHeadline is None:
         sLinksTableDataRow = sLinksTableDataRow.replace("###LINKHEADLINE###", "")
      else:
         sLinksTableDataRow = sLinksTableDataRow.replace("###LINKHEADLINE###", f"{sLinkHeadline}:&nbsp;&nbsp;") # <br/> # :&nbsp;&nbsp;
      return sLinksTableDataRow

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetChangeLogTableBegin(self):
      sChangelogTableBegin = """<h3><font face="Arial" color="#242424">Changelog</font></h3>
<table width="100%" border="1" cellspacing="0" cellpadding="0" frame="box" rules="all" align="left">
"""
      return sChangelogTableBegin

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def GetChangeLogTableDataRow(self, sChangeLog=None):
      sChangeLogTableDataRow = """<tr>
   <td bgcolor="#F5F5F5" width="100%" align="left" style="padding:6pt 6pt 6pt 6pt"><font face="Arial" color="#000000" size="-1">###CHANGELOG###</font></td>
</tr>
"""
      sChangeLogTableDataRow = sChangeLogTableDataRow.replace("###CHANGELOG###", f"{sChangeLog}")
      return sChangeLogTableDataRow

