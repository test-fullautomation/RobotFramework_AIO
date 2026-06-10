# Stage 1: Builder
# Use the official Python 3.13 image based on Debian Bookworm Slim
FROM python:3.13-slim-bookworm AS builder

# --- Build Arguments ---
ARG VERSION_TYPE="extended"
ARG TAG_NAME="dev/aio/0.0.0"
ARG VARIANT="OSS"
ARG BUNDLE_NAME="--bundle_name 'RobotFramework AIO'"
ARG AIO_NAME="RobotFramework AIO"
ARG GENDOC_PLANTUML_PATH="../robotvscode/data/extensions/jebbs.plantuml-2.18.1"
ARG GITHUB_COPILOT_REF_URL=""
ARG GITHUB_COPILOT_EXT_ARG=""
ARG INSTALLER_LOCATION=""
ARG REPO_CONFIG="./config/repositories/repositories_extended.conf"
ARG MAINDOC_CONFIGFILE="./maindoc/maindoc_configs/maindoc_config_OSS_extended.json"

# --- Environment Variables (Migrated from postinst.sh and set_robotenv.sh) ---
ENV BUILD_ENV="docker" \
    AIO_HOME="/opt/rfwaio" \
    AIO_TEST="/root/RobotTest" \
    PYTHON_HOME="/usr/local"

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Step 1: Install system-level dependencies and Setup Groups (OSS uses OpenJDK 17)
RUN apt-get update && apt-get install -y --fix-missing \
    sudo curl git procps libxtst6 liburi-perl sed \
    unzip xz-utils zstd dos2unix \
    pkg-config build-essential python3-dev \
    libcairo2-dev libxt-dev libgirepository1.0-dev

# Create 'robot-aio' group from postinst.sh logic
RUN groupadd -r robot-aio && usermod -a -G robot-aio root

# Step 2: Copy source code
COPY . .

# Step 3: Full Build, Mimic Installation & Permission Logic
RUN dos2unix ./docker/docker-build.sh && \
    chmod +x ./docker/docker-build.sh && \
    ./docker/docker-build.sh

# Stage 2: Final
FROM python:3.13-slim-bookworm

ARG VERSION_TYPE
ARG AIO_NAME
# --- Environment Variables (Migrated from postinst.sh and set_robotenv.sh) ---
ENV AIO_HOME="/opt/rfwaio" \
    AIO_TEST="/root/RobotTest" \
    PYTHON_HOME="/usr/local"

ENV DEBIAN_FRONTEND=noninteractive \
    AIO_NAME="${AIO_NAME}" \
    SubVersion="${VERSION_TYPE}" \
    # Python & Packages
    RobotPythonPath="${PYTHON_HOME}/bin" \
    RobotScriptPath="${PYTHON_HOME}/bin" \
    RobotPythonSitePackagesPath="${PYTHON_HOME}/lib/python3.13/site-packages" \
    # Tools & Dev
    RobotToolsPath="${AIO_HOME}/tools" \
    RobotDevtools="${AIO_HOME}/devtools" \
    RobotNodeJS="${AIO_HOME}/devtools/nodejs" \
    RobotAppium="${AIO_HOME}/devtools/nodejs/bin" \
    RobotAndroidPlatformTools="${AIO_HOME}/devtools/Android/platform-tools" \
    # Workspace
    RobotTestPath="${AIO_TEST}/testcases" \
    RobotLogPath="${AIO_TEST}/logfiles" \
    RobotTutorialPath="${AIO_TEST}/tutorial"

RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo curl git procps libxtst6 openjdk-17-jdk-headless \
    libmariadb-dev-compat libmariadb-dev libmariadb3 \
    && groupadd -r robot-aio && usermod -a -G robot-aio root \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local
COPY --from=builder /opt/rfwaio /opt/rfwaio
COPY --from=builder /root/RobotTest /root/RobotTest

RUN ln -sf /usr/local/bin/python3 /usr/local/bin/python && \
    mkdir -p /opt/rfwaio/python3/bin && \
    ln -sf /usr/local/bin/python3 /opt/rfwaio/python3/bin/python3 && \
    mkdir -p /opt/rfwaio/robotvscode/data/extensions/jebbs.plantuml-2.18.1 && \
    cp /usr/local/lib/plantuml/plantuml.jar /opt/rfwaio/robotvscode/data/extensions/jebbs.plantuml-2.18.1/plantuml.jar && \
    test -s /opt/rfwaio/robotvscode/data/extensions/jebbs.plantuml-2.18.1/plantuml.jar

# Final Path setup - Updated to reflect /opt/rfwaio structure
ENV PATH="${RobotPythonPath}:${RobotAppium}:${RobotAndroidPlatformTools}:/opt/rfwaio/linux:${PATH}"

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]