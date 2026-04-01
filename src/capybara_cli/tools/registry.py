"""Tool registry for managing available tools."""

from __future__ import annotations

from typing import Any

try:
    from .base import BaseTool, ToolResult
    from .bash import BashTool
    from .code_analysis import CodeAnalysisTool
    from .code_execution import CodeExecutionTool
    from .file_edit import FileEditTool
    from .file_read import FileReadTool
    from .git import GitTool
    from .search import SearchTool
    from .web_search import WebSearchTool
except ImportError:
    from base import BaseTool, ToolResult
    from bash import BashTool
    from code_analysis import CodeAnalysisTool
    from code_execution import CodeExecutionTool
    from file_edit import FileEditTool
    from file_read import FileReadTool
    from git import GitTool
    from search import SearchTool
    from web_search import WebSearchTool


class ToolRegistry:
    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._tools: dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        tool_classes = [
            BashTool,
            FileReadTool,
            FileEditTool,
            SearchTool,
            GitTool,
            CodeExecutionTool,
            WebSearchTool,
            CodeAnalysisTool,
        ]
        
        for tool_class in tool_classes:
            tool_name = tool_class.name
            if tool_name not in self.config.get("disabled", []):
                self.register(tool_name, tool_class)
    
    def register(self, name: str, tool_class: type[BaseTool]):
        tool_config = self.config.get(name, {})
        self._tools[name] = tool_class(tool_config)
    
    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)
    
    def list_tools(self) -> list[str]:
        return list(self._tools.keys())
    
    def get_schemas(self) -> list[dict[str, Any]]:
        return [tool.get_schema() for tool in self._tools.values()]
    
    async def execute(self, name: str, **kwargs) -> ToolResult:
        tool = self.get(name)
        if tool is None:
            return ToolResult(
                success=False,
                output="",
                error=f"Tool '{name}' not found",
            )
        
        if name in self.config.get("require_confirmation", []) and not kwargs.get("confirmed"):
            return ToolResult(
                success=False,
                output="",
                error=f"Tool '{name}' requires confirmation",
            )
        
        return await tool.execute(**kwargs)
