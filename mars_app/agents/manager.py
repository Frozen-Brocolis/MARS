from __future__ import annotations

from mars_app.agents.base import BaseAgent
from mars_app.contracts import MANAGED_TASK_SCHEMA
from mars_app.models import Critique, ExecutionPlan, ManagedTask, PlanStep
from mars_app.prompts import MANAGER_PROMPT


class ManagerAgent(BaseAgent):
    def __init__(self, client) -> None:
        super().__init__(client, MANAGER_PROMPT, MANAGED_TASK_SCHEMA)

    def create_task(self, plan: ExecutionPlan, step: PlanStep, memory_context: str) -> ManagedTask:
        result = self.run_structured(
            {
                "plan_goal": plan.goal,
                "plan_notes": plan.notes,
                "step": step,
                "memory_context": memory_context,
            }
        )
        return self._build_task(step, result, retry_count=0)

    def revise_task(
        self,
        plan: ExecutionPlan,
        step: PlanStep,
        previous_task: ManagedTask,
        critique: Critique,
        memory_context: str,
    ) -> ManagedTask:
        result = self.run_structured(
            {
                "plan_goal": plan.goal,
                "step": step,
                "previous_task": previous_task,
                "critique": critique,
                "memory_context": memory_context,
            }
        )
        return self._build_task(step, result, retry_count=previous_task.retry_count + 1)

    def _build_task(self, step: PlanStep, payload: dict, retry_count: int) -> ManagedTask:
        return ManagedTask(
            step_id=step.step_id,
            title=str(payload.get("title", step.title)),
            instructions=str(payload.get("instructions", step.description)),
            acceptance_criteria=self._as_list(payload.get("acceptance_criteria")),
            use_memory=bool(payload.get("use_memory", True)),
            use_web_search=bool(payload.get("use_web_search", False)),
            retry_count=retry_count,
        )

    def _as_list(self, value) -> list[str]:
        if isinstance(value, list):
            return [str(item) for item in value]
        return []
