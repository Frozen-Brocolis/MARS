from __future__ import annotations

import re

from mars_app.models import PostProcessResult


class FinalAnswerPostProcessor:
    _SOURCE_HEADER_RE = re.compile(r"^\s*источники\s*:\s*", re.IGNORECASE)
    _FILE_HEADER_RE = re.compile(r"^\s*файл\s+с\s+информацией\s*:\s*", re.IGNORECASE)
    _NOTES_HEADER_RE = re.compile(r"^\s*\[?\s*заметки\s*\]?\s*$", re.IGNORECASE)
    _BULLET_RE = re.compile(r"^\s*[-*•]\s+")
    _URL_RE = re.compile(r"https?://", re.IGNORECASE)

    def clean(self, original_request: str, draft_content: str) -> PostProcessResult:
        allow_sources = self._requests_sources(original_request)
        allow_file_ref = self._requests_file_reference(original_request)
        allow_notes = self._requests_notes(original_request)

        lines = draft_content.splitlines()
        cleaned_lines: list[str] = []
        removed_fragments: list[str] = []
        index = 0

        while index < len(lines):
            line = lines[index]
            stripped = line.strip()

            if not allow_sources and self._SOURCE_HEADER_RE.match(stripped):
                index, removed = self._consume_service_block(lines, index, consume_urls=True, consume_bullets=True)
                removed_fragments.append(removed)
                continue

            if not allow_file_ref and self._FILE_HEADER_RE.match(stripped):
                removed_fragments.append(line)
                index += 1
                continue

            if not allow_notes and self._NOTES_HEADER_RE.match(stripped):
                index, removed = self._consume_service_block(lines, index, consume_urls=False, consume_bullets=True)
                removed_fragments.append(removed)
                continue

            cleaned_lines.append(line)
            index += 1

        cleaned_text = self._normalize_spacing("\n".join(cleaned_lines))
        removed_fragments = [fragment.strip() for fragment in removed_fragments if fragment.strip()]
        return PostProcessResult(content=cleaned_text, removed_fragments=removed_fragments)

    def _consume_service_block(
        self,
        lines: list[str],
        start_index: int,
        consume_urls: bool,
        consume_bullets: bool,
    ) -> tuple[int, str]:
        removed: list[str] = [lines[start_index]]
        index = start_index + 1
        while index < len(lines):
            stripped = lines[index].strip()
            if not stripped:
                removed.append(lines[index])
                index += 1
                break
            if consume_bullets and self._BULLET_RE.match(stripped):
                removed.append(lines[index])
                index += 1
                continue
            if consume_urls and self._URL_RE.search(stripped):
                removed.append(lines[index])
                index += 1
                continue
            break
        return index, "\n".join(removed)

    def _normalize_spacing(self, text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _requests_sources(self, request: str) -> bool:
        lowered = request.lower()
        return any(token in lowered for token in ("источник", "источники", "ссылк", "reference", "references", "url"))

    def _requests_file_reference(self, request: str) -> bool:
        lowered = request.lower()
        return any(token in lowered for token in ("файл", "название файла", "путь", "path"))

    def _requests_notes(self, request: str) -> bool:
        lowered = request.lower()
        return any(token in lowered for token in ("заметки", "примечания", "notes", "note"))
