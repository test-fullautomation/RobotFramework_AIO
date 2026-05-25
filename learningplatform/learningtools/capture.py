from __future__ import annotations

import io
import sys
import threading
from typing import List


OUTPUT_CAPTURE_ATTR = "_learningtools_capture"


class CapturedStdout(io.TextIOBase):
    def __init__(self, stream: io.TextIOBase):
        self._stream = stream
        self._buffer: List[str] = []
        self._lock = threading.RLock()

    def write(self, text: str) -> int:
        with self._lock:
            self._buffer.append(text)
            return self._stream.write(text)

    def flush(self) -> None:
        self._stream.flush()

    def getvalue(self) -> str:
        with self._lock:
            return "".join(self._buffer)

    def clear(self) -> None:
        with self._lock:
            self._buffer.clear()

    def direct_write(self, text: str) -> None:
        self._stream.write(text)
        self._stream.flush()

    def isatty(self) -> bool:
        return bool(getattr(self._stream, "isatty", lambda: False)())

    def __getattr__(self, name: str):
        return getattr(self._stream, name)


def get_output_capture() -> CapturedStdout:
    # Reuse a single wrapped stdout so every notebook cell writes into the same
    # buffer that Question.check() inspects.
    current = sys.stdout
    if isinstance(current, CapturedStdout):
        return current
    capture = CapturedStdout(current)
    setattr(capture, OUTPUT_CAPTURE_ATTR, True)
    sys.stdout = capture
    return capture


def framework_print(*parts, sep: str = " ", end: str = "\n") -> None:
    # Render framework messages directly to the underlying stream so they do not
    # pollute the learner output that the checker evaluates.
    capture = get_output_capture()
    capture.direct_write(sep.join(str(part) for part in parts) + end)
