#  Copyright 2020-2026 Robert Bosch GmbH
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
# currently experimental version / 28.10.2021
# **************************************************************************************************************

import pytest
import os.path
import time

def pytest_report_header(config):
    sInfo1 = """
================================================="""
    sInfo2 = """Testcases for Robotframework Python Extensions"""
    sInfo3 = """=================================================
"""
    return [sInfo1, sInfo2, sInfo3]

def pytest_sessionstart(session):
    session.results = dict()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_sessionfinish(session, exitstatus):

    outcome = yield

    sSessionInfoFile = "./SessionInfo_AllTests.txt"
    hSessionInfoFile = open(sSessionInfoFile, 'w')

    sFinalSummary = 40*"=" + " FINAL SUMMARY (all tests) " + 40*"="
    print()
    print()
    print(sFinalSummary)
    hSessionInfoFile.write(sFinalSummary + "\n")

    sInfo =  "* Session........: " + time.strftime('%Y.%m.%d - %H:%M:%S')
    print(sInfo)
    hSessionInfoFile.write(sInfo + "\n")

    sInfo = f"* Tests failed...: {session.testsfailed}"
    print(sInfo)
    hSessionInfoFile.write(sInfo + "\n")

    sInfo = f"* Tests collected: {session.testscollected}"
    print(sInfo)
    hSessionInfoFile.write(sInfo + "\n")

    sInfo = f"* Status code....: {exitstatus}"
    print(sInfo)
    hSessionInfoFile.write(sInfo + "\n")

    print()

    hSessionInfoFile.close()

# --------------------------------------------------------------------------------------------------------------
