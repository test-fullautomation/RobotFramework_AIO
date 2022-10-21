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
# //////////////////////////////////////////////////////////////////////////////////////////////////////////////

*** Settings ***

Documentation    test suite 105

Resource    ./imports/selftestimport.resource

Suite Setup      testsuites.testsuite_setup
Suite Teardown   testsuites.testsuite_teardown
Test Setup       testsuites.testcase_setup
Test Teardown    testsuites.testcase_teardown

*** Variables ***

${global_cmdline_var}    global_cmdline_var initial value

*** Test Cases ***

# **************************************************************************************************************

robot_105
    [Documentation]    robot_105

    log    Hello Test Trigger self test    console=yes

    log    global commandline variable (global_cmdline_var): ${global_cmdline_var}    console=yes


