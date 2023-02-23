param(
    [string]$configFile = "$((Split-Path $MyInvocation.MyCommand.Path -Parent) + '\..\..\config\projects\project.json')"
)

$json = Get-Content -Path $configFile -Raw | ConvertFrom-Json
$ScriptPath = Split-Path $MyInvocation.MyCommand.Path -Parent
Write-Host "Project config path: $configFile"

# Convert JSON back to InnoSetup file section
$i = 0
$innoSetupFilesOutput = $json | ForEach-Object {
    "Source: `"$($_.Source)`"; DestDir: `{code:GetUsrDataDir`}`\; Check: IsSelectedProject($i); Flags: ignoreversion onlyifdoesntexist uninsneveruninstall;"
    "Source: `"$($_.Source)`"; DestDir: `{code:GetUsrDataDir`}`\; DestName: RobotTest_config_template.json; Check: IsSelectedProject($i); Flags: ignoreversion onlyifdoesntexist uninsneveruninstall;"
    $i = $i+1
} | Out-String

$innoSetupCodeOutput = @'
[Code]
type
  TProjectHash = record
     Name  : TStringList;         // name of the project
     Index : TStringList;         // index which is forever fix 
                                  // for the initial project name.
     ListPosition : TStringList;  // Free list position must be unique.
  end;

var
  //holds the Project / Project Index Hash
  ProjectHash : TProjectHash;

procedure InitProjectHash();
begin
   //Initialize lists
   ProjectHash.Name  := TStringList.Create();
   ProjectHash.Index := TStringList.Create();
   ProjectHash.ListPosition := TStringList.Create();

'@

$i = 0
$innoSetupHashDefine = $json | ForEach-Object {
    "   ProjectHash.Index.Add`(`'$i`'`);  ProjectHash.Name.Add`(`'$($_.Name)`'`);"
    "   ProjectHash.ListPosition.Add`(`'$i`'`);" 
    $i = $i+1
} | Out-String
$innoSetupCodeOutput = "`r`n$innoSetupCodeOutput`r`n$innoSetupHashDefine"
$innoSetupCodeOutput = "$innoSetupCodeOutput`r`nend;"

$innoSetupFilesOutput = @"
[Files]
$innoSetupFilesOutput
$innoSetupCodeOutput
"@

# Save InnoSetup file to inno_new.iss file
New-Item -ItemType Directory -Force -Path "$ScriptPath\..\..\Output\Include"
$innoSetupFilesOutput | Out-File -Encoding Default -FilePath "$ScriptPath\..\..\Output\Include\install_projects.iss"
