#!/bin/bash
UNAME=$(uname)
if [ "$UNAME" == "Linux" ] ; then
../python39lx/install/bin/python3 ./setup_binary.py download_pandoc
../python39lx/install/bin/python3 ./setup_binary.py bdist_wheel
fi
