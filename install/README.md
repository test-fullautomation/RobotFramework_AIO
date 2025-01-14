<!---

	Copyright (c) 2020 Robert Bosch GmbH and its subsidiaries.
	This program and the accompanying materials are made available under
	the terms of the Bosch Internal Open Source License v4
	which accompanies this distribution, and is available at
	http://bios.intranet.bosch.com/bioslv4.txt

-->

# Robot Framework AIO Guideline For Using Install Script behind proxy  <!-- omit in toc -->

This is the guideline to use CNTLM for running install.sh behind proxy.


## Table of Contents  <!-- omit in toc -->

- [Getting Started](#getting-started)
  - [What is CNTLM](#what-is-CNTLM)
  - [Install CNTLM for Windows 10](#install-cntlm-for-windows-10)
    - [Download and install CNTLM for Windows 10](#download-and-install-cntlm-for-windows-10)
    - [Config CNTLM on Windows 10](#config-cntlm-on-windows-10)
    - [Run CNTLM on Windows 10](#run-cntlm-on-windows-10)
  - [Install CNTLM for Linux](#install-cntlm-for-linux)
    - [Install CNTLM by apt-get command](#install-cntlm-by-apt-get-command)
    - [Config CNTLM for Linux](#config-cntlm-for-linux)
    - [Run CNTLM for Linux](#run-cntlm-for-linux)
- [Extension in AIO packages](#install-extension-in-aio-package)
- [About](#about)
  - [Maintainers](#maintainers)
  - [Contributors](#contributors)

## Getting Started

### What is CNTLM
CNTLM is an authenticating HTTP proxy intended to help you break free from the chains of Microsoft proprietary world. It takes the address of your proxy or proxies (host1..N and port1..N) and opens a listening socket, forwarding each request to the parent proxy (moving in a circular list if the active parent stops working). Along the way, a connection to the parent is created a new and authenticated or, if available, previously cached connection is reused to achieve higher efficiency and faster responses

### Install CNTLM for Windows 10
#### Download and install CNTLM for Windows 10

Follow below steps to install CNTLM on Windows 10:

- Download CNTLM from http://CNTLM.sourceforge.net/
- After download run setup.exe installer

#### Config CNTLM on Windows 10
Afer installation, you have to locate the configuration file, in Windows it should be %PROGRAMFILES%\CNTLM\CNTLM.ini (usually C:\Program Files (x86)\CNTLM\CNTLM.ini).
```
$ cd  "C:\Program Files (x86)"\CNTLM\
$ notepad CNTLM.ini 
```
When you have found it, fire up your favorite editor (not a word processor) and open the file.

First a few rules, though - lines beginning with a hash, #, are comments: completely ignored. There is no required formatting and option names are case insensitive. Option values are parsed literally: a quote means a quote and is taken as part of the string, so do not quote, escape, etc. Anyway, you need to set these core options:
- `Username`: your domain/proxy account name
- `Domain`: the actual domain name
- `Proxy`: IP address (or ping-able hostname) of your proxy; if you use several alternative proxies or know of backup ones, use this option multiple times; if one stops working, CNTLM will move on to the next
- `Listen`: local port number which CNTLM should bind to; the default is OK, but remember you can’t have more than one application per port; you can use netstat to list used up ports (lines with LISTEN)

Next, we need to find out which NTLM dialect your proxy understands:
```
Username AGT2HC
Domain YOURCOMPANYDOMAIN
Auth        NTLMv2
PassNTLMv2  7552B795FA7BFE109476BCA3A31985D9

Proxy private_proxy.company.com:8080
NoProxy dev.company.com,*dev.company.com,.local, localhost, 127.0.0.*, 10.*, 172.17.*
Listen 3128
SOCKS5Proxy 3129
```

Save the configuration and run the following command in cmd or powershell (Change the CNTLM path if it is not "C:\Program Files (x86)\CNTLM" in your system); when asked, enter your proxy access password:
```
$ cd "C:\Program Files (x86)\CNTLM"
$ CNTLM.exe -H
```

The result should contain similar lines. Copy them and replace old password value in your `CNTLM.ini` file.
```
PassLM          7502437055AB9C450C0DBB09CCD7C37B
PassNT          6BCE995FA9D103DDF6529285D3B405AF
PassNTLMv2      6AFBB4E1C82456B4D5D6D66E207ADB65    # Only for user 'AGT2HC', domain 'APAC'
```
#### Run CNTLM on Windows 10

You can use CNTLM Start Menu shortcuts to start, stop and configure the application. CNTLM is installed as an auto-start service.
Or: Start -> Settings -> Control Panel -> Administrative Tools -> Services.

You can also use command line to start CNTLM (make sure to open cmd in `Administrator` mod):
```
$ cd  "C:\Program Files (x86)"\CNTLM\
$ net start CNTLM
```

If you need to check from a commandline try this:
```
$ sc query CNTLM
```
This command should return something like this, if CNTLM is running:
```
SERVICE_NAME: CNTLM
    TYPE               : 10  WIN32_OWN_PROCESS
    STATE              : 4  RUNNING
                            (STOPPABLE, NOT_PAUSABLE, IGNORES_SHUTDOWN)
    WIN32_EXIT_CODE    : 0  (0x0)
    SERVICE_EXIT_CODE  : 0  (0x0)
    CHECKPOINT         : 0x0
    WAIT_HINT          : 0x0
```
If stopped the result looks like this:
```
SERVICE_NAME: CNTLM
    TYPE               : 10  WIN32_OWN_PROCESS
    STATE              : 1  STOPPED
    WIN32_EXIT_CODE    : 0  (0x0)
    SERVICE_EXIT_CODE  : 0  (0x0)
    CHECKPOINT         : 0x0
    WAIT_HINT          : 0x0
```
If you need to stop the service.
```
$ net stop CNTLM
```

### Install CNTLM for Linux
#### Install CNTLM by apt-get command
Before you install CNTLM, it’s best to update and upgrade your machine, use below commands:
```
$ sudo apt-get update
$ sudo apt-get upgrade -y
```
Once the upgrade is complete, install CNTLM with the command:
```
$ sudo apt-get install cntlm -y
```
#### Config CNTLM for Linux
After installed CNTLM for Linux, use below command to get the config information:
```
$ sudo cntlm -H -d $DOMAIN -u $USERNAME
```
Where DOMAIN is the domain to be used and USER is the Windows user.
The output screen should look like this:
```
Password: 
PassLM          EC6398A6D87148B777E43632D37E2957
PassNT          AF5EEAE6B9272E4CE8BC9B1589FD33F3
PassNTLMv2      5E8128822C6FB537ACA3024C448E6B22    # Only for user 'USERNAME'
```
Copy theses hashed passwords (you’ll use one of them in the configuration file).
The default for Linux packages is /etc/cntlm.conf
```
$ sudo nano /etc/cntlm.conf
```
Within that file, you'll find four lines that need to be configured:
```
Username USERNAME
Domain DOMAIN
Proxy IP:PORT
Password PASSWORD
```
Where:
- `USERNAME`: your domain/proxy account name
- `DOMAIN`: the actual domain name
- `IP`: IP address (or ping-able hostname) of your proxy; if you use several alternative proxies or know of backup ones, use this option multiple times; if one stops working, CNTLM will move on to the next
- `PORT`: is the port used by the MS proxy server (most likely 8080)
- `PASSWORD`: is the hashed password you created for your Windows user.

Once you’ve finished your configurations, save and close the file.

#### Run CNTLM for Linux
Restart CNTLM with the command:
```
sudo systemctl restart cntlm
```
At this point, your machine is now capable of connecting to the MS NTLM proxy server. You will then need to configure apps or services to connect using the proxy. If you don’t want to configure the apps, one at a time, you can try this
```
nano ~/.bashrc
```
Paste the following to the bottom of that file: in linux
```
export http_proxy=http://127.0.0.1:3128
export https_proxy=http://127.0.0.1:3128
export socks_proxy=http://127.0.0.1:3129
```
Finally, issue the command:
```
. ~/.bashrc
```
## Install extension in AIO package
This section provides the info for installing Visual Studio Code extensions using a **install.sh** script. Refer: [issues 191](https://github.com/test-fullautomation/RobotFramework_AIO/issues/191#issuecomment-2031051647)

Below extensions can be installed through https://open-vsx.org/

| Publisher           | Name                | Version   |
|---------------------|---------------------|-----------|
| ms-python           | python              | 2024.10.0 |
| d-biehl             | robotcode           | 0.93.1    |
| xabikos             | JavaScriptSnippets  | 1.8.0     |
| redhat              | vscode-xml          | 0.18.1    |
| tomoki1207          | pdf                 | 1.2.2     |
| jebbs               | plantuml            | 2.17.5    |
| hediet              | vscode-drawio       | 1.6.6     |
| ms-python           | debugpy             | 2024.8.0  |


## About

### Maintainers

[Thomas Pollerspöck](mailto:Thomas.Pollerspoeck@de.bosch.com)

[Tran Duy Ngoan](mailto:Ngoan.TranDuy@vn.bosch.com)

[Tran Hoang Nguyen](mailto:Nguyen.TranHoang@vn.bosch.com)

### Contributors

[Thomas Pollerspöck](mailto:Thomas.Pollerspoeck@de.bosch.com)

[Tran Duy Ngoan](mailto:Ngoan.TranDuy@vn.bosch.com)

[Tran Hoang Nguyen](mailto:Nguyen.TranHoang@vn.bosch.com)

[Hua Van Thong](mailto:Thong.Huavan@vn.bosch.com)
