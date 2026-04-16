#!/bin/bash
set -e

echo ">>>> [1/5] SET DYNAMIC VERSIONING ENV..."
export AIO_VERSION_DATE=$(date +%m.%Y)
export AIO_VERSION=${TAG_NAME#[rd]e[vl]/aio/}
export RobotFrameworkVersion=${TAG_NAME#[rd]e[vl]/aio/}
export BUNDLE_VERSION_DATE="--bundle_version_date $(date +%m.%Y)"
export BUNDLE_VERSION="--bundle_version ${TAG_NAME#[rd]e[vl]/aio/}"
export REPO_CONFIG="./config/repositories/repositories_${VERSION_TYPE}.conf"
export MAINDOC_CONFIGFILE="--configfile ./maindoc/maindoc_configs/maindoc_config_OSS_${VERSION_TYPE}.json"
export PYBIN=$(which python3)
export PYTHONBIN=$(which python3)

echo ">>>> [2/5] PREPARE SCRIPTS & CONFIG..."
sed -i 's|../python3lx|/usr/local|g' build
sed -i 's|${PYDIR}/bin/python3|/usr/local/bin/python3|g' build
sed -i 's|/opt/rfwaio/python3|/usr/local|g' ./config/build/dpkg_build/robot

echo ">>>> [3/5] CLONE AND INSTALL COMPONENTS..."
mkdir -p /usr/local/lib/plantuml
curl -L https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar -o /usr/local/lib/plantuml/plantuml.jar
mkdir -p /opt/rfwaio/robotvscode/data/extensions/jebbs.plantuml-2.18.1/
ln -sf /usr/local/lib/plantuml/plantuml.jar /opt/rfwaio/robotvscode/data/extensions/jebbs.plantuml-2.18.1/plantuml.jar

./cloneall --config-file="$REPO_CONFIG"
./install/install.sh --android

echo ">>>> [4/5] EXECUTE BUILD LOGIC..."
./build --config-file=$REPO_CONFIG --sub-version=$SubVersion

echo ">>>> [5/5] SYSTEM INSTALLATION & PERMISSIONS..."
mkdir -p /opt/rfwaio/python3/bin /opt/rfwaio/tools /opt/rfwaio/linux/icon /opt/rfwaio/tutorial /opt/rfwaio/documentation /opt/rfwaio/devtools

# Python Path Compatibility
ln -s /usr/local/bin/python3 /opt/rfwaio/python3/bin/python3

# Executables & Assets
cp ./config/build/dpkg_build/robot /usr/local/bin/robot
chmod +x /usr/local/bin/robot
cp ./config/build/dpkg_build/postinst.sh /usr/local/bin/initRobotFrameworkAIO.sh
chmod +x /usr/local/bin/initRobotFrameworkAIO.sh
cp ./config/build/dpkg_build/robot.ico /opt/rfwaio/linux/icon/
cp ./config/build/dpkg_build/set_robotenv.sh /opt/rfwaio/linux/
cp ./config/tools/appium.sh /opt/rfwaio/devtools/appium
chmod +x /opt/rfwaio/devtools/appium
chmod +x /opt/rfwaio/linux/set_robotenv.sh

# Training & Docs
cp -R -a ../robotframework-tutorial/[0-9][0-9][0-9]_* /opt/rfwaio/tutorial/
cp ../robotframework-documentation/book/RobotFrameworkAIO_Reference*${SubVersion}.pdf /opt/rfwaio/documentation/ 2>/dev/null || true
cp -R -a ../devtools/. /opt/rfwaio/devtools/
cp -R -a ./test/aio-analyzer /opt/rfwaio/tools/aio-analyzer
cp ./version.txt /opt/rfwaio/

# Apply Permissions
chown -R root:robot-aio /opt/rfwaio
chmod -R 0775 /opt/rfwaio
[ -f /opt/rfwaio/devtools/Appium-Inspector.AppImage ] && chmod 4755 /opt/rfwaio/devtools/Appium-Inspector.AppImage

# Workspace folders
mkdir -p ~/RobotTest/logfiles ~/RobotTest/localconfig ~/RobotTest/testcases ~/RobotTest/tutorial
cp -R -a /opt/rfwaio/tutorial/. ~/RobotTest/tutorial
cp -R -a /opt/rfwaio/documentation/. ~/RobotTest/documentation
chown -R root:robot-aio ~/RobotTest/
chmod -R 0775 ~/RobotTest/

echo ">>>> Build OSS Finished successfully!"