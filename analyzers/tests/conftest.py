import pytest
import os
from pathlib import Path

@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    yield
    if "ANTHROPIC_API_KEY" in os.environ:
        del os.environ["ANTHROPIC_API_KEY"]

@pytest.fixture
def sample_vite_project(tmp_path: Path) -> Path:
    """Create a sample Vite project structure for testing."""
    project_dir = tmp_path / "sample_vite_project"
    project_dir.mkdir()

    # Create source directory
    src_dir = project_dir / "src"
    src_dir.mkdir()

    # Create pages directory
    pages_dir = src_dir / "pages"
    pages_dir.mkdir()

    # Create sample files
    files = {
        "package.json": """{
            "name": "vite-project",
            "version": "0.0.0",
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.8.0"
            },
            "devDependencies": {
                "vite": "^4.3.9",
                "@vitejs/plugin-react": "^4.0.0"
            }
        }""",
        "vite.config.ts": """
            import { defineConfig } from 'vite'
            import react from '@vitejs/plugin-react'

            export default defineConfig({
                plugins: [react()],
                build: {
                    outDir: 'dist',
                    sourcemap: true
                }
            })
        """,
        "src/App.tsx": """
            import { BrowserRouter, Routes, Route } from 'react-router-dom'
            import Home from './pages/Home'
            import About from './pages/About'

            function App() {
                return (
                    <BrowserRouter>
                        <Routes>
                            <Route path="/" element={<Home />} />
                            <Route path="/about" element={<About />} />
                        </Routes>
                    </BrowserRouter>
                )
            }

            export default App
        """,
        "src/pages/Home.tsx": """
            export default function Home() {
                return <h1>Home Page</h1>
            }
        """,
        "src/pages/About.tsx": """
            export default function About() {
                return <h1>About Page</h1>
            }
        """
    }

    for file_path, content in files.items():
        file = project_dir / file_path
        file.parent.mkdir(exist_ok=True)
        file.write_text(content)

    return project_dir 