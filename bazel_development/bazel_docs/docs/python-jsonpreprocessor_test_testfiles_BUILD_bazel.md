# BUILD.bazel

**Pfad:** `python-jsonpreprocessor\test\testfiles\BUILD.bazel`  
**Absoluter Pfad:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\test\testfiles\BUILD.bazel`  
**Typ:** Bazel Build File (definiert Targets und Dependencies)

---

## Inhalt

```python
filegroup(
    name = "testfiles",
    srcs = glob([
        "*.jsonp",
        "dynamic_imports/**",
        "import/**",
    ]),
    visibility = ["//python-jsonpreprocessor/test:__subpackages__"],
)

```

---

## Datei-Informationen

- **Größe:** 211 bytes
- **Zeilen:** 9
- **Verzeichnis:** `C:\workplace\ROBFW\components\bazel_aio\python-jsonpreprocessor\test\testfiles`

---

## Navigation

**Übergeordnetes Verzeichnis:** `python-jsonpreprocessor\test\testfiles`

