# **************************************************************************************************************
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
# **************************************************************************************************************
#
# exercise-pg-ts.robot
#
# --------------------------------------------------------------------------------------------------------------

*** Settings ***

Metadata    metadata-pg-ts    metadata-pg-ts-value-top-level-robot-file

Test Setup     tm.testcase_setup
Test Teardown    tm.testcase_teardown


*** Test Cases ***
Test Case exercise-pg-ts
    [documentation]    exercise-pg-ts
    Log    teststring_common : ${teststring_common} (exercise-pg-ts.robot)   console=yes
    Log    teststring_variant : ${teststring_variant} (exercise-pg-ts.robot)    console=yes
    Log    teststring_bench : ${teststring_bench} (exercise-pg-ts.robot)    console=yes

