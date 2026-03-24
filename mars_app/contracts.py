SHIELD_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string"},
        "sanitized_request": {"type": "string"},
        "risk_notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["status", "sanitized_request", "risk_notes"],
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
