from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import BaseTool, ToolResult


class CodeAnalysisTool(BaseTool):
    name = "code_analysis"
    description = "Analyze code for issues, complexity, and suggestions"
    parameters = {
        "path": {
            "type": "string",
            "description": "Path to file or directory to analyze",
            "required": True,
        },
        "analysis_type": {
            "type": "string",
            "description": "Type of analysis (complexity, security, style, all)",
            "required": False,
        },
    }
    
    async def execute(self, path: str, analysis_type: str = "all") -> ToolResult:
        try:
            target = Path(path).resolve()
            
            if not target.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Path not found: {path}",
                )
            
            results = []
            
            if target.is_file():
                results = await self._analyze_file(target, analysis_type)
            else:
                results = await self._analyze_directory(target, analysis_type)
            
            return ToolResult(
                success=True,
                output="\n".join(results),
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e),
            )
    
    async def _analyze_file(self, path: Path, analysis_type: str) -> list[str]:
        results = [f"Analysis of {path}", "=" * 40]
        
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                lines = content.split("\n")
            
            results.append(f"Lines: {len(lines)}")
            results.append(f"Characters: {len(content)}")
            
            if analysis_type in ("complexity", "all"):
                complexity = self._calculate_complexity(content)
                results.append(f"Cyclomatic complexity estimate: {complexity}")
            
            if analysis_type in ("security", "all"):
                issues = self._check_security(content)
                if issues:
                    results.append("Security concerns:")
                    for issue in issues:
                        results.append(f"  - {issue}")
            
        except Exception as e:
            results.append(f"Error analyzing file: {e}")
        
        return results
    
    async def _analyze_directory(self, path: Path, analysis_type: str) -> list[str]:
        results = [f"Directory analysis of {path}", "=" * 40]
        
        file_count = 0
        total_lines = 0
        
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix in (".py", ".js", ".ts", ".java", ".go", ".rs"):
                file_count += 1
                try:
                    with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                        total_lines += len(f.readlines())
                except:
                    pass
        
        results.append(f"Source files: {file_count}")
        results.append(f"Total lines: {total_lines}")
        
        return results
    
    def _calculate_complexity(self, content: str) -> int:
        complexity = 1
        complexity_keywords = ["if", "elif", "else", "for", "while", "except", "with", "and", "or"]
        for keyword in complexity_keywords:
            complexity += content.count(f" {keyword} ")
        return complexity
    
    def _check_security(self, content: str) -> list[str]:
        issues = []
        dangerous_patterns = [
            ("eval(", "Use of eval() is dangerous"),
            ("exec(", "Use of exec() is dangerous"),
            ("subprocess.shell", "Shell execution can be unsafe"),
            ("password", "Hardcoded password detected"),
            ("secret", "Hardcoded secret detected"),
            ("api_key", "Hardcoded API key detected"),
        ]
        
        for pattern, message in dangerous_patterns:
            if pattern in content.lower():
                issues.append(message)
        
        return issues
