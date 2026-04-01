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

WORKDIR /app

# Step 1: Install system-level dependencies
RUN apt-get update && apt-get install -y --fix-missing \
    sudo curl git procps libxtst6 liburi-perl sed \
    unzip xz-utils zstd \
    openjdk-17-jdk-headless \
    pandoc

# Step 2: Copy source code
COPY . .
RUN chmod +x ./requirements_linux.sh ./cloneall ./install/install.sh ./install/python_requirements_lx.lock ./install/python_requirements_lx.txt  ./build

# Step 3: Install Python requirements (Populates system Python 3.13)
RUN ./requirements_linux.sh

RUN python3 -m pip install --no-cache-dir build

RUN python3 -m pip install --no-cache-dir -r ./install/python_requirements_lx.txt

# Step 4: Clone all sub-repositories (Separated for easier debugging of network/git issues)
RUN ./cloneall --config-file="${REPO_CONFIG}"

# Step 5: Install Android and NodeJS components
RUN ./install/install.sh --android

# Step 6: Build Documents and Install Libraries
# Note: Redirect the script to use system Python path instead of python3lx
RUN sed -i 's|../python3lx|/usr/local|g' build && \
    sed -i 's|${PYDIR}/bin/python3|/usr/local/bin/python3|g' build

# Step 6: Build with Minimal Necessary Environment
RUN /bin/bash -e -c " \
    export TAG_NAME='${TAG_NAME}' && \
    export AIO_VERSION_DATE=\$(date +%m.%Y) && \
    export AIO_VERSION=\${TAG_NAME#[rd]e[vl]/aio/} && \
    export RobotFrameworkVersion=\${TAG_NAME#[rd]e[vl]/aio/} && \
    export BUNDLE_VERSION_DATE=\"--bundle_version_date \$(date +%m.%Y)\" && \
    export BUNDLE_VERSION=\"--bundle_version \${TAG_NAME#[rd]e[vl]/aio/}\" && \
    \
    source ./include/bash/common.sh && \
    source ./build --config-file=\$REPO_CONFIG --sub-version=\$SubVersion && \
    generate_version_info && \
    check_and_install_texlive && \
    create_testsuitmanagement_package_context_file && \
    parse_config \"\$ConfigFile\" && \
    \
    echo '>>>> Build finished successfully!'"

# Step 7: Final Cleanup (Note: This only cleans the current layer)
RUN rm -rf ./download && \
    find . -maxdepth 3 -name ".git" -exec rm -rf {} + && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Final Path setup
ENV PATH="/app/devtools/nodejs/bin:/opt/rfwaio/bin:${PATH}"

CMD ["robot"]