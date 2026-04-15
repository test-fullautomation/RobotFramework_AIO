from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable

from .capture import CapturedStdout
from .models import QuestionDefinition, WorkbookDefinition
from .rendering import render_check_result, render_overview, render_panel, render_progress, render_question
from .storage import ProgressStore


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _last_non_empty_line(text: str) -> str:
	# Notebook output may include ANSI color codes and multiple trailing blank
	# lines; the checker compares only the final meaningful printed line.
	normalized = ANSI_RE.sub("", text or "")
	lines = normalized.replace("\r\n", "\n").replace("\r", "\n").split("\n")
	non_empty_lines = [line.strip() for line in lines if line.strip()]
	return non_empty_lines[-1] if non_empty_lines else ""


class Question:
	def __init__(
		self,
		workbook_name: str,
		definition: QuestionDefinition,
		capture: CapturedStdout,
		progress_store: ProgressStore,
	):
		self.workbook_name = workbook_name
		self.definition = definition
		self._capture = capture
		self._progress_store = progress_store

	@property
	def question_id(self) -> str:
		return self.definition.question_id

	def prompt(self) -> None:
		render_question(self.definition, completed=self.status())

	def display(self) -> None:
		self.prompt()

	def hint(self) -> None:
		render_panel(f"Hint: {self.workbook_name}.{self.question_id}", self.definition.hint_text)

	def solution(self) -> None:
		render_panel(f"Solution: {self.workbook_name}.{self.question_id}", self.definition.solution_text)

	def check(self) -> bool:
		# The learner API is intentionally zero-argument: the answer is whatever the
		# previous cell printed before calling qN.check().
		actual_output = _last_non_empty_line(self._capture.getvalue())
		self._capture.clear()
		expected_output = self.definition.expected_output

		if self.definition.validator != "last_non_empty_line_equals":
			raise ValueError(f"Unsupported validator: {self.definition.validator}")

		if actual_output == expected_output:
			# Persist completion immediately so progress survives kernel restarts.
			self._progress_store.mark_completed(self.workbook_name, self.question_id, actual_output)
			render_check_result(True, f"Correct: {self.question_id}", self.definition.success_message)
			return True

		details = (
			f"Expected last non-empty line: `{expected_output}`\n\n"
			f"Actual last non-empty line: `{actual_output}`\n\n"
			f"Use `{self.question_id}.hint()` or `{self.question_id}.solution()` for help."
		)
		render_check_result(False, f"Keep trying: {self.question_id}", self.definition.failure_message, details)
		return False

	def status(self) -> bool:
		return self._progress_store.is_completed(self.workbook_name, self.question_id)

	def __repr__(self) -> str:
		return f"<Question {self.workbook_name}.{self.question_id}>"


@dataclass
class Lesson:
	definition: WorkbookDefinition
	questions: Dict[str, Question]
	progress_store: ProgressStore

	@property
	def name(self) -> str:
		return self.definition.name

	@property
	def title(self) -> str:
		return self.definition.title

	def overview(self) -> None:
		render_overview(self.definition, self.questions.keys(), self.completed_question_ids())

	def progress(self) -> None:
		render_progress(self.definition, self.completed_question_ids())

	def question(self, question_id: str) -> Question:
		return self.questions[question_id]

	def completed_question_ids(self) -> list[str]:
		return [question_id for question_id, question in self.questions.items() if question.status()]

	def items(self) -> Iterable[tuple[str, Question]]:
		return self.questions.items()

	def __repr__(self) -> str:
		return f"<Lesson {self.definition.name}>"
