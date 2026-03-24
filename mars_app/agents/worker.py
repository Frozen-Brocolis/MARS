from __future__ import annotations

from mars_app.agents.base import BaseAgent
from mars_app.contracts import WORKER_OUTPUT_SCHEMA
from mars_app.models import ManagedTask, WorkerOutput
from mars_app.prompts import WORKER_PROMPT


class WorkerAgent(BaseAgent):
    def __init__(self, client) -> None:
        super().__init__(client, WORKER_PROMPT, WORKER_OUTPUT_SCHEMA)

    def execute(self, task: ManagedTask, memory_context: str, web_context: str) -> WorkerOutput:
        result = self.run_structured(
            {
                "task": task,
                "memory_context": memory_context,
                "web_context": web_context,
            }
        )
        return WorkerOutput(
            task_id=task.step_id,
            summary=str(result.get("summary", "")),
            details=str(result.get("details", "")),
            sources=self._as_list(result.get("sources")),
            artifacts=self._as_list(result.get("artifacts")),
        )

    def _as_list(self, value) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return []
