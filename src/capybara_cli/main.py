"""Main entry point for Capybara CLI."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.align import Align

try:
    from .agent import CapybaraAgent
    from .config import Config, load_config
    from .exceptions import CapybaraError
    from .logger import setup_logging
except ImportError:
    from agent import CapybaraAgent
    from config import Config, load_config
    from exceptions import CapybaraError
    from logger import setup_logging

console = Console()


def get_capybara_ascii() -> str:
    return """
    ██████╗  █████╗ ██████╗ ██╗   ██╗██████╗  █████╗ ██████╗  █████╗ 
    ██╔════╝ ██╔══██╗██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗
    ██║     ███████║██████╔╝ ╚████╔╝ ██████╔╝███████║██████╔╝███████║
    ██║     ██╔══██║██╔═══╝   ╚██╔╝  ██╔══██╗██╔══██║██╔══██╗██╔══██║
    ╚██████╗██║  ██║██║        ██║   ██████╔╝██║  ██║██████╔╝██║  ██║
     ╚═════╝╚═╝  ╚═╝╚═╝        ╚═╝   ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝
    """


def get_capybara_small() -> str:
    return """
 ██████             
███ ███████████████ 
████████████████████
    ████████████████
   █████████████████
   ██  ██     █████ 
     ████   ██████  
    """


def print_banner():
    """Print the Capybara CLI banner."""
    ascii_art = get_capybara_small()
    
    banner_text = f"""{ascii_art}
    
    🦫 CAPYBARA CLI v0.1.0
    
    Expert coding agent with superior performance
    on programming tasks, academic reasoning, 
    and cybersecurity evaluations.
    """
    
    console.print(Panel(
        Align.center(banner_text),
        border_style="green",
        padding=(1, 2),
        title="[bold green]Welcome[/bold green]",
        subtitle="[dim]Type 'help' for commands or 'exit' to quit[/dim]"
    ))


def print_interactive_header():
    """Print header for interactive mode like Claude Code."""
    ascii_art = get_capybara_small()
    
    header = f"""╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                                                              │
│{ascii_art:^126}│
│                                                                                                                              │
│   🦫 Capybara CLI v0.1.0                                          Expert coding agent with superior performance             │
│                                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯"""
    console.print(header, style="green")


def print_status_bar(config: Config):
    """Print status bar with current model and settings."""
    model = config.llm.model if config.llm.model else "default"
    provider = config.llm.provider
    
    status = f"╭─ {provider.upper()} · {model} ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮"
    console.print(status, style="dim")


@click.group(invoke_without_command=True)
@click.option("--config", "-c", type=click.Path(), help="Path to config file")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--model", "-m", help="LLM model to use")
@click.pass_context
def cli(ctx: click.Context, config: Optional[str], verbose: bool, model: Optional[str]):
    """🦫 Capybara CLI - Expert coding agent."""
    ctx.ensure_object(dict)
    
    setup_logging(verbose=verbose)
    
    config_path = Path(config) if config else None
    cfg = load_config(config_path)
    
    if model:
        cfg.llm.model = model
    
    ctx.obj["config"] = cfg
    ctx.obj["verbose"] = verbose
    
    if ctx.invoked_subcommand is None:
        asyncio.run(interactive_mode(cfg))


async def interactive_mode(config: Config):
    """Run Capybara in interactive chat mode."""
    print_interactive_header()
    print_status_bar(config)
    console.print()
    
    agent = CapybaraAgent(config)
    
    try:
        await agent.initialize()
        
        while True:
            try:
                user_input = console.input("[bold green]You[/bold green] > ")
                
                if user_input.lower() in ("exit", "quit", "q"):
                    console.print("\n[yellow]Goodbye! 👋[/yellow]")
                    break
                
                if user_input.lower() == "help":
                    print_help()
                    continue
                
                if not user_input.strip():
                    continue
                
                with console.status("[bold green]Capybara is thinking...", spinner="dots"):
                    response = await agent.chat(user_input)
                
                console.print(f"[bold cyan]Capybara[/bold cyan] > {response}\n")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
            except EOFError:
                break
                
    except CapybaraError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    finally:
        await agent.shutdown()


def print_help():
    """Print help information."""
    help_text = """
    [bold]Available Commands:[/bold]
    
    [green]General:[/green]
      help              Show this help message
      exit, quit, q     Exit the session
    
    [green]Prefix Commands:[/green]
      /code <desc>      Generate code from description
      /fix <file>       Fix bugs in a file
      /test <file>      Generate tests for a file
      /explain <target> Explain code or concept
      /refactor <file>  Refactor code
      /review <file>    Review code
      /doc <file>       Generate documentation
      /security <file>  Security analysis
      /git <command>    Git operations
    
    [dim]Or just type naturally and Capybara will understand![/dim]
    """
    console.print(help_text)


@cli.command()
@click.argument("prompt")
@click.option("--file", "-f", multiple=True, help="Files to include as context")
@click.pass_context
def ask(ctx: click.Context, prompt: str, file: tuple[str, ...]):
    """Ask a question about code or concepts."""
    asyncio.run(_ask_command(ctx.obj["config"], prompt, list(file)))


async def _ask_command(config: Config, prompt: str, files: list[str]):
    """Execute ask command."""
    agent = CapybaraAgent(config)
    await agent.initialize()
    
    try:
        response = await agent.ask(prompt, context_files=files)
        console.print(response)
    finally:
        await agent.shutdown()


@cli.command()
@click.argument("description")
@click.option("--output", "-o", help="Output file path")
@click.option("--language", "-l", default="python", help="Target programming language")
@click.pass_context
def code(ctx: click.Context, description: str, output: Optional[str], language: str):
    """Generate code from description."""
    asyncio.run(_code_command(ctx.obj["config"], description, output, language))


async def _code_command(config: Config, description: str, output: Optional[str], language: str):
    """Execute code generation command."""
    agent = CapybaraAgent(config)
    await agent.initialize()
    
    try:
        result = await agent.generate_code(description, language=language, output_path=output)
        if output:
            console.print(f"[green]Code written to:[/green] {output}")
        else:
            console.print(result)
    finally:
        await agent.shutdown()


@cli.command()
@click.argument("file_path")
@click.option("--dry-run", is_flag=True, help="Show changes without applying")
@click.pass_context
def fix(ctx: click.Context, file_path: str, dry_run: bool):
    """Find and fix bugs in a file."""
    asyncio.run(_fix_command(ctx.obj["config"], file_path, dry_run))


async def _fix_command(config: Config, file_path: str, dry_run: bool):
    """Execute fix command."""
    agent = CapybaraAgent(config)
    await agent.initialize()
    
    try:
        result = await agent.fix_bugs(file_path, dry_run=dry_run)
        console.print(result)
    finally:
        await agent.shutdown()


@cli.command()
@click.argument("file_path")
@click.option("--framework", "-f", default="pytest", help="Testing framework")
@click.option("--output", "-o", help="Output test file path")
@click.pass_context
def test(ctx: click.Context, file_path: str, framework: str, output: Optional[str]):
    """Generate tests for a file."""
    asyncio.run(_test_command(ctx.obj["config"], file_path, framework, output))


async def _test_command(config: Config, file_path: str, framework: str, output: Optional[str]):
    """Execute test generation command."""
    agent = CapybaraAgent(config)
    await agent.initialize()
    
    try:
        result = await agent.generate_tests(file_path, framework=framework, output_path=output)
        console.print(result)
    finally:
        await agent.shutdown()


@cli.command()
@click.argument("target")
@click.pass_context
def explain(ctx: click.Context, target: str):
    """Explain code or architecture."""
    asyncio.run(_explain_command(ctx.obj["config"], target))


async def _explain_command(config: Config, target: str):
    """Execute explain command."""
    agent = CapybaraAgent(config)
    await agent.initialize()
    
    try:
        response = await agent.explain(target)
        console.print(response)
    finally:
        await agent.shutdown()


@cli.command()
@click.argument("file_path")
@click.option("--strategy", "-s", default="improve", 
              type=click.Choice(["improve", "simplify", "optimize", "modernize"]),
              help="Refactoring strategy")
@click.pass_context
def refactor(ctx: click.Context, file_path: str, strategy: str):
    """Refactor code with best practices."""
    asyncio.run(_refactor_command(ctx.obj["config"], file_path, strategy))


async def _refactor_command(config: Config, file_path: str, strategy: str):
    """Execute refactor command."""
    agent = CapybaraAgent(config)
    await agent.initialize()
    
    try:
        result = await agent.refactor(file_path, strategy=strategy)
        console.print(result)
    finally:
        await agent.shutdown()


@cli.command()
@click.argument("target", required=False)
@click.option("--all", "scan_all", is_flag=True, help="Scan entire codebase")
@click.pass_context
def security(ctx: click.Context, target: Optional[str], scan_all: bool):
    """Security audit and analysis."""
    asyncio.run(_security_command(ctx.obj["config"], target, scan_all))


async def _security_command(config: Config, target: Optional[str], scan_all: bool):
    """Execute security command."""
    agent = CapybaraAgent(config)
    await agent.initialize()
    
    try:
        result = await agent.security_audit(target=target, scan_all=scan_all)
        console.print(result)
    finally:
        await agent.shutdown()


@cli.command()
@click.pass_context
def version(ctx: click.Context):
    """Show version information."""
    try:
        from . import __version__
    except ImportError:
        from __init__ import __version__
    console.print(f"[bold green]Capybara CLI[/bold green] version [cyan]{__version__}[/cyan]")


def main():
    """Entry point for the CLI."""
    try:
        cli()
    except CapybaraError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        if "--verbose" in sys.argv or "-v" in sys.argv:
            console.print_exception()
        sys.exit(1)


if __name__ == "__main__":
    main()
