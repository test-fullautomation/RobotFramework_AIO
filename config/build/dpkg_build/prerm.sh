#!/bin/bash

rm -rf /opt/rfwaio/robotvscode/
rm -rf /opt/rfwaio/python39/
rm -rf /opt/rfwaio/devtools/

CURRENT_USER=${SUDO_USER}
if [ -z ${CURRENT_USER} ]; then
   CURRENT_USER=$(whoami)
fi
# When executing as root user $HOME can be /root
# Otherwises, /home/<user> should be used
if [ ${CURRENT_USER} != 'root' ]; then
   HOME=/home/${CURRENT_USER}
fi

rm -rf ${HOME}/.local/share/applications/robot.desktop
rm -rf ${HOME}/.local/share/applications/appium.desktop
rm -rf ${HOME}/.local/share/applications/appiumInspector.desktop