from __future__ import annotations

from pathlib import Path
import shutil
from typing import Dict, Optional

from .capture import get_output_capture
from .detection import detect_active_workbook_name, set_available_workbooks
from .loader import list_workbooks as _list_workbooks, load_workbook_definition
from .models import WorkbookDefinition
from .runtime import Lesson, Question
from .storage import ProgressStore


_PACKAGE_DIR = Path(__file__).resolve().parent
_PROGRESS_STORE = ProgressStore()
_ACTIVE_LESSON: Optional[Lesson] = None


def list_workbooks() -> list[str]:
    return _list_workbooks(_PACKAGE_DIR)


set_available_workbooks(list_workbooks())


def activate(workbook_name: str) -> Lesson:
    global _ACTIVE_LESSON
    # Load the jupyter notebook from the template
    template_path = _PACKAGE_DIR / "templates"
    example_path = _PACKAGE_DIR / "examples"
    template: list = workbook_name.split(".")
    i=0
    for part in template:
        i+=1
        if i==len(template):
            part_template = part + "_template.ipynb"
            template_path = template_path / part_template
            part_example = part + ".ipynb"
            example_path = example_path / part_example

        else:
            example_path = example_path / part
            template_path = template_path / part
    if not template_path.exists():
        raise FileNotFoundError(f"Template notebook not found for workbook '{workbook_name}' at expected path: {template_path}")
    shutil.copy2(str(template_path), str(example_path))

    definition = load_workbook_definition(_PACKAGE_DIR, workbook_name)
    capture = get_output_capture()
    # Start each activation with a clean capture buffer so stale notebook output
    # does not affect the next question check.
    capture.clear()
    questions = {
        question_id: Question(definition.name, question_definition, capture, _PROGRESS_STORE)
        for question_id, question_definition in definition.questions.items()
    }
    _ACTIVE_LESSON = Lesson(definition=definition, questions=questions, progress_store=_PROGRESS_STORE)
    return _ACTIVE_LESSON


def current_lesson() -> Optional[Lesson]:
    return _ACTIVE_LESSON


def current_workbook_name() -> Optional[str]:
    if _ACTIVE_LESSON is None:
        return None
    return _ACTIVE_LESSON.name


def show_overview() -> None:
    if _ACTIVE_LESSON is not None:
        _ACTIVE_LESSON.overview()


def list_questions() -> list[str]:
    if _ACTIVE_LESSON is None:
        return []
    return list(_ACTIVE_LESSON.questions.keys())


def question(question_id: str) -> Question:
    if _ACTIVE_LESSON is None:
        raise RuntimeError("No active workbook. Activate a workbook or import from a notebook with detectable name.")
    return _ACTIVE_LESSON.question(question_id)


def get_progress(workbook_name: Optional[str] = None) -> dict:
    target = workbook_name or current_workbook_name()
    return _PROGRESS_STORE.get_progress(target)


def _auto_activate() -> None:
    # Notebook imports should feel zero-config when the workbook can be inferred
    # from the active notebook name or an explicit environment override.
    workbook_name = detect_active_workbook_name()
    if workbook_name:
        activate(workbook_name)


_auto_activate()
