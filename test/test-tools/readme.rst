.. Copyright 2020-2024 Robert Bosch GmbH

.. Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

.. http://www.apache.org/licenses/LICENSE-2.0

.. Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


Code snippet generator
======================

GenSnippetsJPP.py

XC-HWP/ESW3-Queckenstedt

01.03.2024

**GenSnippetsJPP** generates JSONP code snippets and executes the **JsonPreprocessor** with these snippets.

The base of the JSONP code snippets generation is mainly a combination of code patterns and lists of expressions
that are combined under several conditions. The goal is to have *stuff* to stimulate the **JsonPreprocessor**.

The snippets together with the answers from **JsonPreprocessor** are written to a log file in text format (to support diffs)
and to a report file in HTML format (to support better readibility by colored text).

Currently **GenSnippetsJPP** is a one-file tool; no separate configuration files, no command line parameter.

All code pattern are defined directly within class 'CSnippets()'.

Output files are written to script folder.

The purpose behind this script is not to have an automated test. No valuation of results is done.
It's on the user to interprete the results. **GenSnippetsJPP** only produces these results.

