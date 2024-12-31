import json
import pytest
from pathlib import Path
from transformers.vite_config import ViteConfigTransformer

@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory"""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    return project_dir

@pytest.fixture
def vite_config(temp_project_dir):
    """Create a temporary project directory with Vite config"""
    vite_config = """
        import { defineConfig } from 'vite'
        import react from '@vitejs/plugin-react'
        import tsconfigPaths from 'vite-tsconfig-paths'
        
        export default defineConfig({
            plugins: [
                react(),
                tsconfigPaths()
            ],
            build: {
                outDir: 'dist',
                target: 'es2015'
            },
            server: {
                port: 3000,
                host: 'localhost'
            },
            resolve: {
                alias: {
                    '@': './src',
                    '@components': './src/components',
                    '@utils': './src/utils'
                }
            },
            envPrefix: 'VITE_'
        })
    """
    
    (temp_project_dir / "vite.config.ts").write_text(vite_config)
    return temp_project_dir

def test_analyze_config(vite_config):
    """Test analyzing Vite configuration"""
    transformer = ViteConfigTransformer(str(vite_config))
    config = transformer.analyze_config()
    
    # Check plugins
    assert "@vitejs/plugin-react" in config["plugins"]
    assert "vite-tsconfig-paths" in config["plugins"]
    
    # Check build config
    assert config["build"]["outDir"] == "dist"
    assert config["build"]["target"] == "es2015"
    
    # Check server config
    assert config["server"]["port"] == 3000
    assert config["server"]["host"] == "localhost"
    
    # Check resolve config
    assert "@" in config["resolve"]["alias"]
    assert config["resolve"]["alias"]["@"] == "./src"
    
    # Check env prefix
    assert config["env_prefix"] == "VITE_"

def test_generate_transform(vite_config):
    """Test generating Next.js configuration transform"""
    transformer = ViteConfigTransformer(str(vite_config))
    transform = transformer.generate_transform()
    
    # Check Next.js config
    assert transform.next_config["reactStrictMode"] is True
    assert transform.next_config["poweredByHeader"] is False
    
    # Check path aliases
    assert "@" in transform.next_config.get("paths", {})
    assert transform.next_config["paths"]["@"] == ["./src"]
    
    # Check environment variables
    assert transform.env_variables["PORT"] == "3000"
    assert transform.env_variables["HOST"] == "localhost"
    
    # Check additional files
    assert "next.config.js" in transform.additional_files
    assert "tsconfig.json" in transform.additional_files
    assert ".env.local" in transform.additional_files

def test_apply_transform(vite_config):
    """Test applying Next.js configuration transform"""
    transformer = ViteConfigTransformer(str(vite_config))
    transform = transformer.generate_transform()
    transformer.apply_transform(transform)
    
    # Check next.config.js
    next_config_path = vite_config / "next.config.js"
    assert next_config_path.exists()
    content = next_config_path.read_text()
    assert "reactStrictMode: true" in content
    assert "poweredByHeader: false" in content
    
    # Check tsconfig.json
    tsconfig_path = vite_config / "tsconfig.json"
    assert tsconfig_path.exists()
    with open(tsconfig_path) as f:
        tsconfig = json.load(f)
    assert "@" in tsconfig["compilerOptions"]["paths"]
    assert tsconfig["compilerOptions"]["baseUrl"] == "."
    
    # Check .env.local
    env_path = vite_config / ".env.local"
    assert env_path.exists()
    env_content = env_path.read_text()
    assert "PORT=3000" in env_content
    assert "HOST=localhost" in env_content

def test_missing_config(temp_project_dir):
    """Test handling missing Vite config"""
    transformer = ViteConfigTransformer(str(temp_project_dir))
    config = transformer.analyze_config()
    assert not config
    
    transform = transformer.generate_transform()
    assert transform.next_config["reactStrictMode"] is True
    assert not transform.env_variables

def test_empty_config(temp_project_dir):
    """Test handling empty Vite config"""
    (temp_project_dir / "vite.config.js").write_text("export default {}")
    
    transformer = ViteConfigTransformer(str(temp_project_dir))
    config = transformer.analyze_config()
    
    # Empty config should have empty values
    assert not config.get("plugins")
    assert not config.get("build")
    assert not config.get("server")
    assert not config.get("resolve")
    assert not config.get("env_prefix") 