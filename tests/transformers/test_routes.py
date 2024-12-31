import pytest
from pathlib import Path
from transformers.routes import RoutesTransformer

@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory with route files"""
    project_dir = tmp_path / "test-project"
    src_dir = project_dir / "src"
    routes_dir = src_dir / "routes"
    pages_dir = src_dir / "pages"
    
    # Create directory structure
    for dir in [project_dir, src_dir, routes_dir, pages_dir]:
        dir.mkdir(parents=True)
    
    # Create route files
    route_files = {
        routes_dir / "index.tsx": """
            // @route /
            export default function Home() {
                return <div>Home</div>
            }
        """,
        routes_dir / "about.tsx": """
            // @route /about
            export default function About() {
                return <div>About</div>
            }
        """,
        routes_dir / "users" / "[id].tsx": """
            // @route /users/:id
            export default function UserProfile() {
                return <div>User Profile</div>
            }
        """,
        src_dir / "router.ts": """
            export const routes = [
                { path: '/', component: Home },
                { path: '/about', component: About },
                { path: '/users/:id', component: UserProfile }
            ];
        """
    }
    
    # Create the files
    for path, content in route_files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    
    return project_dir

def test_analyze_routes(temp_project_dir):
    """Test analyzing routes"""
    transformer = RoutesTransformer(str(temp_project_dir))
    routes = transformer.analyze_routes()
    
    # Check that all routes were found
    assert len(routes) >= 3
    
    # Check route paths
    paths = {route["route"] for route in routes if route["route"]}
    assert "/" in paths
    assert "/about" in paths
    assert "/users/:id" in paths
    
    # Check parameters
    user_route = next(r for r in routes if r["route"] == "/users/:id")
    assert user_route["params"] == ["id"]

def test_generate_transforms(temp_project_dir):
    """Test generating route transformations"""
    transformer = RoutesTransformer(str(temp_project_dir))
    transforms = transformer.generate_transforms()
    
    # Check that all routes have transforms
    assert len(transforms) >= 3
    
    # Check specific transforms
    for transform in transforms:
        if "users" in transform.source_path:
            # Check dynamic route transformation
            assert "[id]" in transform.target_path
            assert "id" in transform.route_params
        elif "about" in transform.source_path:
            # Check static route transformation
            assert transform.target_path.endswith("about/page.tsx")
            assert not transform.route_params
        elif "index" in transform.source_path:
            # Check index route transformation
            assert transform.target_path.endswith("page.tsx")
            assert not transform.route_params

def test_convert_to_nextjs_path(temp_project_dir):
    """Test converting route paths to Next.js format"""
    transformer = RoutesTransformer(str(temp_project_dir))
    
    # Test various path conversions
    assert transformer._convert_to_nextjs_path("/users/:id") == "/users/[id]"
    assert transformer._convert_to_nextjs_path("about") == "/about"
    assert transformer._convert_to_nextjs_path("/") == "/"

def test_infer_route_path(temp_project_dir):
    """Test inferring route paths from file paths"""
    transformer = RoutesTransformer(str(temp_project_dir))
    
    # Create test paths
    test_paths = {
        Path("pages/index.tsx"): "/",
        Path("pages/about.tsx"): "/about",
        Path("pages/users/[id].tsx"): "/users/:id",
        Path("pages/blog/[slug]/comments.tsx"): "/blog/:slug/comments"
    }
    
    for file_path, expected_route in test_paths.items():
        assert transformer._infer_route_path(file_path) == expected_route

def test_empty_project(tmp_path):
    """Test handling a project with no routes"""
    project_dir = tmp_path / "empty-project"
    project_dir.mkdir()
    (project_dir / "src").mkdir()
    
    transformer = RoutesTransformer(str(project_dir))
    routes = transformer.analyze_routes()
    
    assert len(routes) == 0
    
    transforms = transformer.generate_transforms()
    assert len(transforms) == 0 