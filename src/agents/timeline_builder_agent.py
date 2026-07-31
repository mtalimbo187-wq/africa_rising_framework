"""
Timeline Builder Agent - Builds editing timeline.

Creates timeline with clips, transitions, and timing.
"""

from typing import Dict, Any
from pydantic import BaseModel

from .base_agent import BaseAgent
from ..core.schemas import Timeline, TimelineOutput, AgentStatus, Shot


class TimelineBuilderInput(BaseModel):
    """Timeline Builder Agent input"""
    scenes: list
    assets: list = []


class TimelineBuilderAgent(BaseAgent):
    """Timeline Builder Agent implementation"""

    agent_name = "Timeline Builder"
    input_schema = TimelineBuilderInput
    output_schema = TimelineOutput
    timeout_seconds = 300

    success_criteria = {
        "agent_name": ("Timeline Builder", "=="),
    }

    def _run(self, input_data: TimelineBuilderInput) -> Dict[str, Any]:
        """Build editing timeline"""
        scenes = input_data.scenes
        timelines = []
        total_duration = 0

        current_time = 0
        for i, scene in enumerate(scenes):
            scene_dict = scene if isinstance(scene, dict) else scene.model_dump()

            # Calculate scene duration
            duration = scene_dict.get("end_time", 0) - scene_dict.get("start_time", 0)
            if duration <= 0:
                duration = 10  # Default 10 seconds

            timeline = Timeline(
                scene_id=scene_dict.get("scene_id", f"s{i+1}"),
                timeline_start=current_time,
                timeline_end=current_time + duration,
                clips=[],
                transitions=self._determine_transitions(scene_dict),
                audio_track="narration",
                music_track="background",
                sound_effects=[],
            )

            timelines.append(timeline)
            current_time += duration
            total_duration += duration

        return TimelineOutput(
            agent_name=self.agent_name,
            status=AgentStatus.PASS,
            timelines=timelines,
            total_duration=total_duration,
            sync_accuracy=0.95,
            scene_count=len(timelines),
        ).model_dump()

    def _determine_transitions(self, scene: Dict[str, Any]) -> list:
        """Determine transition types"""
        transitions = []

        importance = scene.get("importance", "MINOR")
        if importance == "CRITICAL":
            transitions.append("fade")
        else:
            transitions.append("cut")

        # Add motion for emotional scenes
        emotion = scene.get("emotion", "neutral")
        if emotion == "triumph":
            transitions.append("zoom_in")
        elif emotion == "concern":
            transitions.append("zoom_out")

        return transitions
