FROM debian:12-slim

ARG VERSION=1
ARG AIO_DEB_PACKAGE

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    procps \
    curl \
    libxtst6 \
    liburi-perl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ${AIO_DEB_PACKAGE} ./packages/

RUN apt-get update && \
    apt-get install -y ./packages/*.deb && \
    rm -rf ./packages/ && \
    rm -rf /var/lib/apt/lists/*

CMD ["robot"]