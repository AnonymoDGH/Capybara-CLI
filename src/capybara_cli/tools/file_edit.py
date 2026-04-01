from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import BaseTool, ToolResult


class FileEditTool(BaseTool):
    name = "file_edit"
    description = "Edit a file by replacing content"
    parameters = {
        "path": {
            "type": "string",
            "description": "Path to the file to edit",
            "required": True,
        },
        "old_string": {
            "type": "string",
            "description": "String to replace",
            "required": True,
        },
        "new_string": {
            "type": "string",
            "description": "Replacement string",
            "required": True,
        },
    }
    
    async def execute(self, path: str, old_string: str, new_string: str) -> ToolResult:
        try:
            file_path = Path(path).resolve()
            
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File not found: {path}",
                )
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if old_string not in content:
                return ToolResult(
                    success=False,
                    output="",
                    error="old_string not found in file",
                )
            
            new_content = content.replace(old_string, new_string, 1)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            return ToolResult(
                success=True,
                output=f"Successfully edited {path}",
                data={"path": str(file_path)},
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )
