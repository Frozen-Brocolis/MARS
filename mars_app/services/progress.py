from __future__ import annotations

from collections.abc import Callable

from mars_app.models import ProgressEvent


ProgressListener = Callable[[ProgressEvent], None]


class ProgressReporter:
    def __init__(self) -> None:
        self._listeners: list[ProgressListener] = []

    def subscribe(self, listener: ProgressListener) -> None:
        self._listeners.append(listener)

    def emit(self, stage: str, title: str, details: str = "", level: str = "info") -> None:
        event = ProgressEvent(stage=stage, title=title, details=details, level=level)
        for listener in list(self._listeners):
            listener(event)
