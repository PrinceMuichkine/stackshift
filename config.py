"""
Configuration module for stackshift
"""

import os
import json
from pathlib import Path
from typing import Optional
from rich.console import Console

def get_api_key(console: Console) -> str:
    """Get Anthropic API key from environment or config file"""
    # Check environment variable
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return api_key
        
    # Check config file
    config_file = Path.home() / ".stackshift" / "config.json"
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
                if "api_key" in config:
                    return config["api_key"]
        except Exception:
            pass
            
    # Prompt user for API key
    console.print("[yellow]No API key found. Please run 'stackshift setup' to configure.[/yellow]")
    raise ValueError("Missing Anthropic API key")
    
def setup_config(api_key: str) -> None:
    """Set up configuration with API key"""
    config_dir = Path.home() / ".stackshift"
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "config.json"
    config = {"api_key": api_key}
    
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
        
def is_vite_project(path: Path) -> bool:
    """Check if directory is a Vite project"""
    package_json = path / "package.json"
    if not package_json.exists():
        return False
        
    try:
        with open(package_json) as f:
            package_data = json.load(f)
            
        # Check dependencies
        deps = {
            **package_data.get("dependencies", {}),
            **package_data.get("devDependencies", {})
        }
        
        return any(dep.startswith("@vitejs/") for dep in deps)
        
    except Exception:
        return False
        
def get_next_version(path: Path) -> Optional[str]:
    """Get installed Next.js version"""
    package_json = path / "package.json"
    if not package_json.exists():
        return None
        
    try:
        with open(package_json) as f:
            package_data = json.load(f)
            
        deps = {
            **package_data.get("dependencies", {}),
            **package_data.get("devDependencies", {})
        }
        
        if "next" in deps:
            return deps["next"].lstrip("^~")
            
    except Exception:
        pass
        
    return None
    
def get_project_name(path: Path) -> str:
    """Get project name from package.json"""
    package_json = path / "package.json"
    if not package_json.exists():
        return path.name
        
    try:
        with open(package_json) as f:
            package_data = json.load(f)
            return package_data.get("name", path.name)
    except Exception:
        return path.name 