from __future__ import annotations

from mars_app.agents.base import BaseAgent
from mars_app.contracts import REQUEST_SEARCH_SCHEMA
from mars_app.models import RequestSearchReport
from mars_app.prompts import REQUEST_SEARCH_PROMPT


class RequestSearchAgent(BaseAgent):
    def __init__(self, client) -> None:
        super().__init__(client, REQUEST_SEARCH_PROMPT, REQUEST_SEARCH_SCHEMA)

    def inspect(self, user_request: str) -> RequestSearchReport:
        result = self.run_structured({"user_request": user_request})
        return RequestSearchReport(
            rewrite_needed=bool(result.get("rewrite_needed", False)),
            notes=self._as_list(result.get("notes")),
            editor_brief=str(result.get("editor_brief", "")),
        )

    def _as_list(self, value) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return []
