from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

from pydantic import BaseModel

class PackageJsonTransform(BaseModel):
    """Represents a transformation to be applied to package.json"""
    dependencies_to_add: Dict[str, str] = {}
    dependencies_to_remove: List[str] = []
    dev_dependencies_to_add: Dict[str, str] = {}
    dev_dependencies_to_remove: List[str] = []
    scripts_to_add: Dict[str, str] = {}
    scripts_to_remove: List[str] = []

class PackageJsonTransformer:
    """Handles the transformation of package.json for Next.js migration"""
    
    NEXTJS_CORE_DEPS: Dict[str, str] = {
        "next": "^14.0.0",
        "react": "^18.2.0",
        "react-dom": "^18.2.0"
    }
    
    NEXTJS_DEV_DEPS: Dict[str, str] = {
        "@types/node": "^20.0.0",
        "@types/react": "^18.2.0",
        "@types/react-dom": "^18.2.0",
        "typescript": "^5.0.0",
        "eslint": "^8.0.0",
        "eslint-config-next": "^14.0.0"
    }
    
    VITE_DEPS_TO_REMOVE: List[str] = [
        "vite",
        "@vitejs/plugin-react",
        "@vitejs/plugin-react-swc"
    ]
    
    NEXTJS_SCRIPTS: Dict[str, str] = {
        "dev": "next dev",
        "build": "next build",
        "start": "next start",
        "lint": "next lint"
    }
    
    def __init__(self, project_path: str) -> None:
        self.project_path = Path(project_path)
        self.package_json_path = self.project_path / "package.json"
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze the current package.json and return insights"""
        if not self.package_json_path.exists():
            raise FileNotFoundError(f"package.json not found at {self.package_json_path}")
        
        with open(self.package_json_path) as f:
            data = json.load(f)
        
        current_deps = data.get("dependencies", {})
        current_dev_deps = data.get("devDependencies", {})
        
        # Identify incompatible dependencies
        incompatible: List[str] = []
        for dep in self.VITE_DEPS_TO_REMOVE:
            if dep in current_deps or dep in current_dev_deps:
                incompatible.append(dep)
        
        # Check for existing Next.js dependencies
        has_nextjs = "next" in current_deps
        has_react = "react" in current_deps and "react-dom" in current_deps
        
        return {
            "incompatible_dependencies": incompatible,
            "has_nextjs": has_nextjs,
            "has_react": has_react,
            "current_dependencies": current_deps,
            "current_dev_dependencies": current_dev_deps
        }
    
    def generate_transform(self) -> PackageJsonTransform:
        """Generate a transformation plan for package.json"""
        analysis = self.analyze()
        
        transform = PackageJsonTransform()
        
        # Add Next.js core dependencies if not present
        for dep, version in self.NEXTJS_CORE_DEPS.items():
            if dep not in analysis["current_dependencies"]:
                transform.dependencies_to_add[dep] = version
        
        # Add Next.js dev dependencies if not present
        for dep, version in self.NEXTJS_DEV_DEPS.items():
            if dep not in analysis["current_dev_dependencies"]:
                transform.dev_dependencies_to_add[dep] = version
        
        # Remove Vite-specific dependencies
        transform.dependencies_to_remove.extend(
            dep for dep in self.VITE_DEPS_TO_REMOVE
            if dep in analysis["current_dependencies"]
        )
        transform.dev_dependencies_to_remove.extend(
            dep for dep in self.VITE_DEPS_TO_REMOVE
            if dep in analysis["current_dev_dependencies"]
        )
        
        # Update scripts
        transform.scripts_to_add = self.NEXTJS_SCRIPTS
        transform.scripts_to_remove = ["serve"]  # Common Vite script to remove
        
        return transform
    
    def apply_transform(self, transform: PackageJsonTransform) -> None:
        """Apply the transformation to package.json"""
        if not self.package_json_path.exists():
            raise FileNotFoundError(f"package.json not found at {self.package_json_path}")
        
        with open(self.package_json_path) as f:
            data = json.load(f)
        
        # Update dependencies
        deps = data.get("dependencies", {})
        for dep in transform.dependencies_to_remove:
            deps.pop(dep, None)
        deps.update(transform.dependencies_to_add)
        data["dependencies"] = deps
        
        # Update dev dependencies
        dev_deps = data.get("devDependencies", {})
        for dep in transform.dev_dependencies_to_remove:
            dev_deps.pop(dep, None)
        dev_deps.update(transform.dev_dependencies_to_add)
        data["devDependencies"] = dev_deps
        
        # Update scripts
        scripts = data.get("scripts", {})
        for script in transform.scripts_to_remove:
            scripts.pop(script, None)
        scripts.update(transform.scripts_to_add)
        data["scripts"] = scripts
        
        # Write back to file
        with open(self.package_json_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")  # Add newline at end of file 