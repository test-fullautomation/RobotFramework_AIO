#!/bin/bash
# Script to setup enviroment for Robotframework AIO on Linux
# This should run 1 time when postinst
IDE_NAME="VSCodium"

DO_UPDATE_VSCODIUM_FLAG=false
[ -f /var/lib/robotframework-aio-do-update-vscodium ] && DO_UPDATE_VSCODIUM_FLAG=true

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
   echo "remove $IDE_NAME related stuffs"

   rm -rf /opt/rfwaio/robotvscode
   rm -rf /opt/rfwaio/linux/robot.desktop
   rm -rf ${APPS_PATH}/robot.desktop

   sed -i '/RobotVsCode/d' /opt/rfwaio/linux/set_robotenv.sh
   sed -i '/GENDOC_PLANTUML_PATH/d' /opt/rfwaio/linux/set_robotenv.sh
}

function remove_android_package(){
   echo "remove Android related stuffs"

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

function install_python_packages() {
   WHEELHOUSE_DIR="/opt/rfwaio/wheelhouse"
   WHEELROBOTFRAMEWORK_DIR="/opt/rfwaio/robotwheel"
   PYTHON_BIN="/opt/rfwaio/python3/bin/python3"

   if [ -d "$WHEELHOUSE_DIR" ] && ls $WHEELHOUSE_DIR/*.whl 1>/dev/null 2>&1; then
      echo -e "${MSG_INFO} Installing Python packages from wheelhouse..."
      $PYTHON_BIN -m pip install --no-index --no-cache-dir --find-links $WHEELHOUSE_DIR --force-reinstall $WHEELHOUSE_DIR/*.whl
      if [ $? -eq 0 ]; then
         echo -e "${MSG_DONE} Python packages installed successfully."
      else
         echo -e "${MSG_ERR} Failed to install Python packages from wheelhouse."
         exit 1
      fi
   else
      echo -e "${MSG_ERR} Wheelhouse directory not found or empty: $WHEELHOUSE_DIR"
      exit 1
   fi

   if [ -d "$WHEELROBOTFRAMEWORK_DIR" ] && ls $WHEELROBOTFRAMEWORK_DIR/robotframework-*.whl 1>/dev/null 2>&1; then
      echo -e "${MSG_INFO} Installing RobotFramework package from robotwheel..."
      $PYTHON_BIN -m pip install --no-index --no-cache-dir --find-links $WHEELROBOTFRAMEWORK_DIR --force-reinstall $WHEELROBOTFRAMEWORK_DIR/robotframework-*.whl
      if [ $? -eq 0 ]; then
         echo -e "${MSG_DONE} RobotFramework package installed successfully."
      else
         echo -e "${MSG_ERR} Failed to install RobotFramework package from robotwheel."
         exit 1
      fi
   fi
}

merge_extensions() {
   local backup_file="$1"
   local new_file="$2"
   local output_file="$3"

   echo "Merging extensions with jq..."
   # Merge: keep all new extensions + add backup extensions not in new
   jq -s '
      (.[0] | map({key: .identifier.id, value: .}) | from_entries) as $backup |
      (.[1] | map({key: .identifier.id, value: .}) | from_entries) as $new |
      ($backup + $new) | to_entries | map(.value)
   ' "$backup_file" "$new_file" > "$output_file"
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
   echo "Performing updates for $IDE_NAME-related components..."

   #
   # Configure Unitiy Launchers - "$IDE_NAME for RobotFramework AIO"
   #
   ###############################################################################
   echo -e "${MSG_DONE} Creating/Updating '$IDE_NAME for RobotFramework AIO' App"
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
   PyPath=/opt/rfwaio/python3/bin
   TestPath=${HOME}/RobotTest/testcases
   VsCodePath=/opt/rfwaio/robotvscode
   WpPath=`echo $TestPath | perl -MURI::file -e 'print URI::file->new(<STDIN>)."\n"'`
   sed -i "s|{RobotPythonPath}|$PyPath|g" /opt/rfwaio/robotvscode/data/user-data/User/settings.json
   sed -i "s|{RobotTestPath}|$WpPath|g" /opt/rfwaio/robotvscode/data/user-data/User/globalStorage/storage.json # > /opt/rfwaio/robotvscode/data/user-data/storage.json
   sed -i "s|{RobotVsCode}|$VsCodePath|g" /opt/rfwaio/robotvscode/data/user-data/User/globalStorage/storage.json # > /opt/rfwaio/robotvscode/data/user-data/storage.json
   if [ -f "$TestPath/.vscode/launch.json" ]; then
      sed -i "s|\"type\"\s*:\s*\"robotframework-lsp\"|\"type\": \"robotcode\"|g" "$TestPath/.vscode/launch.json"
   fi

   # Remind user to install Github Copilot extensions for IDE
   INSTALL_COPILOT_EXTS_SCRIPT=/opt/rfwaio/robotvscode/install-github-copilot-exts.sh
   if [ -f "${INSTALL_COPILOT_EXTS_SCRIPT}" ]; then
      echo "For using Github Copilot extensions with $IDE_NAME, please install them by executing below script:"
      echo "${INSTALL_COPILOT_EXTS_SCRIPT} $GITHUB_COPILOT_EXT_ARG"
   fi

   # Restore user's VSCode extensions for reinstalled IDE
   local BACKUP_DIR="/tmp/vscode_backup"
   local EXT_BACKUP_DIR="$BACKUP_DIR/extensions"
   local STORAGE_BACKUP_DIR="$BACKUP_DIR/globalStorage"
   local VSCODE_DATA_DIR="/opt/rfwaio/robotvscode/data"
   local EXT_NEW_DIR="/tmp/extensions"

   if [ -d "$EXT_BACKUP_DIR" ]; then
      echo "Restoring user's $IDE_NAME extensions..."
      mv "$VSCODE_DATA_DIR/extensions" "$EXT_NEW_DIR"

      cp -R "$EXT_BACKUP_DIR" $VSCODE_DATA_DIR
      cp -R "$EXT_NEW_DIR" $VSCODE_DATA_DIR

      merge_extensions "$EXT_BACKUP_DIR/extensions.json" "$EXT_NEW_DIR/extensions.json" "$VSCODE_DATA_DIR/extensions/extensions.json"

      allow_user_group_permissions "$VSCODE_DATA_DIR/extensions"
   fi

   # Restore user's VSCode global storage for reinstalled IDE
   if [ -d "$STORAGE_BACKUP_DIR" ]; then
      echo "Restoring user's $IDE_NAME global storage..."
      cp -R "$STORAGE_BACKUP_DIR" "$VSCODE_DATA_DIR/user-data/User/"

      allow_user_group_permissions "$VSCODE_DATA_DIR/user-data/User/globalStorage"
   fi

   echo "Clean up temporary backup files..."
   rm -rf "$BACKUP_DIR"
   rm -rf "$EXT_NEW_DIR"
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
DLTCONNECTOR_PATH="/opt/rfwaio/python3/lib/python3.13/site-packages/QConnectionDLTLibrary/tools/DLTConnector/linux/"
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

   allow_user_group_permissions ${HOME}/RobotTest
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

      if [ -d "/opt/rfwaio/robotvscode" ]; then
         cp -R -a /opt/rfwaio/robotvscode/RobotTest/testcases/. ${HOME}/RobotTest/testcases
      fi
      update_owner ${HOME}/RobotTest/testcases
      echo -e "${MSG_DONE} ${action_msg} testcases folder."
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
# The selected components are stored in temporary file by preinst script,
# and postinst script will read and perform update/remove accordingly
# If the file is not existing, it means this script is executed as initRobotFrameworkAIO.sh
SELECTED_CMPTS_FILE=/tmp/robfw_aio_selected_cmpts.tmp
if [ -f "${SELECTED_CMPTS_FILE}" ];then
   # Install Python packages (AIO components + dependencies) from bundled wheelhouse
   install_python_packages

   # Update/remove components based on user selection during installation
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
   if $DO_UPDATE_VSCODIUM_FLAG; then
      # Dev mode
      if [[ " ${SELECTED_CMPTS[@]} " =~ " $IDE_NAME (fresh install) " ]] || \
      [[ " ${SELECTED_CMPTS[@]} " =~ " $IDE_NAME (upgrade/overwrite) " ]]; then

         # Update permission of IDE-related data
         ###########################################################################
         allow_user_group_permissions /opt/rfwaio/robotvscode/data
         allow_user_group_permissions /opt/rfwaio/robotvscode/RobotTest
         chmod 4755 /opt/rfwaio/robotvscode/chrome-sandbox

         # Extra step only for fresh install
         if [[ " ${SELECTED_CMPTS[@]} " =~ " $IDE_NAME (fresh install) " ]]; then
            rm -rf "/tmp/vscode_backup"
         fi

         update_vscodium_related;
      else
         remove_vscodium_package;
      fi
   else
      # End-user mode
      if ! [[ " ${SELECTED_CMPTS[@]} " =~ " $IDE_NAME " ]]; then
         remove_vscodium_package;
      else
         #
         # Update permission of IDE-related data
         #
         #############################################################################
         allow_user_group_permissions /opt/rfwaio/robotvscode/data
         allow_user_group_permissions /opt/rfwaio/robotvscode/RobotTest
         chmod 4755 /opt/rfwaio/robotvscode/chrome-sandbox
         update_vscodium_related;
      fi
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

FLAG_FILE="/var/lib/robotframework-aio-do-update-vscodium"
rm -f "$FLAG_FILE" || true
