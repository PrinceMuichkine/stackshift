from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

class ActionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class RouteInfo(BaseModel):
    path: str
    component_path: str
    layout: Optional[str] = None
    params: List[str] = []
    nextjs_path: Optional[str] = None
    is_dynamic: bool = False
    suggested_pattern: str = "app"
    client_boundary: bool = False
    data_fetching: Optional[Dict[str, str]] = None

class MigrationAction(BaseModel):
    id: str
    title: str
    description: str
    type: str
    dependencies: List[str] = []
    estimated_time: str
    command: Optional[str] = None
    file_changes: List[str] = []
    validation_steps: List[str] = []
    status: ActionStatus = ActionStatus.PENDING

class DependencyInfo(BaseModel):
    name: str
    version: str
    type: str
    nextjs_equivalent: Optional[str] = None
    migration_notes: Optional[str] = None

class RoutingAnalysis(BaseModel):
    current_structure: List[RouteInfo]
    suggested_nextjs_structure: List[str]
    migration_complexity: str
    notes: List[str]
    actions: List[MigrationAction] = []

class DependencyAnalysis(BaseModel):
    dependencies: List[DependencyInfo]
    incompatible_packages: List[str]
    required_nextjs_packages: List[str]
    migration_notes: List[str]
    actions: List[MigrationAction] = []

class ConfigurationAnalysis(BaseModel):
    vite_config: Dict[str, Any]
    suggested_next_config: Dict[str, Any]
    environment_variables: List[Dict[str, str]]
    migration_notes: List[str]
    actions: List[MigrationAction] = []

class AIAnalysis(BaseModel):
    routing: RoutingAnalysis
    dependencies: DependencyAnalysis
    configuration: ConfigurationAnalysis
    migration_complexity: str
    estimated_time: str
    actions: List[MigrationAction]
    completed_actions: List[str] = []
    progress: float = 0.0

class ProjectAnalysis(BaseModel):
    project_name: str
    project_path: str
    framework_version: str
    ai_analysis: Optional[AIAnalysis] = None
    errors: List[str] = []
    warnings: List[str] = [] 