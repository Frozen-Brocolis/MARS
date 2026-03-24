from __future__ import annotations

from mars_app.agents.base import BaseAgent
from mars_app.contracts import PLAN_SCHEMA
from mars_app.models import ExecutionPlan, PlanStep
from mars_app.prompts import PLANNER_PROMPT


class PlannerAgent(BaseAgent):
    def __init__(self, client) -> None:
        super().__init__(client, PLANNER_PROMPT, PLAN_SCHEMA)

    def create_plan(self, safe_request: str, planner_notes: list[str] | None = None) -> ExecutionPlan:
        result = self.run_structured(
            {
                "safe_request": safe_request,
                "planner_notes": planner_notes or [],
            }
        )
        steps = self._parse_steps(result.get("steps"), safe_request)
        return ExecutionPlan(
            goal=result.get("goal", safe_request),
            success_criteria=self._as_list(result.get("success_criteria")),
            steps=steps,
            requires_web_search=bool(result.get("requires_web_search", False)),
            notes=self._as_list(result.get("notes")),
        )

    def _parse_steps(self, raw_steps, fallback_request: str) -> list[PlanStep]:
        if not isinstance(raw_steps, list) or not raw_steps:
            return [PlanStep(step_id="step-1", title="Основная задача", description=fallback_request)]
        steps = []
        for index, item in enumerate(raw_steps, start=1):
            if not isinstance(item, dict):
                continue
            steps.append(
                PlanStep(
                    step_id=str(item.get("step_id", f"step-{index}")),
                    title=str(item.get("title", f"Этап {index}")),
                    description=str(item.get("description", fallback_request)),
                )
            )
        return steps or [PlanStep(step_id="step-1", title="Основная задача", description=fallback_request)]

    def _as_list(self, value) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return []
