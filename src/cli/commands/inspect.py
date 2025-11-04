"""Database inspection CLI commands."""

import typer
from rich.console import Console
from rich.table import Table

from ...database.connection import get_engine, get_session
from ...database.inspector import DatabaseInspector

app = typer.Typer()
console = Console()


@app.command()
def database():
    """Display database schema information."""
    try:
        engine = get_engine()
        inspector = DatabaseInspector(engine)

        tables = inspector.get_all_table_names()

        # Categorize tables
        categories = {
            "Patient": [],
            "Visit": [],
            "Diagnosis": [],
            "Prescription": [],
            "Lab": [],
            "Reference": [],
        }

        for table in tables:
            if "HASTA" in table or "GP_BC" in table:
                categories["Patient"].append(table)
            elif "MUAYENE" in table or "KABUL" in table:
                categories["Visit"].append(table)
            elif "TANI" in table or "ICD" in table:
                categories["Diagnosis"].append(table)
            elif "RECETE" in table or "ILAC" in table:
                categories["Prescription"].append(table)
            elif "TETKIK" in table or "LAB" in table:
                categories["Lab"].append(table)
            elif "LST_" in table:
                categories["Reference"].append(table)

        # Display summary
        console.print(f"\n[bold cyan]Database: {inspector.get_database_name()}[/bold cyan]")
        console.print(f"Total Tables: {len(tables)}\n")

        for category, table_list in categories.items():
            if table_list:
                console.print(f"[bold]{category}:[/bold] {len(table_list)} tables")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def table(name: str = typer.Argument(..., help="Table name")):
    """Show schema for specific table."""
    try:
        engine = get_engine()
        inspector = DatabaseInspector(engine)

        schema = inspector.get_table_schema(name)

        if not schema:
            console.print(f"[red]Table not found: {name}[/red]")
            raise typer.Exit(code=1)

        console.print(f"\n[bold cyan]Table: {name}[/bold cyan]\n")

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Column", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Nullable", style="green")

        for col_name, col_info in schema.items():
            table.add_row(
                col_name,
                str(col_info.get("type", "Unknown")),
                "Yes" if col_info.get("nullable") else "No",
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def stats():
    """Display database statistics."""
    try:
        with get_session() as session:
            from ...models.patient import Patient
            from ...models.visit import Visit

            patient_count = session.query(Patient).count()
            visit_count = session.query(Visit).count()

            console.print("\n[bold cyan]Database Statistics[/bold cyan]\n")
            console.print(f"Total Patients: {patient_count:,}")
            console.print(f"Total Visits: {visit_count:,}")
            console.print(f"Avg Visits per Patient: {visit_count / max(patient_count, 1):.1f}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
