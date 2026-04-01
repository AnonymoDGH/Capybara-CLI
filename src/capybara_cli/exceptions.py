"""Custom exceptions for Capybara CLI."""


class CapybaraError(Exception):
    """Base exception for Capybara CLI."""
    pass


class ConfigurationError(CapybaraError):
    """Raised when there's a configuration error."""
    pass


class LLMError(CapybaraError):
    """Raised when there's an error with the LLM provider."""
    pass


class ToolError(CapybaraError):
    """Raised when a tool execution fails."""
    pass


class ToolNotFoundError(ToolError):
    """Raised when a requested tool is not found."""
    pass


class ToolExecutionError(ToolError):
    """Raised when tool execution fails."""
    pass


class SecurityError(CapybaraError):
    """Raised when a security check fails."""
    pass


class MemoryError(CapybaraError):
    """Raised when there's a memory-related error."""
    pass


class AgentError(CapybaraError):
    """Raised when the agent encounters an error."""
    pass


class MaxIterationsError(AgentError):
    """Raised when the agent reaches maximum iterations."""
    pass


class TimeoutError(AgentError):
    """Raised when an operation times out."""
    pass


class ParseError(CapybaraError):
    """Raised when parsing fails."""
    pass


class GitError(CapybaraError):
    """Raised when a Git operation fails."""
    pass
