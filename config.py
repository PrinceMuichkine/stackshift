"""
Configuration for stackshift
"""

import os
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console

# Constants
ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"
DEFAULT_MODEL = "claude-3-sonnet-20240229"

# Project paths
CONFIG_DIR = Path.home() / ".stackshift"
CONFIG_FILE = CONFIG_DIR / "config.json"

# Console styling
console = Console()

def get_api_key(console: Console) -> str:
    """Get Anthropic API key from environment or config"""
    key = os.environ.get(ANTHROPIC_API_KEY)
    if not key:
        if CONFIG_FILE.exists():
            import json
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                key = config.get(ANTHROPIC_API_KEY)
    
    if not key:
        console.print(
            f"[bold red]No {ANTHROPIC_API_KEY} found. Please run:[/bold red]\n"
            f"stackshift setup"
        )
        sys.exit(1)
    return key

def setup_config(api_key: str) -> None:
    """Setup configuration file with API key"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    config = {
        ANTHROPIC_API_KEY: api_key
    }
    
    with open(CONFIG_FILE, 'w') as f:
        import json
        json.dump(config, f, indent=2)
        
    console.print("[bold green]Configuration saved successfully![/bold green]")

def is_vite_project(path: Path) -> bool:
    """Check if directory is a Vite project"""
    if not (path / "package.json").exists():
        return False
        
    with open(path / "package.json") as f:
        import json
        pkg = json.load(f)
        return "vite" in pkg.get("devDependencies", {}) 