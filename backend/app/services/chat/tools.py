from typing import Any

from langchain.tools import BaseTool, tool
from langchain_tavily import TavilySearch

from app.core.config import settings

WEB_SEARCH_TOOL_NAME = "tavily_search"


def _format_search_result(result: Any) -> str:
    if not isinstance(result, dict):
        return str(result)

    answer = result.get("answer")
    if answer:
        return str(answer)

    snippets: list[str] = []
    for item in result.get("results", [])[:3]:
        if not isinstance(item, dict):
            continue
        title = item.get("title", "")
        content = str(item.get("content", ""))[:200]
        snippets.append(f"{title}: {content}".strip())
    return "\n".join(snippets) or "No web search results found."


def build_web_search_tool() -> BaseTool:
    @tool(
        WEB_SEARCH_TOOL_NAME,
        return_direct=True,
        description=(
            "Searches the web for current, factual, and up-to-date information. "
            "Use it for recent events, factual lookups, statistics, news, "
            "documentation, and information that may have changed. "
            "Input should be a concise, specific search query."
        ),
    )
    async def web_search(query: str) -> Any:
        """Search the web using Tavily."""
        if settings.tavily_api_key is None:
            raise RuntimeError("TAVILY_API_KEY is not configured")

        search = TavilySearch(
            max_results=3,
            topic="general",
            search_depth="basic",
            include_answer=True,
            tavily_api_key=settings.tavily_api_key.get_secret_value(),
        )
        return _format_search_result(await search.ainvoke(query))

    return web_search
