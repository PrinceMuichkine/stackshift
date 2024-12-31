"""
Validation module for checking Next.js migration status
"""

from pathlib import Path
from typing import List, Dict, Any, NamedTuple, Optional
import json
import re
from enum import Enum

class NextJsVersion(Enum):
    PAGES = "pages"
    APP = "app"

class ValidationResult(NamedTuple):
    success: bool
    passed_checks: List[str]
    errors: List[str]
    warnings: List[str]  # Added warnings for suggestions
    router_type: NextJsVersion

class RouteMapping(NamedTuple):
    vite_route: str
    nextjs_route: str
    params: List[str]
    is_dynamic: bool

class MigrationValidator:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.router_type = self._detect_router_type()
        
    def _detect_router_type(self) -> NextJsVersion:
        """Detect if using Pages Router or App Router"""
        if (self.project_path / "app").exists():
            return NextJsVersion.APP
        return NextJsVersion.PAGES
        
    def validate_migration(self) -> ValidationResult:
        """Run all validation checks"""
        passed_checks = []
        errors = []
        warnings = []
        
        # Check 1: Next.js dependencies
        if self._check_nextjs_dependencies():
            passed_checks.append("✓ Next.js dependencies are properly configured")
        else:
            errors.append("✗ Missing or incorrect Next.js dependencies")
            
        # Check 2: Project structure based on router type
        structure_errors, structure_warnings = self._check_project_structure()
        if not structure_errors:
            passed_checks.append(f"✓ Project structure follows Next.js {self.router_type.value} router conventions")
        else:
            errors.extend(structure_errors)
        warnings.extend(structure_warnings)
            
        # Check 3: Component migrations
        component_errors = self._check_components()
        if not component_errors:
            passed_checks.append("✓ Components are properly migrated")
        else:
            errors.extend(component_errors)
            
        # Check 4: Routing based on router type
        routing_errors, routing_warnings = self._check_routing()
        if not routing_errors:
            passed_checks.append("✓ Routing is properly migrated to Next.js")
        else:
            errors.extend(routing_errors)
        warnings.extend(routing_warnings)
            
        # Check 5: Image components
        image_errors = self._check_images()
        if not image_errors:
            passed_checks.append("✓ Images are properly migrated to Next.js Image")
        else:
            errors.extend(image_errors)
            
        # Check 6: API routes
        api_errors, api_warnings = self._check_api_routes()
        if not api_errors:
            passed_checks.append("✓ API routes are properly migrated")
        else:
            errors.extend(api_errors)
        warnings.extend(api_warnings)
            
        return ValidationResult(
            success=len(errors) == 0,
            passed_checks=passed_checks,
            errors=errors,
            warnings=warnings,
            router_type=self.router_type
        )
        
    def _check_nextjs_dependencies(self) -> bool:
        """Check if Next.js dependencies are properly configured"""
        try:
            with open(self.project_path / "package.json") as f:
                package = json.load(f)
                deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
                
                required_deps = {
                    "next": True,
                    "react": True,
                    "react-dom": True
                }
                
                return all(dep in deps for dep in required_deps)
        except Exception:
            return False
            
    def _check_project_structure(self) -> tuple[List[str], List[str]]:
        """Check if project structure follows Next.js conventions"""
        errors = []
        warnings = []
        
        if self.router_type == NextJsVersion.APP:
            # App Router structure
            required_dirs = ["app", "public", "components"]
            required_files = {
                "app/layout.tsx": "Root layout",
                "app/page.tsx": "Root page",
                "middleware.ts": "Optional middleware"
            }
            
            # Check for proper route grouping
            route_groups = list(self.project_path.glob("app/**/(_auth|_dashboard|_admin)"))
            if not route_groups:
                warnings.append("! Consider using route groups (_auth, _dashboard) for better organization")
                
            # Check for proper loading/error handling
            for route_dir in self.project_path.glob("app/**/"):
                if not any(file.name in ["loading.tsx", "error.tsx"] for file in route_dir.iterdir()):
                    warnings.append(f"! Missing loading.tsx or error.tsx in {route_dir.relative_to(self.project_path)}")
                    
        else:
            # Pages Router structure
            required_dirs = ["pages", "public", "components"]
            required_files = {
                "pages/_app.tsx": "Custom App",
                "pages/_document.tsx": "Custom Document",
                "pages/index.tsx": "Home page"
            }
            
            # Check for proper dynamic routes
            dynamic_routes = list(self.project_path.glob("pages/**/[*.tsx"))
            if not dynamic_routes:
                warnings.append("! No dynamic routes found, make sure they're properly migrated")
                
        # Check required directories
        for dir_name in required_dirs:
            if not (self.project_path / dir_name).exists():
                errors.append(f"✗ Missing required directory: {dir_name}/")
                
        # Check required files
        for file_path, description in required_files.items():
            if not (self.project_path / file_path).exists():
                errors.append(f"✗ Missing {description}: {file_path}")
                
        return errors, warnings
        
    def _analyze_vite_routes(self) -> List[RouteMapping]:
        """Analyze Vite routes and map them to Next.js routes"""
        route_mappings = []
        
        # Common Vite route patterns
        vite_patterns = [
            # Basic routes
            (r'path: "/(.*?)"', r'\1'),
            # Dynamic routes
            (r'path: "/:(.*?)"', r'[\1]'),
            # Optional parameters
            (r'path: "/(.*?)\?"', r'[[...slug]]'),
            # Catch-all routes
            (r'path: "/\*(.*?)"', r'[...slug]'),
            # Nested routes
            (r'path: "/(.*?)/(.*?)"', r'\1/\2')
        ]
        
        # Search for route definitions in all files
        for ext in [".tsx", ".jsx", ".ts", ".js"]:
            for file in self.project_path.rglob(f"*{ext}"):
                with open(file) as f:
                    content = f.read()
                    
                    # Look for router configuration
                    if "createBrowserRouter" in content or "Routes" in content:
                        for pattern, nextjs_format in vite_patterns:
                            matches = re.finditer(pattern, content)
                            for match in matches:
                                vite_route = match.group(1)
                                params = re.findall(r':(\w+)', vite_route)
                                is_dynamic = bool(params)
                                
                                if self.router_type == NextJsVersion.APP:
                                    nextjs_route = f"app/{vite_route}/page.tsx"
                                else:
                                    nextjs_route = f"pages/{vite_route}.tsx"
                                    
                                route_mappings.append(RouteMapping(
                                    vite_route=vite_route,
                                    nextjs_route=nextjs_route,
                                    params=params,
                                    is_dynamic=is_dynamic
                                ))
                                
        return route_mappings
        
    def _check_routing(self) -> tuple[List[str], List[str]]:
        """Check if routing is properly migrated to Next.js"""
        errors = []
        warnings = []
        
        # Analyze Vite routes
        route_mappings = self._analyze_vite_routes()
        
        # Check if all Vite routes have corresponding Next.js routes
        for route in route_mappings:
            target_file = self.project_path / route.nextjs_route
            if not target_file.exists():
                errors.append(f"✗ Missing Next.js route for '{route.vite_route}' at {route.nextjs_route}")
                
            if target_file.exists():
                with open(target_file) as f:
                    content = f.read()
                    
                    # Check for proper parameter handling
                    if route.is_dynamic:
                        if self.router_type == NextJsVersion.APP:
                            for param in route.params:
                                if f"params.{param}" not in content:
                                    errors.append(f"✗ Missing parameter '{param}' handling in {route.nextjs_route}")
                        else:
                            for param in route.params:
                                if "useRouter" not in content or f"router.query.{param}" not in content:
                                    errors.append(f"✗ Missing parameter '{param}' handling in {route.nextjs_route}")
                                    
                    # Check for proper imports
                    if self.router_type == NextJsVersion.APP:
                        if "next/navigation" not in content and ("useRouter" in content or "usePathname" in content):
                            errors.append(f"✗ Missing next/navigation import in {route.nextjs_route}")
                    else:
                        if "next/router" not in content and "useRouter" in content:
                            errors.append(f"✗ Missing next/router import in {route.nextjs_route}")
                            
        # Check for proper navigation methods
        for ext in [".tsx", ".jsx"]:
            for file in self.project_path.rglob(f"*{ext}"):
                with open(file) as f:
                    content = f.read()
                    
                    # Check navigation patterns
                    if self.router_type == NextJsVersion.APP:
                        if "router.push" in content and "useRouter" not in content:
                            errors.append(f"✗ Using router.push without useRouter in {file.relative_to(self.project_path)}")
                        if "window.location" in content:
                            warnings.append(f"! Using window.location instead of Next.js navigation in {file.relative_to(self.project_path)}")
                    else:
                        if "router.push" in content and "useRouter" not in content:
                            errors.append(f"✗ Using router.push without useRouter in {file.relative_to(self.project_path)}")
                            
        return errors, warnings
        
    def _check_api_routes(self) -> tuple[List[str], List[str]]:
        """Check if API routes are properly migrated"""
        errors = []
        warnings = []
        
        # Determine API directory based on router type
        api_dir = self.project_path / ("app/api" if self.router_type == NextJsVersion.APP else "pages/api")
        
        if not api_dir.exists():
            return [], []  # No API routes to check
            
        for file in api_dir.rglob("*.ts"):
            with open(file) as f:
                content = f.read()
                
                if self.router_type == NextJsVersion.APP:
                    # App Router API conventions
                    if not any(handler in content for handler in ["GET", "POST", "PUT", "DELETE"]):
                        errors.append(f"✗ Missing HTTP method handlers in API route: {file.relative_to(self.project_path)}")
                    if "next/server" not in content:
                        errors.append(f"✗ Missing next/server import in API route: {file.relative_to(self.project_path)}")
                    if "export async function" not in content:
                        errors.append(f"✗ API handlers should be async functions in {file.relative_to(self.project_path)}")
                else:
                    # Pages Router API conventions
                    if "export default" not in content:
                        errors.append(f"✗ Missing default export in API route: {file.relative_to(self.project_path)}")
                    if "NextApiRequest" not in content or "NextApiResponse" not in content:
                        errors.append(f"✗ Missing Next.js API types in {file.relative_to(self.project_path)}")
                        
                # Common checks
                if "try" not in content or "catch" not in content:
                    warnings.append(f"! Missing error handling in API route: {file.relative_to(self.project_path)}")
                if "process.env" in content and ".env" not in str(self.project_path.glob("*.env*")):
                    warnings.append(f"! Using environment variables but no .env file found for {file.relative_to(self.project_path)}")
                    
        return errors, warnings 