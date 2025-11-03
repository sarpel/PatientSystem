"""Patient analysis CLI commands."""

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import json
from pathlib import Path

from ...database.connection import get_session
from ...clinical.patient_summarizer import PatientSummarizer

app = typer.Typer()
console = Console()


@app.command()
def patient(
    tckn: str = typer.Option(..., "--tckn", help="Patient TCKN"),
    output: str = typer.Option("text", "--output", help="Output format (text/json)"),
    save: Path = typer.Option(None, "--save", help="Save output to file"),
):
    """Analyze patient and generate comprehensive summary."""
    try:
        with get_session() as session:
            summarizer = PatientSummarizer(session)
            summary = summarizer.get_patient_summary(tckn)

            if not summary:
                rprint(f"[red]❌ Patient not found: {tckn}[/red]")
                raise typer.Exit(1)

            if output == "json":
                output_text = json.dumps(summary, indent=2, ensure_ascii=False)
                if save:
                    save.write_text(output_text, encoding="utf-8")
                    rprint(f"[green]✓ Saved to {save}[/green]")
                else:
                    print(output_text)
            else:
                # Text format with Rich tables
                rprint("\n[bold cyan]📋 HASTA ÖZETİ[/bold cyan]")
                rprint("─" * 60)

                demo = summary.get("demographics", {})
                rprint(f"[bold]{demo.get('name', 'N/A')}[/bold]")
                rprint(f"TCKN: {tckn}")
                rprint(f"Yaş: {demo.get('age', 'N/A')} | Cinsiyet: {demo.get('gender', 'N/A')}")

                # Recent visits
                visits = summary.get("recent_visits", [])
                if visits:
                    rprint("\n[bold yellow]📅 Son Vizitler:[/bold yellow]")
                    for visit in visits[:5]:
                        rprint(f"  • {visit.get('date')}: {visit.get('complaint', 'N/A')}")

                # Active diagnoses
                diagnoses = summary.get("active_diagnoses", [])
                if diagnoses:
                    rprint("\n[bold red]🩺 Aktif Tanılar:[/bold red]")
                    for dx in diagnoses:
                        rprint(f"  • {dx.get('diagnosis')} ({dx.get('icd10', 'N/A')})")

                # Medications
                meds = summary.get("current_medications", [])
                if meds:
                    rprint("\n[bold green]💊 Aktif İlaçlar:[/bold green]")
                    for med in meds:
                        rprint(f"  • {med}")

                # Allergies
                allergies = summary.get("allergies", [])
                if allergies:
                    rprint("\n[bold magenta]⚠️  Alerjiler:[/bold magenta]")
                    for allergy in allergies:
                        rprint(f"  • {allergy}")

                if save:
                    save.write_text(str(summary), encoding="utf-8")
                    rprint(f"\n[green]✓ Saved to {save}[/green]")

    except Exception as e:
        rprint(f"[red]❌ Error: {str(e)}[/red]")
        raise typer.Exit(1)
