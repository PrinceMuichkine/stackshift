from pathlib import Path
from typing import List, Dict, Any
import re
import ast

class ComponentTransformer:
    """Handles Next.js-specific component transformations"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        
    def transform_to_client_components(self, file_paths: List[str] = None) -> List[str]:
        """Add 'use client' directive to components that need it"""
        if not file_paths:
            # Find all component files
            file_paths = []
            for ext in ['.tsx', '.jsx']:
                file_paths.extend(self.project_path.glob(f"**/*{ext}"))
        
        transformed_files = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Check if file needs 'use client'
                if self._needs_client_directive(content):
                    # Add 'use client' if not present
                    if 'use client' not in content:
                        new_content = '"use client";\n\n' + content
                        with open(file_path, 'w') as f:
                            f.write(new_content)
                        transformed_files.append(str(file_path))
                        
            except Exception as e:
                print(f"Error transforming {file_path}: {e}")
                
        return transformed_files
        
    def transform_to_server_components(self, file_paths: List[str] = None) -> List[str]:
        """Convert components to server components by removing client-side code"""
        if not file_paths:
            file_paths = []
            for ext in ['.tsx', '.jsx']:
                file_paths.extend(self.project_path.glob(f"**/*{ext}"))
                
        transformed_files = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Remove 'use client' directive if present
                if 'use client' in content:
                    content = re.sub(r'["\']use client["\'];?\n*', '', content)
                    
                # No need to add 'use server' as it's the default in Next.js
                
                # Convert client-side hooks to server actions
                content = self._convert_hooks_to_server_actions(content)
                
                with open(file_path, 'w') as f:
                    f.write(content)
                transformed_files.append(str(file_path))
                
            except Exception as e:
                print(f"Error transforming {file_path}: {e}")
                
        return transformed_files
        
    def migrate_router_to_nextjs(self, file_paths: List[str] = None) -> List[str]:
        """Migrate React Router to Next.js routing with better JSX handling"""
        if not file_paths:
            file_paths = []
            for ext in ['.tsx', '.jsx', '.ts', '.js']:
                file_paths.extend(self.project_path.glob(f"**/*{ext}"))
                
        transformed_files = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Handle imports
                content = re.sub(
                    r'import\s*{([^}]+)}\s*from\s*["\']react-router-dom["\'];?',
                    lambda m: self._convert_router_imports(m.group(1)),
                    content
                )
                
                # Handle Link components with attributes
                content = re.sub(
                    r'<Link\s+([^>]+)>',
                    lambda m: self._convert_link_component(m.group(1)),
                    content
                )
                
                # Handle navigation
                content = re.sub(
                    r'const\s+navigate\s*=\s*useNavigate\(\)',
                    'const router = useRouter()',
                    content
                )
                
                content = re.sub(
                    r'navigate\((.*?)\)',
                    lambda m: self._convert_navigation(m.group(1)),
                    content
                )
                
                # Handle location and params
                content = content.replace('useLocation()', 'usePathname()')
                content = re.sub(
                    r'const\s*{\s*([^}]+)\s*}\s*=\s*useParams\(\)',
                    lambda m: self._convert_params(m.group(1)),
                    content
                )
                
                with open(file_path, 'w') as f:
                    f.write(content)
                transformed_files.append(str(file_path))
                
            except Exception as e:
                print(f"Error transforming {file_path}: {e}")
                
        return transformed_files
        
    def migrate_styles_to_nextjs(self) -> List[str]:
        """Migrate CSS/styles to Next.js conventions"""
        transformed_files = []
        
        # Create global styles directory
        styles_dir = self.project_path / 'styles'
        styles_dir.mkdir(exist_ok=True)
        
        # Move global styles
        global_css = self.project_path / 'src' / 'index.css'
        if global_css.exists():
            new_global_css = styles_dir / 'globals.css'
            global_css.rename(new_global_css)
            transformed_files.append(str(new_global_css))
            
        # Handle CSS modules
        for css_file in self.project_path.glob('**/*.css'):
            if not css_file.name == 'globals.css':
                # Convert to CSS module if not already
                if not css_file.name.endswith('.module.css'):
                    new_name = css_file.stem + '.module.css'
                    new_path = css_file.parent / new_name
                    css_file.rename(new_path)
                    transformed_files.append(str(new_path))
                    
                    # Update imports in associated component
                    component_file = css_file.parent / (css_file.stem + '.tsx')
                    if component_file.exists():
                        with open(component_file, 'r') as f:
                            content = f.read()
                        content = re.sub(
                            f"import ['\"](.*/)?{css_file.name}['\"]",
                            f"import styles from './{new_name}'",
                            content
                        )
                        with open(component_file, 'w') as f:
                            f.write(content)
                        transformed_files.append(str(component_file))
                        
        return transformed_files
        
    def migrate_api_to_nextjs(self) -> List[str]:
        """Migrate API routes to Next.js API routes"""
        transformed_files = []
        
        # Create app/api directory
        api_dir = self.project_path / 'app' / 'api'
        api_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all API files
        api_files = []
        for ext in ['.ts', '.js']:
            api_files.extend(self.project_path.glob(f"**/api/**/*{ext}"))
            
        for api_file in api_files:
            try:
                with open(api_file, 'r') as f:
                    content = f.read()
                    
                # Convert to Next.js API route format
                new_content = self._convert_to_nextjs_api(content)
                
                # Create new file in app/api
                new_path = api_dir / api_file.name
                with open(new_path, 'w') as f:
                    f.write(new_content)
                transformed_files.append(str(new_path))
                
            except Exception as e:
                print(f"Error transforming {api_file}: {e}")
                
        return transformed_files
        
    def migrate_images_to_nextjs(self, file_paths: List[str] = None) -> List[str]:
        """Migrate image imports and usage to Next.js Image component"""
        if not file_paths:
            file_paths = []
            for ext in ['.tsx', '.jsx', '.ts', '.js']:
                file_paths.extend(self.project_path.glob(f"**/*{ext}"))
            
        transformed_files = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Add Next.js Image import if needed
                if '<img' in content and 'next/image' not in content:
                    content = 'import Image from "next/image";\n' + content
                    
                # Convert static image imports
                content = re.sub(
                    r'import\s+(\w+)\s+from\s+["\']\.\.?\/.*\.(png|jpg|jpeg|gif|svg)["\']',
                    lambda m: f'// Moved to public/images/\n// import {m.group(1)} from "../public/images/{m.group(1)}.{m.group(2)}"',
                    content
                )
                
                # Convert img tags to Next.js Image
                content = re.sub(
                    r'<img([^>]*?)src=[\'"](.*?)[\'"]([^>]*?)>',
                    lambda m: self._convert_image_tag(m.groups()),
                    content
                )
                
                # Move image files to public directory
                if file_path.parent.name == 'assets':
                    public_dir = self.project_path / 'public' / 'images'
                    public_dir.mkdir(parents=True, exist_ok=True)
                    
                    for img_ext in ['png', 'jpg', 'jpeg', 'gif', 'svg']:
                        for img_file in file_path.parent.glob(f'*.{img_ext}'):
                            new_path = public_dir / img_file.name
                            if img_file.exists():
                                img_file.rename(new_path)
                                transformed_files.append(str(new_path))
                
                with open(file_path, 'w') as f:
                    f.write(content)
                transformed_files.append(str(file_path))
                
            except Exception as e:
                print(f"Error transforming {file_path}: {e}")
                
        return transformed_files
        
    def _convert_image_tag(self, groups: tuple) -> str:
        """Convert HTML img tag to Next.js Image component"""
        before_attrs, src, after_attrs = groups
        
        # Extract width and height if present
        width_match = re.search(r'width=[\'"](.*?)[\'"]', before_attrs + after_attrs)
        height_match = re.search(r'height=[\'"](.*?)[\'"]', before_attrs + after_attrs)
        
        width = width_match.group(1) if width_match else '0'
        height = height_match.group(1) if height_match else '0'
        
        # Handle different image sources
        if src.startswith('http'):
            # Remote images need width, height, and blurDataURL
            return f'<Image src="{src}" alt="" width={width} height={height} unoptimized />'
        elif src.startswith('./') or src.startswith('../'):
            # Local images from assets - move to public/images
            img_name = src.split('/')[-1]
            return f'<Image src="/images/{img_name}" alt="" width={width} height={height} />'
        else:
            # Already in public directory
            return f'<Image src="{src}" alt="" width={width} height={height} />'
        
    def _needs_client_directive(self, content: str) -> bool:
        """Check if a component needs 'use client' directive using AST parsing"""
        try:
            tree = ast.parse(content)
            
            class ClientFeatureVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.needs_client = False
                    self.client_hooks = {
                        'useState', 'useEffect', 'useContext', 'useReducer',
                        'useCallback', 'useMemo', 'useRef', 'useImperativeHandle',
                        'useLayoutEffect', 'useDebugValue', 'useRouter', 'useSearchParams'
                    }
                    self.browser_apis = {
                        'window', 'document', 'localStorage', 'sessionStorage',
                        'navigator', 'history'
                    }
                    
                def visit_Call(self, node):
                    if isinstance(node.func, ast.Name) and node.func.id in self.client_hooks:
                        self.needs_client = True
                    self.generic_visit(node)
                    
                def visit_Attribute(self, node):
                    if isinstance(node.value, ast.Name) and node.value.id in self.browser_apis:
                        self.needs_client = True
                    self.generic_visit(node)
                    
                def visit_ImportFrom(self, node):
                    if node.module in {'react', 'next/navigation'}:
                        for name in node.names:
                            if name.name in self.client_hooks:
                                self.needs_client = True
                    self.generic_visit(node)
            
            visitor = ClientFeatureVisitor()
            visitor.visit(tree)
            return visitor.needs_client
            
        except SyntaxError:
            # Fallback to regex for JSX content
            return any(hook in content for hook in [
                'useState', 'useEffect', 'useContext', 'useReducer',
                'useCallback', 'useMemo', 'useRef', 'useImperativeHandle',
                'useLayoutEffect', 'useDebugValue', 'useRouter', 'useSearchParams'
            ]) or any(api in content for api in [
                'window.', 'document.', 'localStorage', 'sessionStorage',
                'navigator.', 'history.'
            ])

    def _convert_hooks_to_server_actions(self, content: str) -> str:
        """Convert React hooks to server actions using AST transformation"""
        try:
            tree = ast.parse(content)
            
            class HookTransformer(ast.NodeTransformer):
                def visit_Call(self, node):
                    if isinstance(node.func, ast.Name) and node.func.id == 'useState':
                        # Convert useState to server state
                        if len(node.args) > 0:
                            return ast.Name(id=f'serverState_{node.args[0].value}', ctx=ast.Load())
                    return self.generic_visit(node)
                    
                def visit_With(self, node):
                    if isinstance(node.items[0].context_expr, ast.Call) and \
                       isinstance(node.items[0].context_expr.func, ast.Name) and \
                       node.items[0].context_expr.func.id == 'useEffect':
                        # Convert useEffect to server-side code
                        return node.body
                    return self.generic_visit(node)
            
            transformer = HookTransformer()
            new_tree = transformer.visit(tree)
            
            # Add 'use server' if needed
            if any(isinstance(node, ast.FunctionDef) for node in ast.walk(new_tree)):
                new_tree.body.insert(0, ast.Expr(value=ast.Str(s='use server')))
                
            return ast.unparse(new_tree)
            
        except SyntaxError:
            # Fallback to regex for JSX content
            content = re.sub(
                r'const \[(.*?), set\1\] = useState\((.*?)\)',
                lambda m: f'const {m.group(1)} = serverState({m.group(2)})',
                content
            )
            
            content = re.sub(
                r'useEffect\(\(\) => \{(.*?)\}, \[(.*?)\]\)',
                lambda m: f'// Server-side effect\n{m.group(1)}',
                content,
                flags=re.DOTALL
            )
            
            if 'serverState(' in content:
                content = 'use server;\n\n' + content
                
            return content

    def _convert_router_imports(self, imports: str) -> str:
        """Convert React Router imports to Next.js equivalents"""
        import_map = {
            'Link': 'Link',
            'useNavigate': 'useRouter',
            'useLocation': 'usePathname',
            'useParams': 'useSearchParams',
            'Navigate': 'redirect',
            'Outlet': 'children'
        }
        
        imports = [i.strip() for i in imports.split(',')]
        next_imports = []
        
        for imp in imports:
            if imp in import_map:
                next_imports.append(import_map[imp])
                
        if next_imports:
            return f"import {{ {', '.join(next_imports)} }} from 'next/navigation';"
        return ''
        
    def _convert_link_component(self, attrs: str) -> str:
        """Convert React Router Link attributes to Next.js Link attributes"""
        # Convert to="..." to href="..."
        attrs = re.sub(r'to=(["\'].*?["\'])', r'href=\1', attrs)
        
        # Convert state prop to shallow routing
        if 'state=' in attrs:
            attrs = re.sub(r'state=({.*?})', r'shallow=true', attrs)
            
        return f'<Link {attrs}>'
        
    def _convert_navigation(self, args: str) -> str:
        """Convert navigation calls to Next.js router calls"""
        # Handle different navigation patterns
        if '{' in args:  # Object argument
            return f'router.push({args})'
        elif args.startswith('"') or args.startswith("'"):  # String path
            return f'router.push({args})'
        else:  # Dynamic path
            return f'router.push(`${{{args}}}`)'
            
    def _convert_params(self, params: str) -> str:
        """Convert useParams to useSearchParams"""
        params = [p.strip() for p in params.split(',')]
        conversions = []
        
        for param in params:
            conversions.append(f'const {param} = searchParams.get("{param}")')
            
        return 'const searchParams = useSearchParams();\n' + '\n'.join(conversions)
        
    def _convert_to_nextjs_api(self, content: str) -> str:
        """Convert API route to Next.js format"""
        # Add Next.js API route template
        template = '''import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function GET(request: NextRequest) {
    try {
        // API logic here
        return NextResponse.json({ success: true });
    } catch (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        // API logic here
        return NextResponse.json({ success: true });
    } catch (error) {
        return NextResponse.json({ error: error.message }, { status: 500 });
    }
}
'''
        return template 