from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SafetyReport:
    status: str
    sanitized_request: str
    risk_notes: list[str] = field(default_factory=list)


@dataclass
class PromptGuardReport:
    prompt_override_detected: bool
    notes: list[str] = field(default_factory=list)


@dataclass
class RequestSearchReport:
    rewrite_needed: bool
    notes: list[str] = field(default_factory=list)
    editor_brief: str = ""


@dataclass
class RequestEditResult:
    rewritten_request: str
    change_summary: list[str] = field(default_factory=list)


@dataclass
class PlanStep:
    step_id: str
    title: str
    description: str


@dataclass
class ExecutionPlan:
    goal: str
    success_criteria: list[str] = field(default_factory=list)
    steps: list[PlanStep] = field(default_factory=list)
    requires_web_search: bool = False
    notes: list[str] = field(default_factory=list)


@dataclass
class ManagedTask:
    step_id: str
    title: str
    instructions: str
    acceptance_criteria: list[str] = field(default_factory=list)
    use_memory: bool = True
    use_web_search: bool = False
    retry_count: int = 0


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source_type: str
    trust_level: str


@dataclass
class WorkerOutput:
    task_id: str
    summary: str
    details: str
    sources: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)


@dataclass
class Critique:
    task_id: str
    score: int
    approved: bool
    issues: list[str] = field(default_factory=list)
    retry_guidance: str = ""


@dataclass
class FinalAnswer:
    content: str
    format_name: str = "plain_text"
    notes: list[str] = field(default_factory=list)


@dataclass
class ProgressEvent:
    stage: str
    title: str
    details: str = ""
    level: str = "info"


@dataclass
class PostProcessResult:
    content: str
    removed_fragments: list[str] = field(default_factory=list)


@dataclass
class EditReview:
    score: int
    approved: bool
    preferred_version: str
    issues: list[str] = field(default_factory=list)
    retry_guidance: str = ""
