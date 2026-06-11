#!/bin/bash
# Check if JAVA_HOME is already set
if [ -z "$JAVA_HOME" ]; then
    JDK_PATH=$(readlink -f $(which java) 2> /dev/null) 2> /dev/null
    if [ -n "$JDK_PATH" ]; then
        export JAVA_HOME=$(dirname $(dirname $JDK_PATH)) 2> /dev/null
    fi
fi

exec "$@"