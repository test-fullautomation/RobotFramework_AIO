; Inno Setup Script für Python Distribution
; Wird von Bazel gebaut

#ifndef SourceDir
  #define SourceDir "."
#endif

#ifndef OutputDir
  #define OutputDir "."
#endif

#ifndef AppVersion
  #define AppVersion "3.12.11"
#endif

[Setup]
AppName=Python Portable Environment
AppVersion={#AppVersion}
AppPublisher=Development Team
DefaultDirName={#OutputDir}\PythonPortable
DefaultGroupName=Python Portable
OutputDir={#OutputDir}
OutputBaseFilename=install_python
Compression=lzma2/max
SolidCompression=yes
; ArchitecturesInstallIn64BitMode=x64compatible  ; Benötigt Inno Setup 6.3+
; ArchitecturesAllowed=x64                          ; Für Inno Setup 5 kompatibel
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
; PrivilegesRequiredOverridesAllowed=dialog       ; Benötigt Inno Setup 6+

[Files]
; Python Runtime und installierte Module
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Python Console"; Filename: "{app}\python\python.exe"
Name: "{group}\{cm:UninstallProgram,Python Portable}"; Filename: "{uninstallexe}"

[Registry]
; Optional: PATH-Eintrag für aktuellen Benutzer
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\python"; Flags: preservestringtype; Check: NeedsAddPath(ExpandConstant('{app}\python'))

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER,
    'Environment',
    'Path', OrigPath)
  then begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + Param + ';', ';' + OrigPath + ';') = 0;
end;
