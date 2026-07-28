"""
Staging-Script: Kopiert Dateien in das Staging-Verzeichnis mit korrekter Pfadstruktur.
"""

import argparse
import shutil
import sys
from pathlib import Path


def extract_relative_path(full_path: str) -> str:
    """
    Extrahiert den relevanten relativen Pfad aus einem Bazel-Pfad.
    
    Zielstruktur:
        python.exe
        Lib/
            site-packages/
        DLLs/
        include/
        ...
    
    Beispiele:
        Input:  "external/+http_archive+python_portable_windows/python.exe"
        Output: "python.exe"
        
        Input:  "external/+http_archive+python_portable_windows/Lib/os.py"
        Output: "Lib/os.py"
        
        Input:  "bazel-out/.../site-packages/requests/__init__.py"
        Output: "Lib/site-packages/requests/__init__.py"
    """
    parts = Path(full_path).parts
    
    # Fall 1: Python-Runtime aus http_archive (python_portable_windows)
    # Suche nach dem Repository-Marker
    for i, part in enumerate(parts):
        if "python_portable" in part.lower():
            # Alles nach dem Repository-Namen ist der relative Pfad
            rel_parts = parts[i + 1:]
            if rel_parts:
                return str(Path(*rel_parts))
            break
    
    # Fall 2: site-packages aus pip_install
    # Diese müssen unter Lib/site-packages/ landen
    for i, part in enumerate(parts):
        if part == "site-packages":
            # Lib/site-packages/... 
            return str(Path("Lib", *parts[i:]))
    
    # Letzter Fallback: Nur Dateiname (sollte nicht passieren)
    print(f"WARNING: Konnte Pfad nicht auflösen: {full_path}")
    return Path(full_path).name


def main():
    parser = argparse.ArgumentParser(description="Stage files for installer")
    parser.add_argument("--output-dir", required=True, help="Staging-Verzeichnis")
    parser.add_argument("--manifest", required=True, help="Datei mit Liste der zu kopierenden Dateien")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Manifest lesen
    manifest = Path(args.manifest)
    if not manifest.exists():
        print(f"ERROR: Manifest nicht gefunden: {manifest}")
        sys.exit(1)

    with open(manifest, "r", encoding="utf-8") as f:
        files = [line.strip() for line in f if line.strip()]

    print(f"=== Staging {len(files)} Dateien nach {output_dir} ===")

    for src_path in files:
        src = Path(src_path)
        if not src.exists():
            print(f"WARNING: Datei nicht gefunden: {src}")
            continue

        rel_path = extract_relative_path(src_path)
        dest = output_dir / rel_path

        # Zielverzeichnis erstellen
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Kopieren
        if src.is_file():
            shutil.copy2(src, dest)
        elif src.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)

    print("=== Staging abgeschlossen ===")


if __name__ == "__main__":
    main()
