"""
Error codes and exception handling for Documentary Studio.

Every error has:
- Code (E001-E017)
- Severity (CRITICAL, WARNING)
- Recovery action
- Error message
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ErrorCode(Enum):
    """Error code taxonomy matching engineering spec"""

    E001 = "INSUFFICIENT_VISUAL_COVERAGE"
    E002 = "UNSUPPORTED_CLAIM"
    E003 = "LOW_VISUAL_TEACHING_SCORE"
    E004 = "LOW_QA_SCORE"
    E005 = "LOW_STORY_FLOW"
    E006 = "LOW_AUDIENCE_SATISFACTION"
    E007 = "NOT_BROADCAST_READY"
    E008 = "MAX_RETRIES_EXCEEDED"
    E009 = "TIMEOUT_EXCEEDED"
    E010 = "INVALID_INPUT_SCHEMA"
    E011 = "INVALID_OUTPUT_SCHEMA"
    E012 = "MISSING_REQUIRED_FIELD"
    E013 = "THRESHOLD_NOT_MET"
    E014 = "ASSET_NOT_FOUND"
    E015 = "SYNC_DRIFT_EXCEEDED"
    E016 = "PLACEHOLDER_DETECTED"
    E017 = "GENERIC_VISUAL_DETECTED"


class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ErrorDefinition:
    """Error definition with recovery information"""
    code: ErrorCode
    severity: ErrorSeverity
    message: str
    recovery_action: str
    retry_eligible: bool


class DocumentaryError(Exception):
    """Base exception for Documentary Studio"""

    def __init__(self, error_code: ErrorCode, message: str, context: Optional[dict] = None):
        self.error_code = error_code
        self.message = message
        self.context = context or {}
        super().__init__(f"{error_code.name}: {message}")


class InsufficientCoverageError(DocumentaryError):
    """E001: Visual coverage below 90%"""
    def __init__(self, coverage_pct: float):
        super().__init__(
            ErrorCode.E001,
            f"Visual coverage {coverage_pct:.1f}% below threshold 90%",
            {"coverage": coverage_pct}
        )


class UnsupportedClaimError(DocumentaryError):
    """E002: Claim confidence below 95%"""
    def __init__(self, claim: str, confidence: float):
        super().__init__(
            ErrorCode.E002,
            f"Claim not supported: confidence {confidence:.2f} < 0.95",
            {"claim": claim, "confidence": confidence}
        )


class LowTeachingScoreError(DocumentaryError):
    """E003: Visual teaching score below 90"""
    def __init__(self, score: float):
        super().__init__(
            ErrorCode.E003,
            f"Visual teaching score {score:.0f} below threshold 90",
            {"score": score}
        )


class LowQAScoreError(DocumentaryError):
    """E004: QA score below 90"""
    def __init__(self, score: float):
        super().__init__(
            ErrorCode.E004,
            f"QA score {score:.0f} below threshold 90",
            {"score": score}
        )


class LowStoryFlowError(DocumentaryError):
    """E005: Story flow score below 92"""
    def __init__(self, score: float):
        super().__init__(
            ErrorCode.E005,
            f"Story flow score {score:.0f} below threshold 92",
            {"score": score}
        )


class LowAudienceSatisfactionError(DocumentaryError):
    """E006: Audience satisfaction below 92"""
    def __init__(self, score: float):
        super().__init__(
            ErrorCode.E006,
            f"Audience satisfaction {score:.0f} below threshold 92",
            {"score": score}
        )


class NotBroadcastReadyError(DocumentaryError):
    """E007: Final approval rejected"""
    def __init__(self, reason: str):
        super().__init__(
            ErrorCode.E007,
            f"Not broadcast ready: {reason}",
            {"reason": reason}
        )


class MaxRetriesExceededError(DocumentaryError):
    """E008: Max retries exhausted"""
    def __init__(self, agent_name: str, attempts: int):
        super().__init__(
            ErrorCode.E008,
            f"{agent_name} failed after {attempts} attempts",
            {"agent": agent_name, "attempts": attempts}
        )


class TimeoutError(DocumentaryError):
    """E009: Execution timeout"""
    def __init__(self, agent_name: str, timeout_seconds: int):
        super().__init__(
            ErrorCode.E009,
            f"{agent_name} exceeded timeout {timeout_seconds}s",
            {"agent": agent_name, "timeout": timeout_seconds}
        )


class InvalidInputSchemaError(DocumentaryError):
    """E010: Input doesn't match schema"""
    def __init__(self, agent_name: str, validation_error: str):
        super().__init__(
            ErrorCode.E010,
            f"{agent_name} invalid input: {validation_error}",
            {"agent": agent_name, "validation_error": validation_error}
        )


class InvalidOutputSchemaError(DocumentaryError):
    """E011: Output doesn't match schema"""
    def __init__(self, agent_name: str, validation_error: str):
        super().__init__(
            ErrorCode.E011,
            f"{agent_name} invalid output: {validation_error}",
            {"agent": agent_name, "validation_error": validation_error}
        )


class MissingRequiredFieldError(DocumentaryError):
    """E012: Missing required field in output"""
    def __init__(self, agent_name: str, field_name: str):
        super().__init__(
            ErrorCode.E012,
            f"{agent_name} missing required field: {field_name}",
            {"agent": agent_name, "field": field_name}
        )


class ThresholdNotMetError(DocumentaryError):
    """E013: Confidence or metric threshold not met"""
    def __init__(self, metric: str, value: float, threshold: float):
        super().__init__(
            ErrorCode.E013,
            f"{metric} {value:.2f} below threshold {threshold:.2f}",
            {"metric": metric, "value": value, "threshold": threshold}
        )


class AssetNotFoundError(DocumentaryError):
    """E014: Asset not found"""
    def __init__(self, asset_id: str, source: str):
        super().__init__(
            ErrorCode.E014,
            f"Asset {asset_id} not found in {source}",
            {"asset_id": asset_id, "source": source}
        )


class SyncDriftError(DocumentaryError):
    """E015: Sync drift exceeds tolerance"""
    def __init__(self, drift_seconds: float, tolerance: float):
        super().__init__(
            ErrorCode.E015,
            f"Sync drift {drift_seconds:.2f}s exceeds tolerance {tolerance:.2f}s",
            {"drift": drift_seconds, "tolerance": tolerance}
        )


class PlaceholderDetectedError(DocumentaryError):
    """E016: Placeholder detected in output"""
    def __init__(self, timestamp: str, placeholder_type: str):
        super().__init__(
            ErrorCode.E016,
            f"Placeholder detected at {timestamp}: {placeholder_type}",
            {"timestamp": timestamp, "type": placeholder_type}
        )


class GenericVisualDetectedError(DocumentaryError):
    """E017: Generic visual detected"""
    def __init__(self, timestamp: str, description: str):
        super().__init__(
            ErrorCode.E017,
            f"Generic visual at {timestamp}: {description}",
            {"timestamp": timestamp, "description": description}
        )


# Error recovery mapping
ERROR_RECOVERY = {
    ErrorCode.E001: "Activate AI_GENERATOR or STOP",
    ErrorCode.E002: "STOP production, escalate to Producer",
    ErrorCode.E003: "Return to Visual Planner",
    ErrorCode.E004: "Trigger Re-Edit Agent (max 3 attempts)",
    ErrorCode.E005: "Return to Creative layer, Re-Edit",
    ErrorCode.E006: "Return to Re-Edit Agent",
    ErrorCode.E007: "STOP, return engineering report",
    ErrorCode.E008: "Escalate to Producer, STOP",
    ErrorCode.E009: "Retry with exponential backoff",
    ErrorCode.E010: "STOP, upstream agent failed",
    ErrorCode.E011: "Retry once, then STOP",
    ErrorCode.E012: "Retry agent execution",
    ErrorCode.E013: "Depends on agent, escalate or retry",
    ErrorCode.E014: "Substitute with fallback or AI generate",
    ErrorCode.E015: "Timeline Builder re-syncs, retry",
    ErrorCode.E016: "STOP, return REJECTED",
    ErrorCode.E017: "Return to Visual Planner",
}

# Error severity mapping
ERROR_SEVERITY = {
    ErrorCode.E001: ErrorSeverity.CRITICAL,
    ErrorCode.E002: ErrorSeverity.CRITICAL,
    ErrorCode.E003: ErrorSeverity.CRITICAL,
    ErrorCode.E004: ErrorSeverity.CRITICAL,
    ErrorCode.E005: ErrorSeverity.CRITICAL,
    ErrorCode.E006: ErrorSeverity.CRITICAL,
    ErrorCode.E007: ErrorSeverity.CRITICAL,
    ErrorCode.E008: ErrorSeverity.CRITICAL,
    ErrorCode.E009: ErrorSeverity.CRITICAL,
    ErrorCode.E010: ErrorSeverity.CRITICAL,
    ErrorCode.E011: ErrorSeverity.CRITICAL,
    ErrorCode.E012: ErrorSeverity.CRITICAL,
    ErrorCode.E013: ErrorSeverity.CRITICAL,
    ErrorCode.E014: ErrorSeverity.WARNING,
    ErrorCode.E015: ErrorSeverity.CRITICAL,
    ErrorCode.E016: ErrorSeverity.CRITICAL,
    ErrorCode.E017: ErrorSeverity.CRITICAL,
}


def get_error_recovery(error_code: ErrorCode) -> str:
    """Get recovery action for error code"""
    return ERROR_RECOVERY.get(error_code, "Unknown recovery action")


def get_error_severity(error_code: ErrorCode) -> ErrorSeverity:
    """Get severity level for error code"""
    return ERROR_SEVERITY.get(error_code, ErrorSeverity.CRITICAL)
