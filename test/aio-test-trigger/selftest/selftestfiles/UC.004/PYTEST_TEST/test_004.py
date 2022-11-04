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
# test_004.py
#
# XC-CT/ECA3-Queckenstedt
#
# 20.10.2022
#
# --------------------------------------------------------------------------------------------------------------

# -- import standard Python modules
import pytest

# --------------------------------------------------------------------------------------------------------------
#TM***

class Test_004:
    """Test_004
    """

    # --------------------------------------------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "Description", ["test_004",]
    )
    def test_004(self, Description):
        """pytest 'test_004'"""
        assert 1 == 1

# --------------------------------------------------------------------------------------------------------------

