from __future__ import annotations

import asyncio
import os
import re
import shlex
from pathlib import Path
from typing import Any

from .base import BaseTool, ToolResult


class BashTool(BaseTool):
    name = "bash"
    description = "Execute bash commands in the shell"
    parameters = {
        "command": {
            "type": "string",
            "description": "The bash command to execute",
            "required": True,
        },
        "cwd": {
            "type": "string",
            "description": "Working directory for the command",
            "required": False,
        },
        "timeout": {
            "type": "integer",
            "description": "Timeout in seconds",
            "required": False,
        },
    }
    
    BLOCKED_PATTERNS = [
        r"rm\s+-rf\s+/",
        r">\s*/dev/",
        r":\(\)\{\s*:\|\:&\s*\};:",
        r"curl.*\|.*sh",
        r"wget.*\|.*sh",
        r"mkfs",
        r"dd\s+if=",
        r"\bsu\b",
        r"\bsudo\b",
    ]
    
    def __init__(self, config: dict[str, Any] | None = None):
        super().__init__(config)
        self.timeout = config.get("timeout", 60) if config else 60
        self.allowed_commands = config.get("allowed_commands", []) if config else []
        self.blocked_patterns = config.get("blocked_patterns", self.BLOCKED_PATTERNS) if config else self.BLOCKED_PATTERNS
    
    async def execute(self, command: str, cwd: str | None = None, timeout: int | None = None) -> ToolResult:
        if not self._is_safe(command):
            return ToolResult(
                success=False,
                output="",
                error="Command blocked for security reasons",
            )
        
        working_dir = Path(cwd) if cwd else Path.cwd()
        timeout_val = timeout or self.timeout
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
                env=os.environ.copy(),
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout_val,
            )
            
            output = stdout.decode("utf-8", errors="replace")
            error = stderr.decode("utf-8", errors="replace")
            
            if len(output) > 10000:
                output = output[:10000] + "\n... (truncated)"
            
            return ToolResult(
                success=process.returncode == 0,
                output=output,
                error=error if error else None,
                data={"returncode": process.returncode},
            )
            
        except asyncio.TimeoutError:
            process.kill()
            return ToolResult(
                success=False,
                output="",
                error=f"Command timed out after {timeout_val} seconds",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )
    
    def _is_safe(self, command: str) -> bool:
        for pattern in self.blocked_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return False
        return True
