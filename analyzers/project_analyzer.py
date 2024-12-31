"""
Project analyzer for Next.js migration
"""

from pathlib import Path
from typing import Dict, Any, List
import json
import os

class ProjectAnalyzer:
    """Project analyzer for Next.js migration"""
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze project structure"""
        structure = {
            "items": []
        }
        
        for root, dirs, files in os.walk(self.project_path):
            rel_path = Path(root).relative_to(self.project_path)
            
            # Add directories
            for dir_name in dirs:
                dir_path = rel_path / dir_name
                structure["items"].append({
                    "path": str(dir_path),
                    "type": "directory",
                    "children": []
                })
                
            # Add files
            for file_name in files:
                file_path = rel_path / file_name
                structure["items"].append({
                    "path": str(file_path),
                    "type": "file"
                })
                
        return structure
        
    def analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies"""
        package_json = self.project_path / "package.json"
        if not package_json.exists():
            return {
                "dependencies": [],
                "devDependencies": []
            }
            
        try:
            with open(package_json) as f:
                data = json.load(f)
                
            return {
                "dependencies": [
                    {"name": name, "version": version}
                    for name, version in data.get("dependencies", {}).items()
                ],
                "devDependencies": [
                    {"name": name, "version": version}
                    for name, version in data.get("devDependencies", {}).items()
                ]
            }
        except Exception:
            return {
                "dependencies": [],
                "devDependencies": []
            }
            
    def analyze_routing(self) -> Dict[str, Any]:
        """Analyze routing structure"""
        routes = []
        
        # Check for React Router routes
        for ext in [".tsx", ".jsx", ".ts", ".js"]:
            for file_path in self.project_path.rglob(f"*{ext}"):
                try:
                    content = file_path.read_text()
                    if "Route" in content and "react-router" in content:
                        routes.append({
                            "path": str(file_path.relative_to(self.project_path)),
                            "type": "react-router"
                        })
                except Exception:
                    continue
                    
        return {
            "routes": routes,
            "type": "react-router" if routes else "unknown"
        } 