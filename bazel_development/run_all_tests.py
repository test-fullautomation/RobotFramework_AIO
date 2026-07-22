#!/usr/bin/env python3
"""
run_all_tests.py - Generic Bazel Test Runner

Runs all Bazel test targets separately. Supports multiple test frameworks:
- pytest: Isolation of pytest.ini configurations
- Robot Framework: Execution of Robot tests with separate configurations

Each module can use its own framework configuration.
Prevents conflicts with module-specific settings (junit_suite_name, log_level, etc.).

Usage:
    python run_all_tests.py                          # all tests
    python run_all_tests.py --pattern "//test_trigger/components/..."
    python run_all_tests.py --continue-on-error      # don't stop in case of errors
    python run_all_tests.py --verbose                # dertailled console output
"""

import subprocess
import sys
import os
import shutil
import argparse
from pathlib import Path
from typing import List, Tuple
from colorama import Fore, Style, init

init(autoreset=True)


class BazelTestRunner:
    """Runs Bazel tests separately. Supports pytest and Robot Framework."""

    def __init__(self, continue_on_error: bool = False, verbose: bool = False,
                 workspace_root: str = None, logfile_base_dir: str = None, no_cache: bool = False):
        self.continue_on_error = continue_on_error
        self.verbose = verbose
        self.no_cache = no_cache
        self.results: List[Tuple[str, bool, str]] = []

        # Workspace root (default: aktuelles Verzeichnis)
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()

        # Basis-Verzeichnis für Logdateien (default: test_logfiles im Workspace)
        if logfile_base_dir:
            self.logfile_base_dir = Path(logfile_base_dir)
        else:
            self.logfile_base_dir = self.workspace_root / "test_logfiles"

        # Get and validate Bazel executable from environment
        self.bazel_exe = self.get_bazel_executable()

    @staticmethod
    def get_bazel_executable() -> str:
        """
        Retrieves the Bazel executable path from the BAZEL_EXEC environment variable.

        Returns:
            Path to bazel.exe

        Raises:
            SystemExit: If BAZEL_EXEC is not set or executable doesn't exist
        """
        bazel_exec = os.environ.get('BAZEL_EXEC')

        if not bazel_exec:
            print(f"{Fore.RED}✗ ERROR: Environment variable 'BAZEL_EXEC' is not set!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please set BAZEL_EXEC to the path of your Bazel executable.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Example: set BAZEL_EXEC=C:\\TAF\\tools\\bazelisk\\bazel.exe{Style.RESET_ALL}")
            sys.exit(1)

        bazel_path = Path(bazel_exec)
        if not bazel_path.exists():
            print(f"{Fore.RED}✗ ERROR: Bazel executable not found: {bazel_exec}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please verify the BAZEL_EXEC environment variable points to a valid executable.{Style.RESET_ALL}")
            sys.exit(1)

        return str(bazel_path)

    def derive_logfile_path(self, target: str) -> str:
        """
        Derives the path and name of the JUnit XML log file from the Bazel target.

        Example:
            Target: //test_trigger/components/py_test_module_1:execute_py_test_module_1
            Logfile: {workspace_root}/test_logfiles/components/py_test_module_1/py_test_module_1_log.xml

        Args:
            target: Bazel Target (z.B. "//test_trigger/components/module:target_name")

        Returns:
            Absolute path to the JUnit XML log file
        """
        # Parse Target: //test_trigger/components/py_test_module_1:execute_py_test_module_1
        # Remove leading "//"
        target_path = target.lstrip('/')

        # Trenne Package-Pfad von Target-Name
        if ':' in target_path:
            package_path, target_name = target_path.split(':', 1)
        else:
            # Wenn kein ":" vorhanden, ist Target-Name = letzter Teil des Pfads
            parts = target_path.split('/')
            package_path = '/'.join(parts[:-1])
            target_name = parts[-1]

        # Extrahiere relativen Pfad ab "components"
        # z.B. test_trigger/components/py_test_module_1 -> components/py_test_module_1
        if '/components/' in package_path:
            relative_path = package_path.split('/components/', 1)[1]
            relative_dir = f"components/{relative_path}"
        else:
            # Fallback: Verwende kompletten Package-Pfad
            relative_dir = package_path.replace('/', '_')

        # Extrahiere Modulname aus Target-Name
        # z.B. execute_py_test_module_1 -> py_test_module_1
        if target_name.startswith('execute_'):
            module_name = target_name.replace('execute_', '', 1)
        else:
            module_name = target_name

        # Konstruiere Logfile-Pfad
        # Format: {workspace_root}/test_logfiles/components/{module_path}/{module_name}_log.xml
        logfile_path = self.logfile_base_dir / relative_dir / f"{module_name}_log.xml"

        # Erstelle Verzeichnis falls nicht vorhanden
        logfile_path.parent.mkdir(parents=True, exist_ok=True)

        # Konvertiere zu absoluten Pfad mit Forward-Slashes (Bazel-kompatibel)
        return str(logfile_path.absolute()).replace('\\', '/')

    def detect_framework_type(self, target: str) -> str:
        """
        Detects which test framework a target uses.

        Heuristic:
        - If 'robot' within target name or package path: Robot Framework
        - Else: pytest (default)

        Args:
            target: Bazel Target (z.B. "//test_trigger/components/robot_module_1:execute_robot_module_1")

        Returns:
            Framework-Typ: 'pytest' oder 'robot'
        """
        target_lower = target.lower()

        # Prüfe auf Robot Framework Indikatoren
        if 'robot' in target_lower:
            return 'robot'

        # Default: pytest
        return 'pytest'

    def get_xml_filename(self, framework_type: str) -> str:
        """
        Returns the framework-specific XML file name.

        Args:
            framework_type: Framework-Typ ('pytest' oder 'robot')

        Returns:
            XML-Dateiname im test.outputs Verzeichnis
        """
        xml_filenames = {
            'pytest': 'pytest_results.xml',
            'robot': 'robot_results.xml',
        }
        return xml_filenames.get(framework_type, 'test_results.xml')

    def copy_test_xml_from_test_outputs(self, target: str, dest_logfile: str) -> bool:
        """
        Copies the test XML file from bazel-testlogs/test.outputs to the desired destination.

        Supports several frameworks:
        - pytest: pytest_results.xml
        - Robot Framework: robot_results.xml

        With 'bazel test', the test framework writes the XML to TEST_UNDECLARED_OUTPUTS_DIR.
        Bazel automatically copies it to bazel-testlogs/{target}/test.outputs/{framework}_results.xml
        This method then copies the file to the predetermined destination.

        Args:
            target: Bazel Target (z.B. "//test_trigger/components/py_test_module_2:execute_py_test_module_2")
            dest_logfile: Ziel-Pfad für die XML-Logdatei

        Returns:
            True if copied successfully, otherwise False
        """
        # Detect framework type
        framework_type = self.detect_framework_type(target)
        xml_filename = self.get_xml_filename(framework_type)

        if self.verbose:
            print(f"{Fore.CYAN}  Framework: {framework_type}, XML: {xml_filename}{Style.RESET_ALL}")

        # Parse target path
        target_path = target.lstrip('//')
        if ':' in target_path:
            package_path, target_name = target_path.split(':', 1)
        else:
            parts = target_path.split('/')
            package_path = '/'.join(parts[:-1])
            target_name = parts[-1]

        # Create Bazel test.outputs path
        # Format: bazel-testlogs/{package_path}/{target_name}/test.outputs/{framework}_results.xml
        test_xml = self.workspace_root / "bazel-testlogs" / package_path / target_name / "test.outputs" / xml_filename

        if not test_xml.exists():
            print(f"{Fore.YELLOW}⚠ {xml_filename} not found: {test_xml}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}  Possibly, {framework_type} did not create the XMLt (Test error?){Style.RESET_ALL}")
            return False

        try:
            # Copy pytest XML to destination
            dest_path = Path(dest_logfile)
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # If target exists, delete (prevents permission errors)
            if dest_path.exists():
                try:
                    dest_path.chmod(0o666)  # Define access rights, if read-only
                    dest_path.unlink()
                except Exception as del_error:  # noqa: BLE001
                    print(f"{Fore.YELLOW}⚠ Warning: Failed to delete all XML files: {del_error}{Style.RESET_ALL}")
                    # Nevertheless, try to copy

            # Copy new XML
            shutil.copy2(test_xml, dest_path)

            if self.verbose:
                print(f"{Fore.CYAN}  ✓ XML copied: {test_xml} -> {dest_path}{Style.RESET_ALL}")

            return True

        except Exception as e:  # noqa: BLE001
            print(f"{Fore.YELLOW}⚠ Error while copying the XML file: {e}{Style.RESET_ALL}")
            return False

    def find_test_targets(self, pattern: str) -> List[str]:
        """
        Finds all test targets via bazel query.

        Args:
            pattern: Bazel query pattern (z.B. "//test_trigger/components/...")

        Returns:
            List of Test-Target-Names
        """
        print(f"{Fore.CYAN}🔍 Searching Test-Targets with pattern: {pattern}{Style.RESET_ALL}")

        try:
            # Bazel query: Find all Test-Targets
            result = subprocess.run(
                [self.bazel_exe, "query", f"kind('.*_test rule', {pattern})"],
                capture_output=True,
                text=True,
                check=True
            )

            targets = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]

            if not targets:
                print(f"{Fore.YELLOW}⚠ No Test-Targets found!{Style.RESET_ALL}")
                return []

            print(f"{Fore.GREEN}✓ Found: {len(targets)} Test-Target(s){Style.RESET_ALL}")
            if self.verbose:
                for target in targets:
                    print(f"  - {target}")

            return targets

        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}✗ Error while executing Bazel query: {e}{Style.RESET_ALL}")
            if e.stderr:
                print(f"{Fore.RED}{e.stderr}{Style.RESET_ALL}")
            sys.exit(1)

    def run_test_target(self, target: str) -> Tuple[bool, str]:
        """
        Executes a single Bazel Test-Target

        Args:
            target: Bazel Target (z.B. "//test_trigger/components/module_1_py_binary:execute_py_binary")

        Returns:
            (success: bool, output: str)
        """
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}▶ Test-Target: {target}{Style.RESET_ALL}")

        # Leite Logfile-Pfad aus Target ab
        logfile_path = self.derive_logfile_path(target)
        print(f"{Fore.CYAN}📄 XML Log: {logfile_path}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")

        try:
            # Bazel test (uses sandbox, pytest writes to TEST_UNDECLARED_OUTPUTS_DIR)
            cmd = [self.bazel_exe, "test", target]

            # Deactivate Cache-Test-Results to ensure test execution
            if self.no_cache:
                cmd.append("--nocache_test_results")

            if self.verbose:
                cmd.append("--test_output=all")
            else:
                cmd.append("--test_output=errors")

            # Setze TEST_LOGFILE als Action-Environment-Variable (für Referenz in executepytest.py)
            cmd.append(f"--action_env=TEST_LOGFILE={logfile_path}")

            # Test ausführen mit Environment-Variablen (wichtig: BAZEL_SH für Windows)
            env = os.environ.copy()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,  # Nicht sofort abbrechen bei Fehler
                env=env
            )

            success = result.returncode == 0

            # Nach Test: Kopiere Test-XML aus bazel-testlogs/test.outputs
            # Wichtig: Immer kopieren, auch bei gecachten Tests (Bazel re-creates die XML)
            # Framework wird automatisch erkannt (pytest_results.xml oder robot_results.xml)
            self.copy_test_xml_from_test_outputs(target, logfile_path)

            # Ausgabe
            if success:
                print(f"{Fore.GREEN}✓ Test erfolgreich: {target}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}  Logfile: {logfile_path}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ Test fehlgeschlagen: {target}{Style.RESET_ALL}")
                print(f"{Fore.RED}Exit-Code: {result.returncode}{Style.RESET_ALL}")

            # Bei Fehler oder verbose: Ausgabe zeigen
            if not success or self.verbose:
                if result.stdout:
                    print(f"\n{Fore.YELLOW}STDOUT:{Style.RESET_ALL}")
                    print(result.stdout)
                if result.stderr:
                    print(f"\n{Fore.YELLOW}STDERR:{Style.RESET_ALL}")
                    print(result.stderr)

            return success, result.stdout + result.stderr

        except Exception as e:  # noqa: BLE001
            error_msg = f"Exception beim Ausführen von {target}: {e}"
            print(f"{Fore.RED}✗ {error_msg}{Style.RESET_ALL}")
            return False, error_msg

    def run_all_tests(self, pattern: str) -> int:
        """
        Führt alle gefundenen Test-Targets separat aus.

        Args:
            pattern: Bazel query pattern

        Returns:
            Exit-Code (0 = alle erfolgreich, 1 = mindestens ein Fehler)
        """
        # Targets finden
        targets = self.find_test_targets(pattern)

        if not targets:
            return 1

        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Starte Tests für {len(targets)} Target(s){Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        # Jedes Target separat ausführen
        for i, target in enumerate(targets, 1):
            print(f"\n{Fore.MAGENTA}[{i}/{len(targets)}] {target}{Style.RESET_ALL}")

            success, output = self.run_test_target(target)
            self.results.append((target, success, output))

            # Bei Fehler abbrechen (außer --continue-on-error gesetzt)
            if not success and not self.continue_on_error:
                print(f"\n{Fore.RED}⚠ Test fehlgeschlagen. Abbruch.{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Tipp: Nutze --continue-on-error um alle Tests auszuführen{Style.RESET_ALL}")
                break

        # Zusammenfassung
        self.print_summary()

        # Exit-Code: 0 nur wenn alle erfolgreich
        all_success = all(success for _, success, _ in self.results)
        return 0 if all_success else 1

    def print_summary(self):
        """Gibt eine Zusammenfassung aller Test-Ergebnisse aus."""
        print(f"\n\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}TEST ZUSAMMENFASSUNG{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        success_count = sum(1 for _, success, _ in self.results if success)
        fail_count = len(self.results) - success_count

        for target, success, _ in self.results:
            status_icon = "✓" if success else "✗"
            status_color = Fore.GREEN if success else Fore.RED
            print(f"{status_color}{status_icon} {target}{Style.RESET_ALL}")

        print(f"\n{Fore.CYAN}{'─'*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Erfolgreich: {success_count}{Style.RESET_ALL}")
        print(f"{Fore.RED}Fehlgeschlagen: {fail_count}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Gesamt: {len(self.results)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")

        if fail_count > 0:
            print(f"{Fore.YELLOW}💡 Tipp: Test-Logs finden Sie in:{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}   bazel-testlogs/test_trigger/components/...{Style.RESET_ALL}\n")


def main():
    """Hauptfunktion mit Argument-Parsing."""
    parser = argparse.ArgumentParser(
        description='Generischer Bazel Test Runner - Unterstützt pytest und Robot Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  # Alle Tests in test_trigger/components ausführen
  python run_all_tests.py

  # Alle Tests eines bestimmten Moduls
  python run_all_tests.py --pattern "//test_trigger/components/module_1_py_binary/..."

  # Mit detaillierter Ausgabe und ohne Abbruch bei Fehlern
  python run_all_tests.py --verbose --continue-on-error

Hintergrund:
  Dieses Script führt jedes Bazel Test-Target separat aus, damit jedes
  Modul seine eigene Framework-Konfiguration verwenden kann (pytest.ini,
  robot.ini, etc.). Das verhindert Konflikte bei modulspezifischen
  Konfigurationen (z.B. junit_suite_name, log_level).

  Unterstützte Frameworks:
  - pytest (pytest_results.xml)
  - Robot Framework (robot_results.xml)
"""
    )

    parser.add_argument(
        '--pattern',
        default='//...',
        help='Bazel query pattern für Test-Targets (default: //...)'
    )

    parser.add_argument(
        '--continue-on-error',
        action='store_true',
        help='Führt alle Tests aus, auch wenn einzelne fehlschlagen'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Detaillierte Test-Ausgabe anzeigen'
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Bazel Test-Cache deaktivieren (zwingt Tests immer auszuführen)'
    )

    parser.add_argument(
        '--workspace-root',
        type=str,
        default=None,
        help='Workspace Root-Verzeichnis (default: aktuelles Verzeichnis)'
    )

    parser.add_argument(
        '--logfile-base-dir',
        type=str,
        default=None,
        help='Basis-Verzeichnis für XML Logdateien (default: {workspace_root}/test_logfiles)'
    )

    args = parser.parse_args()

    # Test-Runner erstellen und ausführen
    runner = BazelTestRunner(
        continue_on_error=args.continue_on_error,
        verbose=args.verbose,
        workspace_root=args.workspace_root,
        logfile_base_dir=args.logfile_base_dir,
        no_cache=args.no_cache
    )

    exit_code = runner.run_all_tests(args.pattern)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
