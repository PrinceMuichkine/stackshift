import asyncio
import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from analyzers.ai_analyzer import AIAnalyzer
from models import AIAnalysis

app = typer.Typer()
console = Console()

def display_analysis_results(analysis: AIAnalysis):
    """Display the analysis results in a formatted table."""
    # Display routing analysis
    routing_table = Table(title="Routing Analysis")
    routing_table.add_column("Current Path")
    routing_table.add_column("Next.js Path")
    routing_table.add_column("Component")
    
    for route in analysis.routing.current_structure:
        routing_table.add_row(
            route.path,
            route.nextjs_path,
            route.component_path
        )
    
    console.print(routing_table)
    
    # Display dependency analysis
    dep_table = Table(title="Dependency Analysis")
    dep_table.add_column("Package")
    dep_table.add_column("Action")
    dep_table.add_column("Notes")
    
    for dep in analysis.dependencies.dependencies:
        dep_table.add_row(
            f"{dep.name}@{dep.version}",
            "Remove" if dep.nextjs_equivalent is None else f"Replace with {dep.nextjs_equivalent}",
            dep.migration_notes or ""
        )
    
    console.print(dep_table)
    
    # Display configuration analysis
    config_panel = Panel(
        "\n".join([
            "Configuration Changes:",
            "-------------------",
            *analysis.configuration.migration_notes
        ]),
        title="Configuration Analysis"
    )
    console.print(config_panel)
    
    # Display overall recommendations
    rec_panel = Panel(
        "\n".join([
            f"Migration Complexity: {analysis.migration_complexity}",
            f"Estimated Time: {analysis.estimated_time}",
            "",
            "Recommendations:",
            "---------------",
            *analysis.general_recommendations
        ]),
        title="Overall Recommendations"
    )
    console.print(rec_panel)

@app.command()
def scan(
    project_path: Path = typer.Argument(
        ...,
        help="Path to the Vite project to analyze",
        exists=True,
        file_okay=False,
        dir_okay=True,
        resolve_path=True
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        "-n",
        help="Run in non-interactive mode"
    )
):
    """Scan a Vite project and generate a migration report."""
    try:
        # Initialize analyzer
        analyzer = AIAnalyzer(str(project_path))
        
        # Display project structure
        with console.status("Analyzing project structure..."):
            structure = analyzer.analyze_project_structure()
            
            structure_table = Table(title="Project Structure")
            structure_table.add_column("Path")
            structure_table.add_column("Type")
            structure_table.add_column("Size")
            
            for path, info in structure.items():
                if isinstance(info, dict):
                    structure_table.add_row(
                        path,
                        info.get("type", "unknown"),
                        f"{info.get('size', 0) / 1024:.1f} KB"
                    )
            
            console.print(structure_table)
        
        # Run AI analysis
        with console.status("Running AI analysis..."):
            analysis = asyncio.run(analyzer.analyze_codebase(non_interactive=non_interactive))
        
        # Display results
        display_analysis_results(analysis)
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app() 