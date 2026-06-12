#!/bin/bash
set -e

RF_OPT_DIR="/opt/rfwaio"
PYTHON_SITE_PACKAGES="$RF_OPT_DIR/python3/lib/python3.13/site-packages"
CURL_OPTS="-L"

echo ">>>> [1/6] SET DYNAMIC VERSIONING ENV"
export AIO_VERSION_DATE=$(date +%m.%Y)
export AIO_VERSION=${TAG_NAME#[rd]e[vl]/aio/}
export RobotFrameworkVersion=${TAG_NAME#[rd]e[vl]/aio/}
export BUNDLE_VERSION_DATE="--bundle_version_date $(date +%m.%Y)"
export BUNDLE_VERSION="--bundle_version ${TAG_NAME#[rd]e[vl]/aio/}"
export MAINDOC_CONFIGFILE="./maindoc/maindoc_configs/maindoc_config_OSS_${VERSION_TYPE}.json"
export SUBVERSION=${VERSION_TYPE}

echo ">>>> [2/6] CLEANING SCRIPTS & PERMISSIONS"
SCRIPTS="./build ./cloneall ./install/install.sh ./install/versions.conf ./docker/docker-entrypoint.sh ./requirements_linux.sh"
dos2unix $SCRIPTS
chmod +x $SCRIPTS

echo ">>>> [3/6] PREPARE SCRIPTS & CONFIG"
./requirements_linux.sh
if [ "$VARIANT" = "BIOS" ]; then
    EXTRA_PIP_FLAGS="--break-system-packages --proxy $PROXY_SERVER"
    CURRENT_INSTALL_FLAGS="--use-cntlm --docker"
    BIN_DIR="/usr/bin"
    DEVTOOLS_DIR="./devtools/."
    export PY_DIR=$(which python3)
    PLANTUML_PATH="/usr/lib/plantuml/plantuml.jar"
    export PYBIN=$(which python3)
    sed -i 's|destDir=$(realpath $mypath/../..)|destDir=$(realpath $mypath/..)|g' ./install/install.sh
    sed -i 's|\[ -d "\.\./python3lx" \]|[ -d "./python3lx" ]|g' ./build
    sed -i 's|cd ../python3lx|cd ./python3lx|g' ./build
    export http_proxy="$PROXY_SERVER"
    export https_proxy="$PROXY_SERVER"
    export no_proxy="localhost,127.0.0.1,.bosch.com"
    export REPO_CONFIG="/workspace/build/config/repositories/repositories_${VERSION_TYPE}.conf"
    CURL_OPTS="$CURL_OPTS -x $PROXY_SERVER"
else
    EXTRA_PIP_FLAGS=""
    CURRENT_INSTALL_FLAGS="--android"
    BIN_DIR="/usr/local/bin"
    DEVTOOLS_DIR="../devtools/."
    PY_DIR="/usr/local/lib/python3.13"
    PLANTUML_PATH="/usr/local/lib/plantuml/plantuml.jar"
    export PYBIN=$(which python3)
    PY_PREFIX=$(dirname $(dirname $PYBIN))
    export REPO_CONFIG="./config/repositories/repositories_${VERSION_TYPE}.conf"

    sed -i "s|../python3lx|$PY_PREFIX|g" build
    sed -i "s|\${PYDIR}/bin/python3|$PYBIN|g" build
    sed -i "s|$RF_OPT_DIR/python3|$PY_PREFIX|g" ./config/build/dpkg_build/robot

    echo "Dependency Installation"
    python3 -m pip install $EXTRA_PIP_FLAGS --no-cache-dir build
    python3 -m pip install $EXTRA_PIP_FLAGS --no-cache-dir -r ./install/python_requirements_lx.txt
fi

echo ">>>> [4/6] BUILD"
mkdir -p "$(dirname "$PLANTUML_PATH")"
curl -sfL $CURL_OPTS "https://github.com/plantuml/plantuml/releases/latest/download/plantuml.jar" -o "$PLANTUML_PATH"
if [ ! -s "$PLANTUML_PATH" ]; then
    echo "ERROR: Failed to download plantuml.jar or file is empty"
    exit 1
fi

PLANTUML_EXT_DIR="$RF_OPT_DIR/robotvscode/data/extensions/jebbs.plantuml-2.18.1"
mkdir -p "$PLANTUML_EXT_DIR"
cp "$PLANTUML_PATH" "$PLANTUML_EXT_DIR/plantuml.jar"

if [ "$VARIANT" != "BIOS" ]; then
    ./cloneall --config-file="$REPO_CONFIG"
else
    echo "Skipping cloneall inside Docker for BIOS; using host-cloned workspace"
fi

./install/install.sh $CURRENT_INSTALL_FLAGS
./build --config-file=$REPO_CONFIG --sub-version=$SUBVERSION

# For BIOS, Python with pip is the one built by install.sh into ./python3lx
if [ "$VARIANT" = "BIOS" ]; then
    PYBIN="$(pwd)/python3lx/bin/python3"
fi

# Install all built wheels from wheelhouse into the Python environment
# This is the Docker equivalent of what postinst.sh does for .deb installations
WHEELHOUSE_DIR="$(pwd)/wheelhouse"
if [ -d "$WHEELHOUSE_DIR" ] && ls "$WHEELHOUSE_DIR"/*.whl 1>/dev/null 2>&1; then
    echo "Installing Python packages from wheelhouse..."
    "$PYBIN" -m pip install $EXTRA_PIP_FLAGS --no-cache-dir --find-links="$WHEELHOUSE_DIR" "$WHEELHOUSE_DIR"/*.whl || {
        echo "ERROR: pip install from wheelhouse failed. Listing wheelhouse contents:"
        ls -la "$WHEELHOUSE_DIR"/*.whl
        echo "Retrying with verbose output:"
        "$PYBIN" -m pip install $EXTRA_PIP_FLAGS --no-cache-dir --find-links="$WHEELHOUSE_DIR" "$WHEELHOUSE_DIR"/*.whl -v 2>&1 | tail -50
        exit 1
    }
fi

# Reinstall the extended RF core from robotwheel/ to ensure it is not overridden by stock RF from wheelhouse
ROBOTWHEEL_DIR="$(pwd)/robotwheel"
if [ -d "$ROBOTWHEEL_DIR" ] && ls "$ROBOTWHEEL_DIR"/*.whl 1>/dev/null 2>&1; then
    echo "Reinstalling extended RobotFramework core from robotwheel..."
    "$PYBIN" -m pip install $EXTRA_PIP_FLAGS --no-cache-dir --force-reinstall "$ROBOTWHEEL_DIR"/*.whl
fi

# Copy package_context.json into site-packages (not included in wheel, but required by TSM at runtime)
TSM_SRC_CONFIG="../robotframework-testsuitesmanagement/RobotFramework_TestsuitesManagement/Config/package_context.json"
if [ -f "$TSM_SRC_CONFIG" ]; then
    TSM_DEST=$("$PYBIN" -c "import importlib.util; spec=importlib.util.find_spec('RobotFramework_TestsuitesManagement'); print(spec.submodule_search_locations[0])" 2>/dev/null)
    if [ -n "$TSM_DEST" ] && [ -d "$TSM_DEST/Config" ]; then
        cp "$TSM_SRC_CONFIG" "$TSM_DEST/Config/package_context.json"
        echo "Copied package_context.json to $TSM_DEST/Config/"
    fi
fi

echo ">>>> [5/6] SYSTEM INSTALLATION & PERMISSIONS"
mkdir -p $RF_OPT_DIR/{python3/bin,tools,linux/icon,tutorial,documentation,devtools}

echo "Executables & Assets"
cp ./docker/docker-entrypoint.sh $BIN_DIR/docker-entrypoint.sh
chmod +x $BIN_DIR/docker-entrypoint.sh
cp ./config/build/dpkg_build/robot $BIN_DIR/robot
chmod +x $BIN_DIR/robot
cp ./config/build/dpkg_build/postinst.sh $BIN_DIR/initRobotFrameworkAIO.sh
chmod +x $BIN_DIR/initRobotFrameworkAIO.sh
cp ./config/build/dpkg_build/robot.ico /opt/rfwaio/linux/icon/
cp ./config/build/dpkg_build/set_robotenv.sh /opt/rfwaio/linux/
sed -i "s|/opt/rfwaio/python3/bin|${BIN_DIR}|g" /opt/rfwaio/linux/set_robotenv.sh
sed -i "s|/opt/rfwaio/python3/lib/python3\.[0-9]*|${PY_DIR}|g" /opt/rfwaio/linux/set_robotenv.sh
cp ./config/tools/appium.sh /opt/rfwaio/devtools/appium
chmod +x /opt/rfwaio/devtools/appium
chmod +x /opt/rfwaio/linux/set_robotenv.sh

echo "Training & Docs"
cp -R -a ../robotframework-tutorial/[0-9][0-9][0-9]_* /opt/rfwaio/tutorial/
cp ../robotframework-documentation/book/RobotFrameworkAIO_Reference*${SubVersion}.pdf /opt/rfwaio/documentation/ 2>/dev/null || true
cp -R -a $DEVTOOLS_DIR /opt/rfwaio/devtools/
cp -R -a ./test/aio-analyzer /opt/rfwaio/tools/aio-analyzer
cp ./version.txt /opt/rfwaio/

echo "Permissions"
chown -R root:robot-aio $RF_OPT_DIR
chmod -R 0775 $RF_OPT_DIR

echo "Workspace setup"
mkdir -p ~/RobotTest/{logfiles,localconfig,testcases,tutorial,documentation}
cp -R -a $RF_OPT_DIR/tutorial/. ~/RobotTest/tutorial/
cp -R -a $RF_OPT_DIR/documentation/. ~/RobotTest/documentation/
chown -R root:robot-aio ~/RobotTest
chmod -R 0775 ~/RobotTest

echo ">>>> [6/6] CLEANING UP BUILD"
if [ -d "$PY_DIR" ]; then
    echo "Cleaning up Python cache in $PY_DIR"
    find "$PY_DIR" -type d -name "__pycache__" -exec rm -rf {} +
    find "$PY_DIR" -name "*.pyc" -delete
fi

rm -f $RF_OPT_DIR/devtools/Appium-Inspector.AppImage
rm -rf $RF_OPT_DIR/robbotvscode

echo ">>>> Build $VARIANT finished successfully!"