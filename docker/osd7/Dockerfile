# Use the official Python 3.13 image based on Debian Bookworm (Full version)
FROM python:3.13-bookworm

# Define build arguments
ARG VERSION=1
ARG AIO_DEB_PACKAGE="packages/*.deb"

# Set environment variable to prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install essential system tools and libraries for OSD 7
# procps: for process management
# libxtst6: for X11 Window System testing if required
# liburi-perl: to handle specific URI/file warnings seen in earlier builds
# Note: python3 and python3-pip are already included in the base image
RUN apt-get update && apt-get install -y \
    procps \
    libxtst6 \
    liburi-perl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory within the container
WORKDIR /app

# Copy the custom .deb packages into the container
COPY ${AIO_DEB_PACKAGE} ./packages/

# Install the custom Robot Framework AIO packages and perform cleanup
RUN apt-get update && \
    apt-get install -y ./packages/*.deb && \
    rm -rf ./packages/ && \
    rm -rf /var/lib/apt/lists/*

# Set the path to include the Robot Framework AIO binaries
ENV PATH="/opt/rfwaio/bin:${PATH}"

# Ensure the container starts the robot framework by default
CMD ["robot"]