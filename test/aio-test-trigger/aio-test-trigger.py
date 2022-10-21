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
# aio-test-trigger.py
#
# XC-CT/ECA3-Queckenstedt
#
# --------------------------------------------------------------------------------------------------------------
#
# 21.10.2022
#
# --------------------------------------------------------------------------------------------------------------

import os, sys

import colorama as col

from libs.CTestTriggerConfig import CTestTriggerConfig
from libs.CTestTrigger import CTestTrigger

col.init(autoreset=True)

COLBR = col.Style.BRIGHT + col.Fore.RED
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLBG = col.Style.BRIGHT + col.Fore.GREEN

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

def printerror(sMsg):
   sys.stderr.write(COLBR + f"{sMsg}!\n")

# --------------------------------------------------------------------------------------------------------------

# -- setting up the test trigger configuration (relative to the path of this script)
oRepositoryConfig = None
try:
   oTestTriggerConfig = CTestTriggerConfig(os.path.abspath(sys.argv[0]))
except Exception as ex:
   print()
   printerror(str(ex))
   print()
   sys.exit(ERROR)

# -- setting up the test trigger
try:
   oTestTrigger = CTestTrigger(oTestTriggerConfig)
except Exception as ex:
   print()
   printerror(str(ex))
   print()
   sys.exit(ERROR)

nReturn, bSuccess, sResult = oTestTrigger.Trigger()
if bSuccess is None:
   print()
   printerror(sResult)
   nReturn = ERROR
elif bSuccess is False:
   print()
   printerror(sResult)
elif bSuccess is True:
   print()
   print(COLBG + sResult)
else:
   print()
   printerror("Internal aio-test-trigger error")
   nReturn = ERROR

print()
sys.exit(nReturn)

# --------------------------------------------------------------------------------------------------------------

