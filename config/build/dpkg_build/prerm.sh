#!/bin/bash

# Backup VSCode extensions/global storage
backup_vscode_extensions() {
   echo "Backing up VSCode user data..."
   if [ -d "/opt/rfwaio/robotvscode/data/extensions" ]; then
      mkdir -p /tmp/vscode_backup/
      cp -R /opt/rfwaio/robotvscode/data/extensions /tmp/vscode_backup/
      echo "Backed up extensions to /tmp/vscode_backup/extensions"
   else
      echo "Extensions directory not found, skipping backup"
   fi
}

# Remove application files from /opt/rfwaio
remove_application_files() {
   rm -rf /opt/rfwaio/robotvscode/
   rm -rf /opt/rfwaio/python39/
   rm -rf /opt/rfwaio/python3/
   rm -rf /opt/rfwaio/devtools/

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
      backup_vscode_extensions
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