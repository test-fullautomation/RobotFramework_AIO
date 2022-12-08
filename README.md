<!---

	Copyright (c) 2020 Robert Bosch GmbH and its subsidiaries.
	This program and the accompanying materials are made available under
	the terms of the Bosch Internal Open Source License v4
	which accompanies this distribution, and is available at
	http://bios.intranet.bosch.com/bioslv4.txt

-->

# Robot Framework AIO  <!-- omit in toc -->

[![License: BIOSL v4](http://bios.intranet.bosch.com/bioslv4-badge.svg)](#license)

This respository holds the build tooling for a new Robot Framework AIO (All In One) setup for Windows (and later Linux).


## Table of Contents  <!-- omit in toc -->

- [Getting Started](#getting-started)
  - [Manual build](#manual-build)
  - [Gitlab CI/CD pipeline](#auto-build)
    - [Preconditions](#preconditions)
    - [Jobs](#jobs)
    - [Runners](#runners)
- [Contribution](#contribution-guidelines)
- [Bug/Feature implementation/Support Tracking](#tracking)
- [Feedback](#feedback)
- [About](#about)
  - [Maintainers](#maintainers)
  - [Contributors](#contributors)
  - [3rd Party Licenses](#3rd-party-licenses)
  - [Used Encryption](#used-encryption)
  - [License](#license)

## Getting Started <a name="getting-started"></a>

### Manual build <a name="manual-build"></a>
Clone this build repository with git bash then follow below steps for building process:

1. Clone all related repositories with is configured `config/repositories/repositories.conf` file
	```
	./cloneall		#for both Windows and Linux
	```
	>Note: git bash will use the existing authentication to Gitlab, Github, Soco for cloning resources.

	>In case the authentication(s) is not existing or access to restricted repo(s), the authentication (user & password/PAT) should be provided as environment variables. Please refer [Preconditions in Gitlab CI/CD pipeline](#preconditions).

2. Download and install python (include dependencies which are defined in `wget/python_requirements.txt`), vscode (include the extensions which defined in `wget/vscode_requirement.csv` or stored as *.vsix file under `config/robotvscode/extensions` folder) and pandoc
	```
	./wget/install_via_cntlm.sh		#for Windows
	```
	or 
	```
	./wget/install_linux_ntlm.sh	#for Linux
	```
	>Note: **cntlm should be started before execute above command**
3. Setup and install python package from cloned repos
4. Build the installer package
	```
	./build				#for Windows
	```
	or
	```
	./build_linux		#for Linux
	```
The new generated Robot Framework AIO setup can found under `output/` folder

### Gitlab CI/CD pipeline <a name="auto-build"></a>
#### Preconditions <a name="preconditions"></a>
Below environment variables should be set (**Settings > CI/CD > Variables**) for:
- Authentication to Gitlab (if required):
	- `$GITLAB_BOT_USERNAME`
	- `$GITLAB_BOT_PASSWORD`
- Authentication to Github (if required):
	- `$GITHUB_BOT_USERNAME`
	- `$GITHUB_BOT_PASSWORD`
- Authentication to Socialcoding (if required):
	- `$SOCO_BOT_USERNAME`
	- `$SOCO_BOT_PASSWORD`

#### Jobs <a name="jobs"></a>
Regarding to the automatical build with GitLab CI/CD, the building pipeline contains following stages:
- `mirror`: mirror latest sourcecode from other source version control (Soco, Github)
- `clone` : clone all repos to building runner
- `install` : install python, vscode and their dependencies
- `build` : build the package installer
- `test` : run selftest

#### Runners <a name="runners"></a>
There are 2 type runners for build pipeline:
- Windows runner with tag `windows` for Windows jobs.
- Apertis docker image which run on the shared runner with tag `internal` for Linux jobs.
## Bug/Feature implementation/Support Tracking<a name="tracking"></a>

Robot Framework AIO Project
https://rb-tracker.bosch.com/tracker01/secure/RapidBoard.jspa?rapidView=13300&view=planning.nodetail&epics=visible

## Contribution <a name="contribution-guidelines"></a>

We are always searching support and you are cordially invited to help to improve Robot Framework AIO.

## Feedback <a name="feedback"></a>

Please feel free to give any feedback to us via

Email to: [Robot Framework Support Group](mailto:RobotFrameworkSupportGroup@bcn.bosch.com)

Community: [RobotFramework AIO community](https://connect.bosch.com/communities/community/ROBFW)


## About <a name="about"></a>

### Maintainers <a name="maintainers"></a>

[Thomas Pollersp&ouml;ck](https://connect.bosch.com/profiles/html/profileView.do?userid=CF5E6A27-460A-4D81-A3B2-6F1B66BA6812)

### Contributors <a name="contributors"></a>
[Nguyen Huynh Tri **Cuong**](https://connect.bosch.com/profiles/html/profileView.do?userid=C022F16C-EC4D-4701-BE51-5E743AAA9031#&tabinst=Updates)

[Mai Dinh Nam **Son**](https://connect.bosch.com/profiles/html/profileView.do?userid=CA9FA391-8728-485D-A8B7-2DD840A777D4#&tabinst=Updates)

[Tran Duy **Ngoan**](https://connect.bosch.com/profiles/html/profileView.do?key=8b91aa39-e896-4de7-bee1-32e5e03b5350#&tabinst=Updates)

[**Nguyen** Tran Hoan](https://connect.bosch.com/profiles/html/profileView.do?key=e4f7910a-e3c8-48c7-a6bb-8547060ee2eb#&tabinst=Updates)

### 3rd Party Licenses <a name="3rd-party-licenses"></a>

Please refer to

* ./InnoSetup5.5.1/licence.txt

### Used Encryption <a name="used-encryption"></a>

No encryption is used in this repository.

### License <a name="license"></a>

[![License: BIOSL v4](http://bios.intranet.bosch.com/bioslv4-badge.svg)](#license)

> Copyright (c) 2020 Robert Bosch GmbH and its subsidiaries.
> This program and the accompanying materials are made available under
> the terms of the Bosch Internal Open Source License v4
> which accompanies this distribution, and is available at
> http://bios.intranet.bosch.com/bioslv4.txt

<!---

	Copyright (c) 2020 Robert Bosch GmbH and its subsidiaries.
	This program and the accompanying materials are made available under
	the terms of the Bosch Internal Open Source License v4
	which accompanies this distribution, and is available at
	http://bios.intranet.bosch.com/bioslv4.txt

-->

