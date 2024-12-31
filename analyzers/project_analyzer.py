from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Optional, Any

from analyzers.ai_analyzer import AIAnalyzer
from types import ProjectAnalysis, AIAnalysis

class ProjectAnalyzer:
    def __init__(self, project_path: str) -> None:
        self.project_path = Path(project_path)
        self.ai_analyzer = AIAnalyzer(project_path)
    
    async def analyze_project(self, skip_ai: bool = False, non_interactive: bool = False) -> ProjectAnalysis:
        """Perform comprehensive project analysis."""
        if not await self._is_valid_project():
            raise ValueError("Invalid project directory. Make sure package.json exists.")
        
        print("Starting basic project analysis...")
        project_info = await self._get_project_info()
        
        ai_analysis: Optional[AIAnalysis] = None
        if not skip_ai:
            try:
                print("Starting AI-assisted analysis...")
                ai_analysis = await self.ai_analyzer.analyze_codebase(non_interactive)
                print("AI-assisted analysis complete")
            except Exception as e:
                print(f"Error during AI analysis: {e}")
                print("Continuing with basic analysis results")
        
        return ProjectAnalysis(
            project_name=project_info["name"],
            project_path=str(self.project_path),
            framework_version=project_info["framework_version"],
            ai_analysis=ai_analysis,
            errors=[],
            warnings=[]
        )
    
    async def _is_valid_project(self) -> bool:
        """Check if the project directory is valid."""
        package_json = self.project_path / "package.json"
        return package_json.exists()
    
    async def _get_project_info(self) -> Dict[str, Any]:
        """Extract basic project information."""
        try:
            package_json = self.project_path / "package.json"
            data = json.loads(package_json.read_text())
            
            # Extract Vite version
            dev_deps = data.get("devDependencies", {})
            deps = data.get("dependencies", {})
            vite_version = dev_deps.get("vite") or deps.get("vite") or "unknown"
            
            return {
                "name": data.get("name", "unknown"),
                "framework_version": vite_version,
                "dependencies": {**deps, **dev_deps}
            }
        except Exception as e:
            raise Exception(f"Error reading project info: {str(e)}")
    
    async def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze project dependencies."""
        package_json = self.project_path / "package.json"
        if not package_json.exists():
            return {}
        
        data = json.loads(package_json.read_text())
        return {
            "dependencies": data.get("dependencies", {}),
            "devDependencies": data.get("devDependencies", {}),
            "peerDependencies": data.get("peerDependencies", {})
        }
    
    async def _analyze_configuration(self) -> Dict[str, Any]:
        """Analyze project configuration files."""
        config_files = [
            "vite.config.js",
            "vite.config.ts",
            "tsconfig.json",
            ".env",
            ".env.local"
        ]
        
        configs: Dict[str, str] = {}
        for config_file in config_files:
            path = self.project_path / config_file
            if path.exists():
                try:
                    configs[config_file] = path.read_text()
                except Exception as e:
                    print(f"Error reading {config_file}: {e}")
        
        return configs 