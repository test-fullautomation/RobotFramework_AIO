# **************************************************************************************************************
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
# **************************************************************************************************************
#
# exercise-pg-2.robot
#
# --------------------------------------------------------------------------------------------------------------

*** Settings ***

Library    RobotFramework_TestsuitesManagement    WITH NAME    tm
Library    RobotframeworkExtensions.Collection    WITH NAME    rf.extensions

Suite Setup    tm.testsuite_setup    ./config/exercise-pg_variants.json

Metadata    version_hw    metadata_version_hw
Metadata    my_test_local_metadata    my_test_local_metadata_value

*** Test Cases ***
Test Case exercise-pg-2
   [documentation]    exercise-pg-2
   Log    teststring_common : ${teststring_common} (exercise-pg-2.robot)    console=yes
   Log    teststring_variant : ${teststring_variant} (exercise-pg-2.robot)    console=yes
   Log    teststring_bench : ${teststring_bench} (exercise-pg-2.robot)    console=yes

   rf.extensions.pretty_print    ${SUITE METADATA}


