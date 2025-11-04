"""Drug interaction checking CLI commands."""

import asyncio

import typer
from rich.console import Console
from rich.table import Table

from ...clinical.drug_interaction import DrugInteractionChecker
from ...database.connection import get_session

app = typer.Typer()
console = Console()


@app.command()
def check(
    tckn: str = typer.Option(..., "--tckn", help="Patient TCKN"),
    drug: str = typer.Option(..., "--add", help="Drug name to check"),
    severity: str = typer.Option(
        "all", "--severity", help="Filter by severity (all/major/critical)"
    ),
):
    """Check drug interactions for patient."""
    try:
        with console.status("[bold green]Checking drug interactions..."):
            with get_session() as session:
                checker = DrugInteractionChecker(session)
                result = asyncio.run(checker.check_interactions(tckn=tckn, proposed_drug=drug))

        # Display results
        interactions = result.get("interactions", [])

        # Filter by severity
        if severity != "all":
            interactions = [i for i in interactions if i.get("severity") == severity]

        if not interactions:
            console.print(f"\n[green]✓ No {severity} interactions found for {drug}[/green]")
            return

        console.print(f"\n[bold red]⚠️  DRUG INTERACTIONS DETECTED[/bold red]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Type", style="cyan")
        table.add_column("Severity", style="red")
        table.add_column("Drugs", style="yellow")
        table.add_column("Effect", style="white")

        for interaction in interactions:
            severity_color = {
                "critical": "red",
                "major": "red",
                "moderate": "yellow",
                "minor": "green",
            }.get(interaction.get("severity", "moderate"), "white")

            table.add_row(
                interaction.get("type", ""),
                f"[{severity_color}]{interaction.get('severity', '')}[/{severity_color}]",
                f"{interaction.get('drug1', '')} + {interaction.get('drug2', '')}",
                interaction.get("effect", ""),
            )

        console.print(table)

        # Safe to prescribe
        safe = result.get("safe_to_prescribe", True)
        if not safe:
            console.print(f"\n[bold red]❌ NOT SAFE TO PRESCRIBE[/bold red]")

        # Alternatives
        alternatives = result.get("alternative_drugs", [])
        if alternatives:
            console.print(f"\n[bold green]Alternative Drugs:[/bold green]")
            for alt in alternatives:
                console.print(f"  • {alt}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
