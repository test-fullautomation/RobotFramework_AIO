#!/bin/bash
# Script to setup enviroment for Robotframework AIO on Linux
# This should run 1 time when postinst

# This owner change is required when installation with sudo permission
# File/Folder after copying need to change the owner to actual user instead of root
function update_owner(){
   if [ "$(id -u)" = "0" ]; then
      chown -R "${CURRENT_USER}:${sGROUP}" $1
   fi
}

# Allow user and `robot-aio` group have full permission on app's file/folder
function allow_user_group_permissions(){
   path_to_dir=$1;

   chown -R "${CURRENT_USER}:${sGROUP}" $path_to_dir
   chmod -R 0775 $path_to_dir
   echo -e "${MSG_DONE} Updated permission for $path_to_dir"
}

function remove_vscodium_package(){
   echo remove Vscodium related stuffs

   rm -rf /opt/rfwaio/robotvscode
   rm -rf /opt/rfwaio/linux/robot.desktop
   rm -rf ${APPS_PATH}/robot.desktop

   sed -i '/RobotVsCode/d' /opt/rfwaio/linux/set_robotenv.sh
   sed -i '/GENDOC_PLANTUML_PATH/d' /opt/rfwaio/linux/set_robotenv.sh
}

function remove_android_package(){
   echo remove Android related stuffs

   rm -rf /opt/rfwaio/devtools
   rm -rf /opt/rfwaio/linux/appium.desktop
   rm -rf /opt/rfwaio/linux/appiumInspector.desktop
   rm -rf ${APPS_PATH}/appium.desktop
   rm -rf ${APPS_PATH}/appiumInspector.desktop

   sed -i '/RobotDevtools/d' /opt/rfwaio/linux/set_robotenv.sh
   sed -i '/RobotNodeJS/d' /opt/rfwaio/linux/set_robotenv.sh
   sed -i '/RobotAppium/d' /opt/rfwaio/linux/set_robotenv.sh
   sed -i '/RobotAndroidPlatformTools/d' /opt/rfwaio/linux/set_robotenv.sh   
}

function update_android_related(){
   echo "Performing updates for Android-related components..."

   #
   # Configure Unitiy Launchers - "Appium Server" and Appium Inspector
   #
   #############################################################################
   echo -e "${MSG_DONE} Creating/Updating 'Appium Server' App"
   cp /opt/rfwaio/linux/appium.desktop ${APPS_PATH}/appium.desktop
   update_owner ${APPS_PATH}/appium.desktop
   chmod +x ${APPS_PATH}/appium.desktop

   echo -e "${MSG_DONE} Creating/Updating 'Appium Inspector' App"
   cp /opt/rfwaio/linux/appiumInspector.desktop ${APPS_PATH}/appiumInspector.desktop
   update_owner ${APPS_PATH}/appiumInspector.desktop
   chmod +x ${APPS_PATH}/appiumInspector.desktop
}

function update_vscodium_related(){
   echo "Performing updates for Vscodium-related components..."

   #
   # Configure Unitiy Launchers - "VSCodium for RobotFramework AIO" 
   #
   ############################################################################### 
   echo -e "${MSG_DONE} Creating/Updating 'VSCodium for RobotFramework AIO' App" 
   cp /opt/rfwaio/linux/robot.desktop ${APPS_PATH}/robot.desktop
   update_owner ${APPS_PATH}/robot.desktop
   chmod +x ${APPS_PATH}/robot.desktop

   #
   # Updates Vscodium code-workspace
   #
   #############################################################################
   if [ ! -f ${HOME}/RobotTest/testcases/RobotTest.code-workspace ]; then
      cp -R -a /opt/rfwaio/robotvscode/RobotTest/testcases/RobotTest.code-workspace ${HOME}/RobotTest/testcases
      update_owner ${HOME}/RobotTest/testcases/RobotTest.code-workspace
      echo -e "${MSG_DONE} Initialized workspace (RobotTest.code-workspace)"
   fi

   #
   # Update robotvscode data
   #
   #############################################################################
   #chmod -R 0775 /opt/rfwaio/robotvscode/data/user-data/
   PyPath=/opt/rfwaio/python39/install/bin
   TestPath=${HOME}/RobotTest/testcases
   VsCodePath=/opt/rfwaio/robotvscode
   WpPath=`echo $TestPath | perl -MURI::file -e 'print URI::file->new(<STDIN>)."\n"'`
   sed -i "s|{RobotPythonPath}|$PyPath|g" /opt/rfwaio/robotvscode/data/user-data/User/settings.json
   sed -i "s|{RobotTestPath}|$WpPath|g" /opt/rfwaio/robotvscode/data/user-data/User/globalStorage/storage.json # > /opt/rfwaio/robotvscode/data/user-data/storage.json
   sed -i "s|{RobotVsCode}|$VsCodePath|g" /opt/rfwaio/robotvscode/data/user-data/User/globalStorage/storage.json # > /opt/rfwaio/robotvscode/data/user-data/storage.json

   # Remind user to install Github Copilot extensions for VsCodium
   INSTALL_COPILOT_EXTS_SCRIPT=/opt/rfwaio/robotvscode/install-github-copilot-exts.sh
   if [ -f "${INSTALL_COPILOT_EXTS_SCRIPT}" ]; then
      echo "For using Github Copilot extensions with VsCodium, please install them by executing below script:"
      echo "${INSTALL_COPILOT_EXTS_SCRIPT} $GITHUB_COPILOT_EXT_ARG"
   fi
}

echo "Creating/Updating RobotFramework AIO runtime environment"
echo "----------------------------------------"

COL_GREEN='\033[0;32m'
COL_ORANGE='\033[0;33m'
COL_BLUE='\033[0;34m'
COL_RED='\033[1;31m'
COL_RESET='\033[0m' # No Color

MSG_INFO="${COL_GREEN}[INFO]${COL_RESET}"
MSG_DONE="${COL_ORANGE}[DONE]${COL_RESET}"
MSG_ERR="${COL_RED}[ERR]${COL_RESET} "

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

# Introduce group `robot-aio` which allow access for group of multiple users
sGROUP=robot-aio


if [ "$(id -u)" = "0" ]; then
   # Run with sudo
   if [ ! $(getent group $sGROUP) ]; then
      addgroup $sGROUP
   fi
   usermod -a -G $sGROUP ${CURRENT_USER}
   echo -e "Using group ${sGROUP} as user group for robotframework-aio permission"
else
   if [ ! $(getent group $sGROUP) ]; then
      echo -e "${MSG_ERR} User group '$sGROUP' is not found"
      echo -e "${MSG_ERR} Please verify the installation of robotframework-aio"
      exit 1
   fi

   if groups ${CURRENT_USER} | grep $sGROUP; then
      echo -e "${MSG_INFO} User '${CURRENT_USER}' already belongs to group '$sGROUP'"
   else
      echo -e "${MSG_ERR} Please add '${CURRENT_USER}' to group '$sGROUP' as below command then try again"
      echo -e "${MSG_ERR} sudo usermod -a -G $sGROUP ${CURRENT_USER}"
      exit 1
   fi
fi


# Set schedule for installing DLTConnector (will active in future)
#
############################################################################### 
#if [ -d "${DLTCONNECTOR_PATH}" ]; then
#   echo "@reboot /opt/rfwaio/linux/install_dlt.sh" >> tmpfile 
#   crontab -u ${SUDO_USER} tmpfile 
#   rm tmpfile
#fi

#
# Create/Updates RobotTest workspace folder
#
#############################################################################
if [ ! -d "${HOME}/RobotTest" ]; then
   
   mkdir -p ${HOME}/RobotTest/logfiles
   mkdir -p ${HOME}/RobotTest/localconfig
   mkdir -p ${HOME}/RobotTest/testcases
   mkdir -p ${HOME}/RobotTest/tutorial
   
   #
   # Create RobotTest Workspacce Folder
   #
   ##############################################################################
   if [ -d "/opt/rfwaio/robotvscode" ]; then
      cp -R -a /opt/rfwaio/robotvscode/RobotTest/testcases/. ${HOME}/RobotTest/testcases
   fi
   cp -R -a /opt/rfwaio/tutorial/. ${HOME}/RobotTest/tutorial
   cp -R -a /opt/rfwaio/documentation/. ${HOME}/RobotTest/documentation

   echo -e "${MSG_DONE} Creating initial workspace in ~/RobotTest"
else
   #
   # update tutorial, documentation
   #
   ###########################################################################
   echo -e "${MSG_INFO} Found workspace in ~/RobotTest."
   action_msg="Updated"
   
   if [ -d ${HOME}/RobotTest/tutorial ]; then
      rm -rf ${HOME}/RobotTest/tutorial/*
   else
      mkdir -p ${HOME}/RobotTest/tutorial
      action_msg="Created"
   fi
   cp -R -a /opt/rfwaio/tutorial/. ${HOME}/RobotTest/tutorial
   update_owner ${HOME}/RobotTest/tutorial
   echo -e "${MSG_DONE} ${action_msg} tutorial folder."

   if [ -d ${HOME}/RobotTest/documentation ]; then
      rm -rf ${HOME}/RobotTest/documentation/*
      action_msg="Updated"
   else
      mkdir -p ${HOME}/RobotTest/documentation
      action_msg="Created"
   fi
   cp -R -a /opt/rfwaio/documentation/. ${HOME}/RobotTest/documentation
   update_owner ${HOME}/RobotTest/documentation
   echo -e "${MSG_DONE} ${action_msg} documentation folder."

   if [ ! -d ${HOME}/RobotTest/testcases ]; then
      if [ -f ${HOME}/RobotTest/testcases ]; then
         rm -f ${HOME}/RobotTest/testcases
      fi
      mkdir -p ${HOME}/RobotTest/testcases
   fi
fi

# Configure Unitiy Launchers folder
APPS_PATH=${HOME}/.local/share/applications
if [ -e "${APPS_PATH}" ]; then
   # Check whether it is file or directory
   # remove it in case it is fine then create appropriate directory 
   if [ -f "${APPS_PATH}" ]; then
      rm "${APPS_PATH}"
      mkdir -p "${APPS_PATH}"
   fi
else
   # Create applications launcher folder if not existing
   mkdir -p "${APPS_PATH}"
fi

# Check whether this script is executed in installation or not
SELECTED_CMPTS_FILE=/tmp/robfw_aio_selected_cmpts.tmp
if [ -f "${SELECTED_CMPTS_FILE}" ];then
   readarray -t SELECTED_CMPTS < /tmp/robfw_aio_selected_cmpts.tmp
   if ! [[ " ${SELECTED_CMPTS[@]} " =~ " Android " ]]; then  
      remove_android_package;
   else
      #
      # Update permission of Android-related data
      #
      #############################################################################
      allow_user_group_permissions /opt/rfwaio/devtools/nodejs/lib
      update_android_related;
   fi

   if ! [[ " ${SELECTED_CMPTS[@]} " =~ " Vscodium " ]]; then  
      remove_vscodium_package;
   else
      #
      # Update permission of Vscodium-related data
      #
      #############################################################################
      allow_user_group_permissions /opt/rfwaio/robotvscode/data
      allow_user_group_permissions /opt/rfwaio/robotvscode/RobotTest
      update_vscodium_related;
   fi
   

   rm ${SELECTED_CMPTS_FILE}
else
   if [ -d "/opt/rfwaio/devtools" ]; then
      update_android_related;
   fi
   if [ -d "/opt/rfwaio/robotvscode" ]; then
      update_vscodium_related;
   fi
fi

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
