# MODULE.bazel

**Pfad:** `MODULE.bazel`  
**Absoluter Pfad:** `C:\workplace\ROBFW\components\bazel_aio\MODULE.bazel`  
**Typ:** Bazel Module File (Bzlmod)

---

## Inhalt

```python
module(
    name = "bazel_test",
    version = "0.0.1",
)

# Using rules_python 1.7.0 for Windows compatibility
# Known issue: versions 2.0.0+ have venv/symlink issues on Windows (WinError 87)
# - venv creation uses symlinks with Bzlmod canonical names (contains ++)
# - Windows symlinks reject ++ characters in paths
# - PowerShell ACL issues: "IdentityNotMappedException"
# - Path shortening (output_base) does NOT solve the problem
# TODO: Upgrade to 2.x when Windows support is stable
bazel_dep(name = "rules_python", version = "1.9.0")
# bazel_dep(name = "rules_python", version = "2.0.3")
bazel_dep(name = "platforms", version = "1.0.0")

python = use_extension("@rules_python//python/extensions:python.bzl", "python")
python.toolchain(
    python_version = "3.13",
)

pip = use_extension("@rules_python//python/extensions:pip.bzl", "pip")
pip.parse(
    hub_name = "pypi",
    python_version = "3.13",
    requirements_lock = "//:requirements_lock.txt",
)

use_repo(pip, "pypi")

```

---

## Datei-Informationen

- **Größe:** 986 bytes
- **Zeilen:** 29
- **Verzeichnis:** `C:\workplace\ROBFW\components\bazel_aio`

---

## Navigation

**Übergeordnetes Verzeichnis:** `(Root)`

