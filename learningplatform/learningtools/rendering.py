from __future__ import annotations

from typing import Iterable, Optional
import regex
from .capture import framework_print
from .models import QuestionDefinition, WorkbookDefinition


try:
    from IPython.display import Markdown, display
    from IPython import get_ipython
except Exception:
    Markdown = None
    display = None
    get_ipython = None


def render_markdown(text: str) -> None:
    content = (text or "").strip()
    if not content:
        return
    shell = get_ipython() if get_ipython is not None else None
    shell_name = shell.__class__.__name__ if shell is not None else ""
    # Only use rich Markdown rendering inside a real notebook kernel; plain text
    # fallback keeps terminals and test runs readable.
    if Markdown is not None and display is not None and shell_name == "ZMQInteractiveShell":
        try:
            display(Markdown(content))
            return
        except Exception:
            pass
    framework_print(content)


def render_panel(title: str, body: str) -> None:
    if regex.match(r'^Hint:.+', title, flags=regex.IGNORECASE):
        body = f"<div style=\"background-color: lightpink; color: black; padding: 10px;\">\n\n{body}\n\n</div>"
    elif regex.match(r'^Solution:.+', title, flags=regex.IGNORECASE):
        body = f"<div style=\"background-color: lightblue; color: black; padding: 10px;\">\n\n{body}\n\n</div>"
    else:
        body = f"<div style=\"background-color: lightgreen; color: black; padding: 10px;\">\n\n{body}\n\n</div>"
    render_markdown(f"### {title}\n\n{body}")


def render_question(question: QuestionDefinition, completed: bool = False) -> None:
    status = "Completed" if completed else "Not completed"
    parts = [f"## {question.title}", question.prompt, f"**Status:** {status}"]
    if question.starter_code.strip():
        parts.append("### Starter Code")
        parts.append(f"```python\n{question.starter_code.strip()}\n```")
    render_markdown("\n\n".join(part for part in parts if part.strip()))


def render_overview(workbook: WorkbookDefinition, question_ids: Iterable[str], completed_ids: Iterable[str]) -> None:
    completed = set(completed_ids)
    lines = [f"# {workbook.title}"]
    if workbook.summary.strip():
        lines.append(workbook.summary.strip())
    if workbook.introduction.strip():
        lines.append(workbook.introduction.strip())
    lines.append("## Exercises")
    for question_id in question_ids:
        marker = "Completed" if question_id in completed else "Open"
        question = workbook.questions[question_id]
        lines.append(f"- **{question.title}** (`{question_id}`) - {marker}")
    render_markdown("\n\n".join(lines))


def render_progress(workbook: WorkbookDefinition, completed_ids: Iterable[str]) -> None:
    completed = set(completed_ids)
    total = len(workbook.questions)
    done = len(completed)
    lines = [
        f"## Progress for {workbook.title}",
        f"Completed **{done}** of **{total}** exercises.",
    ]
    for question_id, question in workbook.questions.items():
        state = "Completed" if question_id in completed else "Pending"
        lines.append(f"- `{question_id}`: {question.title} - {state}")
    render_markdown("\n\n".join(lines))


def render_check_result(ok: bool, heading: str, message: str, details: Optional[str] = None) -> None:
    if ok:
        heading = f"<span style=\"color: green; font-weight: bold;\">\n\n### {heading}\n\n</span>"
        message = f"<span style=\"color: green; font-weight: bold;\">\n\n{message}\n\n</span>"
        details = f"<span style=\"color: green;\">\n\n{details}\n\n</span>" if details else None
    else:
        heading = f"<span style=\"color: red; font-weight: bold;\">\n\n### {heading}\n\n</span>"
        message = f"<span style=\"color: red; font-weight: bold;\">\n\n{message}\n\n</span>"
        details = f"<span style=\"color: red;\">\n\n{details}\n\n</span>" if details else None
    parts = [heading, message]
    if details:
        parts.append(details)
    render_markdown("\n\n".join(parts))
