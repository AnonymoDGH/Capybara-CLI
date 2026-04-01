"""
Capybara CLI - An expert coding agent with superior performance.

A powerful AI coding assistant that outperforms previous state-of-the-art models
on programming tasks, academic reasoning, and cybersecurity evaluations.
"""

__version__ = "0.1.0"
__author__ = "Capybara Team"
__license__ = "MIT"

from .agent import CapybaraAgent
from .config import Config, load_config
from .memory import MemoryManager
from .tools import ToolRegistry

__all__ = [
    "CapybaraAgent",
    "Config",
    "load_config",
    "MemoryManager",
    "ToolRegistry",
]
