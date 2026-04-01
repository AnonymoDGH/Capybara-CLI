from __future__ import annotations

from typing import Any

import httpx

from .base import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for information"
    parameters = {
        "query": {
            "type": "string",
            "description": "Search query",
            "required": True,
        },
        "num_results": {
            "type": "integer",
            "description": "Number of results to return",
            "required": False,
        },
    }
    
    async def execute(self, query: str, num_results: int = 5) -> ToolResult:
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={httpx.quote(query)}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    search_url,
                    headers={"User-Agent": "Mozilla/5.0"},
                    timeout=30,
                )
                response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            
            for result in soup.select(".result")[:num_results]:
                title_elem = result.select_one(".result__title")
                snippet_elem = result.select_one(".result__snippet")
                
                if title_elem and snippet_elem:
                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True)
                    results.append(f"{title}\n{snippet}\n")
            
            return ToolResult(
                success=True,
                output="\n".join(results),
                data={"count": len(results)},
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )
