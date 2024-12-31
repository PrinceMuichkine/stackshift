from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import re
import json

from pydantic import BaseModel

class ViteConfigTransform(BaseModel):
    """Represents a transformation from Vite config to Next.js config"""
    next_config: Dict[str, Any] = {}
    env_variables: Dict[str, str] = {}
    additional_files: List[str] = []

class ViteConfigTransformer:
    """Handles the transformation of Vite configuration to Next.js"""
    
    def __init__(self, project_path: str) -> None:
        self.project_path = Path(project_path)
    
    def analyze_config(self) -> Dict[str, Any]:
        """Analyze the Vite configuration"""
        config_files = [
            "vite.config.ts",
            "vite.config.js",
            "vite.config.mjs",
            "vite.config.cjs"
        ]
        
        config_file = None
        for file in config_files:
            path = self.project_path / file
            if path.exists():
                config_file = path
                break
        
        if not config_file:
            return {}
        
        try:
            content = config_file.read_text()
            
            # Check if it's an empty config
            if "export default {}" in content.replace(" ", ""):
                return {}
            
            # Extract configuration using regex patterns
            config: Dict[str, Any] = {
                "plugins": self._extract_plugins(content),
                "build": self._extract_build_config(content),
                "server": self._extract_server_config(content),
                "resolve": self._extract_resolve_config(content),
                "env_prefix": self._extract_env_prefix(content)
            }
            
            return config
            
        except Exception as e:
            print(f"Error analyzing Vite config: {e}")
            return {}
    
    def _extract_plugins(self, content: str) -> List[str]:
        """Extract plugin configurations"""
        plugins: List[str] = []
        
        # Extract import statements
        import_pattern = r"import\s+\w+\s+from\s+['\"]([^'\"]+)['\"]"
        imports = re.finditer(import_pattern, content)
        for match in imports:
            plugin_name = match.group(1)
            if any(name in plugin_name for name in ["plugin", "vite-", "@vitejs"]):
                plugins.append(plugin_name)
        
        return plugins
    
    def _extract_build_config(self, content: str) -> Dict[str, Any]:
        """Extract build configuration"""
        build_config: Dict[str, Any] = {}
        
        # Extract outDir
        out_dir = re.search(r"outDir:\s*['\"]([^'\"]+)['\"]", content)
        if out_dir:
            build_config["outDir"] = out_dir.group(1)
        
        # Extract target
        target = re.search(r"target:\s*['\"]([^'\"]+)['\"]", content)
        if target:
            build_config["target"] = target.group(1)
        
        return build_config
    
    def _extract_server_config(self, content: str) -> Dict[str, Any]:
        """Extract server configuration"""
        server_config: Dict[str, Any] = {}
        
        # Extract port
        port = re.search(r"port:\s*(\d+)", content)
        if port:
            server_config["port"] = int(port.group(1))
        
        # Extract host
        host = re.search(r"host:\s*['\"]([^'\"]+)['\"]", content)
        if host:
            server_config["host"] = host.group(1)
        
        return server_config
    
    def _extract_resolve_config(self, content: str) -> Dict[str, Any]:
        """Extract resolve configuration"""
        resolve_config: Dict[str, Any] = {}
        
        # Extract alias configurations
        alias_pattern = r"alias:\s*{([^}]+)}"
        alias_match = re.search(alias_pattern, content, re.DOTALL)
        
        if alias_match:
            alias_text = alias_match.group(1)
            # Extract key-value pairs
            aliases: Dict[str, str] = {}
            for match in re.finditer(r"['\"]([@\w\-/]+)['\"]:\s*['\"]([^'\"]+)['\"]", alias_text):
                aliases[match.group(1)] = match.group(2)
            resolve_config["alias"] = aliases
        
        return resolve_config
    
    def _extract_env_prefix(self, content: str) -> Optional[str]:
        """Extract environment variable prefix"""
        prefix_match = re.search(r"envPrefix:\s*['\"]([^'\"]+)['\"]", content)
        return prefix_match.group(1) if prefix_match else None
    
    def generate_transform(self) -> ViteConfigTransform:
        """Generate Next.js configuration from Vite config"""
        vite_config = self.analyze_config()
        transform = ViteConfigTransform()
        
        # Basic Next.js configuration
        next_config: Dict[str, Any] = {
            "reactStrictMode": True,
            "poweredByHeader": False,
        }
        
        # Convert aliases to Next.js path aliases
        if "resolve" in vite_config and "alias" in vite_config["resolve"]:
            paths: Dict[str, List[str]] = {}
            for key, value in vite_config["resolve"]["alias"].items():
                if value.startswith("./") or value.startswith("../"):
                    paths[key] = [value]
                else:
                    paths[key] = ["./" + value]
            
            if paths:
                next_config["paths"] = paths
        
        # Convert build configuration
        if "build" in vite_config:
            build = vite_config["build"]
            if "outDir" in build:
                next_config["distDir"] = build["outDir"]
        
        # Convert server configuration
        if "server" in vite_config:
            server = vite_config["server"]
            if "port" in server:
                transform.env_variables["PORT"] = str(server["port"])
            if "host" in server:
                transform.env_variables["HOST"] = server["host"]
        
        transform.next_config = next_config
        
        # Add necessary Next.js files
        transform.additional_files.extend([
            "next.config.js",
            "tsconfig.json",
            ".env.local"
        ])
        
        return transform
    
    def apply_transform(self, transform: ViteConfigTransform) -> None:
        """Apply the Next.js configuration transformation"""
        # Create next.config.js
        next_config_path = self.project_path / "next.config.js"
        next_config_content = self._generate_next_config(transform.next_config)
        next_config_path.write_text(next_config_content)
        
        # Update tsconfig.json with paths if needed
        if "paths" in transform.next_config:
            self._update_tsconfig(transform.next_config["paths"])
        
        # Create or update .env.local
        if transform.env_variables:
            env_path = self.project_path / ".env.local"
            self._update_env_file(env_path, transform.env_variables)
    
    def _generate_next_config(self, config: Dict[str, Any]) -> str:
        """Generate next.config.js content"""
        lines = ["/** @type {import('next').NextConfig} */"]
        lines.append("const nextConfig = {")
        
        for key, value in config.items():
            if isinstance(value, dict):
                lines.append(f"  {key}: {self._dict_to_string(value)},")
            else:
                lines.append(f"  {key}: {self._value_to_string(value)},")
        
        lines.append("}")
        lines.append("")
        lines.append("module.exports = nextConfig")
        
        return "\n".join(lines)
    
    def _dict_to_string(self, d: Dict) -> str:
        """Convert a dictionary to its string representation"""
        parts = []
        for key, value in d.items():
            if isinstance(value, dict):
                parts.append(f"    {key}: {self._dict_to_string(value)}")
            else:
                parts.append(f"    {key}: {self._value_to_string(value)}")
        
        return "{\n" + ",\n".join(parts) + "\n  }"
    
    def _value_to_string(self, value: Any) -> str:
        """Convert a value to its string representation"""
        if isinstance(value, str):
            return f"'{value}'"
        if isinstance(value, bool):
            return str(value).lower()
        if isinstance(value, (list, tuple)):
            return f"[{', '.join(self._value_to_string(v) for v in value)}]"
        return str(value)
    
    def _update_tsconfig(self, paths: Dict[str, List[str]]) -> None:
        """Update tsconfig.json with path aliases"""
        tsconfig_path = self.project_path / "tsconfig.json"
        
        if tsconfig_path.exists():
            try:
                config = json.loads(tsconfig_path.read_text())
            except Exception:
                config = {}
        else:
            config = {}
        
        # Ensure compilerOptions exists
        if "compilerOptions" not in config:
            config["compilerOptions"] = {}
        
        # Update paths
        config["compilerOptions"]["paths"] = paths
        config["compilerOptions"]["baseUrl"] = "."
        
        # Write back
        tsconfig_path.write_text(json.dumps(config, indent=2) + "\n")
    
    def _update_env_file(self, env_path: Path, variables: Dict[str, str]) -> None:
        """Update .env file with new variables"""
        existing_vars: Dict[str, str] = {}
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    existing_vars[key.strip()] = value.strip()
        
        # Update with new variables
        existing_vars.update(variables)
        
        # Write back
        lines = [f"{key}={value}" for key, value in sorted(existing_vars.items())]
        env_path.write_text("\n".join(lines) + "\n") 