# Accept parameters from Inno Setup installer
param(
    [string]$AppPath,
    [string]$InstallPath,
    [string]$BackupVSCodeDataPath
)

$Env:RobotTestPath=[System.Environment]::GetEnvironmentVariable("RobotTestPath","Machine")
$Env:RobotVsCode=[System.Environment]::GetEnvironmentVariable("RobotVsCode","Machine")
$Env:RobotToolsPath=[System.Environment]::GetEnvironmentVariable("RobotToolsPath","Machine")
$Env:RobotPythonPath=[System.Environment]::GetEnvironmentVariable("RobotPythonPath","Machine")

$WpPath = ([System.Uri]$Env:RobotTestPath).AbsoluteUri
$ToolsPath = ($Env:RobotToolsPath) -replace [RegEx]::Escape("\"),"\\"
$PyPath = ($Env:RobotPythonPath) -replace [RegEx]::Escape("\"),"\\"
$VscodePath = ($Env:RobotVsCode) -replace [RegEx]::Escape("\"),"\\"
$PyBin  = "/python3"  
$PyExe  = "\\python.exe"


$StoragePathFile = "$Env:RobotVsCode\data\user-data\User\globalStorage\storage.json"
$SettingsPathFile = "$Env:RobotVsCode\data\user-data\User\settings.json"
$VscodeLaunchPathFile = "$Env:RobotTestPath\.vscode\launch.json"

$StorageContent = (Get-Content -Path $StoragePathFile)

# Check if excluded files/folders exist (indicating existing installation with user data)
$RobotVsCodeDataPath = "$Env:RobotVsCode\data\"

# if (-Not (Test-Path -Path "D:\work\robotfw_build\RobotFramework_AIO\Output\extensions")) {
if (-Not (Test-Path -Path "$BackupVSCodeDataPath\extensions")) {
    Copy-Item -Path "$InstallPath\data\extensions" -Destination $RobotVsCodeDataPath -Recurse -Force
}
else {
    Copy-Item -Path "$BackupVSCodeDataPath\extensions" -Destination $RobotVsCodeDataPath -Recurse -Force
}

$SettingContent = (Get-Content -Path $SettingsPathFile) -replace '{RobotPythonPath}', $PyPath
$SettingContent = $SettingContent -replace $PyBin,$PyExe #-replace 'defaultInterpreterPath','pythonPath'

$SettingWindows = '
    // Execute file with EcomEmu
    "vs-external-tools.externalCommand1.command": "{RobotToolsPath}\\ConEmu\\ConEmu64.exe",
    "vs-external-tools.externalCommand1.args": ["$(ItemPath)"],
    "vs-external-tools.externalCommand1.cwd": "$(ItemDir)",
'

$KeyBindingContent = '
// Place your key bindings in this file to override the defaultsauto[]
[
    {
        "key": "ctrl+alt+r",
        "command": "vs-external-tools.externalCommand1"
    },
    {
        "key": "ctrl+f6",
        "command": "python.execInTerminal"
    }
]'

echo $SettingContent
($SettingContent -replace '// Other specific settings',$SettingWindows -replace '{RobotToolsPath}',$ToolsPath) | Set-Content -Path $SettingsPathFile
($StorageContent -replace '{RobotTestPath}',$WpPath -replace '{RobotVsCode}',$VscodePath) | Set-Content -Path $StoragePathFile
Set-Content -Path $Env:RobotVsCode\data\user-data\User\keybindings.json -Value $KeyBindingContent
(Get-Content -Path $VscodeLaunchPathFile) -replace '"type"\s*:\s*"robotframework-lsp"', '"type": "robotcode"' |  Set-Content -Path $VscodeLaunchPathFile