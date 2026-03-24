from __future__ import annotations

from mars_app.models import Critique, ManagedTask, WorkerOutput


class MemoryService:
    def __init__(self) -> None:
        self.project_notes: list[str] = []
        self.success_log: list[str] = []
        self.failure_log: list[str] = []

    def add_project_note(self, note: str) -> None:
        if note:
            self.project_notes.append(note)

    def record_success(self, task: ManagedTask, output: WorkerOutput) -> None:
        line = f"[SUCCESS] {task.title}: {output.summary}"
        self.success_log.append(line)

    def record_failure(self, task: ManagedTask, critique: Critique) -> None:
        issues = "; ".join(critique.issues) if critique.issues else "без деталей"
        line = f"[FAIL] {task.title}: {issues}"
        self.failure_log.append(line)

    def get_context(self, step_title: str) -> str:
        context_lines = [f"Текущий этап: {step_title}"]
        context_lines.extend(self.project_notes[-3:])
        context_lines.extend(self.success_log[-3:])
        context_lines.extend(self.failure_log[-3:])
        return "\n".join(context_lines)
