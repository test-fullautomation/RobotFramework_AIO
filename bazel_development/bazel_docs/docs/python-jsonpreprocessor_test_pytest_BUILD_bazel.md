# BUILD.bazel

**Pfad:** `python-jsonpreprocessor\test\pytest\BUILD.bazel`  
**Absoluter Pfad:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\test\pytest\BUILD.bazel`  
**Typ:** Bazel Build File (definiert Targets und Dependencies)

---

## Inhalt

```python
load("@rules_python//python:defs.bzl", "py_test")

# ──────────────────────────────────────────
# py_test: Exit-Code will be interpreted
#          as test result (0=OK, >0=ERROR)
# NOTE: Requires symlink permissions on Windows
# ──────────────────────────────────────────
py_test(
    name = "execute_py_test_jpp",
    srcs = ["executepytest_bazel.py"],
    main = "executepytest_bazel.py",
    python_version = "PY3",
    visibility = ["//visibility:public"],
    deps = [
        "@pypi//colorama",
        "@pypi//pytest",
        "@pypi//dotdict",
        "@pypi//pydotdict",
        # "@pypi//pythonextensionscollection",
        "//python-extensions-collection:pythonextensionscollection",
        "//python-jsonpreprocessor/test/pytest/pytestfiles:pytestlibs",
        "//python-jsonpreprocessor/test:component_test",  # component_test.py as py_library
    ],
    data = [
        "pytest.ini",  # pytest.ini als Data-Dependency
        "//python-jsonpreprocessor/test/pytest/pytestfiles:test_files",  # Test-Dateien!
        "//python-jsonpreprocessor/test/testfiles:testfiles",  # JSONP Test Data Files
    ],
    size = "small",
    timeout = "short",
    # platform specific environment variables
    env = select({
        "//:is_windows": {"PLATFORM": "windows"},
        "//:is_linux":   {"PLATFORM": "linux"},
        "//conditions:default": {"PLATFORM": "unknown"},
    }),
)

```

---

## Datei-Informationen

- **Größe:** 1598 bytes
- **Zeilen:** 37
- **Verzeichnis:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\test\pytest`

---

## Navigation

**Übergeordnetes Verzeichnis:** `python-jsonpreprocessor\test\pytest`

