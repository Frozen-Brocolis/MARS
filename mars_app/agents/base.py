from __future__ import annotations

import json
from abc import ABC
from dataclasses import asdict, is_dataclass
from typing import Any

from mars_app.llm_client import LMStudioClient


class BaseAgent(ABC):
    def __init__(self, client: LMStudioClient, system_prompt: str, response_schema: dict[str, Any] | None = None) -> None:
        self.client = client
        self.system_prompt = system_prompt.strip()
        self.response_schema = response_schema

    def run_text(self, payload: dict[str, Any]) -> str:
        return self.client.ask_text(self.system_prompt, self._serialize(payload))

    def run_structured(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.response_schema is None:
            raise ValueError("Structured response schema is not configured for this agent.")
        return self.client.ask_structured(self.system_prompt, self._serialize(payload), self.response_schema)

    def _serialize(self, payload: dict[str, Any]) -> str:
        normalized = {}
        for key, value in payload.items():
            if is_dataclass(value):
                normalized[key] = asdict(value)
            elif isinstance(value, list):
                normalized[key] = [asdict(item) if is_dataclass(item) else item for item in value]
            else:
                normalized[key] = value
        return json.dumps(normalized, ensure_ascii=False, indent=2)
