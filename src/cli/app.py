"""Clinical AI Assistant CLI application using Typer."""

import sys
from pathlib import Path

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.commands import analyze, config, diagnose, drug_check, inspect

# Create Typer app
app = typer.Typer(
    name="clinical-ai",
    help="Clinical AI Assistant - AI-powered clinical decision support",
    add_completion=False,
)

# Add command modules
app.add_typer(analyze.app, name="analyze", help="Analyze patient data")
app.add_typer(diagnose.app, name="diagnose", help="Generate diagnosis")
app.add_typer(inspect.app, name="inspect", help="Inspect database and system")
app.add_typer(config.app, name="config", help="Manage configuration")
app.add_typer(drug_check.app, name="drug-check", help="Check drug interactions")

console = Console()


@app.command()
def version():
    """Display application version and information."""
    from src.config.settings import settings

    table = Table(title="Clinical AI Assistant", show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Version", "0.1.0")
    table.add_row("Python", sys.version.split()[0])
    table.add_row("Database", f"{settings.db_server}/{settings.db_name}")
    table.add_row("AI Providers", "Ollama, Claude, GPT, Gemini")
    table.add_row("Environment", settings.environment)

    console.print(table)


@app.callback()
def main(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
):
    """
    Clinical AI Assistant CLI.

    Multi-interface AI-powered clinical decision support system for family medicine.
    """
    if verbose:
        import logging

        logging.basicConfig(level=logging.DEBUG)


if __name__ == "__main__":
    app()
