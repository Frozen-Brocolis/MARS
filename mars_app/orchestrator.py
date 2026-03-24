from __future__ import annotations

from mars_app.agents import (
    CriticAgent,
    EditorAgent,
    EditorCriticAgent,
    ManagerAgent,
    PlannerAgent,
    PromptGuardAgent,
    RequestEditorAgent,
    RequestSearchAgent,
    WorkerAgent,
)
from mars_app.models import ExecutionPlan, FinalAnswer, ManagedTask, PlanStep, WorkerOutput
from mars_app.services import FinalAnswerPostProcessor, MemoryService, ProgressReporter, WebSearchService


class RecursiveMultiAgentSystem:
    def __init__(
        self,
        prompt_guard: PromptGuardAgent,
        request_search: RequestSearchAgent,
        request_editor: RequestEditorAgent,
        planner: PlannerAgent,
        manager: ManagerAgent,
        worker: WorkerAgent,
        critic: CriticAgent,
        editor: EditorAgent,
        editor_critic: EditorCriticAgent,
        memory: MemoryService,
        web_search: WebSearchService,
        finalizer: FinalAnswerPostProcessor,
        progress: ProgressReporter,
        max_critic_retries: int,
    ) -> None:
        self.prompt_guard = prompt_guard
        self.request_search = request_search
        self.request_editor = request_editor
        self.planner = planner
        self.manager = manager
        self.worker = worker
        self.critic = critic
        self.editor = editor
        self.editor_critic = editor_critic
        self.memory = memory
        self.web_search = web_search
        self.finalizer = finalizer
        self.progress = progress
        self.max_critic_retries = max_critic_retries

    def handle(self, user_request: str) -> FinalAnswer:
        self.progress.emit("system", "Получен новый запрос", user_request)

        prompt_guard_report = self.prompt_guard.inspect(user_request)
        self.progress.emit(
            "prompt_guard",
            "PromptGuard завершил проверку",
            "\n".join(prompt_guard_report.notes) if prompt_guard_report.notes else "Опасных попыток не найдено.",
            level="warning" if prompt_guard_report.prompt_override_detected else "info",
        )

        request_search_report = self.request_search.inspect(user_request)
        self.progress.emit(
            "search",
            "Search проверил сообщение на критичные ошибки",
            "\n".join(request_search_report.notes) if request_search_report.notes else "Критичных проблем не найдено.",
            level="warning" if request_search_report.rewrite_needed else "info",
        )

        planner_notes = list(prompt_guard_report.notes) + list(request_search_report.notes)
        working_request = user_request

        if prompt_guard_report.prompt_override_detected or request_search_report.rewrite_needed:
            request_edit = self.request_editor.rewrite(
                user_request=user_request,
                reasons=planner_notes,
                editor_brief=request_search_report.editor_brief,
            )
            working_request = request_edit.rewritten_request
            planner_notes.extend(request_edit.change_summary)
            self.progress.emit(
                "request_editor",
                "RequestEditor скорректировал входное сообщение",
                "\n".join(request_edit.change_summary) if request_edit.change_summary else working_request,
                level="warning",
            )

        plan = self.planner.create_plan(working_request, planner_notes=planner_notes)
        self.progress.emit("planner", f"Planner построил план из {len(plan.steps)} этапов", plan.goal)
        approved_results: list[WorkerOutput] = []
        final_notes = list(planner_notes) + list(plan.notes)

        for step in plan.steps:
            self.progress.emit("manager", f"Старт этапа {step.step_id}: {step.title}", step.description)
            memory_context = self.memory.get_context(step.title)
            task = self.manager.create_task(plan, step, memory_context)
            self.progress.emit("manager", f"Manager подготовил задачу: {task.title}", task.instructions)
            result, notes = self._execute_task(plan, step, task)
            approved_results.append(result)
            final_notes.extend(notes)
            self.progress.emit("system", f"Этап завершён: {step.title}", result.summary)

        self.progress.emit("editor", "Editor собирает итоговый ответ")
        draft_answer = self.editor.render(
            original_request=user_request,
            approved_results=approved_results,
        )
        postprocess_result = self.finalizer.clean(user_request, draft_answer.content)
        if postprocess_result.removed_fragments:
            self.progress.emit(
                "editor",
                "Пост-обработчик удалил служебные вставки",
                "\n\n".join(postprocess_result.removed_fragments),
                level="warning",
            )
        edit_review = self.editor_critic.review(
            original_request=user_request,
            draft_answer=draft_answer.content,
            cleaned_answer=postprocess_result.content,
            removed_fragments=postprocess_result.removed_fragments,
        )
        self.progress.emit(
            "critic",
            f"Критик редакции выставил {edit_review.score}/10",
            edit_review.retry_guidance or "\n".join(edit_review.issues),
            level="info" if edit_review.approved else "warning",
        )
        final_content = postprocess_result.content
        if edit_review.preferred_version == "draft" and not edit_review.approved:
            final_content = draft_answer.content
            self.progress.emit(
                "editor",
                "Сохранена версия до очистки",
                "Очищенная версия могла удалить запрошенную пользователем информацию.",
                level="warning",
            )
        answer = FinalAnswer(content=final_content, notes=self._deduplicate(final_notes + edit_review.issues))
        self.progress.emit("system", "Ответ готов", "Итог передан пользователю.")
        return answer

    def _execute_task(self, plan: ExecutionPlan, step: PlanStep, task: ManagedTask) -> tuple[WorkerOutput, list[str]]:
        notes: list[str] = []
        current_task = task
        last_output: WorkerOutput | None = None

        for attempt_index in range(self.max_critic_retries + 1):
            self.progress.emit(
                "worker",
                f"Попытка {attempt_index + 1} для задачи: {current_task.title}",
                current_task.instructions,
            )
            memory_context = self.memory.get_context(current_task.title) if current_task.use_memory else ""
            web_context = self.web_search.build_context(current_task.instructions) if current_task.use_web_search else ""

            if current_task.use_memory:
                self.progress.emit("memory", "Подключена память", memory_context)
            if current_task.use_web_search:
                self.progress.emit("web", "Подключён веб-поиск", web_context)

            last_output = self.worker.execute(current_task, memory_context, web_context)
            self.progress.emit("worker", "Worker вернул результат", last_output.summary)
            critique = self.critic.review(current_task, last_output)
            critique_details = critique.retry_guidance or "\n".join(critique.issues)
            self.progress.emit(
                "critic",
                f"Critic выставил {critique.score}/10",
                critique_details,
                level="info" if critique.approved else "warning",
            )

            if critique.approved:
                self.memory.record_success(current_task, last_output)
                self.progress.emit("system", f"Задача принята: {current_task.title}", "Критик одобрил результат.")
                return last_output, notes

            self.memory.record_failure(current_task, critique)
            notes.extend(critique.issues)
            if attempt_index >= self.max_critic_retries:
                break

            self.progress.emit(
                "manager",
                f"Пересборка задачи после критики: {current_task.title}",
                critique.retry_guidance,
                level="warning",
            )
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
        self.progress.emit(
            "system",
            f"Лимит попыток исчерпан: {task.title}",
            "Система продолжает выполнение с последним результатом.",
            level="error",
        )
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
