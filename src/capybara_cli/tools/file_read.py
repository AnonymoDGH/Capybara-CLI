from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import BaseTool, ToolResult


class FileReadTool(BaseTool):
    name = "file_read"
    description = "Read the contents of a file"
    parameters = {
        "path": {
            "type": "string",
            "description": "Path to the file to read",
            "required": True,
        },
        "offset": {
            "type": "integer",
            "description": "Line number to start reading from (1-indexed)",
            "required": False,
        },
        "limit": {
            "type": "integer",
            "description": "Maximum number of lines to read",
            "required": False,
        },
    }
    
    MAX_FILE_SIZE = 1024 * 1024
    MAX_LINES = 10000
    
    async def execute(self, path: str, offset: int | None = None, limit: int | None = None) -> ToolResult:
        try:
            file_path = Path(path).resolve()
            
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File not found: {path}",
                )
            
            if not file_path.is_file():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Path is not a file: {path}",
                )
            
            if file_path.stat().st_size > self.MAX_FILE_SIZE:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File too large (max {self.MAX_FILE_SIZE} bytes)",
                )
            
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            
            start = (offset - 1) if offset else 0
            end = start + limit if limit else len(lines)
            lines = lines[start:end]
            
            if len(lines) > self.MAX_LINES:
                lines = lines[:self.MAX_LINES]
            
            content = "".join(lines)
            
            return ToolResult(
                success=True,
                output=content,
                data={
                    "path": str(file_path),
                    "lines": len(lines),
                    "total_lines": len(lines),
                },
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )
