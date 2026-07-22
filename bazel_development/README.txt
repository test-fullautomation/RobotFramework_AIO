bazel_workspace/                    # Haupt-Repository
+-- .git/                           # Git des Haupt-Repos
+-- .gitmodules                     # Submodule-Konfiguration
+-- BUILD.bazel                     # Root BUILD-Datei
+-- .bazelrc                        # Bazel-Optionen
+-- requirements.txt                # Shared Python-Dependencies
+-- requirements_lock.txt
+-- MODULE.bazel                    # (Optional: Bzlmod)
¦
+-- python-jsonpreprocessor/        # Git Submodule
¦   +-- .git ? (Verweis auf externes Repo)
¦   +-- BUILD.bazel
¦   +-- JsonPreprocessor/
¦   +-- test/
¦   +-- pyproject.toml
¦
+-- python-extensions-collection/   # Git Submodule
¦   +-- .git ? (Verweis auf externes Repo)
¦   +-- BUILD.bazel
¦   +-- PythonExtensionsCollection/
¦   +-- pyproject.toml
¦
+-- robotframework-testsuitesmanagement/  # Git Submodule
    +-- .git ? (Verweis auf externes Repo)
    +-- BUILD.bazel
    +-- ...

