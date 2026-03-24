from __future__ import annotations

from mars_app.agents.base import BaseAgent
from mars_app.contracts import CRITIQUE_SCHEMA
from mars_app.models import Critique, ManagedTask, WorkerOutput
from mars_app.prompts import CRITIC_PROMPT


class CriticAgent(BaseAgent):
    def __init__(self, client) -> None:
        super().__init__(client, CRITIC_PROMPT, CRITIQUE_SCHEMA)

    def review(self, task: ManagedTask, output: WorkerOutput) -> Critique:
        result = self.run_structured({"task": task, "output": output})
        score = int(result.get("score", 0))
        score = max(0, min(score, 10))
        approved = bool(result.get("approved", score >= 7))
        return Critique(
            task_id=task.step_id,
            score=score,
            approved=approved,
            issues=self._as_list(result.get("issues")),
            retry_guidance=str(result.get("retry_guidance", "")),
        )

    def _as_list(self, value) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return []
