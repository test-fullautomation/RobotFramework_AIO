from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import Dict, List

from .models import QuestionDefinition, WorkbookDefinition


def workbooks_dir(package_dir: Path) -> Path:
    return package_dir / "workbooks"


def list_workbooks(package_dir: Path) -> List[str]:
    folder = workbooks_dir(package_dir)
    python_names = {
        path.stem
        for path in folder.glob("*.py")
        if path.name != "__init__.py" and not path.stem.startswith("_")
    }
    jsonp_names = {path.stem for path in folder.glob("*.jsonp")}
    return sorted(python_names & jsonp_names)


def _normalize_multiline(value) -> str:
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    return str(value or "")


def _load_jsonp_file(path: Path) -> dict:
    try:
        from JsonPreprocessor.CJsonPreprocessor import CJsonPreprocessor
        return CJsonPreprocessor().jsonLoad(str(path))
    except Exception:
        # Plain JSON remains a valid fallback so the tutorial content still loads
        # when JsonPreprocessor is not installed.
        return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonp_workbook(package_dir: Path, workbook_name: str) -> dict:
    path = workbooks_dir(package_dir) / f"{workbook_name.replace('.', '/')}.jsonp"
    return _load_jsonp_file(path)


def _load_python_workbook(workbook_name: str) -> dict:
    module = importlib.import_module(f"learningtools.workbooks.{workbook_name}")
    workbook = getattr(module, "WORKBOOK", None)
    if not isinstance(workbook, dict):
        raise TypeError(f"Workbook module '{workbook_name}' must define a WORKBOOK dictionary.")
    return workbook


def load_workbook_definition(package_dir: Path, workbook_name: str) -> WorkbookDefinition:
    # Presentation content comes from JSONP while validation rules live in the
    # Python WORKBOOK module; the runtime consumes the merged definition.
    jsonp_definition = _load_jsonp_workbook(package_dir, workbook_name)
    python_definition = _load_python_workbook(workbook_name)
    question_logic = python_definition.get("questions", {})
    questions: Dict[str, QuestionDefinition] = {}
    for question_data in jsonp_definition.get("questions", []):
        question_id = str(question_data["id"])
        logic = question_logic.get(question_id, {})
        questions[question_id] = QuestionDefinition(
            question_id=question_id,
            title=str(question_data.get("title", question_id.upper())),
            prompt=_normalize_multiline(question_data.get("prompt", "")),
            hint_text=_normalize_multiline(question_data.get("hint", "")),
            solution_text=_normalize_multiline(question_data.get("solution", "")),
            starter_code=_normalize_multiline(question_data.get("starter_code", "")),
            expected_output=str(logic.get("expected_output", "")),
            expected_value=logic.get("expected_value"),
            expected_return_code=int(logic.get("expected_return_code", 0)),
            validator=str(logic.get("validator", "last_non_empty_line_equals")),
            source_variable=str(logic.get("source_variable", "")),
            content_variable=str(logic.get("content_variable", "")),
            parser_kwargs=dict(logic.get("parser_kwargs", {})),
            success_message=str(question_data.get("success_message", "Correct. Keep going.")),
            failure_message=str(question_data.get("failure_message", "Not quite right yet.")),
            tags=[str(item) for item in question_data.get("tags", [])],
        )
    return WorkbookDefinition(
        name=str(jsonp_definition.get("name", workbook_name)),
        title=str(jsonp_definition.get("title", workbook_name)),
        summary=_normalize_multiline(jsonp_definition.get("summary", "")),
        introduction=_normalize_multiline(jsonp_definition.get("introduction", "")),
        questions=questions,
    )
