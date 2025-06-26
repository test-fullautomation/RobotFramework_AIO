#!/bin/bash
export ANDROID_HOME=/opt/rfwaio/devtools/Android/sdk; 
export APPIUM_HOME=/opt/rfwaio/devtools/nodejs/lib;
/opt/rfwaio/devtools/nodejs/bin/node /opt/rfwaio/devtools/nodejs/bin/appium "$@"