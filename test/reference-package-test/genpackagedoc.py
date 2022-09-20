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
# genpackagedoc.py
#
# XC-CT/ECA3-Queckenstedt
#
# --------------------------------------------------------------------------------------------------------------
#
# 30.05.2022
#
# --------------------------------------------------------------------------------------------------------------

import os, sys

import colorama as col

from config.CRepositoryConfig import CRepositoryConfig # providing repository and environment specific information
from GenPackageDoc.CPackageDocConfig import CPackageDocConfig
from GenPackageDoc.CDocBuilder import CDocBuilder

col.init(autoreset=True)

COLBR = col.Style.BRIGHT + col.Fore.RED
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLBG = col.Style.BRIGHT + col.Fore.GREEN

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

def printerror(sMsg):
    sys.stderr.write(COLBR + f"Error: {sMsg}!\n")

def printexception(sMsg):
    sys.stderr.write(COLBR + f"Exception: {sMsg}!\n")

# --------------------------------------------------------------------------------------------------------------

# -- setting up the repository configuration (relative to the path of this script)
oRepositoryConfig = None
try:
    oRepositoryConfig = CRepositoryConfig(os.path.abspath(sys.argv[0]))
except Exception as ex:
    print()
    printexception(str(ex))
    print()
    sys.exit(ERROR)

# -- setting up the GenPackageDoc configuration
oGenPackageDocConfig = None
try:
    oPackageDocConfig = CPackageDocConfig(oRepositoryConfig)
except Exception as ex:
    print()
    printexception(str(ex))
    print()
    sys.exit(ERROR)

# -- setting up and calling the doc builder
try:
    oDocBuilder = CDocBuilder(oPackageDocConfig)
except Exception as ex:
    print()
    printexception(str(ex))
    print()
    sys.exit(ERROR)

bSuccess, sResult = oDocBuilder.Build()
if bSuccess is None:
    print()
    printexception(sResult)
    print()
    sys.exit(ERROR)
elif bSuccess is False:
    print()
    printerror(sResult)
    print()
    sys.exit(ERROR)
else:
   print(COLBY + sResult)
   print()
   print(COLBG + "genpackagedoc done")
   print()
   sys.exit(SUCCESS)

# --------------------------------------------------------------------------------------------------------------

