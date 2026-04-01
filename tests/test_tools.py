import pytest
from pathlib import Path
from capybara_cli.tools import ToolRegistry, BashTool, FileReadTool


@pytest.fixture
def tool_registry():
    return ToolRegistry()


def test_tool_registry_creation(tool_registry):
    tools = tool_registry.list_tools()
    assert "bash" in tools
    assert "file_read" in tools
    assert "file_edit" in tools


def test_tool_get(tool_registry):
    tool = tool_registry.get("bash")
    assert tool is not None
    assert tool.name == "bash"


def test_tool_not_found(tool_registry):
    tool = tool_registry.get("nonexistent")
    assert tool is None


@pytest.mark.asyncio
async def test_bash_tool_echo():
    tool = BashTool()
    result = await tool.execute(command="echo hello")
    assert result.success
    assert "hello" in result.output


@pytest.mark.asyncio
async def test_bash_tool_blocked():
    tool = BashTool()
    result = await tool.execute(command="rm -rf /")
    assert not result.success
    assert "blocked" in result.error.lower()


@pytest.mark.asyncio
async def test_file_read_tool(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World")
    
    tool = FileReadTool()
    result = await tool.execute(path=str(test_file))
    
    assert result.success
    assert "Hello World" in result.output
