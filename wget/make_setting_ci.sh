#!/bin/bash

mypath=$(realpath $(dirname $0))
proxyPath=$mypath/settings.ini

echo '[proxy]' > "$proxyPath"
echo 'enable=yes' >> "$proxyPath"
echo "password=${PROXY_PASSWORD}" >> "$proxyPath"
echo "proxy=rb-proxy-apac.bosch.com:8080" >> "$proxyPath"
echo "username=${PROXY_USERNAME}" >> "$proxyPath"

