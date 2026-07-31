"""
Retry policy system with exponential backoff.

Implements the retry strategy from engineering specification:
- Standard: max 3 attempts, 5s → 10s → 20s backoff
- Per-agent customization available
"""

import time
import logging
from typing import Callable, Any, Optional, List
from dataclasses import dataclass
from .errors import DocumentaryError, ErrorCode, MaxRetriesExceededError


logger = logging.getLogger(__name__)


@dataclass
class RetryPolicy:
    """Retry policy configuration"""
    max_attempts: int = 3
    backoff_base_seconds: float = 5
    backoff_multiplier: float = 2.0
    retry_on_errors: List[str] = None
    no_retry_errors: List[str] = None

    def __post_init__(self):
        if self.retry_on_errors is None:
            self.retry_on_errors = ["E009", "E013"]  # Default retry errors
        if self.no_retry_errors is None:
            self.no_retry_errors = ["E002", "E010"]  # Never retry these


class RetryManager:
    """Manages retry logic for agents"""

    def __init__(self, policy: RetryPolicy, agent_name: str):
        self.policy = policy
        self.agent_name = agent_name
        self.attempt_count = 0
        self.attempt_history = []

    def should_retry(self, error: Exception) -> bool:
        """Determine if error is retryable"""
        if self.attempt_count >= self.policy.max_attempts:
            return False

        # Check if error has error code
        if isinstance(error, DocumentaryError):
            error_name = error.error_code.name
            if error_name in self.policy.no_retry_errors:
                return False
            if self.policy.retry_on_errors and error_name not in self.policy.retry_on_errors:
                return False

        return True

    def get_backoff_delay(self) -> float:
        """Calculate exponential backoff delay"""
        if self.attempt_count == 0:
            return 0  # First attempt is immediate
        return self.policy.backoff_base_seconds * (self.policy.backoff_multiplier ** (self.attempt_count - 1))

    def record_attempt(self, success: bool, error: Optional[Exception] = None, duration_ms: float = 0):
        """Record attempt result"""
        self.attempt_count += 1
        self.attempt_history.append({
            "attempt": self.attempt_count,
            "success": success,
            "error": str(error) if error else None,
            "error_code": error.error_code.name if isinstance(error, DocumentaryError) else None,
            "duration_ms": duration_ms,
        })

        logger.info(
            f"{self.agent_name} attempt {self.attempt_count}: {'SUCCESS' if success else 'FAILED'}",
            extra={
                "agent": self.agent_name,
                "attempt": self.attempt_count,
                "success": success,
                "duration_ms": duration_ms,
            }
        )

    def execute_with_retries(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_error = None

        while self.attempt_count < self.policy.max_attempts:
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                self.record_attempt(success=True, duration_ms=duration_ms)
                return result

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                self.record_attempt(success=False, error=e, duration_ms=duration_ms)
                last_error = e

                if not self.should_retry(e):
                    raise

                # Apply backoff
                backoff = self.get_backoff_delay()
                if backoff > 0:
                    logger.info(
                        f"{self.agent_name} retrying after {backoff}s...",
                        extra={"agent": self.agent_name, "backoff_seconds": backoff}
                    )
                    time.sleep(backoff)

        # Max retries exceeded
        raise MaxRetriesExceededError(self.agent_name, self.attempt_count)

    def get_history(self) -> List[dict]:
        """Get attempt history"""
        return self.attempt_history


# Standard retry policies
STANDARD_RETRY_POLICY = RetryPolicy(
    max_attempts=3,
    backoff_base_seconds=5,
    retry_on_errors=["E009", "E013"],
    no_retry_errors=["E002", "E010", "E016"],
)

ASSET_RETRY_POLICY = RetryPolicy(
    max_attempts=2,
    backoff_base_seconds=10,
    retry_on_errors=["E009"],
    no_retry_errors=["E001"],  # Insufficient coverage doesn't retry, goes to AI Gen
)

QA_RETRY_POLICY = RetryPolicy(
    max_attempts=1,  # QA failures don't retry, trigger Re-Edit
    backoff_base_seconds=0,
    retry_on_errors=[],
    no_retry_errors=["E004", "E005", "E006"],
)

RE_EDIT_RETRY_POLICY = RetryPolicy(
    max_attempts=3,
    backoff_base_seconds=5,
    retry_on_errors=["E009"],
    no_retry_errors=["E008"],  # Max retries error doesn't retry
)

# Get retry policy by agent name
AGENT_RETRY_POLICIES = {
    "Research Agent": STANDARD_RETRY_POLICY,
    "Fact Checker": STANDARD_RETRY_POLICY,
    "Script Analyzer": STANDARD_RETRY_POLICY,
    "Visual Alignment Agent": STANDARD_RETRY_POLICY,
    "Visual Planner": STANDARD_RETRY_POLICY,
    "Asset Finder": ASSET_RETRY_POLICY,
    "AI Generator": STANDARD_RETRY_POLICY,
    "Timeline Builder": STANDARD_RETRY_POLICY,
    "Editor": STANDARD_RETRY_POLICY,
    "QA Reviewer": QA_RETRY_POLICY,
    "Continuity & Story Flow Agent": STANDARD_RETRY_POLICY,
    "Audience Simulation Agent": STANDARD_RETRY_POLICY,
    "Re-Edit Agent": RE_EDIT_RETRY_POLICY,
    "Final Approval Agent": QA_RETRY_POLICY,
}


def get_retry_policy(agent_name: str) -> RetryPolicy:
    """Get retry policy for agent"""
    return AGENT_RETRY_POLICIES.get(agent_name, STANDARD_RETRY_POLICY)
