"""
Narration Agent - Generates/records narration.

Creates voice-over audio for documentary using ElevenLabs.
"""

from typing import Dict, Any
from pydantic import BaseModel

from .base_agent import BaseAgent
from ..core.schemas import AgentStatus
from ..integrations.elevenlabs_narration import ElevenLabsNarration


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
        """Generate narration using ElevenLabs"""
        scenes = input_data.scenes
        narration_files = []
        total_duration = 0

        # Initialize ElevenLabs client
        elevenlabs = ElevenLabsNarration()

        # Get available voices and select one
        voices_result = elevenlabs.list_voices()
        voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice as default

        # Collect narration text from all scenes
        narration_segments = []
        scene_ids = []

        for i, scene in enumerate(scenes):
            scene_dict = scene if isinstance(scene, dict) else scene.model_dump()
            narration_text = scene_dict.get("narration", "")

            if narration_text:
                narration_segments.append(narration_text)
                scene_ids.append(scene_dict.get("scene_id", f"s{i+1}"))

        # Generate multi-part narration
        if narration_segments:
            result = elevenlabs.generate_multi_part_narration(
                narration_segments,
                voice_id=voice_id,
            )

            for segment in result.get("segments", []):
                narration_file = {
                    "scene_id": scene_ids[segment.get("segment_id", 0)],
                    "audio_url": segment.get("audio_url"),
                    "duration_seconds": segment.get("duration", 0),
                    "voice_talent": "ElevenLabs Rachel",
                    "quality": "studio_pro",
                    "format": "mp3",
                }
                narration_files.append(narration_file)
                total_duration += segment.get("duration", 0)

        return NarrationOutput(
            agent_name=self.agent_name,
            status=AgentStatus.PASS,
            narration_files=narration_files,
            total_duration=total_duration,
            audio_format="mp3",
        ).model_dump()
