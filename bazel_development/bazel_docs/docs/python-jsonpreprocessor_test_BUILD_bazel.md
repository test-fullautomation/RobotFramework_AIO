# BUILD.bazel

**Pfad:** `python-jsonpreprocessor\test\BUILD.bazel`  
**Absoluter Pfad:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\test\BUILD.bazel`  
**Typ:** Bazel Build File (definiert Targets und Dependencies)

---

## Inhalt

```python
load("@rules_python//python:defs.bzl", "py_library")

py_library(
    name = "component_test",
    srcs = ["component_test.py"],
    deps = [
        "//python-jsonpreprocessor/test/libs:libs",
        "//python-jsonpreprocessor/JsonPreprocessor:jsonpreprocessor",
    ],
    visibility = ["//python-jsonpreprocessor/test/pytest:__pkg__"],
)

```

---

## Datei-Informationen

- **Größe:** 353 bytes
- **Zeilen:** 11
- **Verzeichnis:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\test`

---

## Navigation

**Übergeordnetes Verzeichnis:** `python-jsonpreprocessor\test`

