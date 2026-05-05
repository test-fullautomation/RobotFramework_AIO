from __future__ import annotations

import inspect
from pprint import pformat
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


def _normalize_value(value):
	if isinstance(value, dict):
		return {str(key): _normalize_value(item) for key, item in value.items()}
	if isinstance(value, (list, tuple)):
		return [_normalize_value(item) for item in value]
	if hasattr(value, "items") and not isinstance(value, (str, bytes)):
		try:
			return {str(key): _normalize_value(item) for key, item in value.items()}
		except Exception:
			return value
	return value


def _find_context_value(*names):
	for frame_info in inspect.stack()[2:]:
		locals_dict = frame_info.frame.f_locals
		globals_dict = frame_info.frame.f_globals
		for name in names:
			if name and name in locals_dict:
				return locals_dict[name]
			if name and name in globals_dict:
				return globals_dict[name]
	return None


def _load_jsonp_from_content(content: str, parser_kwargs: dict):
	from JsonPreprocessor.CJsonPreprocessor import CJsonPreprocessor

	kwargs = dict(parser_kwargs or {})
	parser = CJsonPreprocessor(**kwargs)
	for method_name in ("json_loads", "jsonLoads"):
		method = getattr(parser, method_name, None)
		if callable(method):
			return method(content)
	raise AttributeError("CJsonPreprocessor does not provide json_loads/jsonLoads.")


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
		validator = self.definition.validator

		if validator == "last_non_empty_line_equals":
			# The learner API is intentionally zero-argument: the answer is whatever the
			# previous cell printed before calling qN.check().
			actual_output = _last_non_empty_line(self._capture.getvalue())
			self._capture.clear()
			expected_output = self.definition.expected_output
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

		if validator == "json_object_equals":
			source_variable = self.definition.source_variable or "json_object"
			content_variable = self.definition.content_variable or "content"
			actual_value = _find_context_value(source_variable)
			if actual_value is None:
				content_value = _find_context_value(content_variable)
				if isinstance(content_value, str) and content_value.strip():
					actual_value = _load_jsonp_from_content(content_value, self.definition.parser_kwargs)
				else:
					raise RuntimeError(
						f"Question {self.question_id} requires a `{source_variable}` object or `{content_variable}` string in the notebook context."
					)

			normalized_actual = _normalize_value(actual_value)
			normalized_expected = _normalize_value(self.definition.expected_value)
			self._capture.clear()
			if normalized_actual == normalized_expected:
				self._progress_store.mark_completed(self.workbook_name, self.question_id, pformat(normalized_actual))
				render_check_result(True, f"Correct: {self.question_id}", self.definition.success_message)
				return True

			details = (
				"Expected parsed JSON object:\n\n"
				f"```python\n{pformat(normalized_expected)}\n```\n\n"
				"Actual parsed JSON object:\n\n"
				f"```python\n{pformat(normalized_actual)}\n```\n\n"
				f"Use `{self.question_id}.hint()` or `{self.question_id}.solution()` for help."
			)
			render_check_result(False, f"Keep trying: {self.question_id}", self.definition.failure_message, details)
			return False

		if validator == "robot_code_execute":
			import subprocess
			import sys as _sys
			import tempfile as _tempfile
			from pathlib import Path as _Path

			robot_variable = self.definition.source_variable or "robot_code"
			robot_code = _find_context_value(robot_variable)
			if robot_code is None:
				raise RuntimeError(
					f"Question {self.question_id} requires a `{robot_variable}` string variable in the notebook context."
				)

			robot_code_str = str(robot_code)
			with _tempfile.TemporaryDirectory() as tmpdir:
				suite_path = _Path(tmpdir) / "exercise.robot"
				suite_path.write_text(robot_code_str, encoding="utf-8")
				proc = subprocess.run(
					[_sys.executable, "-m", "robot", "--outputdir", tmpdir, str(suite_path)],
					capture_output=True,
					text=True,
				)

			actual_rc = proc.returncode
			expected_rc = self.definition.expected_return_code
			self._capture.clear()
			if actual_rc == expected_rc:
				self._progress_store.mark_completed(
					self.workbook_name, self.question_id, f"rc={actual_rc}"
				)
				render_check_result(True, f"Correct: {self.question_id}", self.definition.success_message)
				output_log = (proc.stdout + proc.stderr).strip()
				if output_log:
					render_panel("Robot log", f"```\n{output_log}\n```")
				return True

			output_snippet = (proc.stdout + proc.stderr)[:2000]
			details = (
				f"Expected robot return code: `{expected_rc}` (all tests pass).\n\n"
				f"Actual return code: `{actual_rc}`.\n\n"
				f"**Robot output:**\n```\n{output_snippet}\n```\n\n"
				f"Use `{self.question_id}.hint()` or `{self.question_id}.solution()` for help."
			)
			render_check_result(False, f"Keep trying: {self.question_id}", self.definition.failure_message, details)
			return False

		raise ValueError(f"Unsupported validator: {validator}")

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
