from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from rich.console import Console

from .config import Config
from .llm import Message, Role, create_provider
from .llm.base import LLMResponse
from .logger import get_logger
from .memory import MemoryManager
from .tools import ToolRegistry

console = Console()
logger = get_logger("agent")


SYSTEM_PROMPT = """You are Capybara CLI, an expert coding agent with superior performance on programming tasks, academic reasoning, and cybersecurity evaluations.

Your capabilities include:
- Writing, refactoring, and debugging code across multiple languages
- Complex problem-solving with step-by-step analysis
- Security analysis and vulnerability detection
- Code review and best practices
- Git operations and repository management
- Documentation generation

When given a task:
1. Analyze the request carefully
2. Use available tools when needed (bash, file_read, file_edit, search, git, etc.)
3. Provide clear, well-structured responses
4. Include code examples when relevant
5. Explain your reasoning

Always be helpful, accurate, and efficient."""


class CapybaraAgent:
    def __init__(self, config: Config):
        self.config = config
        self.llm = None
        self.memory = MemoryManager(config.memory)
        self.tools = ToolRegistry(config.tools.__dict__ if hasattr(config.tools, "__dict__") else {})
        self.iteration = 0
        self.max_iterations = config.agent.max_iterations
    
    async def initialize(self):
        self.llm = create_provider(
            provider=self.config.llm.provider,
            model=self.config.llm.model,
            api_key=self.config.llm.api_key,
            api_base=self.config.llm.api_base,
            temperature=self.config.llm.temperature,
            max_tokens=self.config.llm.max_tokens,
            top_p=self.config.llm.top_p,
            timeout=self.config.llm.timeout,
            max_retries=self.config.llm.max_retries,
        )
        logger.info("Agent initialized", model=self.config.llm.model)
    
    async def shutdown(self):
        logger.info("Agent shutting down")
    
    async def chat(self, user_input: str) -> str:
        self.memory.add_message("user", user_input)
        
        messages = [
            Message(role=Role.SYSTEM, content=SYSTEM_PROMPT),
        ]
        
        for msg in self.memory.get_messages():
            role = Role.USER if msg["role"] == "user" else Role.ASSISTANT
            messages.append(Message(role=role, content=msg["content"]))
        
        response = await self._call_llm(messages)
        
        self.memory.add_message("assistant", response.content)
        
        return response.content
    
    async def ask(self, prompt: str, context_files: list[str] | None = None) -> str:
        context = ""
        if context_files:
            for file_path in context_files:
                try:
                    content = Path(file_path).read_text(encoding="utf-8")
                    context += f"\n\n--- File: {file_path} ---\n{content}"
                except Exception as e:
                    context += f"\n\n--- Error reading {file_path}: {e} ---"
        
        full_prompt = f"{prompt}\n\n{context}" if context else prompt
        
        return await self.chat(full_prompt)
    
    async def generate_code(self, description: str, language: str = "python", output_path: str | None = None) -> str:
        prompt = f"Generate {language} code for: {description}\n\nProvide only the code, no explanations."
        
        response = await self.chat(prompt)
        
        if output_path:
            Path(output_path).write_text(response, encoding="utf-8")
            return f"Code written to {output_path}"
        
        return response
    
    async def fix_bugs(self, file_path: str, dry_run: bool = False) -> str:
        try:
            content = Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading file: {e}"
        
        prompt = f"Fix bugs in this {file_path} code:\n\n```\n{content}\n```\n\nProvide the fixed code only."
        
        response = await self.chat(prompt)
        
        if not dry_run:
            Path(file_path).write_text(response, encoding="utf-8")
            return f"Fixed code written to {file_path}"
        
        return f"Proposed fix:\n{response}"
    
    async def generate_tests(self, file_path: str, framework: str = "pytest", output_path: str | None = None) -> str:
        try:
            content = Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading file: {e}"
        
        prompt = f"Generate {framework} tests for this code:\n\n```\n{content}\n```\n\nProvide only the test code."
        
        response = await self.chat(prompt)
        
        if output_path:
            Path(output_path).write_text(response, encoding="utf-8")
            return f"Tests written to {output_path}"
        
        return response
    
    async def explain(self, target: str) -> str:
        if Path(target).exists():
            try:
                content = Path(target).read_text(encoding="utf-8")
                prompt = f"Explain this code:\n\n```\n{content}\n```"
            except:
                prompt = f"Explain: {target}"
        else:
            prompt = f"Explain: {target}"
        
        return await self.chat(prompt)
    
    async def refactor(self, file_path: str, strategy: str = "improve") -> str:
        try:
            content = Path(file_path).read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading file: {e}"
        
        prompt = f"Refactor this code to {strategy}:\n\n```\n{content}\n```\n\nProvide the refactored code only."
        
        response = await self.chat(prompt)
        Path(file_path).write_text(response, encoding="utf-8")
        
        return f"Refactored code written to {file_path}"
    
    async def security_audit(self, target: str | None = None, scan_all: bool = False) -> str:
        if scan_all:
            prompt = "Perform a security audit of the entire codebase. Identify vulnerabilities, secrets, and security issues."
        elif target and Path(target).exists():
            content = Path(target).read_text(encoding="utf-8")
            prompt = f"Security audit this code:\n\n```\n{content}\n```\n\nIdentify vulnerabilities, secrets, and security issues."
        else:
            prompt = f"Security audit: {target}"
        
        return await self.chat(prompt)
    
    async def _call_llm(self, messages: list[Message], tools: list[dict] | None = None) -> LLMResponse:
        if self.llm is None:
            raise RuntimeError("Agent not initialized")
        
        kwargs = {}
        if tools:
            kwargs["tools"] = tools
        
        for attempt in range(self.config.llm.max_retries):
            try:
                return await self.llm.chat(messages, **kwargs)
            except Exception as e:
                logger.error("LLM call failed", error=str(e), attempt=attempt + 1)
                if attempt == self.config.llm.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
        
        raise RuntimeError("Max retries exceeded")
