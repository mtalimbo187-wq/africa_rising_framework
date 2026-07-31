"""
Pydantic schemas for all data structures.

These define the contracts between agents.
Every agent input/output MUST validate against these schemas.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
import uuid


# ============================================================================
# ENUMS
# ============================================================================

class MessageType(str, Enum):
    EXECUTE = "EXECUTE"
    RESULT = "RESULT"
    ERROR = "ERROR"
    RETRY = "RETRY"


class AgentStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"


class ProductionState(str, Enum):
    INIT = "INIT"
    RESEARCH = "RESEARCH"
    FACT_CHECK = "FACT_CHECK"
    SCRIPT_ANALYSIS = "SCRIPT_ANALYSIS"
    VISUAL_ALIGNMENT = "VISUAL_ALIGNMENT"
    VISUAL_PLANNING = "VISUAL_PLANNING"
    ASSET_SEARCH = "ASSET_SEARCH"
    AI_GENERATION = "AI_GENERATION"
    TIMELINE_BUILD = "TIMELINE_BUILD"
    PRODUCTION = "PRODUCTION"
    QA_REVIEW = "QA_REVIEW"
    CONTINUITY_CHECK = "CONTINUITY_CHECK"
    AUDIENCE_SIM = "AUDIENCE_SIM"
    RE_EDIT = "RE_EDIT"
    FINAL_APPROVAL = "FINAL_APPROVAL"
    EXPORT = "EXPORT"
    STOPPED = "STOPPED"


class Importance(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class VisualType(str, Enum):
    ARCHIVAL = "archival"
    DOCUMENTARY = "documentary"
    STOCK = "stock"
    MAP = "map"
    SATELLITE = "satellite"
    CHART = "chart"
    DIAGRAM = "diagram"
    PHOTO = "photo"
    AI_GENERATED = "ai_generated"


# ============================================================================
# MESSAGE SYSTEM
# ============================================================================

class MessageMetadata(BaseModel):
    """Metadata for messages"""
    attempt: int = 1
    retry_backoff_seconds: Optional[int] = None
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timeout_seconds: Optional[int] = None


class Message(BaseModel):
    """Standard message envelope"""
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Dict[str, Any]
    metadata: MessageMetadata = Field(default_factory=MessageMetadata)


# ============================================================================
# RESEARCH AGENT
# ============================================================================

class Fact(BaseModel):
    """Extracted fact from script"""
    fact_id: str
    claim: str
    entities: List[str] = []
    people: List[str] = []
    places: List[str] = []
    dates: List[str] = []
    organizations: List[str] = []
    statistics: List[str] = []
    context: Optional[str] = None


class ResearchOutput(BaseModel):
    """Research Agent output"""
    agent_name: str = "Research Agent"
    status: AgentStatus
    facts: List[Fact]
    duration_ms: float
    cost_usd: float = 0.0


# ============================================================================
# FACT CHECKER
# ============================================================================

class VerifiedFact(BaseModel):
    """Verified fact with source"""
    fact_id: str
    claim: str
    status: str = Field(pattern="^(VERIFIED|UNVERIFIED|PARTIAL)$")
    confidence: float = Field(ge=0.0, le=1.0)
    source: str
    source_url: Optional[str] = None


class FactCheckOutput(BaseModel):
    """Fact Checker output"""
    agent_name: str = "Fact Checker"
    status: AgentStatus
    verified_facts: List[VerifiedFact]
    unverified: List[str] = []
    confidence_average: float = Field(ge=0.0, le=1.0)


# ============================================================================
# SCRIPT ANALYZER
# ============================================================================

class Scene(BaseModel):
    """Scene extracted from script"""
    scene_id: str
    start_time: float
    end_time: float
    narration: str
    emotion: str
    importance: Importance
    entities: List[str] = []
    location: Optional[str] = None
    date: Optional[str] = None
    visual_requirements: List[str] = []

    @validator("end_time")
    def end_after_start(cls, v, values):
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("end_time must be greater than start_time")
        return v


class ScriptAnalysisOutput(BaseModel):
    """Script Analyzer output"""
    agent_name: str = "Script Analyzer"
    status: AgentStatus
    scenes: List[Scene]
    total_duration: float
    scene_count: int


# ============================================================================
# VISUAL PLANNER
# ============================================================================

class VisualAssignment(BaseModel):
    """Visual assignment for a scene"""
    scene_id: str
    primary_visual: str
    secondary_visual: str
    fallback_visual: str
    duration_seconds: float = Field(ge=2.0, le=8.0)
    camera_direction: str
    transition: str
    purpose: str


class VisualPlanOutput(BaseModel):
    """Visual Planner output"""
    agent_name: str = "Visual Planner"
    status: AgentStatus
    visual_plan: List[VisualAssignment]


# ============================================================================
# VISUAL ALIGNMENT AGENT
# ============================================================================

class AlignedScene(BaseModel):
    """Scene with visual teaching quality score"""
    scene_id: str
    visual_teaching_score: float = Field(ge=0.0, le=100.0)
    primary_visual: str
    secondary_visual: str
    fallback_visual: str
    purpose: str
    status: AgentStatus


class VisualAlignmentOutput(BaseModel):
    """Visual Alignment Agent output"""
    agent_name: str = "Visual Alignment Agent"
    status: AgentStatus
    aligned_scenes: List[AlignedScene]
    overall_teaching_score: float = Field(ge=0.0, le=100.0)


# ============================================================================
# ASSET FINDER
# ============================================================================

class Asset(BaseModel):
    """Asset found for a visual"""
    asset_id: str
    visual_id: str
    source: str
    url: str
    resolution: str
    quality_score: float = Field(ge=0.0, le=100.0)
    license: str
    status: str = Field(pattern="^(AVAILABLE|UNAVAILABLE)$")


class AssetFinderOutput(BaseModel):
    """Asset Finder output"""
    agent_name: str = "Asset Finder"
    status: AgentStatus
    assets: List[Asset]
    coverage_percentage: float = Field(ge=0.0, le=1.0)
    missing_visuals: List[str] = []


# ============================================================================
# TIMELINE BUILDER
# ============================================================================

class Shot(BaseModel):
    """Shot in timeline"""
    shot_id: str
    scene_id: str
    start_time: float
    end_time: float
    duration: float
    asset_id: str
    transition: str
    caption_sync: float


class TimelineOutput(BaseModel):
    """Timeline Builder output"""
    agent_name: str = "Timeline Builder"
    status: AgentStatus
    timeline: List[Shot]
    total_duration: float
    sync_accuracy: float = Field(ge=0.0, le=1.0)


# ============================================================================
# QA REVIEWER
# ============================================================================

class QAIssue(BaseModel):
    """Quality issue found"""
    timestamp: str
    dimension: str
    description: str
    severity: str


class QAOutput(BaseModel):
    """QA Reviewer output"""
    agent_name: str = "QA Reviewer"
    status: AgentStatus
    visual_relevance: float = Field(ge=0.0, le=100.0)
    narration_sync: float = Field(ge=0.0, le=100.0)
    editing_quality: float = Field(ge=0.0, le=100.0)
    historical_accuracy: float = Field(ge=0.0, le=100.0)
    overall_score: float = Field(ge=0.0, le=100.0)
    issues: List[QAIssue] = []


# ============================================================================
# CONTINUITY AGENT
# ============================================================================

class ContinuityOutput(BaseModel):
    """Continuity & Story Flow Agent output"""
    agent_name: str = "Continuity & Story Flow Agent"
    status: AgentStatus
    story_flow: float = Field(ge=0.0, le=100.0)
    visual_consistency: float = Field(ge=0.0, le=100.0)
    transition_quality: float = Field(ge=0.0, le=100.0)
    educational_value: float = Field(ge=0.0, le=100.0)
    overall_score: float = Field(ge=0.0, le=100.0)
    issues: List[str] = []


# ============================================================================
# AUDIENCE SIMULATION AGENT
# ============================================================================

class AudienceOutput(BaseModel):
    """Audience Simulation Agent output"""
    agent_name: str = "Audience Simulation Agent"
    status: AgentStatus
    hook_strength: float = Field(ge=0.0, le=100.0)
    clarity: float = Field(ge=0.0, le=100.0)
    engagement: float = Field(ge=0.0, le=100.0)
    educational_value: float = Field(ge=0.0, le=100.0)
    overall_satisfaction: float = Field(ge=0.0, le=100.0)
    predicted_dropoffs: List[Dict[str, Any]] = []


# ============================================================================
# FINAL APPROVAL
# ============================================================================

class Failure(BaseModel):
    """Failure in final review"""
    timestamp: Optional[str] = None
    type: str
    description: str


class FinalApprovalOutput(BaseModel):
    """Final Approval Agent output"""
    agent_name: str = "Final Approval Agent"
    status: str = Field(pattern="^(APPROVED|REJECTED)$")
    reason: str
    failures: List[Failure] = []
    certification: Optional[str] = None


# ============================================================================
# PRODUCTION STATE
# ============================================================================

class ProductionStatus(BaseModel):
    """Current production status"""
    state: ProductionState
    current_agent: Optional[str] = None
    progress_percent: float = Field(ge=0.0, le=100.0)
    gates_passed: int = 0
    total_gates: int = 6
    errors: List[Dict[str, Any]] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ProjectPlan(BaseModel):
    """Project plan"""
    project_name: str
    topic: str
    estimated_length_seconds: int
    scene_count: int
    estimated_budget: float
    required_agents: List[str]
    quality_thresholds: Dict[str, float]
