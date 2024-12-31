from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from models import AIAnalysis, ActionStatus, MigrationAction
from pathlib import Path

console = Console()

def display_project_structure(structure: Dict[str, Any]):
    """Display the project structure in a table"""
    table = Table(title="Project Structure")
    table.add_column("Path", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Size", style="yellow")
    
    for path, info in structure.items():
        if isinstance(info, dict):
            table.add_row(
                path,
                info.get("type", "unknown"),
                f"{info.get('size', 0) / 1024:.1f} KB"
            )
    
    console.print(table)

def display_migration_status(analysis: AIAnalysis):
    """Display migration status in a panel"""
    status_panel = Panel(
        "\n".join([
            f"[bold]Migration Complexity:[/bold] {analysis.migration_complexity}",
            f"[bold]Estimated Time:[/bold] {analysis.estimated_time}",
            f"[bold]Progress:[/bold] {analysis.progress:.1f}%"
        ]),
        title="Migration Status",
        border_style="blue"
    )
    console.print(status_panel)

def display_package_changes(analysis: AIAnalysis):
    """Display package changes in a table"""
    critical_deps = [
        dep for dep in analysis.dependencies.dependencies 
        if dep.nextjs_equivalent or dep.name in analysis.dependencies.incompatible_packages
    ]
    
    if critical_deps:
        console.print("\n[bold]Critical Package Changes:[/bold]")
        table = Table(show_header=True, header_style="bold")
        table.add_column("Current Package", style="red")
        table.add_column("Required Change", style="green")
        
        for dep in critical_deps:
            table.add_row(
                f"{dep.name}@{dep.version}",
                f"Replace with {dep.nextjs_equivalent}" if dep.nextjs_equivalent else "Remove (incompatible)"
            )
        console.print(table)

def display_migration_steps(actions: List[MigrationAction]):
    """Display migration steps in a table"""
    pending_actions = [a for a in actions if a.status == ActionStatus.PENDING]
    if pending_actions:
        console.print("\n[bold]Next Migration Steps:[/bold]")
        table = Table(show_header=True, header_style="bold", show_lines=True)
        table.add_column("Step", style="cyan")
        table.add_column("Action", style="white")
        table.add_column("Type", style="yellow")
        table.add_column("Est. Time", style="green")
        
        for i, action in enumerate(pending_actions, 1):
            table.add_row(
                str(i),
                action.title,
                action.type,
                action.estimated_time
            )
        console.print(table)

def display_available_commands(project_path: str = None):
    """Display available commands with proper paths"""
    console.print("\n[bold green]Available Commands:[/bold green]")
    
    # If we're inside a Vite project, don't show the path
    is_inside_project = project_path and Path(project_path) == Path.cwd()
    path_display = "" if is_inside_project else f" {project_path or './test-vite-project'}"
    
    commands = [
        ("Scan and analyze project:", f"stackshift scan{path_display}"),
        ("Execute migration steps:", f"stackshift scan{path_display} --execute"),
        ("Start dev server with auto-fix:", f"stackshift watch{path_display} --dev-command \"npm run dev\" --auto-fix"),
        ("Validate migration:", f"stackshift validate{path_display}"),
        ("Get interactive assistance:", f"stackshift chat{path_display}"),
        ("Install Next.js packages:", f"stackshift install{path_display}"),
        ("Update dependencies:", f"stackshift update{path_display} --all"),
        ("Fix specific issue:", f"stackshift fix{path_display} --error \"error message\"")
    ]
    
    for desc, cmd in commands:
        console.print(f"• {desc}")
        console.print(f"  [cyan]{cmd}[/cyan]")

def display_validation_results(success: bool, passed_checks: List[str], errors: List[str]):
    """Display validation results"""
    console.print("\n[bold]Validation Results:[/bold]")
    
    status = "[green]✓ Migration validation passed[/green]" if success else "[red]✗ Migration validation failed[/red]"
    console.print(status)
    
    if passed_checks:
        console.print("\n[bold]Passed Checks:[/bold]")
        for check in passed_checks:
            console.print(f"[green]✓[/green] {check}")
    
    if errors:
        console.print("\n[bold]Errors:[/bold]")
        for error in errors:
            console.print(f"[red]✗[/red] {error}")

def display_error(error: str):
    """Display an error message"""
    console.print(f"[red]Error: {error}[/red]") 