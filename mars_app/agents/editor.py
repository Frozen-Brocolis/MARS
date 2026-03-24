from __future__ import annotations

from mars_app.agents.base import BaseAgent
from mars_app.models import FinalAnswer, WorkerOutput
from mars_app.prompts import EDITOR_PROMPT


class EditorAgent(BaseAgent):
    def __init__(self, client) -> None:
        super().__init__(client, EDITOR_PROMPT)

    def render(
        self,
        original_request: str,
        approved_results: list[WorkerOutput],
        notes: list[str],
    ) -> FinalAnswer:
        content = self.run_text(
            {
                "original_request": original_request,
                "approved_results": approved_results,
                "notes": notes,
            }
        )
        return FinalAnswer(content=content, notes=notes)
