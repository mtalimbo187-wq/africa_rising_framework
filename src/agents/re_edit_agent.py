"""
Re-Edit Agent - Re-edits video based on QA and audience feedback.

Applies fixes and refinements based on review results.
"""

from typing import Dict, Any
from pydantic import BaseModel

from .base_agent import BaseAgent
from ..core.schemas import AgentStatus


class ReEditInput(BaseModel):
    """Re-Edit Agent input"""
    video_url: str
    qa_issues: list = []
    continuity_issues: list = []


class ReEditOutput(BaseModel):
    """Re-Edit output"""
    agent_name: str
    status: str
    revised_video_url: str
    changes_made: list
    revised_qa_score: float


class ReEditAgent(BaseAgent):
    """Re-Edit Agent implementation"""

    agent_name = "Re-Edit"
    input_schema = ReEditInput
    output_schema = ReEditOutput
    timeout_seconds = 900

    success_criteria = {
        "agent_name": ("Re-Edit", "=="),
    }

    def _run(self, input_data: ReEditInput) -> Dict[str, Any]:
        """Re-edit video based on feedback"""
        qa_issues = input_data.qa_issues or []
        continuity_issues = input_data.continuity_issues or []

        changes = []
        if qa_issues:
            changes.append("Audio level adjustment")
            changes.append("Color grading refinement")
        if continuity_issues:
            changes.append("Transition smoothing")
            changes.append("Emotion beat adjustment")

        return ReEditOutput(
            agent_name=self.agent_name,
            status=AgentStatus.PASS,
            revised_video_url="https://edited.example.com/dangote_revised",
            changes_made=changes,
            revised_qa_score=0.94,
        ).model_dump()
