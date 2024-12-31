from __future__ import annotations
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv

# Load environment variables from .env and .env.local files
load_dotenv()
load_dotenv(".env.local")

from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from models import (
    AIAnalysis, RoutingAnalysis, DependencyAnalysis,
    ConfigurationAnalysis, RouteInfo
)

class AIAnalyzer:
    def __init__(self, project_path: str) -> None:
        self.project_path = Path(project_path)
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = Anthropic()  # It will automatically use ANTHROPIC_API_KEY from env
        
    def _get_file_type(self, path: Path) -> str:
        """Determine the type of a file based on its name and content."""
        if path.name == "package.json":
            return "package_json"
        elif path.name.startswith("vite.config."):
            return "vite_config"
        elif path.suffix in [".ts", ".tsx", ".js", ".jsx"]:
            return "source"
        elif path.name.startswith(".env"):
            return "env"
        elif path.name in ["tsconfig.json", "jsconfig.json"]:
            return "config"
        else:
            return "file"

    def analyze_project_structure(self) -> dict:
        """Recursively analyze the structure of a vite project."""
        project_structure = {}

        for path in self.project_path.glob("**/*"):
            try:
                relative_path = path.relative_to(self.project_path)
                
                if path.is_dir():
                    project_structure[str(relative_path)] = self.analyze_project_structure_recursive(path)
                elif path.is_file():
                    project_structure[str(relative_path)] = {
                        "path": str(path),
                        "size": path.stat().st_size,
                        "type": self._get_file_type(path)
                    }
            except Exception as e:
                print(f"Error analyzing path {path}: {e}")
                continue
        
        return project_structure

    def analyze_project_structure_recursive(self, dir_path: Path) -> dict:
        """Helper method to recursively analyze directory structure."""
        structure = {}
        
        for path in dir_path.glob("*"):
            try:
                relative_path = path.relative_to(self.project_path)
                
                if path.is_dir():
                    structure[str(relative_path)] = self.analyze_project_structure_recursive(path)
                elif path.is_file():
                    structure[str(relative_path)] = {
                        "path": str(path),
                        "size": path.stat().st_size,
                        "type": self._get_file_type(path)
                    }
            except Exception as e:
                print(f"Error analyzing path {path}: {e}")
                continue
                
        return structure

    async def analyze_codebase(self, non_interactive: bool = False) -> AIAnalysis:
        """Analyze the codebase using Claude to generate migration insights."""
        try:
            print("Starting codebase analysis...")
            
            # Analyze project structure
            print("Analyzing project structure...")
            project_structure = self.analyze_project_structure()
            print(f"Found {len(project_structure)} top-level items")
            
            # Get relevant files
            print("Identifying relevant files...")
            relevant_files = await self._get_relevant_files()
            if not relevant_files:
                raise ValueError("No relevant files found in the project directory")
            print(f"Found {len(relevant_files)} relevant files")
            
            # Read codebase files
            print("Reading file contents...")
            codebase_contents = await self._read_codebase_files(relevant_files)
            if not codebase_contents:
                raise ValueError("Failed to read any file contents")
            print(f"Successfully read {len(codebase_contents)} files")
            
            # Perform analyses
            print("\nAnalyzing routing structure...")
            routing_analysis = await self._analyze_routing(codebase_contents)
            
            print("Analyzing dependencies...")
            dependency_analysis = await self._analyze_dependencies(codebase_contents)
            
            print("Analyzing configuration...")
            config_analysis = await self._analyze_configuration(codebase_contents)
            
            # Generate overall recommendations
            print("\nGenerating overall recommendations...")
            recommendations_prompt = """
            Based on the following analysis results, provide overall recommendations for the Vite to Next.js migration:

            Routing Analysis:
            - Complexity: {routing_complexity}
            - Routes to migrate: {route_count}
            - Notes: {routing_notes}...

            Dependency Analysis:
            - Incompatible packages: {incompatible_count}
            - Required Next.js packages: {required_count}
            - Notes: {dependency_notes}...

            Configuration Analysis:
            - Environment variables to migrate: {env_count}
            - Notes: {config_notes}...

            Provide:
            1. General migration strategy
            2. Estimated time based on complexity
            3. Potential risks and mitigation steps
            4. Suggested migration order

            Format as a JSON with these fields:
            {{
                "general_recommendations": ["string"],
                "migration_complexity": "low" | "medium" | "high",
                "estimated_time": "string",
                "migration_order": ["string"]
            }}
            """.format(
                routing_complexity=routing_analysis.migration_complexity,
                route_count=len(routing_analysis.current_structure),
                routing_notes=', '.join(routing_analysis.notes[:3]),
                incompatible_count=len(dependency_analysis.incompatible_packages),
                required_count=len(dependency_analysis.required_nextjs_packages),
                dependency_notes=', '.join(dependency_analysis.migration_notes[:3]),
                env_count=len(config_analysis.environment_variables),
                config_notes=', '.join(config_analysis.migration_notes[:3])
            )

            message = await self.client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": recommendations_prompt
                }]
            )

            try:
                response = message.content[0].text
                import json
                recommendations = json.loads(response)
            except Exception as e:
                print(f"Error parsing recommendations: {e}")
                recommendations = {
                    "general_recommendations": [],
                    "migration_complexity": "medium",
                    "estimated_time": "2-3 weeks",
                    "migration_order": []
                }

            return AIAnalysis(
                routing=routing_analysis,
                dependencies=dependency_analysis,
                configuration=config_analysis,
                general_recommendations=recommendations["general_recommendations"] + recommendations["migration_order"],
                migration_complexity=recommendations["migration_complexity"],
                estimated_time=recommendations["estimated_time"]
            )

        except Exception as e:
            error_msg = f"AI analysis failed: {str(e)}"
            print(f"Error: {error_msg}")
            if not non_interactive:
                raise Exception(error_msg)
            return AIAnalysis(
                routing=RoutingAnalysis(
                    current_structure=[],
                    suggested_nextjs_structure=[],
                    migration_complexity="unknown",
                    notes=[error_msg]
                ),
                dependencies=DependencyAnalysis(
                    dependencies=[],
                    incompatible_packages=[],
                    required_nextjs_packages=[],
                    migration_notes=[error_msg]
                ),
                configuration=ConfigurationAnalysis(
                    vite_config={},
                    suggested_next_config={},
                    environment_variables=[],
                    migration_notes=[error_msg]
                ),
                general_recommendations=[error_msg],
                migration_complexity="unknown",
                estimated_time="unknown"
            )
    
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
        routing_prompt = """
        You are analyzing a Vite/React project for migration to Next.js. Focus on the routing structure and provide a detailed analysis.
        
        For each file, analyze:
        1. React Router route definitions and map them to Next.js App Router equivalents
        2. Dynamic route parameters and how they should be transformed
        3. Layout components and nested routing patterns
        4. Client-side navigation components that need to be converted to Next.js Link
        5. Data fetching patterns that should be moved to server components
        6. Authentication/authorization patterns that should be migrated to middleware
        
        Provide your analysis in the following JSON structure:
        {
            "routes": [
                {
                    "current_path": string,
                    "component_path": string,
                    "layout": string | null,
                    "params": string[],
                    "nextjs_path": string,
                    "is_dynamic": boolean,
                    "data_fetching": {
                        "pattern": string,
                        "recommendation": string
                    }
                }
            ],
            "affected_files": string[],
            "complexity": "low" | "medium" | "high",
            "breaking_changes": string[],
            "migration_notes": string[]
        }
        """
        
        # Filter for routing-related files
        routing_files = {
            path: content for path, content in codebase_contents.items()
            if any(pattern in path.lower() for pattern in [
                'router', 'route', 'nav', 'layout', 'app.', 'index.', 'pages/'
            ])
        }
        
        # Prepare the context for Claude
        context = "\n\nHere are the relevant files from the project:\n\n"
        for path, content in routing_files.items():
            context += f"File: {path}\n```\n{content}\n```\n\n"
        
        # Get analysis from Claude
        message = await self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": routing_prompt + context + "\nAnalyze these files and provide the JSON response as specified above."
            }]
        )
        
        try:
            # Extract JSON from Claude's response
            response = message.content[0].text
            import json
            analysis = json.loads(response)
            
            # Convert the analysis to our RoutingAnalysis model
            return RoutingAnalysis(
                current_structure=[
                    RouteInfo(
                        path=route["current_path"],
                        component_path=route["component_path"],
                        layout=route.get("layout"),
                        params=route.get("params", []),
                        nextjs_path=route["nextjs_path"]
                    ) for route in analysis["routes"]
                ],
                suggested_nextjs_structure=[
                    RouteInfo(
                        path=route["nextjs_path"],
                        component_path=f"app/{route['nextjs_path']}/page.tsx",
                        layout=route.get("layout"),
                        params=route.get("params", [])
                    ) for route in analysis["routes"]
                ],
                migration_complexity=analysis["complexity"],
                notes=analysis["migration_notes"] + [
                    f"Breaking Change: {change}" for change in analysis["breaking_changes"]
                ]
            )
            
        except Exception as e:
            print(f"Error parsing Claude's response: {e}")
            # Fallback to a basic analysis
            return RoutingAnalysis(
                current_structure=[],
                suggested_nextjs_structure=[],
                migration_complexity="medium",
                notes=[f"Error during analysis: {str(e)}"]
            )
    
    async def _analyze_dependencies(self, codebase_contents: Dict[str, str]) -> DependencyAnalysis:
        """Analyze dependencies using Claude."""
        dependency_prompt = """
        You are analyzing a Vite/React project's dependencies for migration to Next.js. Focus on package.json and related configuration files.
        
        Analyze:
        1. Dependencies that need to be:
           - Removed (Vite-specific)
           - Replaced (with Next.js alternatives)
           - Added (required for Next.js)
           - Updated (version compatibility)
        
        2. Build tools and configurations:
           - Development dependencies
           - Build scripts
           - Test frameworks
           - Environment variables
        
        Provide your analysis in the following JSON structure:
        {
            "dependencies": [
                {
                    "name": string,
                    "version": string,
                    "type": "production" | "development" | "peer",
                    "action": "remove" | "replace" | "update" | "keep",
                    "nextjs_equivalent": string | null,
                    "notes": string
                }
            ],
            "incompatible_packages": string[],
            "required_packages": [
                {
                    "name": string,
                    "version": string,
                    "reason": string
                }
            ],
            "migration_notes": string[]
        }
        """
        
        # Filter for dependency-related files
        dep_files = {
            path: content for path, content in codebase_contents.items()
            if any(name in path.lower() for name in [
                'package.json', 'package-lock.json', 'yarn.lock',
                'pnpm-lock.yaml', '.npmrc', '.yarnrc'
            ])
        }
        
        # Prepare context for Claude
        context = "\n\nHere are the relevant dependency files:\n\n"
        for path, content in dep_files.items():
            context += f"File: {path}\n```\n{content}\n```\n\n"
        
        # Get analysis from Claude
        message = await self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": dependency_prompt + context + "\nAnalyze these files and provide the JSON response as specified above."
            }]
        )
        
        try:
            # Extract JSON from Claude's response
            response = message.content[0].text
            import json
            analysis = json.loads(response)
            
            from models import Dependency, DependencyType
            
            # Convert the analysis to our DependencyAnalysis model
            return DependencyAnalysis(
                dependencies=[
                    Dependency(
                        name=dep["name"],
                        version=dep["version"],
                        type=DependencyType(dep["type"]),
                        nextjs_equivalent=dep.get("nextjs_equivalent"),
                        migration_notes=dep.get("notes")
                    ) for dep in analysis["dependencies"]
                ],
                incompatible_packages=analysis["incompatible_packages"],
                required_nextjs_packages=[
                    f"{pkg['name']}@{pkg['version']}"
                    for pkg in analysis["required_packages"]
                ],
                migration_notes=analysis["migration_notes"] + [
                    f"Required Package ({pkg['name']}): {pkg['reason']}"
                    for pkg in analysis["required_packages"]
                ]
            )
            
        except Exception as e:
            print(f"Error parsing Claude's response: {e}")
            # Fallback to a basic analysis
            return DependencyAnalysis(
                dependencies=[],
                incompatible_packages=[],
                required_nextjs_packages=[],
                migration_notes=[f"Error during analysis: {str(e)}"]
            )
    
    async def _analyze_configuration(self, codebase_contents: Dict[str, str]) -> ConfigurationAnalysis:
        """Analyze configuration using Claude."""
        config_prompt = """
        You are analyzing a Vite/React project's configuration for migration to Next.js. Focus on build, development, and environment configurations.
        
        Analyze:
        1. Build Configuration:
           - Output settings and file structure
           - Asset handling and optimization
           - Environment variables
           - Path aliases and module resolution
        
        2. Development Configuration:
           - Dev server settings
           - Proxy configurations
           - Middleware and plugins
           - HMR and live reload settings
        
        3. Performance Optimizations:
           - Code splitting and chunking
           - Caching strategies
           - Compression settings
           - Image and font optimization
        
        Provide your analysis in the following JSON structure:
        {
            "vite_config": {
                "build": object,
                "dev": object,
                "resolve": object,
                "plugins": string[],
                "env": string[]
            },
            "next_config": {
                "build": object,
                "env": object,
                "images": object,
                "rewrites": array,
                "redirects": array,
                "headers": array
            },
            "environment_variables": [
                {
                    "name": string,
                    "current_usage": string,
                    "next_usage": string
                }
            ],
            "migration_notes": string[]
        }
        """
        
        # Filter for configuration files
        config_files = {
            path: content for path, content in codebase_contents.items()
            if any(pattern in path.lower() for pattern in [
                'vite.config', 'next.config',
                '.env', 'tsconfig.json', 'jsconfig.json',
                'postcss.config', 'tailwind.config'
            ])
        }
        
        # Prepare context for Claude
        context = "\n\nHere are the relevant configuration files:\n\n"
        for path, content in config_files.items():
            context += f"File: {path}\n```\n{content}\n```\n\n"
        
        # Get analysis from Claude
        message = await self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4000,
            temperature=0,
            messages=[{
                "role": "user",
                "content": config_prompt + context + "\nAnalyze these files and provide the JSON response as specified above."
            }]
        )
        
        try:
            # Extract JSON from Claude's response
            response = message.content[0].text
            import json
            analysis = json.loads(response)
            
            # Convert the analysis to our ConfigurationAnalysis model
            return ConfigurationAnalysis(
                vite_config=analysis["vite_config"],
                suggested_next_config=analysis["next_config"],
                environment_variables=[
                    f"{env['name']}: {env['current_usage']} -> {env['next_usage']}"
                    for env in analysis["environment_variables"]
                ],
                migration_notes=analysis["migration_notes"]
            )
            
        except Exception as e:
            print(f"Error parsing Claude's response: {e}")
            # Fallback to a basic analysis
            return ConfigurationAnalysis(
                vite_config={},
                suggested_next_config={},
                environment_variables=[],
                migration_notes=[f"Error during analysis: {str(e)}"]
            ) 