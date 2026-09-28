; Inno Setup Script für Framework Distribution
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

; Name of the Bazel target that produced this installer (e.g. "installer_set_1").
; Used as the default installation directory name so that different installer
; variants (installer_set_1, installer_set_2, ...) don't collide when
; installed side by side, and so the suggested folder name always matches
; the Bazel target that built it.
#ifndef TargetName
  #define TargetName "framework"
#endif

[Setup]
AppName=Test Environment TNG
AppVersion={#AppVersion}
AppPublisher=Development Team
; Default install directory name = the Bazel target name (e.g. "installer_set_1").
; Python and VS Code are staged into separate subdirectories underneath it
; (see [Files] below and components/installer/stage_files.py), so they never
; mix inside the installation folder even though both originate from the
; same installer.
DefaultDirName={#OutputDir}\{#TargetName}
DefaultGroupName=Portable FW
OutputDir={#OutputDir}
OutputBaseFilename=install_fw
Compression=lzma2/max
SolidCompression=yes
; ArchitecturesInstallIn64BitMode=x64compatible  ; Benötigt Inno Setup 6.3+
; ArchitecturesAllowed=x64                          ; Für Inno Setup 5 kompatibel
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
; PrivilegesRequiredOverridesAllowed=dialog       ; Benötigt Inno Setup 6+

[Files]
; All staged files (Python runtime + modules under Python/, VS Code
; under VSCode/ - see stage_files.py's extract_relative_path()) are copied
; as-is, preserving the subdirectory structure already established during
; staging.
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Python Console"; Filename: "{app}\Python\python.exe"
Name: "{group}\Visual Studio Code"; Filename: "{app}\VSCode\Code.exe"
Name: "{group}\{cm:UninstallProgram,Python Portable}"; Filename: "{uninstallexe}"

[Run]
; "Solution 2b" (see pip_utils/pip_install.bzl and
; installer/reinstall_console_scripts.py for the full rationale): console-
; script launchers (e.g. rst2latex.exe) that were generated DURING THE
; BAZEL BUILD have a non-relocatable, build-time-only shebang path baked
; in by pip and fail once copied to their real installed location. Fix:
; run reinstall_console_scripts.py exactly once here, at the END of
; installation, using the python.exe that was JUST installed at its REAL,
; final location ({app}\Python\python.exe) - it reinstalls every bundled
; wheel (staged under {app}\Python\_wheels, see stage_files.py's
; "py-wheels" mapping) fully offline (--no-index --find-links=...), which
; makes pip regenerate every launcher with a shebang pointing at THIS
; correct, final interpreter, regardless of where the installer was run.
;
; Flags:
;   runhidden          - no visible console window flashing during install
;   waituntilterminated - installation does not continue/finish until this
;                         step completes, so the launchers are guaranteed
;                         ready by the time the installer exits
Filename: "{app}\Python\python.exe"; Parameters: """{app}\Python\_wheels\reinstall_console_scripts.py"""; WorkingDir: "{app}\Python"; StatusMsg: "Finalizing console scripts..."; Flags: runhidden waituntilterminated

[Registry]
; Optional: PATH-Eintrag für aktuellen Benutzer
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\Python"; Flags: preservestringtype; Check: NeedsAddPath(ExpandConstant('{app}\Python'))

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
