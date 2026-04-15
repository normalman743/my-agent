"""
Google search tool — web search via Google Custom Search API.

Requires GOOGLE_SEARCH_API_KEY and GOOGLE_CSE_ID in .env.
"""
import logging

import requests

from agent.tools.registry import tool
from agent.config import settings

logger = logging.getLogger(__name__)


@tool(description="Search the web using Google. Returns top results with titles, links, and snippets.")
def web_search(query: str, num_results: int = 5) -> str:
    """Search Google Custom Search and return formatted results."""
    if not settings.search.google_enabled:
        return "Error: Google Search not configured. Set GOOGLE_SEARCH_API_KEY and GOOGLE_CSE_ID in .env."

    try:
        resp = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": settings.search.google_api_key,
                "cx": settings.search.google_cse_id,
                "q": query,
                "num": min(num_results, 10),
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return f"Search error: {e}"

    items = data.get("items", [])
    if not items:
        return f"No results found for: {query}"

    results = []
    for i, item in enumerate(items, 1):
        title = item.get("title", "")
        link = item.get("link", "")
        snippet = item.get("snippet", "")
        results.append(f"{i}. {title}\n   {link}\n   {snippet}")

    return "\n\n".join(results)
