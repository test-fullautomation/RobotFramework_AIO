#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bazel Configuration Documentation Generator

Recursively scans a directory for Bazel configuration files and generates
an HTML documentation with navigation structure matching the directory tree.

Usage:
    python generate_bazel_docs.py <root_directory> [--output <output_dir>]

Example:
    python generate_bazel_docs.py C:/workplace/ROBFW/components/bazel_aio
    python generate_bazel_docs.py . --output bazel_docs
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import yaml
import shutil


class BazelDocsGenerator:
    """Generate HTML documentation for Bazel configuration files."""
    
    # Bazel configuration files to search for
    BAZEL_FILES = [
        'BUILD.bazel',
        'BUILD',
        'WORKSPACE',
        'WORKSPACE.bazel',
        'MODULE.bazel',
        '.bazelrc',
        '.bazelversion',
    ]
    
    def __init__(self, root_dir: str, output_dir: str = 'bazel_docs'):
        """
        Initialize the documentation generator.
        
        Args:
            root_dir: Root directory to scan for Bazel files
            output_dir: Output directory for generated documentation
        """
        self.root_dir = Path(root_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.docs_dir = self.output_dir / 'docs'
        self.found_files: List[Tuple[Path, str]] = []
        
    def find_bazel_files(self) -> List[Tuple[Path, str]]:
        """
        Recursively find all Bazel configuration files.
        
        Returns:
            List of tuples (file_path, relative_path)
        """
        print(f"🔍 Scanning directory: {self.root_dir}")
        found = []
        
        for root, dirs, files in os.walk(self.root_dir):
            # Skip common non-relevant directories and Bazel symlink directories
            dirs[:] = [d for d in dirs if not (
                d in ['__pycache__', '.git', 'node_modules', 'venv', '.pytest_cache', '.vscode'] or
                d.startswith('bazel-')  # Bazel output/symlink directories
            )]
            
            for filename in files:
                if filename in self.BAZEL_FILES:
                    file_path = Path(root) / filename
                    rel_path = file_path.relative_to(self.root_dir)
                    found.append((file_path, str(rel_path)))
                    print(f"  ✓ Found: {rel_path}")
        
        self.found_files = sorted(found, key=lambda x: x[1])
        print(f"\n📊 Total files found: {len(self.found_files)}\n")
        return self.found_files
    
    def create_markdown_file(self, bazel_file_path: Path, rel_path: str) -> str:
        """
        Create a Markdown file documenting a Bazel configuration file.
        
        Args:
            bazel_file_path: Absolute path to the Bazel file
            rel_path: Relative path from root directory
            
        Returns:
            Name of the created Markdown file
        """
        # Create safe filename for markdown
        md_filename = rel_path.replace('/', '_').replace('\\', '_').replace('.', '_')
        md_filename = f"{md_filename}.md"
        
        # Read Bazel file content
        try:
            with open(bazel_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            content = f"❌ Error reading file: {e}"
        
        # Determine file type for syntax highlighting
        file_ext = bazel_file_path.suffix
        if file_ext in ['.bazel', '']:
            if bazel_file_path.name in ['BUILD', 'BUILD.bazel', 'MODULE.bazel']:
                lang = 'python'  # Starlark is Python-like
            elif bazel_file_path.name in ['WORKSPACE', 'WORKSPACE.bazel']:
                lang = 'python'
            else:
                lang = 'ini'  # .bazelrc
        else:
            lang = 'text'
        
        # Create markdown content
        md_content = f"""# {bazel_file_path.name}

**Pfad:** `{rel_path}`  
**Absoluter Pfad:** `{bazel_file_path}`  
**Typ:** {self._get_file_type_description(bazel_file_path.name)}

---

## Inhalt

```{lang}
{content}
```

---

## Datei-Informationen

- **Größe:** {bazel_file_path.stat().st_size} bytes
- **Zeilen:** {len(content.splitlines())}
- **Verzeichnis:** `{bazel_file_path.parent}`

---

## Navigation

**Übergeordnetes Verzeichnis:** `{bazel_file_path.parent.relative_to(self.root_dir) if bazel_file_path.parent != self.root_dir else '(Root)'}`

"""
        
        # Write markdown file
        md_file_path = self.docs_dir / md_filename
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return md_filename
    
    def _get_file_type_description(self, filename: str) -> str:
        """Get human-readable description of Bazel file type."""
        descriptions = {
            'BUILD.bazel': 'Bazel Build File (definiert Targets und Dependencies)',
            'BUILD': 'Bazel Build File (legacy name)',
            'WORKSPACE': 'Workspace Configuration (definiert externe Dependencies)',
            'WORKSPACE.bazel': 'Workspace Configuration',
            'MODULE.bazel': 'Bazel Module File (Bzlmod)',
            '.bazelrc': 'Bazel Configuration (Build-Optionen)',
            '.bazelversion': 'Bazel Version Lock File',
        }
        return descriptions.get(filename, 'Bazel Configuration File')
    
    def generate_properdocs_config(self) -> Dict:
        """
        Generate properdocs configuration with navigation tree.
        
        Returns:
            Dictionary with properdocs configuration
        """
        # Build navigation structure from directory tree
        nav_structure = self._build_nav_tree()
        
        config = {
            'site_name': f'Bazel Configuration Documentation - {self.root_dir.name}',
            'site_description': f'Automated documentation of Bazel configuration files in {self.root_dir}',
            'site_author': 'Bazel Docs Generator',
            'docs_dir': 'docs',
            'site_dir': 'bazel_config_doc',
            'theme': {
                'name': 'readthedocs',
                'language': 'de',
                'features': [
                    'navigation.tabs',
                    'navigation.sections',
                    'navigation.expand',
                    'toc.integrate',
                    'search.suggest',
                    'search.highlight',
                ]
            },
            'nav': nav_structure,
            'plugins': [
                {
                    'search': {
                        'lang': ['de', 'en']
                    }
                }
            ],
            'markdown_extensions': [
                'toc',
                'admonition',
                'codehilite',
                'def_list',
                'footnotes',
                'meta',
                'tables',
                'pymdownx.highlight',
                'pymdownx.superfences',
                'pymdownx.inlinehilite',
            ],
            'extra': {
                'version': '1.0',
            },
            'copyright': 'Copyright &copy; 2026 - Auto-generated Bazel Documentation',
        }
        
        return config
    
    def _build_nav_tree(self) -> List:
        """
        Build hierarchical navigation structure from found files.
        
        Returns:
            List representing properdocs navigation structure
        """
        if not self.found_files:
            return [{'Home': 'index.md'}]
        
        # Group files by directory
        dir_structure = {}
        for file_path, rel_path in self.found_files:
            dir_path = file_path.parent.relative_to(self.root_dir)
            
            if str(dir_path) not in dir_structure:
                dir_structure[str(dir_path)] = []
            
            md_filename = rel_path.replace('/', '_').replace('\\', '_').replace('.', '_') + '.md'
            display_name = f"{file_path.name} ({dir_path})" if dir_path != Path('.') else file_path.name
            dir_structure[str(dir_path)].append({display_name: md_filename})
        
        # Build navigation
        nav = [{'Übersicht': 'index.md'}]
        
        # Add root directory files first
        if '.' in dir_structure:
            root_section = {'Root Directory': dir_structure['.']}
            nav.append(root_section)
        
        # Add subdirectories
        sorted_dirs = sorted([d for d in dir_structure.keys() if d != '.'])
        for dir_path in sorted_dirs:
            section_name = dir_path.replace('\\', ' / ').replace('/', ' / ')
            nav.append({section_name: dir_structure[dir_path]})
        
        return nav
    
    def create_index_page(self) -> None:
        """Create index.md overview page."""
        # Statistics
        total_files = len(self.found_files)
        file_types = {}
        for file_path, _ in self.found_files:
            ftype = file_path.name
            file_types[ftype] = file_types.get(ftype, 0) + 1
        
        # Create directory tree visualization
        dir_tree = self._create_directory_tree()
        
        index_content = f"""# Bazel Configuration Documentation

**Projekt:** `{self.root_dir.name}`  
**Root-Pfad:** `{self.root_dir}`  
**Generiert am:** {self._get_timestamp()}

---

## Übersicht

Diese Dokumentation wurde automatisch generiert und zeigt alle Bazel-Konfigurationsdateien im Projekt.

### Statistik

- **Gesamt gefundene Dateien:** {total_files}

**Dateitypen:**

"""
        
        for ftype, count in sorted(file_types.items()):
            index_content += f"- **{ftype}:** {count} Datei(en) - _{self._get_file_type_description(ftype)}_\n"
        
        index_content += f"""

---

## Verzeichnisstruktur

```
{self.root_dir.name}/
{dir_tree}
```

---

## Navigation

Verwenden Sie das Navigationsmenü links, um zu den einzelnen Bazel-Konfigurationsdateien zu navigieren.

### Dateitypen erklärt

| Datei | Beschreibung |
|-------|--------------|
| **BUILD.bazel** | Definiert Build-Targets (py_library, py_test, etc.) und deren Dependencies |
| **WORKSPACE** | Konfiguriert externe Dependencies und Repositories |
| **MODULE.bazel** | Bazel Module Configuration (Bzlmod - neuer Dependency-Manager) |
| **.bazelrc** | Build-Optionen und Konfigurationsflags |
| **.bazelversion** | Locked Bazel Version für reproduzierbare Builds |

---

## Alle gefundenen Dateien

"""
        
        for file_path, rel_path in self.found_files:
            md_filename = rel_path.replace('/', '_').replace('\\', '_').replace('.', '_') + '.md'
            index_content += f"- [{rel_path}]({md_filename})\n"
        
        index_content += "\n---\n\n"
        index_content += "**Generiert mit:** `generate_bazel_docs.py`\n"
        
        # Write index file
        index_path = self.docs_dir / 'index.md'
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
    
    def _create_directory_tree(self) -> str:
        """Create ASCII directory tree representation."""
        tree_lines = []
        
        # Group by directory
        dirs = {}
        for file_path, rel_path in self.found_files:
            dir_path = file_path.parent.relative_to(self.root_dir)
            if str(dir_path) not in dirs:
                dirs[str(dir_path)] = []
            dirs[str(dir_path)].append(file_path.name)
        
        # Sort and format
        for dir_path in sorted(dirs.keys()):
            if dir_path == '.':
                for fname in sorted(dirs[dir_path]):
                    tree_lines.append(f"├── {fname}")
            else:
                tree_lines.append(f"├── {dir_path}/")
                for fname in sorted(dirs[dir_path]):
                    tree_lines.append(f"│   ├── {fname}")
        
        return '\n'.join(tree_lines)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def generate(self) -> None:
        """Main generation process."""
        print("=" * 70)
        print("🚀 Bazel Configuration Documentation Generator")
        print("=" * 70)
        print()
        
        # Step 1: Find all Bazel files
        self.find_bazel_files()
        
        if not self.found_files:
            print("❌ No Bazel configuration files found!")
            return
        
        # Step 2: Create output directory structure
        print(f"📁 Creating output directory: {self.output_dir}")
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 3: Generate Markdown files
        print(f"\n📝 Generating Markdown documentation...")
        for file_path, rel_path in self.found_files:
            md_filename = self.create_markdown_file(file_path, rel_path)
            print(f"  ✓ Created: {md_filename}")
        
        # Step 4: Create index page
        print(f"\n📄 Creating index page...")
        self.create_index_page()
        
        # Step 5: Generate properdocs.yml
        print(f"\n⚙️  Generating properdocs configuration...")
        config = self.generate_properdocs_config()
        config_path = self.output_dir / 'properdocs.yml'
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        print(f"  ✓ Created: {config_path}")
        
        # Step 6: Success message
        print("\n" + "=" * 70)
        print("✅ Documentation generation complete!")
        print("=" * 70)
        print(f"\n📂 Output directory: {self.output_dir}")
        print(f"📄 Config file: {config_path}")
        print(f"📚 Documentation files: {len(self.found_files)} files")
        print()
        print("🌐 To build and view the HTML documentation:")
        print(f"   cd {self.output_dir}")
        print(f"   properdocs build")
        print(f"   properdocs serve")
        print()
        print("   Then open: http://127.0.0.1:8000")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate HTML documentation for Bazel configuration files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_bazel_docs.py C:/workplace/ROBFW/components/bazel_aio
  python generate_bazel_docs.py . --output docs/bazel_config
  python generate_bazel_docs.py ../python-jsonpreprocessor -o bazel_docs
        """
    )
    
    parser.add_argument(
        'root_directory',
        help='Root directory to scan for Bazel configuration files'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='bazel_docs',
        help='Output directory for generated documentation (default: bazel_docs)'
    )
    
    args = parser.parse_args()
    
    # Validate root directory
    root_path = Path(args.root_directory)
    if not root_path.exists():
        print(f"❌ Error: Directory does not exist: {root_path}")
        sys.exit(1)
    
    if not root_path.is_dir():
        print(f"❌ Error: Not a directory: {root_path}")
        sys.exit(1)
    
    # Generate documentation
    generator = BazelDocsGenerator(args.root_directory, args.output)
    generator.generate()


if __name__ == '__main__':
    main()
