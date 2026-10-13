from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


class ProgressStore:
    def __init__(self, base_dir: Optional[Path] = None):
        configured = os.getenv("LEARNINGTOOLS_PROGRESS_DIR")
        if base_dir is None and configured:
            base_dir = Path(configured)
        if base_dir is None:
            base_dir = Path.home() / ".learningtools"
        self._path = base_dir / "progress.json"
        self._data: Optional[dict] = None

    def _load(self) -> dict:
        # Cache the parsed JSON in memory so repeated q.check() calls do not keep
        # re-reading the progress file.
        if self._data is not None:
            return self._data
        if self._path.is_file():
            try:
                self._data = json.loads(self._path.read_text(encoding="utf-8"))
            except Exception:
                self._data = {}
        else:
            self._data = {}
        return self._data

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._load(), indent=2, sort_keys=True), encoding="utf-8")

    def mark_completed(self, workbook_name: str, question_id: str, actual_output: str) -> None:
        data = self._load()
        workbook = data.setdefault(workbook_name, {})
        workbook[question_id] = {
            "completed": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "actual_output": actual_output,
        }
        self._save()

    def is_completed(self, workbook_name: str, question_id: str) -> bool:
        return bool(self._load().get(workbook_name, {}).get(question_id, {}).get("completed"))

    def get_progress(self, workbook_name: Optional[str] = None) -> dict:
        data = self._load()
        if workbook_name is None:
            return data
        return data.get(workbook_name, {})
