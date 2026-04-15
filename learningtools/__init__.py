from __future__ import annotations

import re

from .core import (
    Question,
    activate as _activate_core,
    current_lesson,
    current_workbook_name,
    get_progress,
    list_questions,
    list_workbooks,
    question,
    show_overview,
)


def _install_active_bindings() -> None:
    # Mirror Kaggle-style notebooks by exposing lesson, q1, q2, ... directly at
    # package import time based on the currently active workbook.
    lesson = current_lesson()
    globals()["lesson"] = lesson
    stale_question_ids = [name for name in list(globals()) if re.match(r"^q\d+$", name)]
    for question_id in stale_question_ids:
        globals().pop(question_id, None)
    if lesson is None:
        return
    for question_id, question_obj in lesson.questions.items():
        globals()[question_id] = question_obj


def _refresh_all() -> None:
    global __all__
    __all__ = [
        "Question",
        "activate",
        "current_lesson",
        "current_workbook_name",
        "get_progress",
        "lesson",
        "list_questions",
        "list_workbooks",
        "question",
        "show_overview",
    ]
    lesson = current_lesson()
    if lesson is not None:
        __all__.extend(sorted(lesson.questions.keys()))


def activate(workbook_name: str):
    # Public activation refreshes the dynamic exports so a notebook can switch
    # workbooks without re-importing the package under a different name.
    lesson = _activate_core(workbook_name)
    _install_active_bindings()
    _refresh_all()
    show_overview()
    return lesson


_install_active_bindings()
_refresh_all()
if current_lesson() is not None:
    show_overview()
