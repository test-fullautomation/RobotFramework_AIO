#NoEnv
#SingleInstance Force
SetWorkingDir, %A_ScriptDir%

; ── Konfiguration ──────────────────────────────────────────────────────────────
serverPort := 8084
serverUrl  := "http://localhost:" . serverPort . "/index.html"

; ── Umgebungsvariable explizit auslesen ───────────────────────────────────────
EnvGet, RobotPythonPath, RobotPythonPath

If (RobotPythonPath = "")
{
    MsgBox, 16, Fehler, Die Umgebungsvariable RobotPythonPath ist nicht gesetzt!
    ExitApp
}

; ── 1. Server starten und PID speichern ───────────────────────────────────────
Run, cmd.exe /k "cd /d "%A_ScriptDir%\bazel_config_doc" && "%RobotPythonPath%\python.exe" -m http.server %serverPort%",, , cmdPID

; MsgBox, 16, Info, cmdPID: %cmdPID%

; ── 2. Warten bis Server bereit ist, dann Firefox öffnen ──────────────────────
Sleep, 2000

; Alle bestehenden Firefox-Fenster IDs merken (vor dem Start)
existingWindows := ""
WinGet, windowList, List, ahk_exe firefox.exe
Loop, %windowList%
{
    existingWindows .= windowList%A_Index% . "|"
}

Run, firefox.exe %serverUrl%

; ── 3. Warten bis NEUES Firefox-Fenster erscheint und ID speichern ────────────
docWindowID := 0
attempts := 0
maxAttempts := 10

Loop
{
    attempts++
    Sleep, 1000
    
    WinGet, windowList, List, ahk_exe firefox.exe
    Loop, %windowList%
    {
        windowID := windowList%A_Index%
        
        ; Prüfen ob dies ein neues Fenster ist (nicht in existingWindows)
        IfNotInString, existingWindows, %windowID%|
        {
            ; Neues Fenster gefunden
            docWindowID := windowID
            break 2  ; Beide Loops verlassen
        }
    }
    
    If (attempts >= maxAttempts)
        break
}

If (docWindowID = 0)
{
    MsgBox, 48, Warnung, Dokumentations-Fenster konnte nicht identifiziert werden.`nServer läuft weiter auf Port %serverPort%.
    ExitApp
}

; ── 4. Spezifisches Dokumentations-Fenster überwachen ─────────────────────────
Loop
{
    Sleep, 3000  ; alle 3 Sekunden prüfen

    IfWinNotExist, ahk_id %docWindowID%
    {
        ; Dokumentations-Fenster wurde geschlossen → Server und cmd beenden
        ; Zuerst den gesamten Prozessbaum killen (cmd + python als Child)
        RunWait, cmd.exe /c taskkill /f /pid %cmdPID% /t,, Hide
        
        ; Zur Sicherheit auch noch Process Close
        Process, Close, %cmdPID%
        
        ExitApp
    }
}
