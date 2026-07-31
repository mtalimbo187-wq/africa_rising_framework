"""
Producer Agent - Orchestrates all agents and enforces quality gates.

The Producer:
- Routes messages between agents
- Enforces state machine transitions
- Validates quality gates
- Detects and handles failures
- Coordinates retries
- Generates reports
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from .core.schemas import (
    ProductionState,
    ProductionStatus,
    ProjectPlan,
    Message,
    MessageType,
)
from .core.errors import (
    DocumentaryError,
    ErrorCode,
    get_error_recovery,
    get_error_severity,
)


logger = logging.getLogger(__name__)


class Producer:
    """Producer Agent - Orchestrates documentary production"""

    def __init__(self):
        self.state = ProductionState.INIT
        self.agents = {}
        self.gates_passed = 0
        self.total_gates = 6
        self.errors = []
        self.execution_history = []
        self.current_agent = None
        self.max_re_edit_attempts = 3
        self.re_edit_attempts = 0

        # Quality gate thresholds
        self.quality_gates = {
            "fact_verification": {"threshold": 0.95, "metric": "confidence_average"},
            "visual_teaching": {"threshold": 0.90, "metric": "overall_teaching_score"},
            "asset_coverage": {"threshold": 0.90, "metric": "coverage_percentage"},
            "qa_score": {"threshold": 0.90, "metric": "overall_score"},
            "story_flow": {"threshold": 0.92, "metric": "overall_score"},
            "audience_satisfaction": {"threshold": 0.92, "metric": "overall_satisfaction"},
        }

    def register_agent(self, agent_name: str, agent_instance):
        """Register an agent"""
        self.agents[agent_name] = agent_instance
        logger.info(f"Agent registered: {agent_name}")

    def get_status(self) -> ProductionStatus:
        """Get current production status"""
        progress = (self.gates_passed / self.total_gates) * 100
        return ProductionStatus(
            state=self.state,
            current_agent=self.current_agent,
            progress_percent=progress,
            gates_passed=self.gates_passed,
            total_gates=self.total_gates,
            errors=self.errors,
        )

    def execute_production(self, project_plan: ProjectPlan) -> Dict[str, Any]:
        """Execute full production workflow"""
        logger.info(f"Starting production: {project_plan.project_name}")

        try:
            # Phase 1: Research
            self.state = ProductionState.RESEARCH
            facts = self._execute_agent("Research Agent", {"script": project_plan.topic})

            # Phase 2: Fact Check (GATE 1)
            self.state = ProductionState.FACT_CHECK
            verified = self._execute_agent(
                "Fact Checker",
                {"facts": facts.get("facts", [])},
                gate_name="fact_verification"
            )
            self.gates_passed += 1

            # Phase 3: Script Analysis
            self.state = ProductionState.SCRIPT_ANALYSIS
            scenes = self._execute_agent(
                "Script Analyzer",
                {"script": project_plan.topic, "verified_facts": verified.get("verified_facts", [])}
            )

            # Phase 4: Visual Alignment (GATE 2)
            self.state = ProductionState.VISUAL_ALIGNMENT
            aligned = self._execute_agent(
                "Visual Alignment Agent",
                {"scenes": scenes.get("scenes", [])},
                gate_name="visual_teaching"
            )
            self.gates_passed += 1

            # Phase 5: Visual Planning
            self.state = ProductionState.VISUAL_PLANNING
            visual_plan = self._execute_agent(
                "Visual Planner",
                {"scenes": scenes.get("scenes", [])}
            )

            # Phase 6: Asset Finder (GATE 3)
            self.state = ProductionState.ASSET_SEARCH
            assets = self._execute_agent(
                "Asset Finder",
                {"visual_plan": visual_plan.get("visual_plan", [])},
                gate_name="asset_coverage"
            )
            self.gates_passed += 1

            # Phase 7: AI Generation (conditional)
            coverage = assets.get("coverage_percentage", 0)
            if coverage < 0.90:
                self.state = ProductionState.AI_GENERATION
                assets = self._execute_agent(
                    "AI Generator",
                    {"missing_visuals": assets.get("missing_visuals", [])}
                )

            # Phase 8: Timeline Building
            self.state = ProductionState.TIMELINE_BUILD
            timeline = self._execute_agent(
                "Timeline Builder",
                {
                    "scenes": scenes.get("scenes", []),
                    "assets": assets.get("assets", [])
                }
            )

            # Phase 9: Production (Editor)
            self.state = ProductionState.PRODUCTION
            video = self._execute_agent(
                "Editor",
                {
                    "timeline": timeline.get("timeline", []),
                    "assets": assets.get("assets", [])
                }
            )

            # Phase 10: QA Review (GATE 4)
            self.state = ProductionState.QA_REVIEW
            qa_report = self._execute_agent(
                "QA Reviewer",
                {"video_file": video.get("video_file")},
                gate_name="qa_score"
            )
            self.gates_passed += 1

            # Phase 11: Continuity Check (GATE 5)
            self.state = ProductionState.CONTINUITY_CHECK
            continuity = self._execute_agent(
                "Continuity & Story Flow Agent",
                {"video_file": video.get("video_file")},
                gate_name="story_flow"
            )
            self.gates_passed += 1

            # Phase 12: Audience Simulation (GATE 6)
            self.state = ProductionState.AUDIENCE_SIM
            audience = self._execute_agent(
                "Audience Simulation Agent",
                {"video_file": video.get("video_file")},
                gate_name="audience_satisfaction"
            )
            self.gates_passed += 1

            # Phase 13: Final Approval
            self.state = ProductionState.FINAL_APPROVAL
            approval = self._execute_agent(
                "Final Approval Agent",
                {
                    "video_file": video.get("video_file"),
                    "all_reports": {
                        "qa": qa_report,
                        "continuity": continuity,
                        "audience": audience
                    }
                }
            )

            if approval.get("status") == "REJECTED":
                raise DocumentaryError(
                    ErrorCode.E007,
                    approval.get("reason", "Not broadcast ready")
                )

            # Phase 14: Export
            self.state = ProductionState.EXPORT
            logger.info("Production complete - exporting final video")

            return {
                "status": "SUCCESS",
                "state": self.state.value,
                "video_file": video.get("video_file"),
                "gates_passed": self.gates_passed,
                "total_gates": self.total_gates,
                "approval": approval,
            }

        except DocumentaryError as e:
            return self._handle_failure(e)
        except Exception as e:
            return self._handle_failure(
                DocumentaryError(ErrorCode.E008, str(e))
            )

    def _execute_agent(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        gate_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute an agent and validate output"""
        self.current_agent = agent_name

        if agent_name not in self.agents:
            raise DocumentaryError(
                ErrorCode.E010,
                f"Agent not registered: {agent_name}"
            )

        agent = self.agents[agent_name]

        try:
            logger.info(f"Executing: {agent_name}")
            result = agent.execute(input_data)

            # Check gate if applicable
            if gate_name and gate_name in self.quality_gates:
                self._check_gate(gate_name, result)

            self.execution_history.append({
                "timestamp": datetime.utcnow().isoformat(),
                "agent": agent_name,
                "status": "SUCCESS",
            })

            return result

        except DocumentaryError as e:
            self.errors.append({
                "timestamp": datetime.utcnow().isoformat(),
                "agent": agent_name,
                "error_code": e.error_code.name,
                "message": e.message,
            })
            raise

    def _check_gate(self, gate_name: str, result: Dict[str, Any]):
        """Check quality gate"""
        gate = self.quality_gates[gate_name]
        metric = gate["metric"]
        threshold = gate["threshold"]

        if metric not in result:
            raise DocumentaryError(
                ErrorCode.E012,
                f"Missing metric {metric} for gate {gate_name}"
            )

        value = result[metric]

        if isinstance(value, (int, float)) and value < threshold:
            error_mapping = {
                "fact_verification": ErrorCode.E002,
                "visual_teaching": ErrorCode.E003,
                "asset_coverage": ErrorCode.E001,
                "qa_score": ErrorCode.E004,
                "story_flow": ErrorCode.E005,
                "audience_satisfaction": ErrorCode.E006,
            }
            error_code = error_mapping.get(gate_name, ErrorCode.E013)
            raise DocumentaryError(
                error_code,
                f"Gate {gate_name} failed: {metric}={value:.2f} < {threshold:.2f}"
            )

        logger.info(f"Gate '{gate_name}' PASSED: {metric}={value:.2f}")

    def _handle_failure(self, error: DocumentaryError) -> Dict[str, Any]:
        """Handle production failure"""
        self.state = ProductionState.STOPPED

        recovery = get_error_recovery(error.error_code)
        severity = get_error_severity(error.error_code)

        report = {
            "status": "FAILED",
            "state": self.state.value,
            "error_code": error.error_code.name,
            "error_message": error.message,
            "severity": severity.value,
            "recovery_action": recovery,
            "gates_passed": self.gates_passed,
            "total_gates": self.total_gates,
            "context": error.context,
        }

        logger.error(json.dumps(report))
        return report

    def generate_report(self) -> Dict[str, Any]:
        """Generate production report"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": self.get_status().dict(),
            "execution_history": self.execution_history,
            "errors": self.errors,
            "gates_passed": self.gates_passed,
            "total_gates": self.total_gates,
        }
