import json
import os
from typing import Any

import requests
from dotenv import load_dotenv  # type: ignore

load_dotenv()

DEFAULT_SEARCH_TIMEOUT = 20
DEFAULT_MAX_RESULTS = 5
TAVILY_SEARCH_URL = "https://api.tavily.com/search"


def _normalize_int(value: Any, default: int) -> int:
    try:
        value = int(value)
    except Exception:
        return default

    return value if value > 0 else default


def _safe_json_dumps(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def web_search(
    query: str,
    max_results: int = DEFAULT_MAX_RESULTS,
    search_depth: str = "basic",
    topic: str = "general",
    include_answer: bool = True,
    include_raw_content: bool = False,
):
    """
    Search the web using Tavily.

    Args:
        query: Search query text.
        max_results: Max number of search results to return.
        search_depth: "basic" or "advanced".
        topic: Usually "general" or "news".
        include_answer: Whether to include Tavily's synthesized answer.
        include_raw_content: Whether to include extracted raw content.
    """
    try:
        if not query or not query.strip():
            return "ERROR: query is required"

        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "ERROR: TAVILY_API_KEY not set"

        max_results = _normalize_int(max_results, DEFAULT_MAX_RESULTS)

        payload = {
            "query": query.strip(),
            "search_depth": search_depth,
            "topic": topic,
            "max_results": max_results,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            TAVILY_SEARCH_URL,
            headers=headers,
            json=payload,
            timeout=DEFAULT_SEARCH_TIMEOUT,
        )
        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])
        cleaned_results = []
        for item in results[:max_results]:
            cleaned_results.append(
                {
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "content": item.get("content"),
                    "score": item.get("score"),
                }
            )

        formatted = {
            "query": query.strip(),
            "answer": data.get("answer"),
            "results": cleaned_results,
        }

        return _safe_json_dumps(formatted)

    except requests.exceptions.Timeout:
        return "ERROR: Web search timed out"
    except requests.exceptions.RequestException as e:
        return f"ERROR: Web search request failed → {str(e)}"
    except Exception as e:
        return f"ERROR: Web search failed → {str(e)}"
