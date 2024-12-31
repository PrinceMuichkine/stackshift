from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import re

from pydantic import BaseModel

class RouteTransform(BaseModel):
    """Represents a route transformation from Vite to Next.js"""
    source_path: str
    target_path: str
    route_params: List[str] = []
    layout_file: Optional[str] = None
    additional_files: List[Tuple[str, str]] = []  # (source, target) pairs

class RoutesTransformer:
    """Handles the transformation of routes from Vite to Next.js"""
    
    def __init__(self, project_path: str) -> None:
        self.project_path = Path(project_path)
        self.src_path = self.project_path / "src"
    
    def analyze_routes(self) -> List[Dict[str, Any]]:
        """Analyze the current routing structure"""
        routes: List[Dict[str, Any]] = []
        
        # Look for common routing patterns
        patterns = [
            self.src_path / "routes",
            self.src_path / "pages",
            self.src_path / "views",
        ]
        
        for pattern in patterns:
            if pattern.exists() and pattern.is_dir():
                routes.extend(self._analyze_directory(pattern))
        
        # Also check for router configuration files
        router_files = [
            self.src_path / "router.ts",
            self.src_path / "router.js",
            self.src_path / "routes.ts",
            self.src_path / "routes.js",
        ]
        
        for router_file in router_files:
            if router_file.exists():
                routes.extend(self._analyze_router_file(router_file))
        
        return routes
    
    def _analyze_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """Analyze a directory for route components"""
        routes: List[Dict[str, Any]] = []
        for item in directory.rglob("*"):
            if item.is_file() and item.suffix in [".tsx", ".jsx", ".js", ".ts"]:
                route_info = self._analyze_component_file(item)
                if route_info:
                    routes.append(route_info)
        return routes
    
    def _analyze_component_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a component file for route information"""
        try:
            content = file_path.read_text()
            
            # Look for route path in comments or exports
            route_path = None
            
            # Check for route path in comments
            path_comment = re.search(r"@route\s+([^\n]+)", content)
            if path_comment:
                route_path = path_comment.group(1).strip()
            
            # Check for route definition in code
            route_def = re.search(r"path:\s*['\"]([^'\"]+)['\"]", content)
            if route_def:
                route_path = route_def.group(1)
            
            if not route_path:
                # Infer from file path
                rel_path = file_path.relative_to(self.src_path)
                route_path = self._infer_route_path(rel_path)
            
            # Extract route parameters
            params = re.findall(r":(\w+)", route_path) if route_path else []
            
            return {
                "file": str(file_path.relative_to(self.project_path)),
                "route": route_path,
                "params": params,
                "has_layout": bool(re.search(r"layout", file_path.stem, re.I))
            }
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def _analyze_router_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze a router configuration file"""
        try:
            content = file_path.read_text()
            routes: List[Dict[str, Any]] = []
            
            # Look for route definitions
            route_defs = re.finditer(
                r"{\s*path:\s*['\"]([^'\"]+)['\"]\s*,\s*component:\s*([^,}]+)",
                content
            )
            
            for match in route_defs:
                route_path = match.group(1)
                component = match.group(2).strip()
                
                # Try to find the component file
                component_file = self._find_component_file(component)
                
                routes.append({
                    "file": str(component_file) if component_file else None,
                    "route": route_path,
                    "params": re.findall(r":(\w+)", route_path),
                    "has_layout": False
                })
            
            return routes
            
        except Exception as e:
            print(f"Error analyzing router file {file_path}: {e}")
            return []
    
    def _find_component_file(self, component_name: str) -> Optional[Path]:
        """Try to find a component file based on its name"""
        # Clean up the component name
        component_name = re.sub(r"['\"\s()]", "", component_name)
        
        # Common patterns for component imports
        patterns = [
            f"**/{component_name}.tsx",
            f"**/{component_name}.jsx",
            f"**/{component_name}.js",
            f"**/{component_name}.ts",
        ]
        
        for pattern in patterns:
            matches = list(self.src_path.glob(pattern))
            if matches:
                return matches[0].relative_to(self.project_path)
        
        return None
    
    def _infer_route_path(self, file_path: Path) -> str:
        """Infer a route path from a file path"""
        # Remove extension and index
        path_parts = list(file_path.parts)
        
        # Remove the first part if it's 'pages', 'routes', or 'views'
        if path_parts[0] in ['pages', 'routes', 'views']:
            path_parts = path_parts[1:]
        
        # Handle the file name
        path_parts[-1] = Path(path_parts[-1]).stem
        if path_parts[-1].lower() == "index":
            path_parts.pop()
        
        # Convert to URL path
        route = "/" + "/".join(path_parts) if path_parts else "/"
        
        # Handle dynamic segments
        route = re.sub(r"\[(\w+)\]", r":\1", route)
        
        return route
    
    def generate_transforms(self) -> List[RouteTransform]:
        """Generate transformation plans for routes"""
        routes = self.analyze_routes()
        transforms: List[RouteTransform] = []
        
        for route in routes:
            if not route["file"]:
                continue
                
            source = self.project_path / route["file"]
            
            # Convert route path to Next.js format
            nextjs_path = self._convert_to_nextjs_path(route["route"])
            
            # Determine the target path in the Next.js app directory
            target_path = self._get_nextjs_target_path(nextjs_path)
            
            transform = RouteTransform(
                source_path=str(source),
                target_path=str(target_path),
                route_params=route["params"]
            )
            
            # Add layout file if needed
            if route["has_layout"]:
                layout_path = target_path.parent / "layout.tsx"
                transform.layout_file = str(layout_path)
            
            transforms.append(transform)
        
        return transforms
    
    def _convert_to_nextjs_path(self, route: str) -> str:
        """Convert a route path to Next.js format"""
        # Replace : params with [] syntax
        path = re.sub(r":(\w+)", r"[\1]", route)
        
        # Ensure leading slash
        if not path.startswith("/"):
            path = "/" + path
            
        return path
    
    def _get_nextjs_target_path(self, route: str) -> Path:
        """Get the target path for a Next.js page"""
        # Remove leading slash
        route = route.lstrip("/")
        
        # Convert to file path
        parts = route.split("/")
        
        # Handle index routes
        if not parts[-1]:
            parts[-1] = "page.tsx"
        else:
            parts.append("page.tsx")
        
        return self.project_path / "app" / "/".join(parts) 