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
# CHTMLMail.py
#
# XC-HWP/ESW3-Queckenstedt
#
# 02.01.2024
#
# --------------------------------------------------------------------------------------------------------------

import os, sys, platform, shlex, subprocess, json, argparse
import colorama as col
import pypandoc

from email.mime.text import MIMEText
import smtplib

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.Utils.CUtils import *

col.init(autoreset=True)

COLBR = col.Style.BRIGHT + col.Fore.RED
COLBG = col.Style.BRIGHT + col.Fore.GREEN
COLBY = col.Style.BRIGHT + col.Fore.YELLOW

# --------------------------------------------------------------------------------------------------------------

def printfailure(sMsg, prefix=None):
   if prefix is None:
      sMsg = COLBR + f"{sMsg}!\n\n"
   else:
      sMsg = COLBR + f"{prefix}:\n{sMsg}!\n\n"
   sys.stderr.write(sMsg)

# --------------------------------------------------------------------------------------------------------------

class CHTMLMail():

   def __init__(self, oConfig=None):

      sMethod = "CHTMLMail.__init__"

      if oConfig is None:
         raise Exception(CString.FormatResult(sMethod, None, "oConfig is None"))

      self.__oConfig = oConfig

   def __del__(self):
      pass


   def GenHTMLMail(self, listLinesHTML=None):

      sMethod = "GenHTMLMail"

      if listLinesHTML is None:
         bSuccess = None
         sResult  = CString.FormatResult(sMethod=sMethod, bSuccess=bSuccess, sResult="listLinesHTML is None")
         return bSuccess, sResult

      MAILADDRESS = self.__oConfig.Get('MAILADDRESS')
      if MAILADDRESS is None:
         # without email address no email
         bSuccess = True
         sResult  = "Email address not provided. Email generation skipped."
         return bSuccess, sResult

      # -- get some information to be used in email
      PACKAGE_CONTEXT     = self.__oConfig.Get('PACKAGE_CONTEXT')
      bundle_name         = PACKAGE_CONTEXT['bundle_name']
      bundle_version      = PACKAGE_CONTEXT['bundle_version']
      bundle_version_date = PACKAGE_CONTEXT['bundle_version_date']

      print(COLBY + f"Generating release email - with initial sender and recipient is: '{MAILADDRESS}'")
      print()

      sMailHtml = "\n".join(listLinesHTML)

      mimeMessage = None
      try:
         mimeMessage = MIMEText(sMailHtml, 'html') # 'html|plain'
      except Exception as reason:
         bSuccess = None
         sResult  = CString.FormatResult(sMethod=sMethod, bSuccess=bSuccess, sResult=str(reason))
         return bSuccess, sResult

      sSubject   = f"{bundle_name} release {bundle_version} / {bundle_version_date}"
      sSender    = MAILADDRESS
      sRecipient = MAILADDRESS

      if mimeMessage is not None:
         try:
            mimeMessage['Subject'] = sSubject
            mimeMessage['From']    = sSender
            mimeMessage['To']      = sRecipient
         except Exception as reason:
            bSuccess = None
            sResult  = CString.FormatResult(sMethod=sMethod, bSuccess=bSuccess, sResult=str(reason))
            return bSuccess, sResult

         oSMTP = None
         try:
            oSMTP = smtplib.SMTP(host='rb-smtp-int.bosch.com',port=25)
            oSMTP.sendmail(sSender, sRecipient, mimeMessage.as_string())
         except Exception as reason:
            if oSMTP is not None:
               oSMTP.quit()
            del oSMTP
            bSuccess = None
            sResult  = CString.FormatResult(sMethod=sMethod, bSuccess=bSuccess, sResult=str(reason))
            return bSuccess, sResult

         if oSMTP is not None:
            oSMTP.quit()

         del oSMTP

      # eof if mimeMessage is not None:

      del mimeMessage

      bSuccess = True
      sResult  = f"Release email '{sSubject}' generated and sent"

      return bSuccess, sResult

   # eof def GenHTMLMail(self):

# eof class CHTMLMail():
