"""Configuration management CLI commands."""

import typer
import asyncio
from rich.console import Console
from rich.table import Table

from ...config.settings import settings
from ...ai import create_ai_router

app = typer.Typer()
console = Console()


@app.command()
def show():
    """Display current configuration."""
    table = Table(title="Configuration", show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    # Database settings
    table.add_row("DB Server", settings.db_server)
    table.add_row("DB Name", settings.db_name)
    table.add_row("DB Driver", settings.db_driver)

    # AI settings
    table.add_row("Ollama Model", settings.ollama_model)
    table.add_row("Claude Model", settings.claude_model)
    table.add_row("OpenAI Model", settings.openai_model)
    table.add_row("Gemini Model", settings.gemini_model)
    table.add_row("AI Strategy", settings.ai_routing_strategy)
    table.add_row("AI Fallback", str(settings.ai_enable_fallback))

    # API settings
    table.add_row("API Host", settings.api_host)
    table.add_row("API Port", str(settings.api_port))

    # Environment
    table.add_row("Environment", settings.environment)
    table.add_row("Log Level", settings.log_level)

    console.print(table)


@app.command()
def test_ai():
    """Test AI provider connections."""
    console.print("\n[bold cyan]Testing AI Providers...[/bold cyan]\n")

    try:
        router = create_ai_router()
        results = asyncio.run(router.health_check_all())

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Provider", style="cyan")
        table.add_column("Status", style="green")

        for provider, status in results.items():
            status_icon = "✓" if status else "✗"
            status_color = "green" if status else "red"
            table.add_row(provider, f"[{status_color}]{status_icon}[/{status_color}]")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def set_model(model: str = typer.Argument(..., help="Model name (claude/gpt-4o/gemini)")):
    """Set preferred AI model (requires env var update)."""
    console.print(f"[yellow]To set model preference, update CLAUDE_MODEL, OPENAI_MODEL, or GEMINI_MODEL in .env file[/yellow]")
    console.print(f"Example: OPENAI_MODEL={model}")
