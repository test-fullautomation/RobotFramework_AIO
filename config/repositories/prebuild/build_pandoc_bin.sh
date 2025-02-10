#!/bin/bash
UNAME=$(uname)
if [ "$UNAME" == "Linux" ] ; then
../python3lx/install/bin/python3 ./setup_binary.py download_pandoc
../python3lx/install/bin/python3 ./setup_binary.py bdist_wheel
fi
