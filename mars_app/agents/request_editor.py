from __future__ import annotations

from mars_app.agents.base import BaseAgent
from mars_app.contracts import REQUEST_EDIT_SCHEMA
from mars_app.models import RequestEditResult
from mars_app.prompts import REQUEST_EDITOR_PROMPT


class RequestEditorAgent(BaseAgent):
    def __init__(self, client) -> None:
        super().__init__(client, REQUEST_EDITOR_PROMPT, REQUEST_EDIT_SCHEMA)

    def rewrite(self, user_request: str, reasons: list[str], editor_brief: str) -> RequestEditResult:
        result = self.run_structured(
            {
                "user_request": user_request,
                "reasons": reasons,
                "editor_brief": editor_brief,
            }
        )
        rewritten_request = str(result.get("rewritten_request", user_request)).strip() or user_request
        return RequestEditResult(
            rewritten_request=rewritten_request,
            change_summary=self._as_list(result.get("change_summary")),
        )

    def _as_list(self, value) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return []
