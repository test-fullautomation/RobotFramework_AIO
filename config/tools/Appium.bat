@echo off

REM UIAutomator2 driver need to find adb to be able to connect to the device

set path=%path%;
set ANDROID_HOME=%RobotDevtools%\Android
set APPIUM_HOME=%RobotNodeJS%

start "Appium" "%RobotAppium%"\appium

@echo on