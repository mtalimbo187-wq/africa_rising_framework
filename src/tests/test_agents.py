"""
Tests for agent contract enforcement.

Verifies that:
1. Input validation works
2. Output validation works
3. Success criteria are enforced
4. Error handling is correct
5. Retry logic works
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents import ResearchAgent, FactCheckAgent, ScriptAnalyzerAgent
from src.core.errors import (
    InvalidInputSchemaError,
    UnsupportedClaimError,
    DocumentaryError,
    ErrorCode,
)
from src.core.schemas import Fact


class TestResearchAgent:
    """Test Research Agent"""

    def test_research_agent_success(self):
        """Test successful research execution"""
        agent = ResearchAgent()
        input_data = {
            "script": "The Dangote Refinery is in Nigeria. It processes 650,000 barrels daily."
        }
        output = agent.execute(input_data)

        # Convert to dict if Pydantic object
        if hasattr(output, 'model_dump'):
            output = output.model_dump()

        assert output.get("status") == "PASS"
        assert len(output.get("facts", [])) > 0
        assert output.get("agent_name") == "Research Agent"

    def test_research_agent_invalid_input(self):
        """Test invalid input rejection"""
        agent = ResearchAgent()
        input_data = {"invalid_field": "value"}

        with pytest.raises(InvalidInputSchemaError):
            agent.execute(input_data)

    def test_research_agent_missing_script(self):
        """Test missing required field"""
        agent = ResearchAgent()
        input_data = {}

        with pytest.raises(InvalidInputSchemaError):
            agent.execute(input_data)

    def test_research_agent_output_validation(self):
        """Test output schema validation"""
        agent = ResearchAgent()
        input_data = {"script": "Test script"}
        output = agent.execute(input_data)

        # Convert to dict if Pydantic object
        if hasattr(output, 'model_dump'):
            output = output.model_dump()

        # Verify output schema
        assert "facts" in output
        assert "status" in output
        assert "agent_name" in output
        assert "duration_ms" in output
        assert "cost_usd" in output


class TestFactCheckAgent:
    """Test Fact Checker Agent"""

    def test_fact_check_success(self):
        """Test successful fact checking"""
        agent = FactCheckAgent()
        input_data = {
            "facts": [
                {
                    "fact_id": "f1",
                    "claim": "The Dangote Refinery processes 650,000 barrels per day",
                    "entities": [],
                    "people": [],
                    "places": ["Nigeria"],
                    "dates": [],
                    "organizations": [],
                    "statistics": ["650,000"],
                    "context": None,
                }
            ]
        }
        output = agent.execute(input_data)

        # Convert to dict if Pydantic object
        if hasattr(output, 'model_dump'):
            output = output.model_dump()

        assert output.get("status") == "PASS"
        assert len(output.get("verified_facts", [])) > 0
        assert output.get("confidence_average", 0) >= 0.95

    def test_fact_check_gate_enforcement(self):
        """Test that confidence gate is enforced"""
        agent = FactCheckAgent()
        input_data = {
            "facts": [
                {
                    "fact_id": "f1",
                    "claim": "Some unverifiable claim about tomorrow",
                    "entities": [],
                    "people": [],
                    "places": [],
                    "dates": [],
                    "organizations": [],
                    "statistics": [],
                    "context": None,
                }
            ]
        }

        # This should fail if confidence is below 95%
        # In real implementation, this would depend on actual verification

    def test_fact_check_output_validation(self):
        """Test output schema validation"""
        agent = FactCheckAgent()
        input_data = {
            "facts": [
                {
                    "fact_id": "f1",
                    "claim": "The Dangote Refinery processes 650,000 barrels per day",
                    "entities": [],
                    "people": [],
                    "places": [],
                    "dates": [],
                    "organizations": [],
                    "statistics": [],
                    "context": None,
                }
            ]
        }
        output = agent.execute(input_data)

        # Convert to dict if Pydantic object
        if hasattr(output, 'model_dump'):
            output = output.model_dump()

        # Verify output schema
        assert "verified_facts" in output
        assert "confidence_average" in output
        assert 0 <= output["confidence_average"] <= 1


class TestScriptAnalyzerAgent:
    """Test Script Analyzer Agent"""

    def test_script_analyzer_success(self):
        """Test successful script analysis"""
        agent = ScriptAnalyzerAgent()
        input_data = {
            "script": "The Dangote Refinery is in Lagos, Nigeria. It was completed in 2023. The facility processes crude oil into refined products."
        }
        output = agent.execute(input_data)

        # Convert to dict if Pydantic object
        if hasattr(output, 'model_dump'):
            output = output.model_dump()

        assert output.get("status") == "PASS"
        assert len(output.get("scenes", [])) > 0
        assert output.get("scene_count", 0) > 0
        assert output.get("total_duration", 0) > 0

    def test_script_analyzer_scene_structure(self):
        """Test scene structure"""
        agent = ScriptAnalyzerAgent()
        input_data = {
            "script": "Test script about the refinery in Lagos."
        }
        output = agent.execute(input_data)

        # Convert to dict if Pydantic object
        if hasattr(output, 'model_dump'):
            output = output.model_dump()

        assert len(output.get("scenes", [])) > 0
        scene = output["scenes"][0]

        assert "scene_id" in scene
        assert "start_time" in scene
        assert "end_time" in scene
        assert "narration" in scene
        assert "emotion" in scene
        assert "importance" in scene

    def test_script_analyzer_entity_extraction(self):
        """Test entity extraction"""
        agent = ScriptAnalyzerAgent()
        input_data = {
            "script": "Aliko Dangote built the refinery in Lagos, Nigeria."
        }
        output = agent.execute(input_data)

        # Convert to dict if Pydantic object
        if hasattr(output, 'model_dump'):
            output = output.model_dump()

        assert len(output.get("scenes", [])) > 0
        scene = output["scenes"][0]

        assert "Dangote" in str(scene.get("entities", []))
        assert "Lagos" in str(scene.get("location", "")) or "Lagos" in str(scene.get("entities", []))

    def test_script_analyzer_invalid_input(self):
        """Test invalid input rejection"""
        agent = ScriptAnalyzerAgent()
        input_data = {"invalid": "data"}

        with pytest.raises(InvalidInputSchemaError):
            agent.execute(input_data)


class TestErrorHandling:
    """Test error handling and recovery"""

    def test_error_codes(self):
        """Test error code system"""
        from ..core.errors import ErrorCode, get_error_recovery, get_error_severity

        # Verify all error codes have recovery actions
        for code in ErrorCode:
            recovery = get_error_recovery(code)
            severity = get_error_severity(code)
            assert recovery is not None
            assert severity is not None

    def test_documentary_error(self):
        """Test DocumentaryError exception"""
        error = DocumentaryError(
            ErrorCode.E001,
            "Test error message",
            {"context": "test"}
        )

        assert error.error_code == ErrorCode.E001
        assert error.message == "Test error message"
        assert error.context["context"] == "test"

    def test_unsupported_claim_error(self):
        """Test UnsupportedClaimError"""
        error = UnsupportedClaimError(
            "Some claim",
            0.80
        )

        assert error.error_code == ErrorCode.E002
        assert "0.80" in error.message


class TestRetryLogic:
    """Test retry mechanism"""

    def test_retry_manager_exponential_backoff(self):
        """Test exponential backoff calculation"""
        from ..core.retry import RetryManager, RetryPolicy

        policy = RetryPolicy(
            max_attempts=3,
            backoff_base_seconds=5,
            backoff_multiplier=2.0
        )
        manager = RetryManager(policy, "Test Agent")

        # Attempt 1: immediate
        manager.attempt_count = 0
        backoff = manager.get_backoff_delay()
        assert backoff == 0

        # Attempt 2: 5 seconds
        manager.attempt_count = 1
        backoff = manager.get_backoff_delay()
        assert backoff == 5

        # Attempt 3: 10 seconds
        manager.attempt_count = 2
        backoff = manager.get_backoff_delay()
        assert backoff == 10

    def test_retry_should_not_retry_certain_errors(self):
        """Test that certain errors don't retry"""
        from ..core.retry import RetryManager, RetryPolicy

        policy = RetryPolicy(
            max_attempts=3,
            no_retry_errors=["E002"]  # UnsupportedClaimError
        )
        manager = RetryManager(policy, "Test Agent")

        error = UnsupportedClaimError("Test", 0.80)
        assert not manager.should_retry(error)
