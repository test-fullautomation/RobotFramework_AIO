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
# ReferenceModule_2py
#
# XC-CT/ECA3-Queckenstedt
#
# 19.09.2022
#
# --------------------------------------------------------------------------------------------------------------

"""
Python module containing all methods to generate tex sources.
"""

# --------------------------------------------------------------------------------------------------------------

import os, sys, time, platform

SUCCESS = 0
ERROR   = 1

# --------------------------------------------------------------------------------------------------------------
#TM***

def AmbiguousFunction(self):
   """ReferenceModule_2.py / AmbiguousFunction
   """
   bSuccess = True
   sResult  = "passed"
   return bSuccess, sResult

# --------------------------------------------------------------------------------------------------------------
#TM***

class CReference_2_A():
   """ReferenceModule_2.py / CReference_2_A
   """

   def __init__(self):
      """ReferenceModule_2.py / CReference_2_A / __init__
      """
      pass

   def __del__(self):
      """ReferenceModule_2py / CReference_2_A / __del__
      """
      pass

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def Method_1(self):
      """ReferenceModule_2.py / CReference_2_A / Method_1
      """
      bSuccess = True
      sResult  = "passed"
      return bSuccess, sResult

   def Method_2(self):
      """ReferenceModule_2.py / CReference_2_A / Method_2
      """
      bSuccess = True
      sResult  = "passed"
      return bSuccess, sResult

   def Method_3(self):
      """ReferenceModule_2.py / CReference_2_A / Method_3
      """
      bSuccess = True
      sResult  = "passed"
      return bSuccess, sResult

   # --------------------------------------------------------------------------------------------------------------

# eof class CReference_2_A():

# --------------------------------------------------------------------------------------------------------------

class CReference_2_B():
   """ReferenceModule_2.py / CReference_2_B
   """

   def __init__(self):
      """ReferenceModule_2.py / CReference_2_B / __init__
      """
      pass

   def __del__(self):
      """ReferenceModule_2.py / CReference_2_B / __del__
      """
      pass

   # --------------------------------------------------------------------------------------------------------------
   #TM***

   def Method_1(self):
      """ReferenceModule_2.py / CReference_2_B / Method_1
      """
      bSuccess = True
      sResult  = "passed"
      return bSuccess, sResult

   def Method_2(self):
      """ReferenceModule_2.py / CReference_2_B / Method_2
      """
      bSuccess = True
      sResult  = "passed"
      return bSuccess, sResult

   def Method_3(self):
      """ReferenceModule_2.py / CReference_2_B / Method_3
      """
      bSuccess = True
      sResult  = "passed"
      return bSuccess, sResult

   # --------------------------------------------------------------------------------------------------------------

# eof class CReference_2_B():

# --------------------------------------------------------------------------------------------------------------
