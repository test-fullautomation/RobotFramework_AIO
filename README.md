<!---

	Copyright (c) 2020 Robert Bosch GmbH and its subsidiaries.
	This program and the accompanying materials are made available under
	the terms of the Bosch Internal Open Source License v4
	which accompanies this distribution, and is available at
	http://bios.intranet.bosch.com/bioslv4.txt

-->

# Robot Framework AIO  <!-- omit in toc -->

This respository holds the build tooling for a new Robot Framework AIO (All In One) setup for Windows (and later Linux).


## Table of Contents  <!-- omit in toc -->

- [Getting Started](#getting-started)
  - [Manual build](#manual-build)
	 - [Preconditions](#preconditions)
	 - [Execute build scripts](#execute-build-scripts)
  - [Github Actions](#github-actions)
    - [Workflow](#workflow)
    - [Runners](#runners)
- [Contribution](#contribution)
- [Feedback](#feedback)
- [About](#about)
  - [Maintainers](#maintainers)
  - [Contributors](#contributors)
  - [3rd Party Licenses](#3rd-party-licenses)
  - [License](#license)

## Getting Started

### Manual build
Currently, RobotFramework AIO is supported to build with both **Windows** and **Linux** environments.

#### Preconditions
When building RobotFramework AIO package, the document is also generated with [GenPackageDoc](https://github.com/test-fullautomation/python-genpackagedoc)
using [TeX Live](https://www.tug.org/texlive/) tool.

So, Tex Live should be installed first.
The full collection is recommended when installing texlive to avoid issue when generating document but it will take long time for the installation. 

In case the full collection installation is not possible, at least 2 collections `texlive-latex-extra` and `texlive-fonts-recommended` should be installed together with the basic package.

#### Execute build scripts
Clone this [RobotFramework_AIO](https://github.com/test-fullautomation/RobotFramework_AIO) repository first
```
git clone https://github.com/test-fullautomation/RobotFramework_AIO.git
```

Then follow below steps for building process:

1. Clone all related repositories with is configured `config/repositories/repositories.conf` file
	```
	./cloneall
	```

2. Download and install python (include dependencies which are defined in `install/python_requirements.txt`), vscode (include the extensions which defined in `install/vscode_requirement.csv` or stored as *.vsix file under `config/robotvscode/extensions` folder) and pandoc
	```
	./install/install.sh
	```
	>Note: In case you are working behind the proxy, [cntlm authentication proxy](https://sourceforge.net/projects/cntlm/) should be installed and started first then
	execute the `install.sh` with `--use-cntlm` argument as below command:
	
	```
	./install/install.sh --use-cntlm
	```

3. Build the installer package
	```
	./build
	```

The new generated RobotFramework AIO setup can found under `Output/` folder on
Windows and `output_lx` on Linux machine.

### Github Actions

#### Workflow
The workflow to build RobotFramework AIO package is available in Github Actions
os this repo as below:

[![Build RobotFramework AIO packages](https://github.com/test-fullautomation/RobotFramework_AIO/actions/workflows/build_robotframework_aio.yml/badge.svg)](https://github.com/test-fullautomation/RobotFramework_AIO/actions/workflows/build_robotframework_aio.yml)

There are 2 build jobs for both environment **Windows** and **Linux**, 
the building jobs contains following main steps:
- `Install dependencies`: install dependency packages for build job
- `Clone repositories` : clone all related repos to build runner
- `Install` : install python, vscode and their dependencies
- `Build` : build the package installer
- `Upload built package` : save the built package as workflow artifactory 

#### Runners
Currently, there are 2 available runners (GitHub-hosted) for build pipeline:
- Windows runner: [Windows Server 2022](https://github.com/actions/runner-images/blob/main/images/win/Windows2022-Readme.md) with label `windows-latest` for Windows job.
- Ubuntu runner: [Ubuntu 20.04](https://github.com/actions/runner-images/blob/main/images/linux/Ubuntu2004-Readme.md) with label `ubuntu-latest` for Linux job.

## Contribution

We are always searching support and you are cordially invited to help to improve Robot Framework AIO.

## Feedback

To give us a feedback, you can send an email to [Thomas
Pollerspöck](mailto:Thomas.Pollerspoeck@de.bosch.com)

In case you want to report a bug or request any interesting feature,
please don\'t hesitate to raise a ticket


## About

### Maintainers

[Thomas Pollerspöck](mailto:Thomas.Pollerspoeck@de.bosch.com)

[Tran Duy Ngoan](mailto:Ngoan.TranDuy@vn.bosch.com)

[Tran Hoang Nguyen](mailto:Nguyen.TranHoang@vn.bosch.com)

### Contributors

[Holger Queckenstedt](mailto:Holger.Queckenstedt@de.bosch.com)

[Nguyen Huynh Tri Cuong](mailto:Cuong.NguyenHuynhTri@vn.bosch.com)

[Mai Dinh Nam Son](mailto:Son.MaiDinhNam@vn.bosch.com)


### 3rd Party Licenses

Please refer to

* ./InnoSetup5.5.1/licence.txt

### License

Copyright 2020-2022 Robert Bosch GmbH

Licensed under the Apache License, Version 2.0 (the \"License\"); you
may not use this file except in compliance with the License. You may
obtain a copy of the License at

> [![License: Apache
> v2](https://img.shields.io/pypi/l/robotframework.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an \"AS IS\" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.