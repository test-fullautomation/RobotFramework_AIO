# BUILD.bazel

**Pfad:** `python-extensions-collection\BUILD.bazel`  
**Absoluter Pfad:** `C:\workplace\ROBFW\components\bazel_aio\python-extensions-collection\BUILD.bazel`  
**Typ:** Bazel Build File (definiert Targets und Dependencies)

---

## Inhalt

```python
load("@rules_python//python:defs.bzl", "py_library")

# Python Extensions Collection Library
# This is a local fixed version to avoid circular dependencies in PyPI
py_library(
    name = "pythonextensionscollection",
    srcs = glob([
        "PythonExtensionsCollection/**/*.py",
    ]),
    imports = ["."],
    visibility = ["//visibility:public"],
)

```

---

## Datei-Informationen

- **Größe:** 366 bytes
- **Zeilen:** 12
- **Verzeichnis:** `C:\workplace\ROBFW\components\bazel_aio\python-extensions-collection`

---

## Navigation

**Übergeordnetes Verzeichnis:** `python-extensions-collection`

