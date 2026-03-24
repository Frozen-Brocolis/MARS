from __future__ import annotations

from mars_app.models import SearchResult


class WebSearchService:
    def __init__(self, enabled: bool = False) -> None:
        self.enabled = enabled

    def search(self, query: str) -> list[SearchResult]:
        if not self.enabled:
            return [
                SearchResult(
                    title="Web search disabled",
                    url="",
                    snippet="Веб-поиск пока не подключён. Нужен реальный backend для поиска и фильтрации источников.",
                    source_type="system",
                    trust_level="none",
                )
            ]
        return [
            SearchResult(
                title="Search backend is not implemented",
                url="",
                snippet=f"Запрос получен, но backend ещё не добавлен: {query}",
                source_type="system",
                trust_level="none",
            )
        ]

    def build_context(self, query: str) -> str:
        results = self.search(query)
        lines = []
        for result in results:
            lines.append(
                f"[{result.trust_level}] {result.title} | {result.url} | {result.snippet}"
            )
        return "\n".join(lines)
