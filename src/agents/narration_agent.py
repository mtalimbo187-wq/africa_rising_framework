"""
Narration Agent - Generates/records narration.

Creates voice-over audio for documentary.
"""

from typing import Dict, Any
from pydantic import BaseModel

from .base_agent import BaseAgent
from ..core.schemas import AgentStatus


class NarrationInput(BaseModel):
    """Narration Agent input"""
    scenes: list
    voice_talent: str = "neutral_narrator"


class NarrationOutput(BaseModel):
    """Narration output"""
    agent_name: str
    status: str
    narration_files: list
    total_duration: float
    audio_format: str


class NarrationAgent(BaseAgent):
    """Narration Agent implementation"""

    agent_name = "Narration"
    input_schema = NarrationInput
    output_schema = NarrationOutput
    timeout_seconds = 600

    success_criteria = {
        "agent_name": ("Narration", "=="),
    }

    def _run(self, input_data: NarrationInput) -> Dict[str, Any]:
        """Generate narration"""
        scenes = input_data.scenes
        narration_files = []
        total_duration = 0

        for i, scene in enumerate(scenes):
            scene_dict = scene if isinstance(scene, dict) else scene.model_dump()
            narration_text = scene_dict.get("narration", "")

            if narration_text:
                # Estimate duration (approx 3 words per second)
                duration = len(narration_text.split()) / 3
                total_duration += duration

                narration_file = {
                    "scene_id": scene_dict.get("scene_id", f"s{i+1}"),
                    "audio_url": f"https://narration.example.com/scene_{i+1}.wav",
                    "duration_seconds": duration,
                    "voice_talent": input_data.voice_talent,
                    "quality": "studio_pro",
                }
                narration_files.append(narration_file)

        return NarrationOutput(
            agent_name=self.agent_name,
            status=AgentStatus.PASS,
            narration_files=narration_files,
            total_duration=total_duration,
            audio_format="wav",
        ).model_dump()
