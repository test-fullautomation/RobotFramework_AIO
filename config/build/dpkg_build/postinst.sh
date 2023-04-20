#!/bin/bash
# Script to setup enviroment for tml on Linux
# This should run 1 time when postinst

#set -x

echo "Creating/Updating RobotFramework AIO runtime environment"
echo "----------------------------------------"

CURRENT_USER=${SUDO_USER}
if [ -z ${CURRENT_USER} ]; then
   CURRENT_USER=$(whoami)
fi
# When executing as root user $HOME can be /root
# Otherwises, /home/<user> should be used
if [ ${CURRENT_USER} != 'root' ]; then
   HOME=/home/${CURRENT_USER}
fi
DLTCONNECTOR_PATH="/opt/rfwaio/python39/install/lib/python3.9/site-packages/QConnectionDLTLibrary/tools/DLTConnector/linux/"
DLTCONNECTOR_NAME="DLTConnector_v1.3.9.deb"

#in osd4 group name is the user name.
#in osd5 group name is "domain users". Therefore
#look if a group wi th the user name exists, if not
#then we assume that we are on OSD5
sGROUP=$(id -G)
if ! getent group "${sGROUP}" | grep "${sGROUP}" ; then
   sGROUP='domain users'
   echo -e "Assuming OSD5 and using group 'domain users' as user group for private files"
else
   echo -e "Assuming OSD4 and using group ${sGROUP} as user group for private files"
fi

COL_GREEN='\033[0;32m'
COL_ORANGE='\033[0;33m'
COL_BLUE='\033[0;34m'
COL_RED='\033[1;31m'
COL_RESET='\033[0m' # No Color

MSG_INFO="${COL_GREEN}[INFO]${COL_RESET}"
MSG_DONE="${COL_ORANGE}[DONE]${COL_RESET}"
MSG_ERR="${COL_RED}[ERR]${COL_RESET} "


chown -R "${CURRENT_USER}:${sGROUP}" /opt/rfwaio/robotvscode/data
chmod -R 0775 /opt/rfwaio/robotvscode/data
echo -e "${MSG_DONE} Updated permission for /opt/rfwaio/robotvscode/data"
   
if [ ! -d "${HOME}/RobotTest" ]; then
   
   mkdir -p ${HOME}/RobotTest/logfiles
   #mkdir -p ${HOME}/RobotTest/ctrlfiles
   mkdir -p ${HOME}/RobotTest/localconfig
   mkdir -p ${HOME}/RobotTest/testcases
   mkdir -p ${HOME}/RobotTest/tutorial
   #mkdir -p ${HOME}/RobotTest/workspace
   
   #
   # Create VS Code Workspacce
   #
   ##############################################################################
   cp -R -a /opt/rfwaio/robotvscode/RobotTest/testcases/. ${HOME}/RobotTest/testcases
   cp -R -a /opt/rfwaio/robotvscode/RobotTest/tutorial/. ${HOME}/RobotTest/tutorial
   cp -R -a /opt/rfwaio/robotvscode/RobotTest/documentation/. ${HOME}/RobotTest/documentation
   
   
   #
   # assure access rights to files in ~/ROBFW
   #
   ###############################################################################                          
   chown "${CURRENT_USER}:${sGROUP}" ${HOME}/RobotTest
   chown -R "${CURRENT_USER}:${sGROUP}" ${HOME}/RobotTest/logfiles
   chown -R "${CURRENT_USER}:${sGROUP}" ${HOME}/RobotTest/localconfig
   chown -R "${CURRENT_USER}:${sGROUP}" ${HOME}/RobotTest/testcases
   chown -R "${CURRENT_USER}:${sGROUP}" ${HOME}/RobotTest/tutorial
   chown -R "${CURRENT_USER}:${sGROUP}" ${HOME}/RobotTest/documentation
   chmod 0775 ${HOME}/RobotTest
   echo -e "${MSG_DONE} Creating initial workspace in ~/RobotTest"
else
   #
   # update tutorial
   #
   ###########################################################################
   if [ -d ${HOME}/RobotTest/tutorial ]; then
      rm -rf ${HOME}/RobotTest/tutorial/*
   fi
   cp -R -a /opt/rfwaio/robotvscode/RobotTest/tutorial/. ${HOME}/RobotTest/tutorial
   chown -R "${CURRENT_USER}:${sGROUP}" ${HOME}/RobotTest/tutorial

   echo -e "${MSG_DONE} Found workspace in ~/RobotTest. Updated only tutorial."
fi
   cp -R -a -n /opt/rfwaio/robotvscode/RobotTest/testcases/RobotTest.code-workspace ${HOME}/RobotTest/testcases
   mkdir -p ${HOME}/RobotTest/documentation
   cp -R -a -n /opt/rfwaio/robotvscode/RobotTest/documentation/* ${HOME}/RobotTest/documentation

# Set schedule for installing DLTConnector (will active in future)
#
############################################################################### 
#if [ -d "${DLTCONNECTOR_PATH}" ]; then
#   echo "@reboot /opt/rfwaio/linux/install_dlt.sh" >> tmpfile 
#   crontab -u ${SUDO_USER} tmpfile 
#   rm tmpfile
#fi

# configure Unitiy Launchers
#
############################################################################### 
echo -e "${MSG_DONE} Creating/Updating Unity Launchers" 
cp /opt/rfwaio/linux/robot.desktop ${HOME}/.local/share/applications
chown -R "${CURRENT_USER}:${sGROUP}" /home/${CURRENT_USER}/.local/share/applications/robot.desktop

#
# configure login/non login shells
#
###############################################################################    

# Delete old version environment setup
if grep -q "/opt/bosch/robfw/linux/set_robotenv.sh" ${HOME}/.bashrc; then
   sed -i '/\/opt\/bosch\/robfw\/linux\/set_robotenv.sh/d' ~/.bashrc
fi

if grep -q "/opt/bosch/robfw/linux/set_robotenv.sh" ${HOME}/.profile; then
   sed -i '/\/opt\/bosch\/robfw\/linux\/set_robotenv.sh/d' ~/.profile
fi

if grep -q "/opt/rfwaio/linux/set_robotenv.sh" ${HOME}/.bashrc; then
   echo -e "${MSG_INFO} Robot configuration for .bashrc found, nothing to do. "
else 
   echo -e "${MSG_DONE} Add Robot configuration to .bashrc"
   echo "#configure environment for Robot" >> ${HOME}/.bashrc
   echo ". /opt/rfwaio/linux/set_robotenv.sh || export rfwaio_set_env=-1" >> ${HOME}/.bashrc
fi

if grep -q "/opt/rfwaio/linux/set_robotenv.sh" ${HOME}/.profile; then
   echo -e "${MSG_INFO} Robot configuration for .profile found, nothing to do. "
else 
   echo -e "${MSG_DONE} Add Robot configuration to .profile"
   echo "#configure environment for Robot" >> ${HOME}/.profile
   echo ". /opt/rfwaio/linux/set_robotenv.sh" >> ${HOME}/.profile
fi

#
# Remind user for install DLTConnector
#
############################################################################### 
if [ -d "${DLTCONNECTOR_PATH}" ]; then
   echo "For using QConnectionDLTLibrary, please install DTLConnector by below commands:"
   echo "sudo dpkg -i ${DLTCONNECTOR_PATH}${DLTCONNECTOR_NAME}"
fi

#
# Update robotvscode data
#
###############################################################################
#chmod -R 0775 /opt/rfwaio/robotvscode/data/user-data/
PyPath=/opt/rfwaio/python39/install/bin
TestPath=${HOME}/RobotTest/testcases
WpPath=`echo $TestPath | perl -MURI::file -e 'print URI::file->new(<STDIN>)."\n"'`
sed -i "s|{RobotPythonPath}|$PyPath|g" /opt/rfwaio/robotvscode/data/user-data/User/settings.json
sed -i "s|{RobotTestPath}|$WpPath|g" /opt/rfwaio/robotvscode/data/user-data/User/globalStorage/storage.json # > /opt/rfwaio/robotvscode/data/user-data/storage.json
