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
# compare_selftest_log.py
#
# XC-CT/ECA3-Queckenstedt
#
# --------------------------------------------------------------------------------------------------------------
#
import os, sys

import colorama as col

from PythonExtensionsCollection.String.CString import CString
from PythonExtensionsCollection.Comparison.CComparison import CComparison

col.init(autoreset=True)

COLBR = col.Style.BRIGHT + col.Fore.RED
COLBY = col.Style.BRIGHT + col.Fore.YELLOW
COLBG = col.Style.BRIGHT + col.Fore.GREEN

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------

sReferencePath = CString.NormalizePath(os.path.dirname(os.path.realpath(__file__)))

sFile_1      = CString.NormalizePath(sPath=r"./selftest_reference.log", sReferencePathAbs=sReferencePath)
sFile_2      = CString.NormalizePath(sPath=r"./selftest.log", sReferencePathAbs=sReferencePath)
sPatternFile = CString.NormalizePath(sPath=r"./selftest_pattern.txt", sReferencePathAbs=sReferencePath)

oComparison = CComparison()

bIdentical, bSuccess, sResult = oComparison.Compare(sFile_1, sFile_2, sPatternFile=sPatternFile)

print()
print()
print(f"=========== ReferencePath : {sReferencePath}")
print()
print(f"=========== File 1  : {sFile_1}")
print(f"=========== File 2  : {sFile_2}")
print(f"=========== Pattern : {sPatternFile}")
print()
print(f"=========== Identical : {bIdentical}")
print(f"=========== Success   : {bSuccess}")
print(f"=========== Result    : {sResult}")
print()
print()


# --------------------------------------------------------------------------------------------------------------

print(COLBG + "Comparison done")
print()
sys.exit(SUCCESS)

# --------------------------------------------------------------------------------------------------------------

