import os
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from ..ai_analyzer import AIAnalyzer
from models import (
    AIAnalysis, RoutingAnalysis, DependencyAnalysis,
    ConfigurationAnalysis, RouteInfo, Dependency, DependencyType
)

@pytest.fixture
def mock_anthropic():
    with patch('anthropic.Anthropic') as mock:
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock()
        mock.return_value = mock_client
        
        # Set up the mock to return itself when instantiated
        mock.return_value = mock
        
        # Mock the API key environment variable
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            yield mock

@pytest.fixture
def test_project_path(tmp_path):
    # Create a temporary test project structure
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Create test files
    (project_dir / "src").mkdir()
    (project_dir / "src/App.tsx").write_text("""
        import { BrowserRouter, Route, Routes } from 'react-router-dom';
        export default function App() {
            return (
                <BrowserRouter>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/about" element={<About />} />
                    </Routes>
                </BrowserRouter>
            );
        }
    """)
    
    (project_dir / "package.json").write_text("""
        {
            "dependencies": {
                "react": "^18.0.0",
                "react-router-dom": "^6.0.0",
                "vite": "^4.0.0"
            }
        }
    """)
    
    (project_dir / "vite.config.ts").write_text("""
        import { defineConfig } from 'vite';
        export default defineConfig({
            plugins: [],
            build: {
                outDir: 'dist'
            }
        });
    """)
    
    return project_dir

def test_analyze_project_structure(test_project_path):
    """Test analyzing project structure."""
    with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
        analyzer = AIAnalyzer(str(test_project_path))
        structure = analyzer.analyze_project_structure()
        
        # Check if all expected files are found
        assert "src/App.tsx" in str(structure)
        assert "package.json" in str(structure)
        assert "vite.config.ts" in str(structure)
        
        # Check file types
        package_json = structure.get("package.json", {})
        assert package_json.get("type") == "package_json"
        
        vite_config = structure.get("vite.config.ts", {})
        assert vite_config.get("type") == "vite_config"
        
        app_tsx = structure.get("src/App.tsx", {})
        assert app_tsx.get("type") == "source"

@pytest.mark.asyncio
async def test_analyze_routing(test_project_path, mock_anthropic):
    """Test analyzing routing structure."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="""
        {
            "routes": [
                {
                    "current_path": "/",
                    "component_path": "src/pages/Home.tsx",
                    "layout": null,
                    "params": [],
                    "nextjs_path": "/",
                    "is_dynamic": false,
                    "data_fetching": {
                        "pattern": "none",
                        "recommendation": "Convert to server component"
                    }
                }
            ],
            "affected_files": ["src/App.tsx"],
            "complexity": "low",
            "breaking_changes": ["Remove react-router"],
            "migration_notes": ["Convert to App Router"]
        }
    """)]
    
    mock_anthropic.messages.create = AsyncMock(return_value=mock_response)
    
    analyzer = AIAnalyzer(str(test_project_path))
    analyzer.client = mock_anthropic  # Replace the client with our mock
    
    codebase_contents = await analyzer._read_codebase_files(await analyzer._get_relevant_files())
    result = await analyzer._analyze_routing(codebase_contents)
    
    assert isinstance(result, RoutingAnalysis)
    assert len(result.current_structure) == 1
    assert result.migration_complexity == "low"
    assert "Convert to App Router" in result.notes

@pytest.mark.asyncio
async def test_analyze_dependencies(test_project_path, mock_anthropic):
    """Test analyzing dependencies."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="""
        {
            "dependencies": [
                {
                    "name": "react-router-dom",
                    "version": "^6.0.0",
                    "type": "production",
                    "action": "remove",
                    "nextjs_equivalent": null,
                    "notes": "Not needed with Next.js App Router"
                }
            ],
            "incompatible_packages": ["react-router-dom"],
            "required_packages": [
                {
                    "name": "next",
                    "version": "^14.0.0",
                    "reason": "Core Next.js framework"
                }
            ],
            "migration_notes": ["Remove react-router-dom"]
        }
    """)]
    
    mock_anthropic.messages.create = AsyncMock(return_value=mock_response)
    
    analyzer = AIAnalyzer(str(test_project_path))
    analyzer.client = mock_anthropic  # Replace the client with our mock
    
    codebase_contents = await analyzer._read_codebase_files(await analyzer._get_relevant_files())
    result = await analyzer._analyze_dependencies(codebase_contents)
    
    assert isinstance(result, DependencyAnalysis)
    assert len(result.dependencies) == 1
    assert "react-router-dom" in result.incompatible_packages
    assert len(result.required_nextjs_packages) == 1
    assert "next@^14.0.0" in result.required_nextjs_packages

@pytest.mark.asyncio
async def test_analyze_configuration(test_project_path, mock_anthropic):
    """Test analyzing configuration."""
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="""
        {
            "vite_config": {
                "build": {"outDir": "dist"},
                "dev": {},
                "resolve": {},
                "plugins": [],
                "env": []
            },
            "next_config": {
                "build": {},
                "env": {},
                "images": {"domains": []},
                "rewrites": [],
                "redirects": [],
                "headers": []
            },
            "environment_variables": [],
            "migration_notes": ["Convert vite.config.ts to next.config.js"]
        }
    """)]
    
    mock_anthropic.messages.create = AsyncMock(return_value=mock_response)
    
    analyzer = AIAnalyzer(str(test_project_path))
    analyzer.client = mock_anthropic  # Replace the client with our mock
    
    codebase_contents = await analyzer._read_codebase_files(await analyzer._get_relevant_files())
    result = await analyzer._analyze_configuration(codebase_contents)
    
    assert isinstance(result, ConfigurationAnalysis)
    assert result.vite_config["build"]["outDir"] == "dist"
    assert "Convert vite.config.ts to next.config.js" in result.migration_notes

@pytest.mark.asyncio
async def test_analyze_codebase_integration(test_project_path, mock_anthropic):
    """Test the full codebase analysis integration."""
    responses = [
        # Routing analysis response
        MagicMock(content=[MagicMock(text="""
            {
                "routes": [],
                "affected_files": [],
                "complexity": "low",
                "breaking_changes": [],
                "migration_notes": []
            }
        """)]),
        # Dependency analysis response
        MagicMock(content=[MagicMock(text="""
            {
                "dependencies": [],
                "incompatible_packages": [],
                "required_packages": [],
                "migration_notes": []
            }
        """)]),
        # Configuration analysis response
        MagicMock(content=[MagicMock(text="""
            {
                "vite_config": {
                    "build": {"outDir": "dist"},
                    "dev": {},
                    "resolve": {},
                    "plugins": [],
                    "env": []
                },
                "next_config": {},
                "environment_variables": [],
                "migration_notes": []
            }
        """)]),
        # Overall recommendations response
        MagicMock(content=[MagicMock(text="""
            {
                "general_recommendations": ["Migrate routing first"],
                "migration_complexity": "medium",
                "estimated_time": "2-3 weeks",
                "migration_order": ["routing", "dependencies", "configuration"]
            }
        """)])
    ]
    
    # Create an async mock that returns each response in sequence
    mock_create = AsyncMock()
    mock_create.side_effect = responses
    mock_anthropic.messages.create = mock_create
    
    analyzer = AIAnalyzer(str(test_project_path))
    analyzer.client = mock_anthropic  # Replace the client with our mock
    
    result = await analyzer.analyze_codebase()
    
    assert isinstance(result, AIAnalysis)
    assert result.migration_complexity == "medium"
    assert result.estimated_time == "2-3 weeks"
    assert "Migrate routing first" in result.general_recommendations 