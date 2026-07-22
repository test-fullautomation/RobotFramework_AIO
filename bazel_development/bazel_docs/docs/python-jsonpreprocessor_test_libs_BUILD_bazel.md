# BUILD.bazel

**Pfad:** `python-jsonpreprocessor\test\libs\BUILD.bazel`  
**Absoluter Pfad:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\test\libs\BUILD.bazel`  
**Typ:** Bazel Build File (definiert Targets und Dependencies)

---

## Inhalt

```python
load("@rules_python//python:defs.bzl", "py_library")

py_library(
    name = "libs",
    srcs = glob(["*.py"]),
    imports = [".."],  # Damit 'from libs.CConfig import' funktioniert
    deps = [
        "//python-jsonpreprocessor/test/testconfig:testconfig",
    ],
    visibility = ["//python-jsonpreprocessor/test:__subpackages__"],
)

```

---

## Datei-Informationen

- **Größe:** 349 bytes
- **Zeilen:** 11
- **Verzeichnis:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\test\libs`

---

## Navigation

**Übergeordnetes Verzeichnis:** `python-jsonpreprocessor\test\libs`

