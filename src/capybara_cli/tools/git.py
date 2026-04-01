from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from .base import BaseTool, ToolResult


class GitTool(BaseTool):
    name = "git"
    description = "Execute git commands"
    parameters = {
        "command": {
            "type": "string",
            "description": "Git subcommand to execute (e.g., status, log, diff)",
            "required": True,
        },
        "args": {
            "type": "array",
            "description": "Additional arguments",
            "required": False,
        },
        "cwd": {
            "type": "string",
            "description": "Working directory",
            "required": False,
        },
    }
    
    ALLOWED_COMMANDS = [
        "status", "log", "diff", "show", "branch", "remote",
        "ls-files", "ls-tree", "rev-parse", "config", "describe",
    ]
    
    async def execute(self, command: str, args: list[str] | None = None, cwd: str | None = None) -> ToolResult:
        if command not in self.ALLOWED_COMMANDS:
            return ToolResult(
                success=False,
                output="",
                error=f"Command '{command}' not allowed. Allowed: {', '.join(self.ALLOWED_COMMANDS)}",
            )
        
        working_dir = Path(cwd) if cwd else Path.cwd()
        args = args or []
        full_command = f"git {command} {' '.join(args)}"
        
        try:
            process = await asyncio.create_subprocess_shell(
                full_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            output = stdout.decode("utf-8", errors="replace")
            error = stderr.decode("utf-8", errors="replace")
            
            return ToolResult(
                success=process.returncode == 0,
                output=output,
                error=error if error else None,
            )
            
        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                output="",
                error="Git command timed out",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )
