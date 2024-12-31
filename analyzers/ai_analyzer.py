from __future__ import annotations
import os
from pathlib import Path
from typing import List, Dict, Optional, Any

import anthropic
from types import (
    AIAnalysis, RoutingAnalysis, DependencyAnalysis,
    ConfigurationAnalysis, RouteInfo
)

class AIAnalyzer:
    def __init__(self, project_path: str) -> None:
        self.project_path = Path(project_path)
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
    async def analyze_codebase(self, non_interactive: bool = False) -> AIAnalysis:
        """Analyze the codebase using Claude to generate migration insights."""
        try:
            relevant_files = await self._get_relevant_files()
            codebase_contents = await self._read_codebase_files(relevant_files)
            
            routing_analysis = await self._analyze_routing(codebase_contents)
            dependency_analysis = await self._analyze_dependencies(codebase_contents)
            config_analysis = await self._analyze_configuration(codebase_contents)
            
            return AIAnalysis(
                routing=routing_analysis,
                dependencies=dependency_analysis,
                configuration=config_analysis,
                general_recommendations=[],  # Will be populated by Claude
                migration_complexity="medium",  # Will be determined by Claude
                estimated_time="2-3 days"  # Will be estimated by Claude
            )
        except Exception as e:
            raise Exception(f"AI analysis failed: {str(e)}")
    
    async def _get_relevant_files(self) -> List[Path]:
        """Get list of relevant files for analysis."""
        patterns = [
            "**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx",
            "**/vite.config.*", "**/package.json",
            "**/.env*", "**/tsconfig.json"
        ]
        files: List[Path] = []
        for pattern in patterns:
            files.extend(self.project_path.glob(pattern))
        return files
    
    async def _read_codebase_files(self, files: List[Path]) -> Dict[str, str]:
        """Read contents of relevant files."""
        contents: Dict[str, str] = {}
        for file in files:
            try:
                contents[str(file.relative_to(self.project_path))] = file.read_text()
            except Exception as e:
                print(f"Error reading {file}: {e}")
        return contents
    
    async def _analyze_routing(self, codebase_contents: Dict[str, str]) -> RoutingAnalysis:
        """Analyze routing structure using Claude."""
        # TODO: Implement Claude-based routing analysis
        return RoutingAnalysis(
            current_structure=[],
            suggested_nextjs_structure=[],
            migration_complexity="medium",
            notes=[]
        )
    
    async def _analyze_dependencies(self, codebase_contents: Dict[str, str]) -> DependencyAnalysis:
        """Analyze dependencies using Claude."""
        # TODO: Implement Claude-based dependency analysis
        return DependencyAnalysis(
            dependencies=[],
            incompatible_packages=[],
            required_nextjs_packages=[],
            migration_notes=[]
        )
    
    async def _analyze_configuration(self, codebase_contents: Dict[str, str]) -> ConfigurationAnalysis:
        """Analyze configuration using Claude."""
        # TODO: Implement Claude-based configuration analysis
        return ConfigurationAnalysis(
            vite_config={},
            suggested_next_config={},
            environment_variables=[],
            migration_notes=[]
        ) 