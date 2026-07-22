SetTitleMatchMode, 2

Run, %comspec% /k, ./
WinWait, cmd.exe
WinWaitActive, cmd.exe

Sleep, 500

SendInput C:\workplace\RobotFramework\python3\Scripts\properdocs.exe build

