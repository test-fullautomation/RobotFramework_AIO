# Use the official Python 3.13 image based on Debian Bookworm Slim
FROM python:3.13-slim-bookworm

# --- Build Arguments ---
ARG VERSION_TYPE="extended"
ARG TAG_NAME="dev/aio/0.0.0"
ARG VARIANT="OSS"
ARG BUNDLE_NAME="--bundle_name 'RobotFramework AIO'"
ARG AIO_NAME="RobotFramework AIO"
ARG GENDOC_PLANTUML_PATH="../robotvscode/data/extensions/jebbs.plantuml-2.18.1"
ARG GITHUB_COPILOT_REF_URL=""
ARG GITHUB_COPILOT_EXT_ARG=""
ARG REPOSITORY=""
ARG PULL_REQUEST_BRANCH=""
ARG INSTALLER_LOCATION=""

# --- Environment Variables (Migrated from postinst.sh and set_robotenv.sh) ---
ENV DEBIAN_FRONTEND=noninteractive
ENV SubVersion="${VERSION_TYPE}"
ENV AIO_NAME="${AIO_NAME}"

# Define tools paths as in postinst logic
ENV RobotPythonPath="/usr/local/bin"
ENV RobotPythonSitePackagesPath="/usr/local/lib/python3.13/site-packages"
ENV RobotScriptPath="/usr/local/bin"
ENV RobotToolsPath="/opt/rfwaio/tools"
ENV RobotTestPath="~/RobotTest/testcases"
ENV RobotLogPath="~/RobotTest/logfiles"
ENV RobotTutorialPath="~/RobotTest/tutorial"
ENV RobotDevtools="/opt/rfwaio/devtools"
ENV RobotNodeJS="/opt/rfwaio/devtools/nodejs"
ENV RobotAppium="/opt/rfwaio/devtools/nodejs/bin"
ENV RobotAndroidPlatformTools="/opt/rfwaio/devtools/Android/platform-tools"

WORKDIR /app

# Step 1: Install system-level dependencies and Setup Groups (OSS uses OpenJDK 17)
RUN apt-get update && apt-get install -y --fix-missing \
    sudo curl git procps libxtst6 liburi-perl sed \
    unzip xz-utils zstd \
    openjdk-17-jdk-headless \
    pandoc && \
    # Create 'robot-aio' group from postinst.sh logic
    groupadd -r robot-aio && usermod -a -G robot-aio root

# Step 2: Copy source code
COPY . .
RUN chmod +x ./requirements_linux.sh ./cloneall ./install/install.sh ./build

# Step 3: Global Python Requirements
RUN ./requirements_linux.sh && \
    python3 -m pip install --no-cache-dir build && \
    python3 -m pip install --no-cache-dir -r ./install/python_requirements_lx.txt

# Step 4: Full Build, Mimic Installation & Permission Logic
RUN /bin/bash -e -c " \
    # --- 1. SET DYNAMIC VERSIONING ENV ---
    export TAG_NAME='${TAG_NAME}' && \
    export AIO_VERSION_DATE=\$(date +%m.%Y) && \
    export AIO_VERSION=\${TAG_NAME#[rd]e[vl]/aio/} && \
    export RobotFrameworkVersion=\${TAG_NAME#[rd]e[vl]/aio/} && \
    export BUNDLE_VERSION_DATE=\"--bundle_version_date \$(date +%m.%Y)\" && \
    export BUNDLE_VERSION=\"--bundle_version \${TAG_NAME#[rd]e[vl]/aio/}\" && \
    export INSTALLER_LOCATION='${INSTALLER_LOCATION}' && \
    export AIO_NAME='${AIO_NAME}' && \
    export REPO_CONFIG='./config/repositories/repositories_${VERSION_TYPE}.conf' && \
    export MAINDOC_CONFIGFILE='--configfile ./maindoc/maindoc_configs/maindoc_config_OSS_${VERSION_TYPE}.json' && \
    \
    # --- 2. PREPARE SCRIPTS & CONFIG ---
    sed -i 's|../python3lx|/usr/local|g' build && \
    sed -i 's|\${PYDIR}/bin/python3|/usr/local/bin/python3|g' build && \
    sed -i 's/^[[:space:]]*build_debian[[:space:]]*$/: # build_debian/g' build && \
    sed -i 's/^[[:space:]]*build_windows[[:space:]]*$/: # build_windows/g' build && \
    sed -i 's|/opt/rfwaio/python3|/usr/local|g' ./config/build/dpkg_build/robot && \
    git config -f \"\$REPO_CONFIG\" --remove-section \"github.robotframework-documentation\" 2>/dev/null || true && \
    export PYBIN=\$(which python3) && \
    export PYTHONBIN=\$(which python3) && \
    \
    # --- 3. CLONE AND INSTALL COMPONENTS ---
    ./cloneall --config-file=\"\$REPO_CONFIG\" && \
    ./install/install.sh --android && \
    \
    # --- 4. EXECUTE BUILD LOGIC ---
    source ./include/bash/common.sh && \
    source ./build --config-file=\$REPO_CONFIG --sub-version=\$SubVersion && \
    check_and_install_texlive && \
    generate_version_info && \
    create_testsuitmanagement_package_context_file && \
    parse_config \"\$REPO_CONFIG\" && \
    \
    # --- 5. SYSTEM INSTALLATION & PERMISSIONS (Postinst logic) ---
    echo '>>>> Deploying components and applying permissions...' && \
    mkdir -p /opt/rfwaio/python3/bin /opt/rfwaio/tools /opt/rfwaio/linux/icon /opt/rfwaio/tutorial /opt/rfwaio/documentation /opt/rfwaio/devtools && \
    # Python Path Compatibility
    ln -s /usr/local/bin/python3 /opt/rfwaio/python3/bin/python3 && \
    \
    # 5.1 Executables & Scripts
    cp ./config/build/dpkg_build/robot /usr/local/bin/robot && \
    chmod +x /usr/local/bin/robot && \
    cp ./config/build/dpkg_build/postinst.sh /usr/local/bin/initRobotFrameworkAIO.sh && \
    chmod +x /usr/local/bin/initRobotFrameworkAIO.sh && \
    \
    # 5.2 Assets & Config
    cp ./config/build/dpkg_build/robot.ico /opt/rfwaio/linux/icon/ && \
    cp ./config/build/dpkg_build/set_robotenv.sh /opt/rfwaio/linux/ && \
    cp ./config/tools/appium.sh /opt/rfwaio/devtools/appium && \
    chmod +x /opt/rfwaio/devtools/appium && \
    chmod +x /opt/rfwaio/linux/set_robotenv.sh && \
    \
    # 5.3 Training, Docs & Tools
    cp -R -a ../robotframework-tutorial/[0-9][0-9][0-9]_* /opt/rfwaio/tutorial/ && \
    cp ../robotframework-documentation/book/RobotFrameworkAIO_Reference*${SubVersion}.pdf /opt/rfwaio/documentation/ 2>/dev/null || true && \
    cp -R -a ../devtools/. /opt/rfwaio/devtools/ && \
    cp -R -a ./test/aio-analyzer /opt/rfwaio/tools/aio-analyzer && \
    cp ./version.txt /opt/rfwaio/ && \
    \
    # 5.4 Apply Permissions (From postinst.sh allow_user_group_permissions)
    chown -R root:robot-aio /opt/rfwaio && \
    chmod -R 0775 /opt/rfwaio && \
    # SUID for Appium Inspector AppImage
    [ -f /opt/rfwaio/devtools/Appium-Inspector.AppImage ] && chmod 4755 /opt/rfwaio/devtools/Appium-Inspector.AppImage && \
    \
    # Create/Updates RobotTest workspace folder
    mkdir -p ~/RobotTest/logfiles && \
    mkdir -p ~/RobotTest/localconfig && \
    mkdir -p ~/RobotTest/testcases && \
    mkdir -p ~/RobotTest/tutorial && \
    cp -R -a /opt/rfwaio/tutorial/. ~/RobotTest/tutorial && \
    cp -R -a /opt/rfwaio/documentation/. ~/RobotTest/documentation && \
    chown -R root:robot-aio ~/RobotTest/ && \
    chmod -R 0775 ~/RobotTest/ && \
    \
    # --- 6. DEEP CLEANUP ---
    echo '>>>> Starting Aggressive Deep Cleanup...' && \
    conf_paths=\$(git config -f \"\$REPO_CONFIG\" --get-regexp '.path' | awk '{print \$2}') && \
    for path in \$conf_paths; do rm -rf \"\$path\"; done && \
    apt-get autoremove -y && apt-get clean && \
    rm -rf /usr/share/doc/* /usr/share/man/* /usr/local/share/doc/* && \
    rm -rf /robotframework* /python* /vscode* && \
    find /opt/rfwaio -name '*.tar*' -delete && \
    rm -rf /devtools /RobotFramework_AIO_website /testresultwebapp && \
    rm -rf ./download ./output_lx && \
    find . -maxdepth 3 -name '.git' -exec rm -rf {} + && \
    cd / && rm -rf /app/* && \
    rm -rf /root/.cache /tmp/* && \
    echo '>>>> Build OSS Finished successfully!'"

# Final Path setup - Updated to reflect /opt/rfwaio structure
ENV PATH="/opt/rfwaio/linux:/usr/local/bin:${RobotNodeJS}/bin:${RobotAndroidPlatformTools}:${PATH}"

# Default entry point
CMD ["robot"]