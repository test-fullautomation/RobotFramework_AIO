from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class QuestionDefinition:
    question_id: str
    title: str
    prompt: str
    hint_text: str
    solution_text: str
    starter_code: str
    expected_output: str
    validator: str = "last_non_empty_line_equals"
    success_message: str = "Correct. Keep going."
    failure_message: str = "Not quite right yet."
    tags: List[str] = field(default_factory=list)


@dataclass
class WorkbookDefinition:
    name: str
    title: str
    summary: str
    introduction: str
    questions: Dict[str, QuestionDefinition]
