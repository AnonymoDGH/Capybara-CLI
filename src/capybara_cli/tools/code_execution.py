from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any

from .base import BaseTool, ToolResult


class CodeExecutionTool(BaseTool):
    name = "code_execution"
    description = "Execute Python code in a sandboxed environment"
    parameters = {
        "code": {
            "type": "string",
            "description": "Python code to execute",
            "required": True,
        },
        "language": {
            "type": "string",
            "description": "Programming language (python, javascript)",
            "required": False,
        },
    }
    
    async def execute(self, code: str, language: str = "python") -> ToolResult:
        if language == "python":
            return await self._execute_python(code)
        elif language == "javascript":
            return await self._execute_javascript(code)
        else:
            return ToolResult(
                success=False,
                output="",
                error=f"Unsupported language: {language}",
            )
    
    async def _execute_python(self, code: str) -> ToolResult:
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            process = await asyncio.create_subprocess_exec(
                "python", temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                timeout=30,
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            Path(temp_path).unlink(missing_ok=True)
            
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
                error="Code execution timed out",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )
    
    async def _execute_javascript(self, code: str) -> ToolResult:
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            process = await asyncio.create_subprocess_exec(
                "node", temp_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
            
            Path(temp_path).unlink(missing_ok=True)
            
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
                error="Code execution timed out",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )
