"""Advanced retry strategies with circuit breaker pattern"""

import time
import random
import logging
from typing import Callable, Any, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker pattern implementation"""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering half-open state")
            else:
                raise Exception(f"Circuit breaker is OPEN (will retry in {self._time_until_retry()}s)")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        logger.debug("Circuit breaker success, resetting to CLOSED")

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker OPEN after {self.failure_count} failures")

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset"""
        if not self.last_failure_time:
            return False

        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def _time_until_retry(self) -> int:
        """Time until circuit breaker will retry"""
        if not self.last_failure_time:
            return 0

        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return max(0, int(self.recovery_timeout - elapsed))


class AdvancedRetryManager:
    """Advanced retry manager with exponential backoff and jitter"""

    # Per-agent retry policies
    AGENT_POLICIES = {
        "Research Agent": {"max_attempts": 3, "backoff_base": 1, "jitter": True},
        "Fact Checker": {"max_attempts": 3, "backoff_base": 2, "jitter": True},
        "Script Analyzer": {"max_attempts": 2, "backoff_base": 1, "jitter": False},
        "Visual Alignment Agent": {"max_attempts": 2, "backoff_base": 1, "jitter": True},
        "Asset Finder": {"max_attempts": 2, "backoff_base": 2, "jitter": True},
        "AI Generator": {"max_attempts": 1, "backoff_base": 0, "jitter": False},
        "Timeline Builder": {"max_attempts": 1, "backoff_base": 0, "jitter": False},
        "Editor": {"max_attempts": 1, "backoff_base": 0, "jitter": False},
        "QA Reviewer": {"max_attempts": 1, "backoff_base": 0, "jitter": False},
        "Narration Agent": {"max_attempts": 2, "backoff_base": 2, "jitter": True},
    }

    DEFAULT_POLICY = {"max_attempts": 3, "backoff_base": 1, "jitter": True}

    def __init__(self, agent_name: str = "Generic"):
        self.agent_name = agent_name
        self.policy = self.AGENT_POLICIES.get(agent_name, self.DEFAULT_POLICY)
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

    def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with retry logic"""
        max_attempts = self.policy["max_attempts"]
        backoff_base = self.policy["backoff_base"]
        use_jitter = self.policy["jitter"]

        for attempt in range(1, max_attempts + 1):
            try:
                return self.circuit_breaker.call(func, *args, **kwargs)

            except Exception as e:
                if attempt == max_attempts:
                    logger.error(f"{self.agent_name}: All {max_attempts} attempts failed: {e}")
                    raise

                # Calculate backoff with jitter
                delay = self._calculate_backoff(attempt, backoff_base, use_jitter)
                logger.warning(f"{self.agent_name}: Attempt {attempt}/{max_attempts} failed, retrying in {delay}s: {e}")
                time.sleep(delay)

    def _calculate_backoff(
        self,
        attempt: int,
        base: int,
        use_jitter: bool
    ) -> float:
        """Calculate exponential backoff with optional jitter"""
        # Exponential backoff: base^attempt
        delay = base ** attempt

        if use_jitter:
            # Add random jitter: 0-25% variation
            jitter = random.uniform(0, delay * 0.25)
            delay += jitter

        return delay

    def get_retry_config(self) -> Dict[str, Any]:
        """Get retry configuration for this agent"""
        return {
            "agent_name": self.agent_name,
            "policy": self.policy,
            "circuit_breaker": {
                "state": self.circuit_breaker.state.value,
                "failure_count": self.circuit_breaker.failure_count,
                "failure_threshold": self.circuit_breaker.failure_threshold
            }
        }


class FallbackChain:
    """Execute functions with fallback chain"""

    def __init__(self, fallback_sequence: list[tuple[Callable, str]]):
        """
        Args:
            fallback_sequence: List of (function, description) tuples
        """
        self.fallback_sequence = fallback_sequence

    def execute(self) -> Any:
        """Execute functions in sequence, falling back on failure"""
        last_error = None

        for func, description in self.fallback_sequence:
            try:
                logger.info(f"Trying: {description}")
                result = func()
                logger.info(f"Success: {description}")
                return result

            except Exception as e:
                last_error = e
                logger.warning(f"Failed: {description} - {e}")
                continue

        # All fallbacks failed
        logger.error(f"All fallback options exhausted")
        raise last_error or Exception("No fallback options available")
