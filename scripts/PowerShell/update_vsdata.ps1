# Accept parameters from Inno Setup installer
param(
    [string]$AppPath,
    [string]$BackupVSCodeDataPath
)

function Merge-Extensions {
    param(
        [string]$BackupFile,
        [string]$NewFile,
        [string]$OutputFile
    )

    Write-Host "Merging extensions..."

    # Read and parse JSON files
    $backupExtensions = Get-Content -Path $BackupFile -Raw | ConvertFrom-Json
    $newExtensions = Get-Content -Path $NewFile -Raw | ConvertFrom-Json

    # Create hashtable with backup extensions (keyed by identifier.id)
    $mergedHash = @{}
    foreach ($ext in $backupExtensions) {
        $key = $ext.identifier.id
        $mergedHash[$key] = $ext
    }

    # Add/overwrite with new extensions (new takes precedence)
    foreach ($ext in $newExtensions) {
        $key = $ext.identifier.id
        $mergedHash[$key] = $ext
    }

    # Convert back to array
    $mergedExtensions = @($mergedHash.Values)

    # Write to output file
    $mergedExtensions | ConvertTo-Json -Depth 100 | Set-Content -Path $OutputFile -Encoding UTF8

    Write-Host "Extensions merged successfully to $OutputFile"
}

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

if (Test-Path -Path "$BackupVSCodeDataPath\extensions") {
    Move-Item -Path "$RobotVsCodeDataPath\extensions" -Destination "$BackupVSCodeDataPath\extensions_new" -Force

    Copy-Item -Path "$BackupVSCodeDataPath\extensions" -Destination $RobotVsCodeDataPath -Recurse -Force

    Merge-Extensions -BackupFile "$BackupVSCodeDataPath\extensions\extensions.json" -NewFile "$RobotVsCodeDataPath\extensions_new\extensions.json" -OutputFile "$RobotVsCodeDataPath\extensions\extensions.json"

    # Copy items from extensions_new except extensions.json
    Get-ChildItem -Path "$BackupVSCodeDataPath\extensions_new" -Exclude "extensions.json" | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination "$RobotVsCodeDataPath\extensions" -Recurse -Force
    }
}

if (Test-Path -Path "$BackupVSCodeDataPath\globalStorage") {
    Copy-Item -Path "$BackupVSCodeDataPath\globalStorage" -Destination "$RobotVsCodeDataPath\user-data\User" -Recurse -Force
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

($SettingContent -replace '// Other specific settings',$SettingWindows -replace '{RobotToolsPath}',$ToolsPath) | Set-Content -Path $SettingsPathFile
($StorageContent -replace '{RobotTestPath}',$WpPath -replace '{RobotVsCode}',$VscodePath) | Set-Content -Path $StoragePathFile
Set-Content -Path $Env:RobotVsCode\data\user-data\User\keybindings.json -Value $KeyBindingContent
(Get-Content -Path $VscodeLaunchPathFile) -replace '"type"\s*:\s*"robotframework-lsp"', '"type": "robotcode"' |  Set-Content -Path $VscodeLaunchPathFile