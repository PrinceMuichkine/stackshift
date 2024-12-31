"""
Validation module for Next.js migration
"""

from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional
import re
import ast
import json

class NextJsVersion(Enum):
    """Next.js router version"""
    APP = "app"
    PAGES = "pages"

class ValidationResult:
    """Result of migration validation"""
    def __init__(self, router_type: NextJsVersion):
        self.router_type = router_type
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed_checks: List[str] = []
        self.success: bool = True
        
class MigrationValidator:
    """Validator for Next.js migration"""
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        
    def validate(self, router_type: NextJsVersion) -> ValidationResult:
        """Validate the migration"""
        result = ValidationResult(router_type)
        
        # Check project structure
        self._validate_project_structure(result)
        
        # Check routing
        self._validate_routing(result)
        
        # Check components
        self._validate_components(result)
        
        # Check dependencies
        self._validate_dependencies(result)
        
        # Check configuration
        self._validate_configuration(result)
        
        # Update success status
        result.success = len(result.errors) == 0
        
        return result
        
    def _validate_project_structure(self, result: ValidationResult) -> None:
        """Validate project structure"""
        # Check required directories
        required_dirs = ["app"] if result.router_type == NextJsVersion.APP else ["pages"]
        for dir_name in required_dirs:
            dir_path = self.project_path / dir_name
            if not dir_path.exists():
                result.errors.append(f"Missing required directory: {dir_name}")
                
        # Check required files
        required_files = self._get_required_files(result.router_type)
        for file_info in required_files:
            file_path = self.project_path / file_info["path"]
            if not file_path.exists():
                result.errors.append(f"Missing required file: {file_info['path']}")
                
        # Check for Vite remnants
        vite_files = ["vite.config.ts", "vite.config.js"]
        for file_name in vite_files:
            if (self.project_path / file_name).exists():
                result.warnings.append(f"Found Vite configuration file: {file_name}")
                
    def _validate_routing(self, result: ValidationResult) -> None:
        """Validate routing implementation"""
        router_dir = self.project_path / ("app" if result.router_type == NextJsVersion.APP else "pages")
        if not router_dir.exists():
            return
            
        # Check route files
        for route_file in router_dir.rglob("*.tsx"):
            relative_path = route_file.relative_to(self.project_path)
            
            # Read file content
            try:
                content = route_file.read_text()
            except Exception:
                result.errors.append(f"Could not read route file: {relative_path}")
                continue
                
            # Validate route implementation
            if result.router_type == NextJsVersion.APP:
                self._validate_app_route(relative_path, content, result)
            else:
                self._validate_pages_route(relative_path, content, result)
                
    def _validate_app_route(self, path: Path, content: str, result: ValidationResult) -> None:
        """Validate App Router route"""
        # Check for proper exports
        if not re.search(r"export\s+default\s+function", content):
            result.errors.append(f"Missing default export in route: {path}")
            
        # Check for proper metadata
        if "page.tsx" in str(path) and not re.search(r"export\s+const\s+metadata", content):
            result.warnings.append(f"Missing metadata in page: {path}")
            
        # Check for proper error handling
        if "error.tsx" in str(path) and not "'use client'" in content:
            result.errors.append(f"Error boundary must be client component: {path}")
            
        # Check for proper loading states
        if "loading.tsx" in str(path) and not re.search(r"export\s+default\s+function\s+Loading", content):
            result.errors.append(f"Invalid loading component: {path}")
            
    def _validate_pages_route(self, path: Path, content: str, result: ValidationResult) -> None:
        """Validate Pages Router route"""
        # Check for proper exports
        if not re.search(r"export\s+default", content):
            result.errors.append(f"Missing default export in route: {path}")
            
        # Check for getServerSideProps/getStaticProps
        if re.search(r"getInitialProps", content):
            result.warnings.append(f"Found legacy getInitialProps in: {path}")
            
        # Check for proper error handling
        if "_error.tsx" in str(path) and not re.search(r"Error\s*extends\s*React\.Component", content):
            result.errors.append(f"Invalid error page implementation: {path}")
            
    def _validate_components(self, result: ValidationResult) -> None:
        """Validate component implementations"""
        component_dirs = ["components", "src/components"]
        for dir_name in component_dirs:
            component_dir = self.project_path / dir_name
            if not component_dir.exists():
                continue
                
            # Check each component
            for component_file in component_dir.rglob("*.tsx"):
                relative_path = component_file.relative_to(self.project_path)
                
                try:
                    content = component_file.read_text()
                except Exception:
                    result.errors.append(f"Could not read component: {relative_path}")
                    continue
                    
                # Validate component implementation
                self._validate_component(relative_path, content, result)
                
    def _validate_component(self, path: Path, content: str, result: ValidationResult) -> None:
        """Validate a single component"""
        # Check for client-side features
        uses_client_features = any(feature in content for feature in [
            "useState",
            "useEffect",
            "useRouter",
            "onClick",
            "onChange"
        ])
        
        # Check for 'use client' directive
        has_use_client = "'use client'" in content or '"use client"' in content
        
        if uses_client_features and not has_use_client:
            result.errors.append(f"Missing 'use client' directive in client component: {path}")
            
        # Check for proper exports
        if not re.search(r"export\s+(?:default|const|function)", content):
            result.errors.append(f"Missing component export: {path}")
            
        # Check for proper types
        if not re.search(r":\s*(?:React\.)?(?:FC|FunctionComponent|ComponentType)", content):
            result.warnings.append(f"Missing type definition in component: {path}")
            
    def _validate_dependencies(self, result: ValidationResult) -> None:
        """Validate project dependencies"""
        package_json = self.project_path / "package.json"
        if not package_json.exists():
            result.errors.append("Missing package.json")
            return
            
        try:
            with open(package_json) as f:
                package_data = json.load(f)
        except Exception:
            result.errors.append("Invalid package.json")
            return
            
        # Check required dependencies
        required_deps = {
            "next": "^14.0.0",
            "react": "^18.0.0",
            "react-dom": "^18.0.0"
        }
        
        deps = {**package_data.get("dependencies", {}), **package_data.get("devDependencies", {})}
        
        for dep, version in required_deps.items():
            if dep not in deps:
                result.errors.append(f"Missing required dependency: {dep}")
                
        # Check for conflicting dependencies
        conflicts = ["react-router", "react-router-dom", "@vitejs/plugin-react"]
        for conflict in conflicts:
            if conflict in deps:
                result.errors.append(f"Found conflicting dependency: {conflict}")
                
    def _validate_configuration(self, result: ValidationResult) -> None:
        """Validate project configuration"""
        # Check Next.js config
        next_config = self.project_path / "next.config.js"
        if not next_config.exists():
            result.errors.append("Missing next.config.js")
        else:
            try:
                content = next_config.read_text()
                if not re.search(r"module\.exports\s*=", content):
                    result.errors.append("Invalid next.config.js format")
            except Exception:
                result.errors.append("Could not read next.config.js")
                
        # Check TypeScript config
        tsconfig = self.project_path / "tsconfig.json"
        if not tsconfig.exists():
            result.errors.append("Missing tsconfig.json")
        else:
            try:
                with open(tsconfig) as f:
                    ts_config = json.load(f)
                    
                # Check compiler options
                compiler_options = ts_config.get("compilerOptions", {})
                if not compiler_options.get("jsx"):
                    result.warnings.append("Missing JSX configuration in tsconfig.json")
                    
                if not compiler_options.get("baseUrl"):
                    result.warnings.append("Missing baseUrl in tsconfig.json")
                    
            except Exception:
                result.errors.append("Invalid tsconfig.json")
                
    def _get_required_files(self, router_type: NextJsVersion) -> List[Dict[str, str]]:
        """Get list of required files based on router type"""
        common_files = [
            {
                "path": "next.config.js",
                "type": "config",
                "description": "Next.js configuration file"
            },
            {
                "path": "tsconfig.json",
                "type": "config",
                "description": "TypeScript configuration file"
            },
            {
                "path": "package.json",
                "type": "config",
                "description": "Package configuration file"
            }
        ]
        
        if router_type == NextJsVersion.APP:
            return common_files + [
                {
                    "path": "app/layout.tsx",
                    "type": "layout",
                    "description": "Root layout component"
                },
                {
                    "path": "app/page.tsx",
                    "type": "page",
                    "description": "Home page component"
                }
            ]
        else:
            return common_files + [
                {
                    "path": "pages/_app.tsx",
                    "type": "layout",
                    "description": "Custom App component"
                },
                {
                    "path": "pages/index.tsx",
                    "type": "page",
                    "description": "Home page component"
                }
            ] 