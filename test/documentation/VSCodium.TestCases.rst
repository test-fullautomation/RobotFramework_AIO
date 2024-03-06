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

VSCodium test
=============

Self test cases of VSCodium extensions in the context of RobotFramework AIO.


Appearance
----------

On VSCodium start, the predefined workspace is opened

Workspace contains: main documentation, testcases folder with HelloWorld example, logfiles folder, tutorial

The main documentation is up to date


Executions
----------

Robot test file executed by Run button
=> Log files created at configured position

Python file executed by "Run Python File in Terminal"
=> VSCodium detects and selects proper Python interpreter


Persistence
===========

Log files can be written to hard disc

Predefined workspace can be saved; folders added to workspace, are persisted and available after restart


Editor
------

jsonp files have jsonp specific syntax highlighting

Robot Framework files (.robot, .resource) have Robot Framework specific syntax highlighting

Editor displays interface description of keywords provided by RobotFramework AIO components

Editor supports "Go to Definition" and "Go to References" for keywords provided by RobotFramework AIO components


Previews
--------

Previews work properly for files of following type:
rst, md, puml, pdf, png, jpeg, bmp

