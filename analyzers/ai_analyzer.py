"""
AI-powered analyzer for Vite to Next.js migration
"""

from pathlib import Path
from typing import List, Dict, Any
from anthropic import Anthropic

from .validation import MigrationValidator, ValidationResult
from .project_analyzer import ProjectAnalyzer

class AIAnalyzer:
    def __init__(self, project_path: str, api_key: str):
        self.project_path = Path(project_path)
        self.client = Anthropic(api_key=api_key)
        self.validator = MigrationValidator(project_path)
        
    def validate_migration(self) -> ValidationResult:
        """Validate the migration progress"""
        return self.validator.validate_migration()
        
    # ... rest of the AIAnalyzer implementation ... 