PROMPT_GUARD_SCHEMA = {
    "type": "object",
    "properties": {
        "prompt_override_detected": {"type": "boolean"},
        "notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["prompt_override_detected", "notes"],
}

REQUEST_SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "rewrite_needed": {"type": "boolean"},
        "notes": {"type": "array", "items": {"type": "string"}},
        "editor_brief": {"type": "string"},
    },
    "required": ["rewrite_needed", "notes", "editor_brief"],
}

REQUEST_EDIT_SCHEMA = {
    "type": "object",
    "properties": {
        "rewritten_request": {"type": "string"},
        "change_summary": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["rewritten_request", "change_summary"],
}

PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "goal": {"type": "string"},
        "success_criteria": {"type": "array", "items": {"type": "string"}},
        "requires_web_search": {"type": "boolean"},
        "notes": {"type": "array", "items": {"type": "string"}},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step_id": {"type": "string"},
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                },
                "required": ["step_id", "title", "description"],
            },
        },
    },
    "required": ["goal", "success_criteria", "requires_web_search", "notes", "steps"],
}

MANAGED_TASK_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "instructions": {"type": "string"},
        "acceptance_criteria": {"type": "array", "items": {"type": "string"}},
        "use_memory": {"type": "boolean"},
        "use_web_search": {"type": "boolean"},
    },
    "required": ["title", "instructions", "acceptance_criteria", "use_memory", "use_web_search"],
}

WORKER_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "details": {"type": "string"},
        "sources": {"type": "array", "items": {"type": "string"}},
        "artifacts": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "details", "sources", "artifacts"],
}

CRITIQUE_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer"},
        "approved": {"type": "boolean"},
        "issues": {"type": "array", "items": {"type": "string"}},
        "retry_guidance": {"type": "string"},
    },
    "required": ["score", "approved", "issues", "retry_guidance"],
}

EDITOR_REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer"},
        "approved": {"type": "boolean"},
        "preferred_version": {"type": "string"},
        "issues": {"type": "array", "items": {"type": "string"}},
        "retry_guidance": {"type": "string"},
    },
    "required": ["score", "approved", "preferred_version", "issues", "retry_guidance"],
}
