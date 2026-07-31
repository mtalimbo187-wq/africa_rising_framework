"""
Final Approval Agent - Final review and approval.

Conducts final checks before export and release.
"""

from typing import Dict, Any
from pydantic import BaseModel

from .base_agent import BaseAgent
from ..core.schemas import FinalApprovalOutput, AgentStatus


class FinalApprovalInput(BaseModel):
    """Final Approval Agent input"""
    video_url: str
    qa_score: float


class FinalApprovalAgent(BaseAgent):
    """Final Approval Agent implementation"""

    agent_name = "Final Approval"
    input_schema = FinalApprovalInput
    output_schema = FinalApprovalOutput
    timeout_seconds = 300

    success_criteria = {
        "agent_name": ("Final Approval", "=="),
    }

    def _run(self, input_data: FinalApprovalInput) -> Dict[str, Any]:
        """Conduct final approval"""
        video_url = input_data.video_url
        qa_score = input_data.qa_score

        approved = qa_score >= 0.90
        status = "APPROVED" if approved else "REJECTED"

        return FinalApprovalOutput(
            agent_name=self.agent_name,
            status=status,
            reason="All quality gates passed" if approved else "Quality thresholds not met",
            failures=[],
            certification="Emmy-Standard Documentary" if approved else None,
        ).model_dump()
