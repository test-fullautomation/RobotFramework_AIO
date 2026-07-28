"""
Build-Script für Inno Setup Installer.
Wird von Bazel als py_binary Tool aufgerufen.
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def get_iscc_version(iscc_path: str) -> tuple:
    """Ermittelt die ISCC-Version."""
    try:
        result = subprocess.run(
            [iscc_path],
            capture_output=True,
            text=True,
            check=False,  # ISCC gibt Exit-Code 1 ohne Argumente
        )
        # Output ist in stderr bei Fehler, stdout bei Erfolg
        output = result.stdout + result.stderr
        
        # Suche nach "Inno Setup X" oder "Inno Setup X.Y"
        match = re.search(r'Inno Setup (\d+)(?:\.(\d+))?', output)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2)) if match.group(2) else 0
            return (major, minor)
    except OSError as e:
        print(f"WARNING: Konnte ISCC-Version nicht ermitteln: {e}")
    return (0, 0)


def main():
    parser = argparse.ArgumentParser(description="Build Inno Setup Installer")
    parser.add_argument("--iscc", required=True, help="Pfad zu ISCC.exe")
    parser.add_argument("--iss", required=True, help="Pfad zur .iss Datei")
    parser.add_argument("--source-dir", required=True, help="Verzeichnis mit zu installierenden Dateien")
    parser.add_argument("--output", required=True, help="Ausgabepfad für die EXE")
    parser.add_argument("--version", default="1.0.0", help="Version für den Installer")
    parser.add_argument("--min-iscc-version", default="5.0", help="Minimale ISCC-Version (z.B. '6.3')")
    args = parser.parse_args()

    # Absoluten Output-Pfad ermitteln
    output_path = Path(args.output).resolve()
    output_dir = output_path.parent
    output_name = output_path.stem  # Ohne .exe

    # Source-Verzeichnis auflösen
    source_dir = Path(args.source_dir).resolve()

    print("=== Inno Setup Installer Build ===")
    print(f"ISCC:       {args.iscc}")
    print(f"ISS:        {args.iss}")
    print(f"Source:     {source_dir}")
    print(f"Output:     {output_path}")
    print(f"Version:    {args.version}")

    # Prüfen ob ISCC existiert
    if not Path(args.iscc).exists():
        print(f"ERROR: ISCC.exe nicht gefunden: {args.iscc}")
        sys.exit(1)

    # ISCC-Version prüfen
    iscc_version = get_iscc_version(args.iscc)
    print(f"ISCC Version: {iscc_version[0]}.{iscc_version[1]}")
    
    # Minimale Version parsen und prüfen
    min_parts = args.min_iscc_version.split('.')
    min_version = (int(min_parts[0]), int(min_parts[1]) if len(min_parts) > 1 else 0)
    
    if iscc_version < min_version:
        print(f"ERROR: ISCC-Version {iscc_version[0]}.{iscc_version[1]} ist zu alt!")
        print(f"       Benötigt wird mindestens Version {args.min_iscc_version}")
        print("       Bitte Inno Setup aktualisieren oder ISS-Datei anpassen.")
        sys.exit(1)

    # Prüfen ob Source-Verzeichnis existiert
    if not source_dir.exists():
        print(f"ERROR: Source-Verzeichnis nicht gefunden: {source_dir}")
        sys.exit(1)

    # Output-Verzeichnis erstellen
    output_dir.mkdir(parents=True, exist_ok=True)

    # Inno Setup aufrufen
    cmd = [
        args.iscc,
        f"/DSourceDir={source_dir}",
        f"/DOutputDir={output_dir}",
        f"/DAppVersion={args.version}",
        f"/F{output_name}",  # Output-Dateiname ohne .exe
        args.iss,
    ]

    print(f"\nAusführe: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Inno Setup fehlgeschlagen (Exit Code {e.returncode})")
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        sys.exit(1)

    # Prüfen ob Output erstellt wurde
    expected_output = output_dir / f"{output_name}.exe"
    if not expected_output.exists():
        print(f"ERROR: Erwartete Ausgabedatei nicht erstellt: {expected_output}")
        sys.exit(1)

    # Falls Output an anderem Ort erwartet wird, verschieben
    if expected_output != output_path:
        shutil.move(str(expected_output), str(output_path))

    print(f"\n=== Installer erfolgreich erstellt: {output_path} ===")


if __name__ == "__main__":
    main()
