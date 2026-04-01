FROM ubuntu:22.04

ARG VERSION=1
ARG AIO_DEB_PACKAGE

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    sudo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ${AIO_DEB_PACKAGE} ./packages/

RUN apt-get update && \
    apt-get install -y ./packages/*.deb || apt-get install -y -f && \
    rm -rf ./packages/

ENV PATH="/opt/rfwaio/bin:${PATH}"

CMD ["robot"]