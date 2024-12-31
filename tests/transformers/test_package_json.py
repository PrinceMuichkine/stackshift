import json
import pytest
from pathlib import Path
from transformers.package_json import PackageJsonTransformer, PackageJsonTransform

@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory with a package.json"""
    package_json = {
        "name": "test-vite-app",
        "version": "0.1.0",
        "dependencies": {
            "react": "^17.0.0",
            "vite": "^4.0.0"
        },
        "devDependencies": {
            "@vitejs/plugin-react": "^3.0.0",
            "typescript": "^4.9.0"
        },
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "serve": "vite preview"
        }
    }
    
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    
    with open(project_dir / "package.json", "w") as f:
        json.dump(package_json, f, indent=2)
    
    return project_dir

def test_analyze_package_json(temp_project_dir):
    """Test analyzing package.json"""
    transformer = PackageJsonTransformer(str(temp_project_dir))
    analysis = transformer.analyze()
    
    assert analysis["incompatible_dependencies"] == ["vite", "@vitejs/plugin-react"]
    assert not analysis["has_nextjs"]
    assert "react" in analysis["current_dependencies"]
    assert "@vitejs/plugin-react" in analysis["current_dev_dependencies"]

def test_generate_transform(temp_project_dir):
    """Test generating package.json transformation"""
    transformer = PackageJsonTransformer(str(temp_project_dir))
    transform = transformer.generate_transform()
    
    # Check dependencies to add
    assert "next" in transform.dependencies_to_add
    assert "react-dom" in transform.dependencies_to_add
    
    # Check dependencies to remove
    assert "vite" in transform.dependencies_to_remove
    
    # Check dev dependencies to add
    assert "@types/react" in transform.dev_dependencies_to_add
    assert "eslint-config-next" in transform.dev_dependencies_to_add
    
    # Check dev dependencies to remove
    assert "@vitejs/plugin-react" in transform.dev_dependencies_to_remove
    
    # Check scripts
    assert transform.scripts_to_add["dev"] == "next dev"
    assert "serve" in transform.scripts_to_remove

def test_apply_transform(temp_project_dir):
    """Test applying package.json transformation"""
    transformer = PackageJsonTransformer(str(temp_project_dir))
    transform = transformer.generate_transform()
    transformer.apply_transform(transform)
    
    # Read the transformed package.json
    with open(temp_project_dir / "package.json") as f:
        result = json.load(f)
    
    # Check dependencies
    assert "next" in result["dependencies"]
    assert "vite" not in result["dependencies"]
    assert "react-dom" in result["dependencies"]
    
    # Check dev dependencies
    assert "@vitejs/plugin-react" not in result["devDependencies"]
    assert "eslint-config-next" in result["devDependencies"]
    assert "@types/react" in result["devDependencies"]
    
    # Check scripts
    assert result["scripts"]["dev"] == "next dev"
    assert result["scripts"]["build"] == "next build"
    assert "serve" not in result["scripts"]

def test_missing_package_json(tmp_path):
    """Test handling missing package.json"""
    transformer = PackageJsonTransformer(str(tmp_path))
    
    with pytest.raises(FileNotFoundError):
        transformer.analyze()

def test_empty_package_json(temp_project_dir):
    """Test handling empty package.json"""
    # Write empty package.json
    with open(temp_project_dir / "package.json", "w") as f:
        json.dump({}, f)
    
    transformer = PackageJsonTransformer(str(temp_project_dir))
    analysis = transformer.analyze()
    
    assert analysis["incompatible_dependencies"] == []
    assert not analysis["has_nextjs"]
    assert not analysis["current_dependencies"]
    assert not analysis["current_dev_dependencies"] 