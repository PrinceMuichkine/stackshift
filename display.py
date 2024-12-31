"""
Display module for stackshift
"""

from typing import List, Dict, Any
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.tree import Tree

console = Console()

def display_project_structure(structure: Dict[str, Any]) -> None:
    """Display project structure in a tree format"""
    tree = Tree("📁 Project Structure")
    
    def add_items(items: List[Dict[str, Any]], parent: Tree) -> None:
        for item in sorted(items, key=lambda x: x["path"]):
            if item["type"] == "directory":
                branch = parent.add(f"📁 {Path(item['path']).name}")
                if "children" in item:
                    add_items(item["children"], branch)
            else:
                parent.add(f"📄 {Path(item['path']).name}")
                
    add_items(structure["items"], tree)
    console.print(tree)
    
def display_migration_status(analysis: Dict[str, Any]) -> None:
    """Display migration status and complexity"""
    panel = Panel(
        f"""[bold]Migration Analysis[/bold]

Complexity: {analysis['complexity']}
Estimated Time: {analysis['estimated_time']}

[bold]Status:[/bold]
✓ {len(analysis['passed_checks'])} checks passed
✗ {len(analysis['errors'])} errors found
⚠ {len(analysis['warnings'])} warnings found""",
        title="Migration Status"
    )
    console.print(panel)
    
def display_package_changes(analysis: Dict[str, Any]) -> None:
    """Display package changes in a table"""
    table = Table(title="Package Changes")
    
    table.add_column("Package", style="cyan")
    table.add_column("Current", style="yellow")
    table.add_column("Required", style="green")
    table.add_column("Status", style="bold")
    
    for pkg in analysis["package_changes"]:
        status = "✓" if pkg["status"] == "ok" else "✗"
        table.add_row(
            pkg["name"],
            pkg["current_version"] or "-",
            pkg["required_version"],
            status
        )
        
    console.print(table)
    
def display_migration_steps(steps: List[Dict[str, Any]]) -> None:
    """Display migration steps in a table"""
    table = Table(title="Migration Steps")
    
    table.add_column("Step", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Status", style="bold")
    
    for i, step in enumerate(steps, 1):
        status = "✓" if step["completed"] else "⋯"
        table.add_row(
            f"{i}. {step['title']}",
            step["description"],
            status
        )
        
    console.print(table)
    
def display_available_commands(project_path: str) -> None:
    """Display available commands"""
    table = Table(title="Available Commands")
    
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="white")
    
    commands = [
        ("stackshift scan", "Analyze project for migration"),
        ("stackshift validate", "Check migration progress"),
        ("stackshift transform all", "Transform all components"),
        ("stackshift chat", "Get interactive assistance")
    ]
    
    for cmd, desc in commands:
        table.add_row(cmd, desc)
        
    console.print(table)
    
def display_validation_results(success: bool, passed: List[str], errors: List[str], warnings: List[str]) -> None:
    """Display validation results"""
    if errors:
        console.print("\n[red]Errors:[/red]")
        for error in errors:
            console.print(f"[red]• {error}[/red]")
            
    if warnings:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in warnings:
            console.print(f"[yellow]• {warning}[/yellow]")
            
    if passed:
        console.print("\n[green]Passed Checks:[/green]")
        for check in passed:
            console.print(f"[green]• {check}[/green]")
            
    if success:
        console.print("\n[bold green]✓ Validation passed[/bold green]")
    else:
        console.print("\n[bold red]✗ Validation failed[/bold red]")
        
def display_file_changes(file_path: str, original: str, modified: str) -> None:
    """Display file changes with syntax highlighting"""
    console.print(f"\n[bold]Changes in {file_path}:[/bold]")
    
    # Show original
    console.print("\n[yellow]Original:[/yellow]")
    syntax = Syntax(original, "typescript", theme="monokai")
    console.print(syntax)
    
    # Show modified
    console.print("\n[green]Modified:[/green]")
    syntax = Syntax(modified, "typescript", theme="monokai")
    console.print(syntax)
    
def display_error(message: str) -> None:
    """Display error message"""
    console.print(f"[bold red]Error: {message}[/bold red]")
    
def display_success(message: str) -> None:
    """Display success message"""
    console.print(f"[bold green]✓ {message}[/bold green]")
    
def display_warning(message: str) -> None:
    """Display warning message"""
    console.print(f"[bold yellow]⚠ {message}[/bold yellow]")
    
def display_info(message: str) -> None:
    """Display info message"""
    console.print(f"[bold blue]ℹ {message}[/bold blue]")
    
def display_scan_results(results: Dict[str, Any]) -> None:
    """Display scan results"""
    # Display project structure
    display_project_structure(results["structure"])
    
    # Display migration status
    display_migration_status(results["analysis"])
    
    # Display package changes
    display_package_changes(results["analysis"])
    
    # Display migration steps
    display_migration_steps(results["analysis"]["steps"])
    
    # Display available commands
    display_available_commands(results["project_path"])
    
def display_transformation_results(results: Dict[str, Any]) -> None:
    """Display transformation results"""
    # Display summary
    panel = Panel(
        f"""[bold]Transformation Results[/bold]

Files Transformed: {len(results['transformed_files'])}
Errors: {len(results['errors'])}
Warnings: {len(results['warnings'])}""",
        title="Summary"
    )
    console.print(panel)
    
    # Display transformed files
    if results['transformed_files']:
        console.print("\n[bold]Transformed Files:[/bold]")
        for file in results['transformed_files']:
            console.print(f"[green]✓ {file}[/green]")
            
    # Display errors
    if results['errors']:
        console.print("\n[red]Errors:[/red]")
        for error in results['errors']:
            console.print(f"[red]• {error}[/red]")
            
    # Display warnings
    if results['warnings']:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in results['warnings']:
            console.print(f"[yellow]• {warning}[/yellow]")
            
    console.print("\n[bold green]✓ Transformation completed[/bold green]") 