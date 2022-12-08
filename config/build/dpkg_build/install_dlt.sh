#!/bin/bash
DLTCONNECTOR_PATH="/opt/bosch/robfw/python39/install/lib/python3.9/site-packages/QConnectionDLTLibrary/tools/DLTConnector/linux/"

sudo dpkg -r DLTConnector
unalias DLTConnector
sudo dpkg -i "${DLTCONNECTOR_PATH}DLTConnector_v1.3.9.deb"

crontab -l | grep -v '@reboot /home/ugc1hc/Project/crontest/install_dlt.sh'  | crontab -
