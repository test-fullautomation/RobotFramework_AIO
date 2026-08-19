#!/bin/bash

###############################################################################
# Dev-only flag
# Enable by running:
#   echo 1 | sudo tee /var/lib/robotframework-aio-do-update-vscodium
#   sudo apt-get install -y ./*.deb --fix-missing --reinstall --allow-downgrades
###############################################################################
if [ -x "/opt/rfwaio/robotvscode/bin/codium" ]; then
   IDE_NAME="VSCodium"
elif [ -x "/opt/rfwaio/robotvscode/bin/code" ]; then
   IDE_NAME="VSCode"
else
   IDE_NAME="VSCodium"
fi
DO_UPDATE_VSCODIUM_FLAG=false
[ -f /var/lib/robotframework-aio-do-update-vscodium ] && DO_UPDATE_VSCODIUM_FLAG=true

# Backup VSCode extensions/global storage
backup_vscode_extensions() {
   echo "Backing up $IDE_NAME user data..."

   local VSCODE_DATA_DIR="/opt/rfwaio/robotvscode/data"
   local BACKUP_DIR="/tmp/vscode_backup"

   mkdir -p "$BACKUP_DIR"

   # Backup extensions
   if [ -d "$VSCODE_DATA_DIR/extensions" ]; then
      cp -R "$VSCODE_DATA_DIR/extensions" "$BACKUP_DIR/"
      echo "Backed up extensions"
   fi

   # Backup global storage
   if [ -d "$VSCODE_DATA_DIR/user-data/User/globalStorage" ]; then
      cp -R "$VSCODE_DATA_DIR/user-data/User/globalStorage" "$BACKUP_DIR/"
      echo "Backed up global storage"
   fi
}

# Remove application files from /opt/rfwaio
remove_application_files() {
   rm -rf /opt/rfwaio/robotvscode/
   rm -rf /opt/rfwaio/python39/
   rm -rf /opt/rfwaio/python3/
   rm -rf /opt/rfwaio/devtools/

   # When run via sudo, $HOME may be /root even though we want to clean up
   # files from the invoking user's home directory, so derive HOME from
   # SUDO_USER (or the current user) when that user is not root.
   CURRENT_USER=${SUDO_USER:-$(whoami)}
   if [ "${CURRENT_USER}" != 'root' ]; then
      HOME=/home/${CURRENT_USER}
   fi

   rm -rf ${HOME}/.local/share/applications/robot.desktop
   rm -rf ${HOME}/.local/share/applications/appium.desktop
   rm -rf ${HOME}/.local/share/applications/appiumInspector.desktop
}

case "$1" in
   upgrade)
      echo "Upgrading RobotFramework AIO..."
      if $DO_UPDATE_VSCODIUM_FLAG; then

         backup_vscode_extensions
      fi
      remove_application_files
      ;;

   remove)
      echo "Removing RobotFramework AIO..."
      remove_application_files
      ;;

   *)
      echo "prerm called with unknown argument: $1"
      ;;
esac

exit 0