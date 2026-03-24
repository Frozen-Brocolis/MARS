from __future__ import annotations

from mars_app.agents.base import BaseAgent
from mars_app.contracts import PROMPT_GUARD_SCHEMA
from mars_app.models import PromptGuardReport
from mars_app.prompts import PROMPT_GUARD_PROMPT


class PromptGuardAgent(BaseAgent):
    def __init__(self, client) -> None:
        super().__init__(client, PROMPT_GUARD_PROMPT, PROMPT_GUARD_SCHEMA)

    def inspect(self, user_request: str) -> PromptGuardReport:
        result = self.run_structured({"user_request": user_request})
        return PromptGuardReport(
            prompt_override_detected=bool(result.get("prompt_override_detected", False)),
            notes=self._as_list(result.get("notes")),
        )

    def _as_list(self, value) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return []
