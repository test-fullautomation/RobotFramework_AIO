# Use the official Python 3.13 image based on Debian Bookworm
FROM python:3.13-bookworm

# Define build arguments
ARG VERSION=1
ARG AIO_DEB_PACKAGE

# Set environment variable to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install essential system tools and libraries
# Including 'sudo' as requested for the OSS version
RUN apt-get update && apt-get install -y \
    procps \
    curl \
    libxtst6 \
    liburi-perl \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the custom .deb packages into the container
COPY ${AIO_DEB_PACKAGE} ./packages/

# Install custom packages with a fallback for dependency resolution (-f)
RUN apt-get update && \
    (apt-get install -y ./packages/*.deb || apt-get install -y -f) && \
    rm -rf ./packages/ && \
    rm -rf /var/lib/apt/lists/*

# Set the path to include the Robot Framework AIO binaries
ENV PATH="/opt/rfwaio/bin:${PATH}"

# Default command to run Robot Framework
CMD ["robot"]