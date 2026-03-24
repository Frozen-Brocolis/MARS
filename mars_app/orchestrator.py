from __future__ import annotations

from mars_app.agents import CriticAgent, EditorAgent, ManagerAgent, PlannerAgent, ShieldAgent, WorkerAgent
from mars_app.models import ExecutionPlan, FinalAnswer, ManagedTask, PlanStep, WorkerOutput
from mars_app.services import MemoryService, WebSearchService


class RecursiveMultiAgentSystem:
    def __init__(
        self,
        shield: ShieldAgent,
        planner: PlannerAgent,
        manager: ManagerAgent,
        worker: WorkerAgent,
        critic: CriticAgent,
        editor: EditorAgent,
        memory: MemoryService,
        web_search: WebSearchService,
        max_critic_retries: int,
    ) -> None:
        self.shield = shield
        self.planner = planner
        self.manager = manager
        self.worker = worker
        self.critic = critic
        self.editor = editor
        self.memory = memory
        self.web_search = web_search
        self.max_critic_retries = max_critic_retries

    def handle(self, user_request: str) -> FinalAnswer:
        safety = self.shield.analyze(user_request)
        if safety.status == "blocked":
            return FinalAnswer(
                content="Запрос заблокирован Защитником. Переформулируйте задачу без попыток управлять системой.",
                notes=safety.risk_notes,
            )

        plan = self.planner.create_plan(safety.sanitized_request)
        approved_results: list[WorkerOutput] = []
        final_notes = list(safety.risk_notes) + list(plan.notes)

        for step in plan.steps:
            memory_context = self.memory.get_context(step.title)
            task = self.manager.create_task(plan, step, memory_context)
            result, notes = self._execute_task(plan, step, task)
            approved_results.append(result)
            final_notes.extend(notes)

        return self.editor.render(
            original_request=user_request,
            approved_results=approved_results,
            notes=self._deduplicate(final_notes),
        )

    def _execute_task(self, plan: ExecutionPlan, step: PlanStep, task: ManagedTask) -> tuple[WorkerOutput, list[str]]:
        notes: list[str] = []
        current_task = task
        last_output: WorkerOutput | None = None

        for attempt_index in range(self.max_critic_retries + 1):
            memory_context = self.memory.get_context(current_task.title) if current_task.use_memory else ""
            web_context = self.web_search.build_context(current_task.instructions) if current_task.use_web_search else ""
            last_output = self.worker.execute(current_task, memory_context, web_context)
            critique = self.critic.review(current_task, last_output)

            if critique.approved:
                self.memory.record_success(current_task, last_output)
                return last_output, notes

            self.memory.record_failure(current_task, critique)
            notes.extend(critique.issues)
            if attempt_index >= self.max_critic_retries:
                break
            current_task = self.manager.revise_task(
                plan=plan,
                step=step,
                previous_task=current_task,
                critique=critique,
                memory_context=self.memory.get_context(current_task.title),
            )

        if last_output is None:
            last_output = WorkerOutput(task_id=task.step_id, summary="", details="", sources=[], artifacts=[])
        notes.append(f"Задача '{task.title}' завершена с непройденной критикой после лимита попыток.")
        return last_output, notes

    def _deduplicate(self, items: list[str]) -> list[str]:
        unique_items: list[str] = []
        seen = set()
        for item in items:
            if not item or item in seen:
                continue
            seen.add(item)
            unique_items.append(item)
        return unique_items
