import os
import sys
import click
from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console

from config import console, get_api_key, setup_config, is_vite_project
from analyzers.project_analyzer import ProjectAnalyzer
from analyzers.ai_analyzer import AIAnalyzer
from display import (
    display_project_structure,
    display_migration_status,
    display_package_changes,
    display_migration_steps,
    display_available_commands,
    display_validation_results,
    display_error
)

def get_project_path(path: str = None) -> str:
    """Get absolute project path, checking if inside or outside project"""
    if not path:
        # Check if current directory is a Vite project
        current = Path.cwd()
        if is_vite_project(current):
            return str(current)
        return None
    
    project_path = Path(path).resolve()
    if not project_path.exists():
        raise click.BadParameter(f"Project path {path} does not exist")
    if not is_vite_project(project_path):
        raise click.BadParameter(f"Directory {path} is not a Vite project")
    return str(project_path)

@click.group()
def app():
    """stackshift - Vite to Next.js migration tool"""
    pass

@app.command()
def setup():
    """Configure stackshift with your Anthropic API key"""
    api_key = click.prompt("Enter your Anthropic API key", type=str)
    setup_config(api_key)

@app.command()
@click.argument('project', required=False)
@click.option('--execute', is_flag=True, help='Execute migration steps')
def scan(project, execute):
    """Scan and analyze a Vite project for Next.js migration"""
    try:
        project_path = get_project_path(project)
        if not project_path:
            display_error("No Vite project found. Please specify a project path.")
            return
            
        api_key = get_api_key(console)
        analyzer = AIAnalyzer(project_path, api_key)
        
        # Display project structure
        structure = analyzer.analyze_project_structure()
        display_project_structure(structure)
        
        # Run analysis
        analysis = analyzer.analyze_codebase()
        
        # Display results
        display_migration_status(analysis)
        display_package_changes(analysis)
        display_migration_steps(analysis.actions)
        display_available_commands(project_path)
        
        if execute:
            analyzer.execute_all_actions()
            
    except Exception as e:
        display_error(str(e))

@app.command()
@click.argument('project', required=False)
@click.option('--all', is_flag=True, help='Run all transformations')
@click.option('--client', is_flag=True, help='Add "use client" to components')
@click.option('--router', is_flag=True, help='Migrate from React Router to Next.js')
@click.option('--styles', is_flag=True, help='Migrate CSS/styles to Next.js')
@click.option('--api', is_flag=True, help='Migrate API routes to Next.js')
@click.option('--images', is_flag=True, help='Migrate images to Next.js Image component')
def transform(project, all, client, router, styles, api, images):
    """Transform specific aspects of the codebase"""
    try:
        project_path = get_project_path(project)
        if not project_path:
            display_error("No Vite project found. Please specify a project path.")
            return
            
        api_key = get_api_key(console)
        analyzer = AIAnalyzer(project_path, api_key)
        
        # If --all is specified, run all transformations
        if all:
            client = router = styles = api = images = True
        
        transformed_files = []
        
        if client:
            files = analyzer.transform_to_client_components()
            transformed_files.extend(files)
            console.print(f"✓ Added 'use client' to {len(files)} components")
            
        if router:
            files = analyzer.migrate_router_to_nextjs()
            transformed_files.extend(files)
            console.print(f"✓ Migrated {len(files)} files from React Router to Next.js")
            
        if styles:
            files = analyzer.migrate_styles_to_nextjs()
            transformed_files.extend(files)
            console.print(f"✓ Migrated {len(files)} style files to Next.js")
            
        if api:
            files = analyzer.migrate_api_to_nextjs()
            transformed_files.extend(files)
            console.print(f"✓ Migrated {len(files)} API routes to Next.js")
            
        if images:
            files = analyzer.migrate_images_to_nextjs()
            transformed_files.extend(files)
            console.print(f"✓ Migrated {len(files)} images to Next.js Image component")
            
        if transformed_files:
            console.print(f"\nTotal files transformed: {len(set(transformed_files))}")
            
    except Exception as e:
        display_error(str(e))

@app.command()
@click.argument('project', required=False)
def validate(project):
    """Validate migration progress"""
    try:
        project_path = get_project_path(project)
        if not project_path:
            display_error("No Vite project found. Please specify a project path.")
            return
            
        api_key = get_api_key(console)
        analyzer = AIAnalyzer(project_path, api_key)
        results = analyzer.validate_migration()
        
        display_validation_results(
            results.success,
            results.passed_checks,
            results.errors
        )
        
    except Exception as e:
        display_error(str(e))

if __name__ == '__main__':
    app() 