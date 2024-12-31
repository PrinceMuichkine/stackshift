"""
Command-line interface for stackshift
"""

import os
import sys
from typing import List, Optional
import click
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from analyzers.validation import NextJsVersion, MigrationValidator, ValidationResult
from analyzers.fixer import MigrationFixer
from config import get_api_key, setup_config, is_vite_project
from display import display_scan_results, display_validation_results, display_transformation_results

console = Console()

def get_project_path() -> Path:
    """Get the project path based on current directory"""
    cwd = Path.cwd()
    
    # Check if we're inside a Vite project
    if is_vite_project(cwd):
        return cwd
        
    # Look for Vite project in subdirectories
    for path in cwd.iterdir():
        if path.is_dir() and is_vite_project(path):
            return path
            
    # No Vite project found
    console.print("[red]Error: No Vite project found in current directory[/red]")
    sys.exit(1)
    
def create_completer(commands: List[str]) -> WordCompleter:
    """Create command completer"""
    return WordCompleter(commands, ignore_case=True)
    
@click.group()
def app():
    """stackshift - Migrate Vite projects to Next.js"""
    pass
    
@app.command()
@click.argument("project_path", required=False)
@click.option("--router", type=click.Choice(["app", "pages"]), default="app", help="Next.js router type")
def scan(project_path: Optional[str], router: str):
    """Scan a Vite project for migration"""
    try:
        # Get project path
        path = Path(project_path) if project_path else get_project_path()
        
        # Validate project
        validator = MigrationValidator(str(path))
        result = validator.validate(NextJsVersion.APP if router == "app" else NextJsVersion.PAGES)
        
        # Display results
        if result.errors:
            console.print("\n[red]Migration Issues:[/red]")
            for error in result.errors:
                console.print(f"[red]• {error}[/red]")
                
        if result.warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in result.warnings:
                console.print(f"[yellow]• {warning}[/yellow]")
                
        if result.passed_checks:
            console.print("\n[green]Passed Checks:[/green]")
            for check in result.passed_checks:
                console.print(f"[green]• {check}[/green]")
                
        # Show overall status
        if result.success:
            console.print("\n[green]✓ Project is ready for migration[/green]")
        else:
            console.print("\n[red]✗ Project requires fixes before migration[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
        
@app.command()
@click.argument("project_path", required=False)
@click.option("--router", type=click.Choice(["app", "pages"]), default="app", help="Next.js router type")
@click.option("--fix", is_flag=True, help="Automatically fix issues")
def validate(project_path: Optional[str], router: str, fix: bool):
    """Validate Next.js migration"""
    try:
        # Get project path
        path = Path(project_path) if project_path else get_project_path()
        
        # Get API key
        api_key = get_api_key(console)
        
        # Validate project
        validator = MigrationValidator(str(path))
        result = validator.validate(NextJsVersion.APP if router == "app" else NextJsVersion.PAGES)
        
        # Display results
        if result.errors:
            console.print("\n[red]Validation Errors:[/red]")
            for error in result.errors:
                console.print(f"[red]• {error}[/red]")
                
            if fix:
                # Create missing files
                fixer = MigrationFixer(str(path), api_key)
                created_files = fixer.create_missing_files(result)
                
                if created_files:
                    console.print("\n[green]Created files:[/green]")
                    for file in created_files:
                        console.print(f"[green]• {file}[/green]")
                        
                # Fix issues in existing files
                fixed_files = fixer.fix_issues(result)
                
                if fixed_files:
                    console.print("\n[green]Fixed files:[/green]")
                    for file in fixed_files:
                        console.print(f"[green]• {file}[/green]")
                        
                if not created_files and not fixed_files:
                    console.print("\n[yellow]No files were fixed[/yellow]")
                    
        if result.warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in result.warnings:
                console.print(f"[yellow]• {warning}[/yellow]")
                
        if result.passed_checks:
            console.print("\n[green]Passed Checks:[/green]")
            for check in result.passed_checks:
                console.print(f"[green]• {check}[/green]")
                
        # Show overall status
        if result.success:
            console.print("\n[green]✓ Validation passed[/green]")
        else:
            console.print("\n[red]✗ Validation failed[/red]")
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
        
@app.command()
@click.argument("project_path", required=False)
async def transform(project_path: Optional[str]):
    """Transform all components"""
    try:
        # Get project path
        path = Path(project_path) if project_path else get_project_path()
        
        # Get API key
        api_key = get_api_key(console)
        
        # Create fixer
        fixer = MigrationFixer(str(path), api_key)
        
        # Transform components
        with console.status("[bold green]Transforming components..."):
            fixed_files = await fixer.fix_issues(ValidationResult(NextJsVersion.APP))
            
        if fixed_files:
            console.print("\n[green]Transformed files:[/green]")
            for file in fixed_files:
                console.print(f"[green]• {file}[/green]")
        else:
            console.print("\n[yellow]No files were transformed[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
        
@app.command()
def setup():
    """Configure stackshift"""
    try:
        # Get API key
        api_key = click.prompt("Enter your Anthropic API key", type=str)
        
        # Save configuration
        setup_config(api_key)
        
        console.print("[green]Configuration saved successfully[/green]")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
        
@app.command()
@click.argument("project_path", required=False)
def chat(project_path: Optional[str]):
    """Interactive chat for migration assistance"""
    try:
        # Get project path
        path = Path(project_path) if project_path else get_project_path()
        
        # Get API key
        api_key = get_api_key(console)
        
        # Create session
        history = FileHistory(os.path.expanduser("~/.stackshift_history"))
        session = PromptSession(history=history)
        
        # Create completer
        commands = ["help", "scan", "validate", "transform", "exit"]
        completer = create_completer(commands)
        
        console.print("[bold]Migration Assistant[/bold]")
        console.print("Type 'help' for available commands or 'exit' to quit")
        
        while True:
            try:
                # Get user input
                text = session.prompt(
                    "\nstackshift> ",
                    completer=completer
                )
                
                if text.lower() == "exit":
                    break
                elif text.lower() == "help":
                    show_help()
                else:
                    # Process command
                    process_command(text, path, api_key)
                    
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
                
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
        
def show_help():
    """Show help information"""
    table = Table(title="Available Commands")
    
    table.add_column("Command", style="cyan")
    table.add_column("Description", style="green")
    
    table.add_row("scan", "Scan project for migration")
    table.add_row("validate", "Validate migration progress")
    table.add_row("transform", "Transform all components")
    table.add_row("help", "Show this help message")
    table.add_row("exit", "Exit the assistant")
    
    console.print(table)
    
async def process_command(command: str, project_path: Path, api_key: str):
    """Process chat command"""
    parts = command.split()
    cmd = parts[0].lower()
    
    if cmd == "scan":
        # Run scan
        validator = MigrationValidator(str(project_path))
        result = validator.validate(NextJsVersion.APP)
        display_scan_results(result)
        
    elif cmd == "validate":
        # Run validation
        validator = MigrationValidator(str(project_path))
        result = validator.validate(NextJsVersion.APP)
        display_validation_results(result)
        
    elif cmd == "transform":
        # Transform components
        fixer = MigrationFixer(str(project_path), api_key)
        fixed_files = await fixer.fix_issues(ValidationResult(NextJsVersion.APP))
        display_transformation_results(fixed_files)
        
    else:
        console.print(f"[red]Unknown command: {cmd}[/red]")
        
if __name__ == "__main__":
    app() 