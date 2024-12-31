from __future__ import annotations
from typing import List, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel

class DependencyType(str, Enum):
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    PEER = "peer"

class Dependency(BaseModel):
    name: str
    version: str
    type: DependencyType
    nextjs_equivalent: Optional[str] = None
    migration_notes: Optional[str] = None

class RouteInfo(BaseModel):
    path: str
    component_path: str
    layout: Optional[str] = None
    params: List[str] = []
    nextjs_path: Optional[str] = None

class RoutingAnalysis(BaseModel):
    current_structure: List[RouteInfo]
    suggested_nextjs_structure: List[RouteInfo]
    migration_complexity: str
    notes: List[str] = []

class DependencyAnalysis(BaseModel):
    dependencies: List[Dependency]
    incompatible_packages: List[str] = []
    required_nextjs_packages: List[str] = []
    migration_notes: List[str] = []

class ConfigurationAnalysis(BaseModel):
    vite_config: Dict[str, Any]
    suggested_next_config: Dict[str, Any]
    environment_variables: List[str] = []
    migration_notes: List[str] = []

class AIAnalysis(BaseModel):
    routing: RoutingAnalysis
    dependencies: DependencyAnalysis
    configuration: ConfigurationAnalysis
    general_recommendations: List[str] = []
    migration_complexity: str
    estimated_time: str

class ProjectAnalysis(BaseModel):
    project_name: str
    project_path: str
    framework_version: str
    ai_analysis: Optional[AIAnalysis] = None
    errors: List[str] = []
    warnings: List[str] = [] 