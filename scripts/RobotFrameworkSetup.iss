; Script generated by the Inno Setup Script Wizard.
;
; Online Help: http://www.jrsoftware.org/ishelp/
;
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!
;
#ifndef SETUPVersion
   #define SETUPVersion "0.1.4.0"
#endif
#pragma message "SETUPVersion is : " + SETUPVersion
;Change History

#define MyAppName "RobotFramework AIO (All In One)"

;Commandline argument 
;iscc /DRobotFrameworkVersion=version /DSETUPVersion=version
;allows to set a RobotFramework- and Setup version 
;If nothing is provided, then use an empty string. The resulting
;installer will be called __RobotFramework_setup__.exe in this case
;otherwise it is called   __RobotFramework_setup_RobotFrameworkVersion__SETUPVersion.exe
#ifndef RobotFrameworkVersion
   #define RobotFrameworkVersion ""
#endif
#pragma message "RobotFrameworkVersion is   : " + RobotFrameworkVersion

#ifdef ITrackService
   #define DoInstallTracking 
   #define InstallTrackingService StringChange(ITrackService,"\","/")
   #pragma message "ITrackService is: " + InstallTrackingService
#else
   #pragma message "ITrackService is: not defined"
#endif

#define MyAppVersion "RobotFramework AIO " + RobotFrameworkVersion + " (Installer " + SETUPVersion + ")"
#define MyAppFileName "RobotFramework_AIO_setup_" + RobotFrameworkVersion.
#define MyAppPublisher "Robert Bosch GmbH"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppID={{7E31B2B5-7E89-4E63-A321-EA5A00B4156F}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={sd}\Program Files\RobotFramework
DefaultGroupName=RobotFramework
DisableProgramGroupPage=yes
OutputBaseFilename={#MyAppFileName}
Compression=lzma/Max
SolidCompression=true
AppCopyright=Robert Bosch Car Multimedia GmbH
AppVerName={#MyAppVersion}
RestartIfNeededByRun=false
PrivilegesRequired=admin
ShowLanguageDialog=no
AlwaysRestart=true
AllowUNCPath=false
ChangesAssociations=true
ChangesEnvironment=true
OutputDir=..\Output\


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
;;;
;;; {code:GetUsrDataDir} directory
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;
;;; will be unchanged after inital installation
;;;
;write hello world visual code project
Source: ..\config\RobotTest\testcases\*; DestDir: {code:GetUsrDataDir}\testcases; Flags: ignoreversion onlyifdoesntexist uninsneveruninstall; Permissions: users-full;
;Manually add the launch.json file in hidden folder .vscode
Source: ..\config\RobotTest\testcases\.vscode\*; DestDir: {code:GetUsrDataDir}\testcases\.vscode; Flags: ignoreversion onlyifdoesntexist uninsneveruninstall; Permissions: users-full;

;;;
;;; post install script
;;;
;update visual stuidio code follow installer path
Source: .\PowerShell\update_vsdata.ps1; DestDir: "{tmp}"; Flags: ignoreversion; Permissions: users-full;

;;;
;;; will be overwritten with each new installation/update
;;;

;Tutorial installation
Source: "A:\robotframework-tutorial\*"; Excludes: ".git"; DestDir: {code:GetUsrDataDir}\tutorial; Flags: ignoreversion recursesubdirs overwritereadonly; Permissions: users-full;

;python 3.9 with RobotFramework and all installed packages delivered with Robot Framework AIO
Source: "A:\python39\*"; Excludes: ".git,*.pyc"; DestDir: {app}\python39; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: everyone-full;
 
;selftest installation
Source: "A:\robotframework-selftest\*"; Excludes: ".git"; DestDir: {app}\selftest; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: everyone-full;

;Visual Studio Code installation
Source: "A:\robotvscode\*"; Excludes: ".git"; DestDir: {app}\robotvscode; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: everyone-full;

;tools installation
Source: "..\config\tools\*"; Excludes: ".git,*.pyc"; DestDir: {app}\tools; Flags: ignoreversion recursesubdirs createallsubdirs; Permissions: everyone-full;

;Android related
;Source: "..\..\devtools\Windows\Android\*"; Excludes: ".git"; DestDir: {app}\devtools\Windows\Android; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist uninsneveruninstall; Permissions: users-full; Components: "Android"
;Source: "..\..\devtools\Windows\Appium\*"; Excludes: ".git"; DestDir: {app}\devtools\Windows\Appium; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist uninsneveruninstall; Permissions: users-full; Components: "Android"
;Source: "..\..\devtools\Windows\nodejs\*"; Excludes: ".git"; DestDir: {app}\devtools\Windows\nodejs; Flags: ignoreversion recursesubdirs createallsubdirs onlyifdoesntexist uninsneveruninstall; Permissions: users-full; Components: "Android"

[Icons]
;
;   DESKTOP
;
Name: {commondesktop}\HelloWorld.robot; Filename: {code:GetUsrDataDir}\testcases\HelloWorld.robot; WorkingDir: {code:GetUsrDataDir}\testcases;
Name: "{commondesktop}\Visual Code for RobotFramework"; Filename: {app}\robotvscode\VSCodium.exe; WorkingDir: {code:GetUsrDataDir}\testcases;

;
;   START MENU
;
;  !! Attention !! space after \ is intended. win10 sorts entries alphabetically and this bring the corresponding entries
;                  up before Android links
Name: "{group}\ Visual Code for RobotFramework"; Filename: {app}\robotvscode\VSCodium.exe; WorkingDir: {code:GetUsrDataDir};
Name: "{group}\ HelloWorld.robot"; Filename: {code:GetUsrDataDir}\testcases\HelloWorld.robot; WorkingDir: {code:GetUsrDataDir}\testcases\;
Name: "{group}\ TestCase Base Folder"; Filename: {code:GetUsrDataDir}\testcases; WorkingDir: {code:GetUsrDataDir}\testcases; 
Name: "{group}\ Tutorial Base Folder"; Filename: {code:GetUsrDataDir}\tutorial; WorkingDir: {code:GetUsrDataDir}\tutorial; 


[Types]
Name: Standard; Description: "Standard Installation"; 
Name: Full; Description: "Full installation of all components."; 

[Components]
Name: "RobotFramework_AIO_All_In_One"; Description: "All in One required to develop and execute RobotFramework test cases"; Flags: fixed; Types: Standard;
Name: "Android"; Description: "Android Tools required for Android based test cases (Appium-desktop, nodejs and Android platform-tools."; Types: Standard Full;

[Registry]
Root: HKCR; SubKey: .robot; ValueType: string; ValueData: RobotFramework.testcase.file; Flags: UninsDeleteKey;
Root: HKCR; SubKey: .resource; ValueType: string; ValueData: RobotFramework.resource.file; Flags: UninsDeleteKey;

Root: HKCR; SubKey: RobotFramework.testcase.file; ValueType: dword; ValueName: EditFlags; ValueData: 00000000; Flags: UninsDeleteKey;
Root: HKCR; SubKey: RobotFramework.testcase.file; ValueType: dword; ValueName: BrowserFlags; ValueData: 00000008; Flags: UninsDeleteKey;
Root: HKCR; SubKey: RobotFramework.testcase.file; ValueType: string; ValueData: "Robot Framework Test Case File"; Flags: UninsDeleteKey; 
Root: HKCR; SubKey: RobotFramework.testcase.file; ValueType: string; ValueName: AlwaysShowExt; Flags: UninsDeleteKey;
Root: HKCR; SubKey: RobotFramework.testcase.file\DefaultIcon; ValueType: string; ValueData:  "{app}\robotvscode\icons\robotframework_icon_132027.ico"; Flags: UninsDeleteKey; 
Root: HKCR; SubKey: RobotFramework.testcase.file\shell; ValueType: string; ValueData: &Open; Flags: UninsDeleteKey;
Root: HKCR; SubKey: RobotFramework.testcase.file\shell\&Open\command; ValueType: string; ValueData: """{app}\Python39\python.exe"" ""{app}\python39\scripts\robot-script.py"" ""%1"" %*"; Flags: UninsDeleteKey;
Root: HKCR; SubKey: RobotFramework.testcase.file\shell\&Open\ddeexec\Application; ValueType: string; ValueData: RobotFramework; Flags: UninsDeleteKey;
Root: HKCR; SubKey: RobotFramework.testcase.file\shell\&Open\ddeexec\Topic; ValueType: string; ValueData: System; Flags: UninsDeleteKey;

Root: HKCR; SubKey: RobotFramework.resource.file; ValueType: dword; ValueName: EditFlags; ValueData: 00000000; Flags: UninsDeleteKey;
Root: HKCR; SubKey: RobotFramework.resource.file; ValueType: dword; ValueName: BrowserFlags; ValueData: 00000008; Flags: UninsDeleteKey;
Root: HKCR; SubKey: RobotFramework.resource.file; ValueType: string; ValueData: "Robot Framework Resource File"; Flags: UninsDeleteKey; 
Root: HKCR; SubKey: RobotFramework.resource.file; ValueType: string; ValueName: AlwaysShowExt; Flags: UninsDeleteKey;
Root: HKCR; SubKey: RobotFramework.resource.file\DefaultIcon; ValueType: string; ValueData:  "{app}\robotvscode\icons\robotframework_icon_resource.ico"; Flags: UninsDeleteKey;


;Environment variables
Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: RobotPythonPath; ValueData: {app}\python39;
Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: RobotScriptPath; ValueData: {app}\python39\scripts;
Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: RobotVsCode; ValueData: {app}\robotvscode; 
Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: RobotToolsPath; ValueData: {app}\tools;
Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: RobotTestPath; ValueData: {code:GetUsrDataDir}\testcases;
Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: RobotLogPath; ValueData: {code:GetUsrDataDir}\logfiles;
Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: RobotTutorialPath; ValueData: {code:GetUsrDataDir}\tutorial;

; ROBFW Doesn't change ANDROID_HOME
; The idea is that the ROBFW Frameworks sets ANDRDOID_HOME locally for the ROBFW process(es) where ever required to the android sdk delivered with ROBFW Framework
; If Android SDK is installed and ANDROID_HOME is existing, then it will be locally overridden, but not globally by ROBFW installation.

;Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: expandsz; ValueName: Path; Check:NeedCreateEnvVar('ANDROID_HOME'); ValueData: "{olddata};{app}\devtools\Windows\Android\platform-tools\tools"; Components: "Android"
;Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: ANDROID_HOME; Check:NeedCreateEnvVar('ANDROID_HOME'); ValueData: {app}\devtools\Windows\Android\platform-tools; Components : "Android"

;Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: RobotNodeJS; ValueData: {app}\devtools\Windows\nodejs; Components: "Android"
;Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: RobotAndroidPlatformTools; ValueData: {app}\devtools\Windows\Android\platform-tools; Components: "Android"
;Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: RobotAppium; ValueData: {app}\devtools\Windows\Appium; Components: "Android"
;Root: HKLM; SubKey: "SYSTEM\CurrentControlSet\Control\Session Manager\Environment"; ValueType: string; ValueName: RobotDevtools; ValueData: {app}\devtools; Components: "Android"

;Switch off "Script need to long for IE": http://support.microsoft.com/kb/175500
Root: HKCU; SubKey: "Software\Microsoft\Internet Explorer\Styles"; ValueType: dword; ValueName: MaxScriptStatements; ValueData: $FFFFFFFF;

;enable VirtualTerminalLevel
Root: HKCU; SubKey: "Console"; ValueType: dword; ValueName: VirtualTerminalLevel; ValueData: 00000001;

[Dirs]
Name: {code:GetUsrDataDir}\testcases; Flags: UninsNeverUninstall; 
Name: {code:GetUsrDataDir}\testcases\config; Flags: UninsNeverUninstall; 
Name: {code:GetUsrDataDir}\testcases\lib; Flags: UninsNeverUninstall; 
Name: {code:GetUsrDataDir}\logfiles; Flags: UninsNeverUninstall; 
Name: {code:GetUsrDataDir}\testcases\doc; Flags: UninsNeverUninstall;
Name: {app}\robotvscode\data; Permissions: users-full; 

[INI]

[RUN]
Filename: "powershell.exe"; \
  Parameters: "-ExecutionPolicy Bypass -File ""{tmp}\update_vsdata.ps1"""; \
  WorkingDir: {app}; Flags: runhidden runasoriginaluser;
 
[UninstallRun]


[code]
// Helper type for mapping of Project Index to ListPosition.
// Name and Index are in a fix relationship. Listposition can be
// selected free to be free in the order of the displayed list.
// Inno scripts don't support own classes and THashStringList is not
// existing. Therefore use a record to store the data.
type
  TProjectHash = record
     Name  : TStringList;         // name of the project
     Index : TStringList;         // index which is forever fix 
                                  // for the initial project name.
     ListPosition : TStringList;  // Free list position must be unique.
  end;

var
  //MsgPage1: TOutputMsgWizardPage;
  MsgPage2: TOutputMsgWizardPage;
  MsgPage3: TOutputMsgWizardPage;
  //MsgPage4: TOutputMsgWizardPage;
  UsrDataDirPage: TInputDirWizardPage;
  ProjectPage : TWizardPage;
  ProjectListBox: TNewListBox;
  //holds the Project / Project Index Hash
  ProjectHash : TProjectHash;  
  

//
// Initialize the Project / Project Index Hash
// !!! The Name/Index releationship must be forever fix !!!
//     Otherwise wrong Project will be installed on update
//     of RobotFramework.
//////////////////////////////////////////////////////////////////
procedure InitProjectHash();
begin
   //Initialize lists
   ProjectHash.Name  := TStringList.Create();
   ProjectHash.Index := TStringList.Create();
   ProjectHash.ListPosition := TStringList.Create();
   
   ProjectHash.Index.Add('0');  ProjectHash.Name.Add('Generic');                          
   ProjectHash.ListPosition.Add('0');
   
   //ProjectHash.Index.Add('11');  ProjectHash.Name.Add('G3g');                                           
   //ProjectHash.ListPosition.Add('1');
   
   // don't display from here onwards
   //ProjectHash.Index.Add('8');  ProjectHash.Name.Add('Volvo ICM MCA');                                  
   //ProjectHash.ListPosition.Add('-1'); //don't display this
   
end;


//
// Maps a given ListPosition to a fix project index
//////////////////////////////////////////////////////////////
function GetIndexByListPosition(ListPosition:Integer):Integer;
var
  ProjectListCounter : Integer;
  res : Integer;
  
begin
   res := -1;
   for ProjectListCounter:=0 to ProjectHash.Name.Count-1 do
    begin
       if StrToInt(ProjectHash.ListPosition[ProjectListCounter])=ListPosition then
          begin
            res:=StrToInt(ProjectHash.Index[ProjectListCounter]);
          end;
    end;
    
    Result:=res; 
end;

//
// Maps a fix project index to a List Position
////////////////////////////////////////////////////////////
function GetListPositionByIndex(Index:Integer):Integer;
var
  ProjectListCounter : Integer;
  res : Integer;
  
begin
   res := -1;
   for ProjectListCounter:=0 to ProjectHash.Name.Count-1 do
    begin
       if StrToInt(ProjectHash.Index[ProjectListCounter])=Index then
          begin
            res:=StrToInt(ProjectHash.ListPosition[ProjectListCounter]);
          end;
    end;
    
    Result:=res; 
end;

//
// Gives write access to a protected Win7 folder
/////////////////////////////////////////////////////////////////////
procedure Win7GiveWriteAccess(sPath:String);
var
  ResultCode: Integer;
  sCmdBuffer: String;
  sCmdArgBuffer: String;
begin
  //at first take over ownership
  sCmdBuffer:='takeown'; 
  sCmdArgBuffer:=ExpandConstant('/S {computername} /U users /F "'+sPath+'\*" /R');
  Exec(sCmdBuffer,sCmdArgBuffer,'',SW_HIDE,ewWaitUntilTerminated,ResultCode);
  sCmdArgBuffer:=ExpandConstant('/S {computername} /U users /F "'+sPath+'" /R');
  Exec(sCmdBuffer,sCmdArgBuffer,'',SW_HIDE,ewWaitUntilTerminated,ResultCode);
  //for debugging
  //MsgBox(sCmdArgBuffer,mbInformation, MB_OK);
           
  //now grant access rights 
  sCmdBuffer:='icacls'; 
  sCmdArgBuffer:=ExpandConstant('"'+sPath+'" /grant users:F');
  Exec(sCmdBuffer,sCmdArgBuffer,'',SW_HIDE,ewWaitUntilTerminated,ResultCode);
           
  //now remove critical attributes
  sCmdBuffer:='attrib'; 
  sCmdArgBuffer:=ExpandConstant('-A -R -S "'+sPath+'" /S /D');
  Exec(sCmdBuffer,sCmdArgBuffer,'',SW_HIDE,ewWaitUntilTerminated,ResultCode);
end;

{ ///////////////////////////////////////////////////////////////////// }
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;


{ ///////////////////////////////////////////////////////////////////// }
function IsUpgrade(): Boolean;
begin
  Result := (GetUninstallString() <> '');
end;

{ ///////////////////////////////////////////////////////////////////// }
function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
{ Return Values: }
{ 1 - uninstall string is empty }
{ 2 - error executing the UnInstallString }
{ 3 - successfully executed the UnInstallString }

  { default return value }
  Result := 0;

  { get the uninstall string of the old app }
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;
//
// Called after each SetupStep
//////////////////////////////////////////////////////////////////////////////////
procedure CurStepChanged(CurStep: TSetupStep); 
var
  bUninstallerExists : Boolean;
  ResultCode: Integer;
  sUninstallCommand: String;
  sCmdBuffer: String;
  sCmdArgBuffer: String;
  i : Integer;
  Version: TWindowsVersion;
  
  sNewInstallation: String;
  sRobotFrameworkPath: String;
 
#ifdef DoInstallTracking
  WinHttpReq: Variant;
#endif

begin
  sNewInstallation:='True';  


  //directly before installation validate if Files are already existing.
  //If yes, call uninstaller to avoid mixed versions.
  if CurStep=ssInstall then
    begin
      //check if this is a new installation
      //idea is to check if the RobotFramework environment variables exist. If not, then RobotFramework was
      //most likely never installed - or properly uninstalled before installation
      // sRobotFrameworkPath:=ExpandConstant('{%RobotTestPath|False}');
      // if sRobotFrameworkPath<>'False' then
	  try
		if (IsUpgrade()) then
		begin
			sNewInstallation:='False';
			UnInstallOldVersion();
		end;
	  except
	  end;
             
      //uninstaller can be 001,002,003... This loop is to hit the proper number
//      for i:=0 to 9 do
//       begin
//          bUninstallerExists := FileExists(ExpandConstant('{app}\unins00'+IntToStr(i)+'.exe'));
//          if bUninstallerExists=True then
//            begin
//              try
                //in order to avoid uninstall problems due to read only files
                //remove "R"-attribute
//                sCmdBuffer:='attrib'
//                sCmdArgBuffer:=ExpandConstant('-R -A "{app}\AutoTest\*.*"  /D /S')
//                Exec(sCmdBuffer,sCmdArgBuffer,'',SW_HIDE,ewWaitUntilTerminated,ResultCode);
//              except
//              end;
              
              //seperate try block, otherwise uninstaller will not be executed
              //if attrib fails.
//              try
                //now call the uninstaller.
//                sUninstallCommand:=ExpandConstant('{app}\unins00'+IntToStr(i)+'.exe');  
//                Exec(sUninstallCommand,'/SILENT','',SW_SHOW,ewWaitUntilTerminated,ResultCode);
//              except
//              end;
//            end;
//       end;  // rof i:=0
    end; // fi CurStep=ssInstall then
    
  //directly after installation this will be executed
  if CurStep=ssPostInstall then
    begin
      GetWindowsVersionEx(Version);

      //if the platform is younger or equal to Windows Vista, then
      //win32com has a problem with creating the COM interface files
      //in gen_py folder.
      //In order to avoid this as post installation process the
      //ownership and accessrights will be transfered to the user who installes RobotFramework
      if (Version.NTPlatform) and (Version.Major>=6) then
        begin
           //
           // grant access rights for {app}\Python279\Lib\site-packages\win32com\gen_py
           //////////////////////////////////////////////////////////////////////////////////
//           Win7GiveWriteAccess('{app}\Python279\Lib\site-packages\win32com\gen_py');
        
           //
           // grant access rights for {app}\robotvscode\data folder
           //////////////////////////////////////////////////////////////////////////////////
           Win7GiveWriteAccess('{app}\robotvscode\data');
           
           //
           // grant access rights for ConEmu config file
           //////////////////////////////////////////////////////////////////////////////////
//           Win7GiveWriteAccess('{app}\ConEmu\ConEmu.xml');
           

        end;


#ifdef DoInstallTracking
        //installation tracking
        try
           WinHttpReq := CreateOleObject('WinHttp.WinHttpRequest.5.1');
           WinHttpReq.Open('GET', ExpandConstant('{#InstallTrackingService}?v={#MyAppVersion};u={username};m={computername};d={%USERDOMAIN};f='+sNewInstallation), false);
           WinHttpReq.Send();  
        except
           //ignore any issue. Setup must complete...
        end;
#endif


    end;
    
end;

//
// Called before Wizard is displayed
//////////////////////////////////////////////////////////////////////////////////
procedure InitializeWizard;
var
 StaticText : TNewStaticText;
 ProjectListCounter : Integer;
 i:Integer;
 
begin
  InitProjectHash();

  //create MsgPage1
  MsgPage2 := CreateOutputMsgPage(wpWelcome,
             'General Information', 'How to execute a RobotFramework test case?',
             'After installation any *.robot file is a directly executable file at your computer. As a result you can run a RobotFramework test case the following ways: '#13#13+
             '  1. Double click with the mouse.'#13#13+
             '  2. Directly from the command line.'#13#13+
             '  4. Directly from batch files.');
             
  //create MsgPage1
  MsgPage3 := CreateOutputMsgPage(MsgPage2.ID,
             'Update Information', 'How to update an already installed version?',
             'You can easily update RobotFramework AIO (All In One) with the following steps:'#13#13+
             '  1. General hint: make a backup of your data.'#13#13+
             '  2. Simply install the new version.'#13#13+
             '  3. Setup will recognize an already installed version and update.'#13#13+#13#13+
             'The uninstall-/install setup will take care of your test case files.');             
  
  //create page for selecting project  
  ProjectPage := CreateCustomPage(MsgPage3.ID, 
                           'RobotFramework AIO (All In One) configuration', 
                           'Please select here your project!');
  
  StaticText := TNewStaticText.Create(ProjectPage);
  StaticText.Top :=  ScaleY(0);
  StaticText.Caption := 'In order to configure the RobotFramework AIO (All In One) properly it is required to select '#13+'your project.'#13#13+'If your project is not listed, then please select "Generic":';
  StaticText.AutoSize := True;
  StaticText.Parent := ProjectPage.Surface;
  
  ProjectListBox := TNewListBox.Create(ProjectPage);
  ProjectListBox.Top := ScaleY(58);
  ProjectListBox.Width := ProjectPage.SurfaceWidth;
  ProjectListBox.Height := ScaleY(150);
  ProjectListBox.Parent := ProjectPage.Surface;
  
  //build up the list based on the ProjectHash and contained 
  //ProjectListbox positions
  for ProjectListCounter:=0 to ProjectHash.Name.Count-1 do
   begin
     //the list is unsorted => we have do search the whole Hash
     //which element has to be added to the ProjectListbox next.
     for i:=0 to ProjectHash.Name.Count-1 do
       begin
         if StrToInt(ProjectHash.ListPosition[i])=ProjectListCounter then
           begin;
             ProjectListBox.Items.Add(ProjectHash.Name[i]);
           end;
        end;
     end;
  
  //set focus to previous project or "unknown" in case of first installation
  ProjectListbox.ItemIndex:=GetListPositionByIndex(StrToInt(GetPreviousData('SelectedProject','0')))
    
  //create user data directory page
  UsrDataDirPage := CreateInputDirPage(wpSelectDir,
    'Select Test Case Data Directory', 'Where will the RobotFramework test case files be developed?',
    'Select the folder which Setup configures for the RobotFramework test case development, then click Next.',
    True, 'RobotTest');
  UsrDataDirPage.Add('');
  
  //initialize user data directory page with last directory
  UsrDataDirPage.Values[0] := GetPreviousData('UsrDataDir',ExpandConstant('{sd}\RobotTest'));

end;

//
// Returns selected project
//////////////////////////////////////////////////////////////////////////////////  
function IsSelectedProject(InputProject:Integer):Boolean;
begin  
  Result:=(GetIndexByListPosition(ProjectListBox.ItemIndex)=InputProject)
end;  

//
// Returns user data dir 
//////////////////////////////////////////////////////////////////////////////////
function GetUsrDataDir(Param:String):String;
begin  
  Result:=UsrDataDirPage.Values[0];
end;

//
// Updates the reade memo before displayed
//////////////////////////////////////////////////////////////////////////////////
function UpdateReadyMemo(Space, NewLine, MemoUserInfoInfo, MemoDirInfo, MemoTypeInfo,
  MemoComponentsInfo, MemoGroupInfo, MemoTasksInfo: String): String;
var
  sTextToDisplay: String;
  sProject: String;
begin
  { Fill the 'Ready Memo' with the normal settings and the custom settings }
  sProject:=ProjectListBox.Items.Strings[ProjectListBox.ItemIndex]
  
  //custom settings
  sTextToDisplay:='Your project:' + NewLine
  sTextToDisplay:=sTextToDisplay + '      ' + sProject 
  sTextToDisplay:=sTextToDisplay + NewLine + NewLine;
  
  //normal settings
  sTextToDisplay:=sTextToDisplay+ MemoDirInfo + NewLine + NewLine;
  
  //custom settings
  sTextToDisplay:=sTextToDisplay + 'Test case directory:' + NewLine  
  sTextToDisplay:=sTextToDisplay + '     ' + GetUsrDataDir('') + NewLine + NewLine;

  Result:=sTextToDisplay;
end;

//
// Registers the settings to be available in case of new run of setup for update
//////////////////////////////////////////////////////////////////////////////////
procedure RegisterPreviousData(PreviousDataKey: Integer);
begin
  SetPreviousData(PreviousDataKey, 'SelectedProject', IntToStr(GetIndexByListPosition(ProjectListBox.ItemIndex)));
  SetPreviousData(PreviousDataKey, 'UsrDataDir', GetUsrDataDir(''));
end;

function NeedCreateEnvVar(keyname: String): Boolean; 
begin
  if GetEnv(keyname) = '' then
    Result:=True
  else
    Result:=False;
end;

[UninstallDelete]
Name: {app}\robotvscode\*; Type: filesandordirs;
Name: {app}\python39\*; Type: filesandordirs;
Name: {app}\tools\*; Type: filesandordirs;
Name: {app}\selftest\*; Type: filesandordirs;
;Name: {app}\devtools\*; Type: filesandordirs;
Name: {code:GetUsrDataDir}\tutorial; Type: filesandordirs;

[InstallDelete]
Name: {app}\robotvscode\*; Type: filesandordirs;
Name: {app}\python39\*; Type: filesandordirs;
Name: {app}\tools\*; Type: filesandordirs;
Name: {app}\selftest\*; Type: filesandordirs;
;Name: {app}\devtools\*; Type: filesandordirs;
Name: {code:GetUsrDataDir}\tutorial; Type: filesandordirs;

