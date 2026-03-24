from __future__ import annotations

from mars_app.agents.base import BaseAgent
from mars_app.contracts import EDITOR_REVIEW_SCHEMA
from mars_app.models import EditReview
from mars_app.prompts import EDITOR_CRITIC_PROMPT


class EditorCriticAgent(BaseAgent):
    def __init__(self, client) -> None:
        super().__init__(client, EDITOR_CRITIC_PROMPT, EDITOR_REVIEW_SCHEMA)

    def review(
        self,
        original_request: str,
        draft_answer: str,
        cleaned_answer: str,
        removed_fragments: list[str],
    ) -> EditReview:
        result = self.run_structured(
            {
                "original_request": original_request,
                "draft_answer": draft_answer,
                "cleaned_answer": cleaned_answer,
                "removed_fragments": removed_fragments,
            }
        )
        score = int(result.get("score", 0))
        score = max(0, min(score, 10))
        preferred_version = str(result.get("preferred_version", "cleaned")).strip().lower()
        if preferred_version not in {"draft", "cleaned"}:
            preferred_version = "cleaned"
        return EditReview(
            score=score,
            approved=bool(result.get("approved", preferred_version == "cleaned" and score >= 7)),
            preferred_version=preferred_version,
            issues=self._as_list(result.get("issues")),
            retry_guidance=str(result.get("retry_guidance", "")),
        )

    def _as_list(self, value) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return []
