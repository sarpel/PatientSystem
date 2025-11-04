"""Diagnosis generation CLI commands."""

import asyncio
import json

import typer
from rich.console import Console
from rich.table import Table

from ...clinical.diagnosis_engine import DiagnosisEngine
from ...database.connection import get_session

app = typer.Typer()
console = Console()


@app.command()
def generate(
    tckn: str = typer.Option(..., "--tckn", help="Patient TCKN"),
    complaint: str = typer.Option(..., "--complaint", help="Chief complaint"),
    model: str = typer.Option(None, "--model", help="AI model (claude/gpt-5/gemini/ollama)"),
    output: str = typer.Option("text", "--output", "-o", help="Output format (text/json)"),
):
    """Generate differential diagnosis from symptoms."""
    try:
        with console.status("[bold green]Analyzing symptoms..."):
            with get_session() as session:
                engine = DiagnosisEngine(session)

                result = asyncio.run(
                    engine.generate_differential_diagnosis_ai(
                        tckn=tckn,
                        chief_complaint=complaint,
                        preferred_provider=model,
                    )
                )

        if output == "json":
            console.print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            _display_diagnosis(result)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


def _display_diagnosis(result: dict):
    """Display diagnosis results in formatted table."""
    console.print("\n[bold cyan]🩺 DIFFERENTIAL DIAGNOSIS[/bold cyan]\n")

    # Diagnosis table
    diagnoses = result.get("differential_diagnosis", [])
    if diagnoses:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Diagnosis", style="cyan")
        table.add_column("ICD-10", style="yellow")
        table.add_column("Probability", justify="right", style="green")
        table.add_column("Urgency", style="red")

        for dx in diagnoses:
            table.add_row(
                dx.get("diagnosis", "Unknown"),
                dx.get("icd10", ""),
                f"{dx.get('probability', 0) * 100:.1f}%",
                dx.get("urgency", "moderate"),
            )

        console.print(table)

    # Red flags
    red_flags = result.get("red_flags", [])
    if red_flags:
        console.print("\n[bold red]🚨 RED FLAGS:[/bold red]")
        for flag in red_flags:
            console.print(f"  • {flag}")

    # Recommended tests
    tests = result.get("recommended_tests", [])
    if tests:
        console.print("\n[bold]🔬 Recommended Tests:[/bold]")
        for test in tests:
            console.print(f"  • {test}")
