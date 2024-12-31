import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress

from analyzers import ProjectAnalyzer
from __init__ import __version__

app = typer.Typer(
    name="stackshift",
    help="CLI tool to migrate web applications from Vite to Next.js",
    add_completion=False,
)
console = Console()

def version_callback(value: bool):
    if value:
        console.print(f"StackShift CLI Version: {__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show the application version and exit.",
        callback=version_callback,
        is_eager=True,
    )
):
    """
    StackShift CLI - Migrate your Vite apps to Next.js with ease
    """
    pass

@app.command()
def analyze(
    project_path: Path = typer.Argument(
        ...,
        help="Path to the Vite project to analyze",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
    skip_ai: bool = typer.Option(
        False,
        "--skip-ai",
        "-s",
        help="Skip AI-assisted analysis",
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        "-n",
        help="Run in non-interactive mode",
    ),
):
    """
    Analyze a Vite project for migration to Next.js
    """
    async def run_analysis():
        try:
            analyzer = ProjectAnalyzer(str(project_path))
            with Progress() as progress:
                task = progress.add_task("Analyzing project...", total=100)
                
                # Update progress as analysis proceeds
                progress.update(task, advance=30)
                analysis = await analyzer.analyze_project(skip_ai, non_interactive)
                progress.update(task, advance=70)
                
                # Print analysis results
                console.print("\n[bold green]Analysis Complete![/bold green]")
                console.print(f"\nProject: {analysis.project_name}")
                console.print(f"Framework Version: {analysis.framework_version}")
                
                if analysis.ai_analysis:
                    console.print("\n[bold]AI Analysis Results:[/bold]")
                    console.print(f"Migration Complexity: {analysis.ai_analysis.migration_complexity}")
                    console.print(f"Estimated Time: {analysis.ai_analysis.estimated_time}")
                    
                    if analysis.ai_analysis.general_recommendations:
                        console.print("\n[bold]Recommendations:[/bold]")
                        for rec in analysis.ai_analysis.general_recommendations:
                            console.print(f"• {rec}")
                
                if analysis.warnings:
                    console.print("\n[yellow]Warnings:[/yellow]")
                    for warning in analysis.warnings:
                        console.print(f"• {warning}")
                
                if analysis.errors:
                    console.print("\n[red]Errors:[/red]")
                    for error in analysis.errors:
                        console.print(f"• {error}")
                
        except Exception as e:
            console.print(f"\n[red]Error:[/red] {str(e)}")
            raise typer.Exit(1)
    
    asyncio.run(run_analysis())

@app.command()
def migrate(
    project_path: Path = typer.Argument(
        ...,
        help="Path to the Vite project to migrate",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True,
    ),
):
    """
    Migrate a Vite project to Next.js (Not implemented yet)
    """
    console.print("[yellow]Migration command not implemented yet[/yellow]")
    raise typer.Exit(1)

if __name__ == "__main__":
    app() 