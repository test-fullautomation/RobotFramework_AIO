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
# robot2db-mock.py
#
# XC-CT/ECA3-Queckenstedt
#
# 26.09.2022
#
# --------------------------------------------------------------------------------------------------------------

"""Mock for database access; only prints the command line parameters to console (instead of writing something to
database).

This is to support the development of main script 'aio-test-trigger.py'.

To activate the database access this mock has to be replaced by the corresponding real application in the
test trigger configuration 'testtrigger_config.json'.
"""

import sys

print()
print("I am database access mock for tests of type ROBOT")
print()
for index, arg in enumerate(sys.argv):
   print(f"-> arg[{index}] = '{arg}'")
print()



