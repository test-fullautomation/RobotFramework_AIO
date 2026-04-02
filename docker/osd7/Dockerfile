# Use the official Python 3.13 image based on Debian Bookworm (Full version)
FROM python:3.13-bookworm

# --- Build Arguments ---
ARG VERSION_TYPE="extended"
ARG TAG_NAME="dev/aio/0.0.0"
ARG REPOSITORY=""
ARG PULL_REQUEST_BRANCH=""
ARG GITHUB_COPILOT_REF_URL=""
ARG GITHUB_COPILOT_EXT_ARG=""

# --- Environment Variables ---
ENV DEBIAN_FRONTEND=noninteractive
ENV VARIANT="OSS"
ENV SubVersion="${VERSION_TYPE}"
ENV REPO_CONFIG="./config/repositories/repositories_${VERSION_TYPE}.conf"
ENV MAINDOC_CONFIGFILE="--configfile ./maindoc/maindoc_configs/maindoc_config_OSS_${VERSION_TYPE}.json"
ENV GENDOC_PLANTUML_PATH="../robotvscode/data/extensions/jebbs.plantuml-2.18.1"
ENV BUNDLE_NAME="--bundle_name 'RobotFramework AIO'"
ENV RobotPythonPath="/usr/local"

WORKDIR /app

# Step 1: Install system-level dependencies
# Combining update and install to reduce image layers
RUN apt-get update && apt-get install -y --fix-missing \
    sudo curl git procps libxtst6 liburi-perl sed \
    unzip xz-utils zstd \
    openjdk-17-jdk-headless \
    pandoc

# Step 2: Copy source code and set permissions
COPY . .
RUN chmod +x ./requirements_linux.sh ./cloneall ./install/install.sh ./build

# Step 3: Global Python Requirements
# Installing 'build' and project-specific requirements into system Python
RUN ./requirements_linux.sh && \
    python3 -m pip install --no-cache-dir build && \
    python3 -m pip install --no-cache-dir -r ./install/python_requirements_lx.txt

# Step 4-7: The "Heavy Lift" - Chained Command for maximum size optimization
# This includes: Cloning -> Android/Node Install -> Build Documents -> Installing Libs -> Deep Cleanup
RUN /bin/bash -e -c " \
    # --- 1. SET DYNAMIC VERSIONING ENV ---
    # Calculating version tags and build dates dynamically using shell logic
    export TAG_NAME='${TAG_NAME}' && \
    export AIO_VERSION_DATE=\$(date +%m.%Y) && \
    export AIO_VERSION=\${TAG_NAME#[rd]e[vl]/aio/} && \
    export RobotFrameworkVersion=\${TAG_NAME#[rd]e[vl]/aio/} && \
    export BUNDLE_VERSION_DATE=\"--bundle_version_date \$(date +%m.%Y)\" && \
    export BUNDLE_VERSION=\"--bundle_version \${TAG_NAME#[rd]e[vl]/aio/}\" && \
    \
    # --- 2. PREPARE SCRIPTS ---
    # Patch the build script to use system Python path instead of portable python3lx
    sed -i 's|../python3lx|/usr/local|g' build && \
    sed -i 's|\${PYDIR}/bin/python3|/usr/local/bin/python3|g' build && \
    \
    # Comment out the line that actually starts the build_debian function
    # This prevents the script from auto-executing when sourced with arguments
    sed -i 's/^[[:space:]]*build_debian[[:space:]]*$/: # build_debian/g' build && \
    sed -i 's/^[[:space:]]*build_windows[[:space:]]*$/: # build_windows/g' build && \
    \
    export PYBIN=\$(which python3) && \
    export PYTHONBIN=\$(which python3) && \
    \
    # --- 3. CLONE AND INSTALL COMPONENTS ---
    # Cloning sub-repositories and installing Android/NodeJS tools
    ./cloneall --config-file=\"\$REPO_CONFIG\" && \
    ./install/install.sh --android && \
    \
    # --- 4. EXECUTE BUILD LOGIC ---
    # Sourcing functions to generate metadata and install all Robot libraries
    source ./include/bash/common.sh && \
    source ./build --config-file=\$REPO_CONFIG --sub-version=\$SubVersion && \
    check_and_install_texlive && \
    generate_version_info && \
    create_testsuitmanagement_package_context_file && \
    parse_config \"\$REPO_CONFIG\" && \
    \
    # --- 5. SYSTEM INSTALLATION (Headless - Mimicking .deb package deployment) ---
    # Since we are bypassing the actual .deb package creation to save space and time,
    # we manually deploy the essential assets to standard Linux paths (/opt and /usr/bin).
    echo '>>>> Installing CLI components to /opt/rfwaio...' && \
    \
    # Create the internal directory structure for the AIO framework
    mkdir -p /opt/rfwaio/tools /opt/rfwaio/linux/icon /opt/rfwaio/tutorial /opt/rfwaio/documentation /opt/rfwaio/devtools && \

    # 5.1 Main Executables: Install the 'robot' entry point and init script to system PATH
    cp ./config/build/dpkg_build/robot /usr/local/bin/robot && \
    chmod +x /usr/local/bin/robot && \
    cp ./config/build/dpkg_build/postinst.sh /usr/local/bin/initRobotFrameworkAIO.sh && \
    chmod +x /usr/local/bin/initRobotFrameworkAIO.sh && \

    # 5.2 System Assets: Copy Linux-specific icons and environment setup scripts
    cp ./config/build/dpkg_build/robot.ico /opt/rfwaio/linux/icon/ && \
    cp ./config/build/dpkg_build/set_robotenv.sh /opt/rfwaio/linux/ && \
    chmod +x /opt/rfwaio/linux/set_robotenv.sh && \

    # 5.3 Training & Docs: Copy tutorials and reference documentation
    # Use -a to preserve original file timestamps and permissions
    cp -R -a ../robotframework-tutorial/[0-9][0-9][0-9]_* /opt/rfwaio/tutorial/ && \
    # Ensure PDF documentation is available (ignores error if documentation build was skipped)
    cp ../robotframework-documentation/book/RobotFrameworkAIO_Reference*${SubVersion}.pdf /opt/rfwaio/documentation/ 2>/dev/null || true && \

    # 5.4 DevTools: Deploy external tools like Appium Inspector and AIO Analyzer
    cp -R -a ../devtools/. /opt/rfwaio/devtools/ && \
    chmod +x /opt/rfwaio/devtools/Appium-Inspector.AppImage && \
    cp ./config/tools/appium.sh /opt/rfwaio/devtools/appium && \
    chmod +x /opt/rfwaio/devtools/appium && \
    cp -R -a ./test/aio-analyzer /opt/rfwaio/tools/aio-analyzer && \

    # 5.5 Versioning: Store the build version file in the central directory
    cp ./version.txt /opt/rfwaio/ && \
    \
    # --- 6. DEEP CLEANUP ---
    # To minimize image size, we remove the source code of cloned repositories
    # and temporary files after the libraries are installed in site-packages.
    echo '>>>> Starting Deep Cleanup...' && \
    # Extract paths of all cloned repos from config and delete them
    conf_paths=\$(git config -f \"\$REPO_CONFIG\" --get-regexp '.path' | awk '{print \$2}') && \
    for path in \$conf_paths; do \
        rm -rf \"\$path\"; \
    done && \
    # Final wipe of temporary build artifacts and git histories
    rm -rf ./download ./output_lx && \
    find . -maxdepth 3 -name '.git' -exec rm -rf {} + && \
    rm -rf /tmp/* && \
    echo '>>>> Build and Cleanup finished successfully!'"

# Final System Path setup
ENV PATH="/app/devtools/nodejs/bin:/opt/rfwaio/bin:${PATH}"

# Default entry point
CMD ["robot"]