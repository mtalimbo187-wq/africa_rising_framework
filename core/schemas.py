#!/usr/bin/env python3
"""
Data Contracts & JSON Schemas

Formal pydantic models for all inter-agent communication.
Ensures data integrity, type safety, and enables validation gates.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    QUERY = "query"
    RESPONSE = "response"
    STATUS = "status"
    ERROR = "error"
    VALIDATION = "validation"


class EntityType(str, Enum):
    PERSON = "person"
    PLACE = "place"
    ORGANIZATION = "organization"
    EVENT = "event"
    DATE = "date"
    CONCEPT = "concept"


class EmotionType(str, Enum):
    DRAMATIC = "dramatic"
    DOCUMENTARY = "documentary"
    INVESTIGATIVE = "investigative"
    EMPATHETIC = "empathetic"
    ENERGETIC = "energetic"
    SOMBER = "somber"
    EDUCATIONAL = "educational"


class LicenseType(str, Enum):
    CC0 = "CC0"
    CC_BY = "CC-BY-4.0"
    CC_BY_SA = "CC-BY-SA-4.0"
    CC_BY_NC = "CC-BY-NC-4.0"
    PROPRIETARY = "proprietary"
    ROYALTY_FREE = "royalty-free"
    PUBLIC_DOMAIN = "public-domain"


class VisualType(str, Enum):
    STOCK_FOOTAGE = "stock_footage"
    AI_GENERATED_VIDEO = "ai_generated_video"
    ARCHIVAL = "archival"
    INFOGRAPHIC = "infographic"
    MAP = "map"
    TIMELINE = "timeline"
    DIAGRAM = "diagram"
    INTERVIEW = "interview"


class TransitionType(str, Enum):
    FADE = "fade"
    CROSS_FADE = "cross_fade"
    WIPE_RIGHT = "wipe_right"
    WIPE_LEFT = "wipe_left"
    CUT = "cut"
    DISSOLVE = "dissolve"


class AgentMessage(BaseModel):
    """Inter-agent communication contract"""
    sender: str = Field(..., description="Agent name sending message")
    recipient: str = Field(..., description="Agent name receiving message")
    timestamp: datetime = Field(default_factory=datetime.now)
    message_type: MessageType
    payload: Dict[str, Any] = Field(default_factory=dict)
    request_id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    priority: int = Field(default=0, ge=0, le=10)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Entity(BaseModel):
    """Extracted entity with metadata"""
    text: str
    entity_type: EntityType
    confidence: float = Field(default=1.0, ge=0, le=1)
    start_char: int
    end_char: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Shot(BaseModel):
    """Core unit: one scene/section of video"""
    shot_id: str
    shot_number: int
    text: str = Field(description="Narration or scene description")
    duration_seconds: float = Field(gt=0)
    emotions: List[EmotionType] = Field(default_factory=list)
    visual_type: VisualType = Field(default=VisualType.STOCK_FOOTAGE)
    entities: List[Entity] = Field(default_factory=list)
    map_locations: List[str] = Field(default_factory=list)
    timeline_events: List[Dict[str, Any]] = Field(default_factory=list)
    color_grade: str = Field(default="documentary")
    min_visual_duration: float = Field(default=2.0)
    max_visual_duration: float = Field(default=8.0)
    confidence: float = Field(default=1.0, ge=0, le=1)

    @validator('duration_seconds')
    def validate_duration(cls, v):
        if v <= 0:
            raise ValueError("Duration must be positive")
        return v


class Asset(BaseModel):
    """Downloaded/generated media file"""
    asset_id: str
    source: str = Field(description="pexels, archive.org, nasa, loc, ai_generated, etc")
    url: str
    file_path: Optional[str] = None
    license: LicenseType
    attribution_required: bool = False
    credited_to: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[float] = None
    download_status: str = Field(default="pending")
    download_timestamp: Optional[datetime] = None
    cost_usd: float = Field(default=0.0)
    search_query: str = Field(description="What was searched to find this")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Timeline(BaseModel):
    """Edited clip with timing and effects"""
    clip_id: str
    shot_id: str
    start_time_seconds: float = Field(ge=0)
    end_time_seconds: float = Field(gt=0)
    asset_ref: str = Field(description="Asset ID used for this clip")
    transition_type: TransitionType = Field(default=TransitionType.CROSS_FADE)
    transition_duration: float = Field(default=0.5, ge=0)
    overlay_text: Optional[str] = None
    overlay_position: str = Field(default="lower_third")
    subtitle_text: Optional[str] = None
    subtitle_region: str = Field(default="bottom")
    audio_mix_level: float = Field(default=1.0, ge=0, le=1)
    animation_effect: Optional[str] = None
    animation_duration: float = Field(default=3.0)

    @validator('end_time_seconds')
    def validate_time_order(cls, v, values):
        if 'start_time_seconds' in values and v <= values['start_time_seconds']:
            raise ValueError("End time must be after start time")
        return v


class QualityScore(BaseModel):
    """Final quality assessment"""
    overall_score: float = Field(ge=0, le=100)
    claims_verified: bool
    claims_verified_count: int = 0
    unsupported_claims: List[str] = Field(default_factory=list)
    visuals_complete: bool
    missing_visuals: List[int] = Field(default_factory=list)
    audio_sync_quality: float = Field(ge=0, le=100, default=0)
    subtitle_quality: float = Field(ge=0, le=100, default=0)
    pacing_issues: List[Dict[str, Any]] = Field(default_factory=list)
    resolution_issues: List[str] = Field(default_factory=list)
    duplicate_shots: List[tuple] = Field(default_factory=list)
    clipping_detected: bool = False
    clipping_timestamps: List[float] = Field(default_factory=list)
    subtitle_drift: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    approval_status: str = Field(default="pending")


class AgentResult(BaseModel):
    """Standard agent execution result"""
    agent_name: str
    status: str = Field(description="COMPLETED, FAILED, PARTIAL")
    output: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time_seconds: float = 0.0
    cost_usd: float = 0.0
    prompt_version: str = "1.0"
    model_used: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ProjectMetadata(BaseModel):
    """Complete project context"""
    project_name: str
    project_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    script_file: str
    total_shots: int = 0
    estimated_duration_seconds: float = 0.0
    estimated_cost_usd: float = 0.0
    actual_cost_usd: float = 0.0
    status: str = Field(default="initialized")
    agents_used: List[str] = Field(default_factory=list)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class WorkflowState(BaseModel):
    """Complete workflow state for resumability"""
    project_metadata: ProjectMetadata
    shots: List[Shot] = Field(default_factory=list)
    assets: List[Asset] = Field(default_factory=list)
    timeline: List[Timeline] = Field(default_factory=list)
    quality_score: Optional[QualityScore] = None
    agent_results: Dict[str, AgentResult] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
