from __future__ import annotations

import fnmatch
import re
from pathlib import Path
from typing import Any

from .base import BaseTool, ToolResult


class SearchTool(BaseTool):
    name = "search"
    description = "Search for files or content in the codebase"
    parameters = {
        "query": {
            "type": "string",
            "description": "Search query (regex or glob pattern)",
            "required": True,
        },
        "path": {
            "type": "string",
            "description": "Directory to search in",
            "required": False,
        },
        "pattern": {
            "type": "string",
            "description": "File pattern to match (e.g., *.py)",
            "required": False,
        },
        "content": {
            "type": "boolean",
            "description": "Search in file contents (default: True)",
            "required": False,
        },
    }
    
    IGNORE_PATTERNS = [
        ".git",
        "__pycache__",
        "*.pyc",
        "node_modules",
        ".venv",
        "venv",
        ".env",
        "dist",
        "build",
        ".pytest_cache",
        ".mypy_cache",
    ]
    
    async def execute(self, query: str, path: str | None = None, pattern: str | None = None, content: bool = True) -> ToolResult:
        try:
            search_path = Path(path) if path else Path.cwd()
            file_pattern = pattern or "*"
            
            results = []
            
            if content:
                results = await self._search_content(search_path, query, file_pattern)
            else:
                results = await self._search_files(search_path, query)
            
            output = "\n".join(results[:50])
            if len(results) > 50:
                output += f"\n... and {len(results) - 50} more results"
            
            return ToolResult(
                success=True,
                output=output,
                data={"count": len(results)},
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )
    
    async def _search_content(self, path: Path, query: str, pattern: str) -> list[str]:
        results = []
        try:
            regex = re.compile(query, re.IGNORECASE)
        except re.error:
            regex = re.compile(re.escape(query), re.IGNORECASE)
        
        for file_path in path.rglob(pattern):
            if self._should_ignore(file_path):
                continue
            
            if not file_path.is_file():
                continue
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if regex.search(line):
                            results.append(f"{file_path}:{i}:{line.strip()}")
                            if len(results) >= 100:
                                return results
            except:
                pass
        
        return results
    
    async def _search_files(self, path: Path, pattern: str) -> list[str]:
        results = []
        for file_path in path.rglob("*"):
            if self._should_ignore(file_path):
                continue
            
            if fnmatch.fnmatch(file_path.name, pattern):
                results.append(str(file_path))
        
        return results
    
    def _should_ignore(self, path: Path) -> bool:
        for ignore in self.IGNORE_PATTERNS:
            if ignore in str(path):
                return True
        return False
