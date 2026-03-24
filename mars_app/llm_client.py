from __future__ import annotations

import json
from typing import Any

import lmstudio as lms


class LMStudioClient:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.model = lms.llm(model_name)

    def ask_text(self, system_prompt: str, user_prompt: str) -> str:
        chat = lms.Chat(system_prompt)
        chat.add_user_message(user_prompt)
        response = self.model.respond(chat)
        return self._extract_text(response)

    def ask_structured(self, system_prompt: str, user_prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        chat = lms.Chat(system_prompt)
        chat.add_user_message(user_prompt)
        response = self.model.respond(chat, response_format=schema)
        parsed = self._extract_parsed(response)
        if isinstance(parsed, dict):
            return parsed
        raise TypeError(f"Expected dict response from LM Studio, got: {type(parsed)!r}")

    def _extract_parsed(self, response: Any) -> Any:
        if hasattr(response, "parsed"):
            parsed = response.parsed
            if hasattr(parsed, "model_dump"):
                return parsed.model_dump()
            return parsed
        return response

    def _extract_text(self, response: Any) -> str:
        if hasattr(response, "content") and isinstance(response.content, str):
            return response.content.strip()
        if hasattr(response, "text") and isinstance(response.text, str):
            return response.text.strip()
        parsed = self._extract_parsed(response)
        if isinstance(parsed, str):
            return parsed.strip()
        return json.dumps(parsed, ensure_ascii=False, indent=2)
