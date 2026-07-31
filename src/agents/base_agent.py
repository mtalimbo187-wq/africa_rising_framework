"""
Base agent class implementing contract enforcement.

Every agent MUST:
1. Validate input against schema
2. Execute business logic
3. Validate output against schema
4. Check success criteria
5. Log everything
"""

import time
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
from pydantic import BaseModel, ValidationError

from ..core.schemas import Message, MessageType, MessageMetadata, AgentStatus
from ..core.errors import (
    DocumentaryError,
    InvalidInputSchemaError,
    InvalidOutputSchemaError,
    MissingRequiredFieldError,
    ThresholdNotMetError,
)
from ..core.retry import RetryManager, get_retry_policy


logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents"""

    # Override in subclasses
    agent_name: str = "Base Agent"
    input_schema: Type[BaseModel] = None
    output_schema: Type[BaseModel] = None
    success_criteria: Dict[str, tuple] = {}  # {"metric": (threshold, operator)}
    timeout_seconds: int = 300

    def __init__(self):
        self.retry_manager = RetryManager(get_retry_policy(self.agent_name), self.agent_name)

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent with full contract enforcement"""
        start_time = time.time()

        try:
            # Step 1: Validate input
            validated_input = self._validate_input(input_data)

            # Step 2: Execute with retry
            result = self.retry_manager.execute_with_retries(
                self._run,
                validated_input
            )

            # Step 3: Validate output
            validated_output = self._validate_output(result)

            # Step 4: Check success criteria
            self._check_success_criteria(validated_output)

            # Step 5: Log success
            duration_ms = (time.time() - start_time) * 1000
            self._log_execution(
                status="SUCCESS",
                duration_ms=duration_ms,
                output=validated_output
            )

            return validated_output

        except DocumentaryError as e:
            duration_ms = (time.time() - start_time) * 1000
            self._log_execution(
                status="FAILED",
                duration_ms=duration_ms,
                error=e
            )
            raise

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self._log_execution(
                status="FAILED",
                duration_ms=duration_ms,
                error=e
            )
            raise

    def _validate_input(self, input_data: Dict[str, Any]) -> BaseModel:
        """Validate input against schema"""
        if self.input_schema is None:
            return input_data

        try:
            return self.input_schema(**input_data)
        except ValidationError as e:
            raise InvalidInputSchemaError(self.agent_name, str(e))

    def _validate_output(self, output_data: Any) -> BaseModel:
        """Validate output against schema"""
        if self.output_schema is None:
            return output_data

        if isinstance(output_data, self.output_schema):
            return output_data

        # Convert dict to schema
        try:
            validated = self.output_schema(**output_data)
            return validated
        except ValidationError as e:
            raise InvalidOutputSchemaError(self.agent_name, str(e))

    def _check_success_criteria(self, output: BaseModel):
        """Check if output meets success criteria"""
        for metric, criteria in self.success_criteria.items():
            if not hasattr(output, metric):
                raise MissingRequiredFieldError(self.agent_name, metric)

            value = getattr(output, metric)

            # Handle tuple format: (threshold, operator)
            if isinstance(criteria, tuple):
                threshold, operator = criteria

                # Check threshold
                if isinstance(threshold, (int, float)):
                    if operator == ">=" and value < threshold:
                        raise ThresholdNotMetError(metric, value, threshold)
                    elif operator == "<=" and value > threshold:
                        raise ThresholdNotMetError(metric, value, threshold)
                    elif operator == ">" and value <= threshold:
                        raise ThresholdNotMetError(metric, value, threshold)
                    elif operator == "<" and value >= threshold:
                        raise ThresholdNotMetError(metric, value, threshold)
                elif isinstance(threshold, str):
                    # String comparison (e.g., status == "PASS")
                    if value != threshold:
                        raise ThresholdNotMetError(metric, value, threshold)

    @abstractmethod
    def _run(self, input_data: BaseModel) -> Any:
        """Execute agent business logic - must be implemented by subclass"""
        pass

    def _log_execution(
        self,
        status: str,
        duration_ms: float,
        output: Optional[BaseModel] = None,
        error: Optional[Exception] = None
    ):
        """Log execution details"""
        log_entry = {
            "timestamp": time.time(),
            "agent_name": self.agent_name,
            "status": status,
            "duration_ms": duration_ms,
            "attempt": self.retry_manager.attempt_count,
            "retry_history": self.retry_manager.get_history(),
        }

        if output:
            if isinstance(output, BaseModel):
                log_entry["output"] = output.model_dump()
            elif isinstance(output, dict):
                log_entry["output"] = output
            else:
                log_entry["output"] = str(output)

        if error:
            log_entry["error"] = str(error)
            if isinstance(error, DocumentaryError):
                log_entry["error_code"] = error.error_code.name

        logger.info(json.dumps(log_entry))

    def create_message(self, to_agent: str, payload: Dict[str, Any]) -> Message:
        """Create outgoing message"""
        return Message(
            from_agent=self.agent_name,
            to_agent=to_agent,
            message_type=MessageType.RESULT,
            payload=payload,
            metadata=MessageMetadata(attempt=self.retry_manager.attempt_count)
        )


class DummyAgent(BaseAgent):
    """Placeholder agent for testing"""

    agent_name = "Dummy Agent"

    def _run(self, input_data: BaseModel) -> Dict[str, Any]:
        """Dummy implementation"""
        return {"status": "PASS", "message": "Dummy execution"}
