# BUILD.bazel

**Pfad:** `python-jsonpreprocessor\test\pytest\pytestfiles\BUILD.bazel`  
**Absoluter Pfad:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\test\pytest\pytestfiles\BUILD.bazel`  
**Typ:** Bazel Build File (definiert Targets und Dependencies)

---

## Inhalt

```python
load("@rules_python//python:defs.bzl", "py_library")

py_library(
    name = "pytestlibs",
    srcs = glob(["pytestlibs/**/*.py"]),
    imports = ["."],
    visibility = ["//python-jsonpreprocessor/test/pytest:__pkg__"],
)

filegroup(
    name = "test_files",
    srcs = glob(["test_*.py"]),
    visibility = ["//python-jsonpreprocessor/test/pytest:__pkg__"],
)

```

---

## Datei-Informationen

- **Größe:** 376 bytes
- **Zeilen:** 14
- **Verzeichnis:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\test\pytest\pytestfiles`

---

## Navigation

**Übergeordnetes Verzeichnis:** `python-jsonpreprocessor\test\pytest\pytestfiles`

