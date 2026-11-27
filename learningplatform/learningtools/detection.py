from __future__ import annotations

import inspect
import json
import os
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlencode
from urllib.request import urlopen


_AVAILABLE_WORKBOOKS: List[str] = []


def set_available_workbooks(workbooks: List[str]) -> None:
    global _AVAILABLE_WORKBOOKS
    _AVAILABLE_WORKBOOKS = list(workbooks)


def detect_active_workbook_name() -> Optional[str]:
    available = list(_AVAILABLE_WORKBOOKS)
    if not available:
        return None

    # Allow callers to bypass notebook discovery entirely when they already know
    # which workbook should be active.
    env_value = os.getenv("LEARNINGTOOLS_WORKBOOK", "").strip()
    if env_value in available:
        return env_value

    candidates: List[str] = []
    candidates.extend(_candidate_paths_from_ipython())
    candidates.extend(_candidate_paths_from_stack())
    notebook_path = _candidate_notebook_path_from_kernel()
    if notebook_path:
        candidates.append(notebook_path)

    normalized = {name.lower(): name for name in available}
    for candidate in candidates:
        # Workbook names are matched from notebook stems so notebooks can live in
        # any folder as long as their filename maps to a known workbook.
        stem = Path(candidate).stem.lower()
        if stem in normalized:
            return normalized[stem]
    return None


def _candidate_paths_from_ipython() -> List[str]:
    try:
        from IPython import get_ipython
    except Exception:
        return []

    shell = get_ipython()
    if shell is None:
        return []

    user_ns = getattr(shell, "user_ns", {})
    result = []
    for key in ("__vsc_ipynb_file__", "__file__", "NOTEBOOK_PATH", "LEARNINGTOOLS_NOTEBOOK"):
        value = user_ns.get(key)
        if isinstance(value, str) and value.strip():
            result.append(value)
    return result


def _candidate_paths_from_stack() -> List[str]:
    result = []
    for frame_info in inspect.stack():
        globals_dict = frame_info.frame.f_globals
        for key in ("__vsc_ipynb_file__", "__file__", "NOTEBOOK_PATH", "LEARNINGTOOLS_NOTEBOOK"):
            value = globals_dict.get(key)
            if isinstance(value, str) and value.strip():
                result.append(value)
    return result


def _candidate_notebook_path_from_kernel() -> Optional[str]:
    # Skip Jupyter detection if disabled (e.g., in API mode)
    if os.getenv('LEARNINGTOOLS_DISABLE_JUPYTER_DETECTION', '').lower() in ('1', 'true', 'yes'):
        return None
    
    try:
        from ipykernel.connect import get_connection_file
        from jupyter_core.paths import jupyter_runtime_dir
    except Exception:
        return None

    try:
        connection_file = Path(get_connection_file()).name
    except Exception:
        return None

    if "kernel-" not in connection_file:
        return None

    # Fall back to the Jupyter sessions API when the notebook path is not
    # available in IPython globals, which is common outside VS Code notebooks.
    kernel_id = connection_file.split("kernel-", 1)[1].split(".", 1)[0]
    runtime_dir = Path(jupyter_runtime_dir())
    server_files = list(runtime_dir.glob("jpserver-*.json")) + list(runtime_dir.glob("nbserver-*.json"))
    for server_file in server_files:
        try:
            server = json.loads(server_file.read_text(encoding="utf-8"))
        except Exception:
            continue
        sessions_url = server.get("url", "").rstrip("/") + "/api/sessions"
        token = server.get("token", "")
        query = urlencode({"token": token}) if token else ""
        if query:
            sessions_url = f"{sessions_url}?{query}"
        try:
            with urlopen(sessions_url, timeout=1) as response:
                sessions = json.loads(response.read().decode("utf-8"))
        except Exception:
            continue
        for session in sessions:
            try:
                if session["kernel"]["id"] != kernel_id:
                    continue
                notebook = session.get("notebook", {})
                notebook_path = notebook.get("path")
                if not notebook_path:
                    continue
                root_dir = server.get("root_dir") or server.get("notebook_dir")
                if root_dir:
                    return str(Path(root_dir) / notebook_path)
                return str(notebook_path)
            except Exception:
                continue
    return None
