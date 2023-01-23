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
# --------------------------------------------------------------------------------------------------------------
#
# test_tutorial.py
#
# XC-CT/ECA3-Queckenstedt
#
# 23.01.2023
#
# --------------------------------------------------------------------------------------------------------------

# -- import standard Python modules
import os, sys, shlex, subprocess, pytest

from PythonExtensionsCollection.String.CString import CString

# --------------------------------------------------------------------------------------------------------------
#TM***

class Test_tutorial:
   """Test_tutorial
   """

   # --------------------------------------------------------------------------------------------------------------

   @pytest.mark.parametrize(
      "Description", ["test_tutorial",]
   )
   def test_tutorial(self, Description):
      """pytest 'test_tutorial'"""
      sThisScriptPath = os.path.dirname(CString.NormalizePath(__file__))
      sPython         = CString.NormalizePath(sys.executable)
      sTutorialTest   = CString.NormalizePath("../tutorial-test.py", sReferencePathAbs=sThisScriptPath)
      print(f"(debug) sTutorialTest: {sTutorialTest}")
      listCmdLineParts = []
      listCmdLineParts.append(f"\"{sPython}\"")
      listCmdLineParts.append(f"\"{sTutorialTest}\"")
      sCmdLine = " ".join(listCmdLineParts)
      print(f"(debug) sCmdLine: {sCmdLine}")
      listCmdLineParts = shlex.split(sCmdLine)
      nReturn = subprocess.call(listCmdLineParts)
      assert nReturn == 0

# --------------------------------------------------------------------------------------------------------------

