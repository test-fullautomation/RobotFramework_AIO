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
# CJsonTools.py
#
# Tran Duy Ngoan
#
# 19.04.2024
#
# --------------------------------------------------------------------------------------------------------------
class CJsonTools():
   """The collection of json tools
   """

   @classmethod
   def get_failed_json_doc(cls, jsonDecodeError=None, areaBeforePosition=50, areaAfterPosition=20, oneLine=True):
      failedJsonDoc = None
      if jsonDecodeError is None:
         return failedJsonDoc
      try:
         jsonDoc = jsonDecodeError.doc
      except:
         # 'jsonDecodeError' seems not to be a JSON exception object ('doc' not available)
         return failedJsonDoc
      jsonDocSize     = len(jsonDoc)
      positionOfError = jsonDecodeError.pos
      if areaBeforePosition > positionOfError:
         areaBeforePosition = positionOfError
      if areaAfterPosition > (jsonDocSize - positionOfError):
         areaAfterPosition = jsonDocSize - positionOfError
      failedJsonDoc = jsonDoc[positionOfError-areaBeforePosition:positionOfError+areaAfterPosition]
      failedJsonDoc = f"... {failedJsonDoc} ..."
      if oneLine is True:
         failedJsonDoc = failedJsonDoc.replace("\n", r"\n")
      return failedJsonDoc