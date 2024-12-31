"""
AI-powered fixer for Next.js migration issues
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from anthropic import Anthropic
import json
import re
import ast
import shutil
from datetime import datetime

from .validation import NextJsVersion, ValidationResult

class MigrationFixer:
    def __init__(self, project_path: str, api_key: str):
        self.project_path = Path(project_path)
        self.client = Anthropic(api_key=api_key)
        self.fixed_files: Set[str] = set()
        
    def fix_issues(self, validation_result: ValidationResult) -> List[str]:
        """Fix migration issues using AI"""
        self.fixed_files.clear()
        
        # Group issues by file and type
        file_issues: Dict[str, Dict[str, List[str]]] = {}
        for error in validation_result.errors:
            if ":" in error:
                file_path = error.split(":")[1].strip()
                issue_type = self._categorize_issue(error)
                
                if file_path not in file_issues:
                    file_issues[file_path] = {}
                if issue_type not in file_issues[file_path]:
                    file_issues[file_path][issue_type] = []
                    
                file_issues[file_path][issue_type].append(error)
                
        # Fix issues file by file, handling dependencies
        for file_path, issues_by_type in file_issues.items():
            # Sort issues by priority
            sorted_issues = self._sort_issues_by_priority(issues_by_type)
            
            # Fix each issue type in order
            for issue_type, issues in sorted_issues:
                if self._fix_file(file_path, issues, issue_type, validation_result.router_type):
                    self.fixed_files.add(file_path)
                    
                    # Fix related files if needed
                    related_files = self._find_related_files(file_path, issue_type)
                    for related_file in related_files:
                        if self._fix_related_file(related_file, file_path, issue_type, validation_result.router_type):
                            self.fixed_files.add(str(related_file))
                
        return list(self.fixed_files)
        
    def _categorize_issue(self, error: str) -> str:
        """Categorize issue type for prioritization"""
        if any(kw in error.lower() for kw in ["import", "require", "dependency"]):
            return "imports"
        elif "route" in error.lower():
            return "routing"
        elif "client" in error.lower():
            return "components"
        elif "api" in error.lower():
            return "api"
        elif "style" in error.lower():
            return "styles"
        else:
            return "other"
            
    def _sort_issues_by_priority(self, issues_by_type: Dict[str, List[str]]) -> List[tuple[str, List[str]]]:
        """Sort issues by priority for optimal fixing"""
        priority_order = ["imports", "routing", "components", "api", "styles", "other"]
        return sorted(
            issues_by_type.items(),
            key=lambda x: priority_order.index(x[0]) if x[0] in priority_order else len(priority_order)
        )
        
    def _find_related_files(self, file_path: Path, issue_type: str) -> List[Path]:
        """Find related files that might need updates"""
        related_files = []
        file_content = Path(file_path).read_text()
        
        if issue_type == "routing":
            # Find components used in the route
            component_matches = re.finditer(r'import\s+(\w+)\s+from\s+["\'](.+?)["\']', file_content)
            for match in component_matches:
                component_path = self.project_path / match.group(2)
                if component_path.exists():
                    related_files.append(component_path)
                    
        elif issue_type == "components":
            # Find files importing this component
            component_name = Path(file_path).stem
            for ext in [".tsx", ".jsx", ".ts", ".js"]:
                for source_file in self.project_path.rglob(f"*{ext}"):
                    if source_file.read_text().find(component_name) != -1:
                        related_files.append(source_file)
                        
        return related_files
        
    def _fix_file(self, file_path: str, issues: List[str], issue_type: str, router_type: NextJsVersion) -> bool:
        """Fix issues in a single file using AI"""
        try:
            full_path = self.project_path / file_path
            if not full_path.exists():
                return False
                
            with open(full_path) as f:
                content = f.read()
                
            # Get file context
            context = self._get_file_context(full_path, issue_type)
            
            # Generate AI prompt based on issues and context
            prompt = self._generate_fix_prompt(content, issues, issue_type, router_type, context)
            
            # Get AI suggestion
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            fixed_content = self._extract_code(response.content)
            if fixed_content and fixed_content != content:
                # Validate the fixed content
                if self._validate_fixed_content(fixed_content, content, issue_type):
                    # Backup original file
                    backup_path = full_path.with_suffix(full_path.suffix + ".bak")
                    with open(backup_path, "w") as f:
                        f.write(content)
                        
                    # Write fixed content
                    with open(full_path, "w") as f:
                        f.write(fixed_content)
                    return True
                
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            
        return False
        
    def _get_file_context(self, file_path: Path, issue_type: str) -> Dict[str, Any]:
        """Get relevant context for fixing the file"""
        context = {
            "imports": set(),
            "exports": set(),
            "dependencies": set(),
            "related_files": []
        }
        
        try:
            with open(file_path) as f:
                content = f.read()
                tree = ast.parse(content)
                
            # Collect imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    context["imports"].update(n.name for n in node.names)
                elif isinstance(node, ast.ImportFrom):
                    context["imports"].add(node.module)
                    
            # Get package dependencies
            package_json = self.project_path / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    pkg = json.load(f)
                    context["dependencies"].update(pkg.get("dependencies", {}).keys())
                    context["dependencies"].update(pkg.get("devDependencies", {}).keys())
                    
        except Exception as e:
            print(f"Error getting context for {file_path}: {e}")
            
        return context
        
    def _validate_fixed_content(self, fixed_content: str, original_content: str, issue_type: str) -> bool:
        """Validate that the fixed content is safe to apply"""
        try:
            # Check that it's valid syntax
            ast.parse(fixed_content)
            
            # Check that core functionality is preserved
            original_tree = ast.parse(original_content)
            fixed_tree = ast.parse(fixed_content)
            
            original_functions = {n.name for n in ast.walk(original_tree) if isinstance(n, ast.FunctionDef)}
            fixed_functions = {n.name for n in ast.walk(fixed_tree) if isinstance(n, ast.FunctionDef)}
            
            if not original_functions.issubset(fixed_functions):
                return False
                
            # Check specific to issue type
            if issue_type == "components":
                if "'use client'" not in fixed_content and '"use client"' not in fixed_content:
                    if any(hook in fixed_content for hook in ["useState", "useEffect", "useRouter"]):
                        return False
                        
            return True
            
        except Exception:
            return False
            
    def _fix_related_file(self, file_path: Path, source_file: str, issue_type: str, router_type: NextJsVersion) -> bool:
        """Fix a related file based on changes in the source file"""
        try:
            if not file_path.exists() or str(file_path) in self.fixed_files:
                return False
                
            with open(file_path) as f:
                content = f.read()
                
            # Generate prompt for related file
            prompt = self._generate_related_fix_prompt(
                content,
                source_file,
                issue_type,
                router_type
            )
            
            # Get AI suggestion
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            fixed_content = self._extract_code(response.content)
            if fixed_content and fixed_content != content:
                if self._validate_fixed_content(fixed_content, content, issue_type):
                    # Backup original file
                    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                    with open(backup_path, "w") as f:
                        f.write(content)
                        
                    # Write fixed content
                    with open(file_path, "w") as f:
                        f.write(fixed_content)
                    return True
                    
        except Exception as e:
            print(f"Error fixing related file {file_path}: {e}")
            
        return False
        
    def _generate_related_fix_prompt(self, content: str, source_file: str, issue_type: str, router_type: NextJsVersion) -> str:
        """Generate AI prompt for fixing related files"""
        prompt = f"""Update this file to be compatible with changes made to {source_file} during Next.js {router_type.value} migration.

The file needs to be updated because it's related to a {issue_type} change.

Current code:
```
{content}
```

Please provide the updated code that:
1. Follows Next.js {router_type.value} best practices
2. Maintains existing functionality
3. Uses proper imports and dependencies
4. Includes 'use client' directive if needed
5. Uses Next.js components (Image, Link, etc.)

Return only the fixed code without explanations."""

        return prompt
        
    def _generate_fix_prompt(self, content: str, issues: List[str], issue_type: str, router_type: NextJsVersion, context: Dict[str, Any]) -> str:
        """Generate AI prompt for fixing issues"""
        prompt = f"""Fix the following issues in a {issue_type} file for Next.js {router_type.value} migration:

Issues:
{chr(10).join(f'- {issue}' for issue in issues)}

Current code:
```
{content}
```

Context:
- Imports: {', '.join(context['imports'])}
- Dependencies: {', '.join(context['dependencies'])}

Please provide the fixed code that:
1. Follows Next.js {router_type.value} best practices
2. Maintains existing functionality
3. Uses proper imports and dependencies
4. Includes 'use client' directive if needed
5. Uses Next.js components (Image, Link, etc.)

Return only the fixed code without explanations."""

        return prompt
        
    def _extract_code(self, response: str) -> Optional[str]:
        """Extract code from AI response"""
        # Try to find code between triple backticks
        code_match = re.search(r'```(?:\w+)?\n(.*?)```', response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        # If no code blocks found, try to extract the entire response
        # after removing any markdown-style formatting
        clean_response = re.sub(r'^[#\-*].*$', '', response, flags=re.MULTILINE)
        clean_response = clean_response.strip()
        
        if clean_response:
            return clean_response
        
        return None
        
    def _backup_file(self, file_path: Path) -> None:
        """Create a backup of the file before modifying it"""
        backup_dir = self.project_path / ".stackshift" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"{file_path.name}.{timestamp}.bak"
        
        shutil.copy2(file_path, backup_path)
        
    def _restore_backup(self, file_path: Path) -> bool:
        """Restore the most recent backup of a file"""
        backup_dir = self.project_path / ".stackshift" / "backups"
        if not backup_dir.exists():
            return False
            
        # Find the most recent backup
        backups = list(backup_dir.glob(f"{file_path.name}.*.bak"))
        if not backups:
            return False
            
        latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
        
        # Restore the backup
        shutil.copy2(latest_backup, file_path)
        return True
        
    def rollback_fixes(self) -> None:
        """Rollback all fixes made in the current session"""
        for file_path in self.fixed_files:
            path = Path(file_path)
            if path.exists():
                if self._restore_backup(path):
                    print(f"Rolled back changes to {file_path}")
                else:
                    print(f"No backup found for {file_path}")
                    
        self.fixed_files.clear()
        
    def _get_component_dependencies(self, file_path: Path) -> List[str]:
        """Get list of components that depend on this component"""
        dependencies = []
        component_name = file_path.stem
        
        for ext in [".tsx", ".jsx", ".ts", ".js"]:
            for source_file in self.project_path.rglob(f"*{ext}"):
                if source_file == file_path:
                    continue
                    
                try:
                    content = source_file.read_text()
                    if re.search(rf"\b{component_name}\b", content):
                        dependencies.append(str(source_file))
                except Exception:
                    continue
                    
        return dependencies
        
    def _analyze_component_usage(self, content: str) -> Dict[str, bool]:
        """Analyze how a component is used"""
        analysis = {
            "uses_state": False,
            "uses_effects": False,
            "uses_router": False,
            "uses_dom": False,
            "is_event_handler": False
        }
        
        # Check for React hooks
        analysis["uses_state"] = bool(re.search(r"\buseState\b", content))
        analysis["uses_effects"] = bool(re.search(r"\buseEffect\b", content))
        analysis["uses_router"] = bool(re.search(r"\buseRouter\b", content))
        
        # Check for DOM manipulation
        analysis["uses_dom"] = bool(re.search(r"\bdocument\b|\bwindow\b", content))
        
        # Check for event handlers
        analysis["is_event_handler"] = bool(re.search(r"on[A-Z]\w+=[{]", content))
        
        return analysis
        
    def _should_be_client_component(self, analysis: Dict[str, bool]) -> bool:
        """Determine if a component should be a client component"""
        return any([
            analysis["uses_state"],
            analysis["uses_effects"],
            analysis["uses_router"],
            analysis["uses_dom"],
            analysis["is_event_handler"]
        ])
        
    def _update_imports(self, content: str, router_type: NextJsVersion) -> str:
        """Update imports to use Next.js components"""
        # Replace React Router imports
        content = re.sub(
            r"import [^;]+? from ['\"](react-router-dom)['\"];?",
            "import { useRouter, usePathname } from 'next/navigation';",
            content
        )
        
        # Replace image imports
        content = re.sub(
            r"import [^;]+? from ['\"](.*?\.(?:png|jpg|jpeg|gif|svg))['\"];?",
            lambda m: f"import Image from 'next/image';\n// Update image import: {m.group(1)}",
            content
        )
        
        return content
        
    def _update_jsx_elements(self, content: str) -> str:
        """Update JSX elements to use Next.js components"""
        # Replace Link elements
        content = re.sub(
            r"<Link to=['\"]([^'\"]+?)['\"]([^>]*?)>",
            r'<Link href="\1"\2>',
            content
        )
        
        # Replace img elements
        content = re.sub(
            r"<img src=['\"]([^'\"]+?)['\"]([^>]*?)>",
            lambda m: self._convert_to_next_image(m.group(1), m.group(2)),
            content
        )
        
        return content
        
    def _convert_to_next_image(self, src: str, attrs: str) -> str:
        """Convert img element to Next.js Image component"""
        # Extract width and height if present
        width_match = re.search(r"width=['\"]?(\d+)", attrs)
        height_match = re.search(r"height=['\"]?(\d+)", attrs)
        
        width = width_match.group(1) if width_match else "0"
        height = height_match.group(1) if height_match else "0"
        
        # Remove width and height from other attributes
        other_attrs = re.sub(r"(?:width|height)=['\"]?\d+['\"]?", "", attrs)
        
        return f'<Image src="{src}" width={width} height={height} alt="" {other_attrs.strip()} />'
        
    def create_missing_files(self, validation_result: ValidationResult) -> List[str]:
        """Create missing required files using AI"""
        created_files = []
        
        # Create app directory if needed
        app_dir = self.project_path / "app"
        if not app_dir.exists():
            app_dir.mkdir(parents=True)
            
        # Define required files
        required_files = [
            {
                "path": "next.config.js",
                "type": "config",
                "description": "Next.js configuration file"
            },
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
        
        # Create each missing file
        for file_info in required_files:
            file_path = self.project_path / file_info["path"]
            if not file_path.exists():
                # Create parent directories if needed
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Create the file using AI
                if self._create_file(file_path, file_info, validation_result.router_type):
                    created_files.append(str(file_path))
                    
        # Update package.json
        package_json = self.project_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    package_data = json.load(f)
                    
                # Add Next.js dependency
                if "dependencies" not in package_data:
                    package_data["dependencies"] = {}
                package_data["dependencies"]["next"] = "^14.1.0"
                
                # Remove Vite dependencies
                if "devDependencies" in package_data:
                    vite_deps = [dep for dep in package_data["devDependencies"] if "vite" in dep.lower()]
                    for dep in vite_deps:
                        del package_data["devDependencies"][dep]
                        
                # Update scripts
                if "scripts" not in package_data:
                    package_data["scripts"] = {}
                package_data["scripts"].update({
                    "dev": "next dev",
                    "build": "next build",
                    "start": "next start"
                })
                
                # Write updated package.json
                with open(package_json, "w") as f:
                    json.dump(package_data, f, indent=2)
                    
                created_files.append(str(package_json))
                
            except Exception as e:
                print(f"Error updating package.json: {e}")
                
        # Update tsconfig.json
        tsconfig = self.project_path / "tsconfig.json"
        if tsconfig.exists():
            try:
                with open(tsconfig) as f:
                    tsconfig_data = json.load(f)
                    
                # Update compiler options
                if "compilerOptions" not in tsconfig_data:
                    tsconfig_data["compilerOptions"] = {}
                    
                tsconfig_data["compilerOptions"].update({
                    "target": "es5",
                    "lib": ["dom", "dom.iterable", "esnext"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "strict": True,
                    "forceConsistentCasingInFileNames": True,
                    "noEmit": True,
                    "esModuleInterop": True,
                    "module": "esnext",
                    "moduleResolution": "node",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "jsx": "preserve",
                    "incremental": True,
                    "plugins": [
                        {
                            "name": "next"
                        }
                    ],
                    "baseUrl": "."
                })
                    
                # Add Next.js specific includes
                tsconfig_data["include"] = ["next-env.d.ts", "**/*.ts", "**/*.tsx"]
                tsconfig_data["exclude"] = ["node_modules"]
                    
                # Write updated tsconfig.json
                with open(tsconfig, "w") as f:
                    json.dump(tsconfig_data, f, indent=2)
                    
                created_files.append(str(tsconfig))
                    
            except Exception as e:
                print(f"Error updating tsconfig.json: {e}")
                
        return created_files
        
    def _create_file(self, file_path: Path, file_info: Dict[str, str], router_type: NextJsVersion) -> bool:
        """Create a new file using AI"""
        try:
            # Generate prompt
            prompt = self._generate_file_prompt(file_info, router_type)
            
            # Get AI suggestion
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # Extract code from response
            code = self._extract_code(response.content)
            if code:
                # Write the file
                with open(file_path, "w") as f:
                    f.write(code)
                return True
                
        except Exception as e:
            print(f"Error creating file {file_path}: {e}")
            
        return False
        
    def _generate_file_prompt(self, file_info: Dict[str, str], router_type: NextJsVersion) -> str:
        """Generate AI prompt for creating new files"""
        prompt = f"""Create a new {file_info['type']} file for Next.js {router_type.value}.

File information:
{chr(10).join(f'- {k}: {v}' for k, v in file_info.items())}

Please provide code that:
1. Follows Next.js {router_type.value} best practices
2. Includes necessary imports
3. Uses proper TypeScript types
4. Includes 'use client' directive if needed
5. Uses Next.js components (Image, Link, etc.)

Return only the code without explanations."""

        return prompt
        
    def _generate_config_prompt(self, file_info: Dict[str, str], router_version: str) -> str:
        """Generate prompt for configuration files"""
        return f"""Create a {file_info["description"]} for a Next.js project using the {router_version}.

The configuration should:
1. Include all necessary settings for the {router_version}
2. Enable TypeScript support
3. Configure proper module resolution
4. Set up path aliases if needed
5. Include required dependencies
6. Add helpful comments explaining key settings

Return only the configuration code without any explanation."""
        
    def _generate_component_prompt(self, file_info: Dict[str, str], router_version: str) -> str:
        """Generate prompt for React components"""
        return f"""Create a {file_info["description"]} for a Next.js project using the {router_version}.

The component should:
1. Follow {router_version} conventions
2. Include proper TypeScript types
3. Add 'use client' directive if needed
4. Handle errors appropriately
5. Include loading states if applicable
6. Add helpful comments
7. Follow best practices for {file_info["type"]} components

Return only the component code without any explanation."""
        
    def _generate_generic_prompt(self, file_info: Dict[str, str], router_version: str) -> str:
        """Generate prompt for other file types"""
        return f"""Create a {file_info["description"]} for a Next.js project using the {router_version}.

The file should:
1. Follow Next.js best practices
2. Include proper configuration
3. Add helpful comments
4. Be well-structured and maintainable

Return only the code without any explanation.""" 