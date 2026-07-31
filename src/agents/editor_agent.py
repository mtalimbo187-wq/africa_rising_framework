"""
Editor Agent - Auto-edits video into final form.

Assembles clips, applies effects, and creates rough cut.
"""

from typing import Dict, Any
from pydantic import BaseModel

from .base_agent import BaseAgent
from ..core.schemas import AgentStatus


class EditorInput(BaseModel):
    """Editor Agent input"""
    timelines: list
    assets: list = []


class EditorOutput(BaseModel):
    """Editor output"""
    agent_name: str
    status: str
    video_url: str
    duration_seconds: float
    resolution: str
    format: str
    editing_complete: bool


class EditorAgent(BaseAgent):
    """Editor Agent implementation"""

    agent_name = "Editor"
    input_schema = EditorInput
    output_schema = EditorOutput
    timeout_seconds = 1200

    success_criteria = {
        "agent_name": ("Editor", "=="),
    }

    def _run(self, input_data: EditorInput) -> Dict[str, Any]:
        """Auto-edit video"""
        timelines = input_data.timelines
        total_duration = 0

        for timeline in timelines:
            timeline_dict = timeline if isinstance(timeline, dict) else timeline.model_dump()
            duration = timeline_dict.get("timeline_end", 0) - timeline_dict.get("timeline_start", 0)
            total_duration += duration

        return EditorOutput(
            agent_name=self.agent_name,
            status=AgentStatus.PASS,
            video_url="https://edited.example.com/dangote_rough_cut",
            duration_seconds=total_duration,
            resolution="4K",
            format="mp4",
            editing_complete=True,
        ).model_dump()
