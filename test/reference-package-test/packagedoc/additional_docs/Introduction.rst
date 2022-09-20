.. Copyright 2020-2022 Robert Bosch GmbH

.. Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

.. http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

The Python package ``ReferencePackage`` is a reference package to test the documentation tool chain.

This reference package contains a set of Python source files, files in rst format (= **r**\ e **s**\ tructured **t**\ ext)
and files in LaTeX format, that contain all layout elements that can be used for documentation:

* headlines
* links to files on external web servers
* imported pictures
* tables in rst format
* certain LaTeX styles (e.g. syntax highlighting for Robot Framework code and Python code, several admonitions)

The purpose is mostly to check manually - by simply taking a look at the content of the PDF output -, if all layout elements work properly.
If it is possible and makes sense, later some tests might be automated also.

The reference package is part of the tests of the build repository and can be found here:

   `reference-package-test <https://gitlab-apertispro.boschdevcloud.com/robotframework-aio/main/build/test/reference-package-test>`_

The output - the generated PDF documentation - can be found here:

   `ReferencePackage.pdf <https://gitlab-apertispro.boschdevcloud.com/robotframework-aio/main/build/test/reference-package-test/ReferencePackage/ReferencePackage.pdf>`_

