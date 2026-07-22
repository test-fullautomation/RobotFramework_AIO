# BUILD.bazel

**Pfad:** `python-jsonpreprocessor\test\testconfig\BUILD.bazel`  
**Absoluter Pfad:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\test\testconfig\BUILD.bazel`  
**Typ:** Bazel Build File (definiert Targets und Dependencies)

---

## Inhalt

```python
load("@rules_python//python:defs.bzl", "py_library")

py_library(
    name = "testconfig",
    srcs = glob(["*.py"]),
    imports = [".."],  # Damit 'from testconfig.TestConfig import' funktioniert
    visibility = ["//python-jsonpreprocessor/test:__subpackages__"],
)

```

---

## Datei-Informationen

- **Größe:** 277 bytes
- **Zeilen:** 8
- **Verzeichnis:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\test\testconfig`

---

## Navigation

**Übergeordnetes Verzeichnis:** `python-jsonpreprocessor\test\testconfig`

