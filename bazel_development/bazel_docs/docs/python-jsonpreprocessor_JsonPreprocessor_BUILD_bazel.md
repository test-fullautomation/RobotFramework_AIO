# BUILD.bazel

**Pfad:** `python-jsonpreprocessor\JsonPreprocessor\BUILD.bazel`  
**Absoluter Pfad:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\JsonPreprocessor\BUILD.bazel`  
**Typ:** Bazel Build File (definiert Targets und Dependencies)

---

## Inhalt

```python
load("@rules_python//python:defs.bzl", "py_library")

py_library(
    name = "jsonpreprocessor",
    srcs = glob(["*.py"]),
    imports = [".."],  # Damit 'from JsonPreprocessor.CJsonPreprocessor import' funktioniert
    deps = [
        "@pypi//regex",
    ],
    visibility = ["//visibility:public"],
)

```

---

## Datei-Informationen

- **Größe:** 316 bytes
- **Zeilen:** 11
- **Verzeichnis:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\JsonPreprocessor`

---

## Navigation

**Übergeordnetes Verzeichnis:** `python-jsonpreprocessor\JsonPreprocessor`

