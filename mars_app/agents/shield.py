from __future__ import annotations

from mars_app.agents.base import BaseAgent
from mars_app.contracts import SHIELD_SCHEMA
from mars_app.models import SafetyReport
from mars_app.prompts import SHIELD_PROMPT


class ShieldAgent(BaseAgent):
    def __init__(self, client) -> None:
        super().__init__(client, SHIELD_PROMPT, SHIELD_SCHEMA)

    def analyze(self, user_request: str) -> SafetyReport:
        result = self.run_structured({"user_request": user_request})
        return SafetyReport(
            status=result.get("status", "allowed"),
            sanitized_request=result.get("sanitized_request", user_request),
            risk_notes=self._as_list(result.get("risk_notes")),
        )

    def _as_list(self, value) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return []
