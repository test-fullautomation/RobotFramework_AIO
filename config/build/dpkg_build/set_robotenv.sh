#!/bin/bash

#create environment variables
export RobotPythonPath=/opt/rfwaio/python39/install/bin
export RobotScriptPath=/opt/rfwaio/python39/install/bin
export RobotVsCode=/opt/rfwaio/robotvscode
export RobotToolsPath=/opt/rfwaio/tools
export RobotTestPath=~/RobotTest/testcases
export RobotLogPath=~/RobotTest/logfiles
export RobotTutorialPath=~/RobotTest/tutorial
export GENDOC_PLANTUML_PATH=$RobotVsCode/data/extensions/jebbs.plantuml-2.17.5


# Check if JAVA_HOME is already set
if [ -z "$JAVA_HOME" ]; then
    # Find the path of OpenJDK using the update-alternatives command
    JDK_PATH=$(update-alternatives --query javac | grep 'Value: ' | grep -o '/.*/bin/java')
    
    if [ -n "$JDK_PATH" ]; then
        # Export JAVA_HOME if OpenJDK path is found
        export JAVA_HOME=$(dirname $(dirname $JDK_PATH))
        echo "JAVA_HOME set to $JAVA_HOME"
    fi
fi
