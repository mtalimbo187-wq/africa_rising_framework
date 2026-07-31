"""
Script Analyzer - Breaks script into scenes.

Extracts scenes with metadata:
- Timecode
- Narration
- Emotion
- Importance
- Entities
- Visual requirements
"""

from typing import Dict, Any
from pydantic import BaseModel

from .base_agent import BaseAgent
from ..core.schemas import Scene, ScriptAnalysisOutput, AgentStatus, Importance


class ScriptAnalysisInput(BaseModel):
    """Script Analyzer input"""
    script: str
    verified_facts: list = []


class ScriptAnalyzerAgent(BaseAgent):
    """Script Analyzer implementation"""

    agent_name = "Script Analyzer"
    input_schema = ScriptAnalysisInput
    output_schema = ScriptAnalysisOutput
    timeout_seconds = 300

    success_criteria = {
        "scenes": (1, ">="),  # At least 1 scene
    }

    def _run(self, input_data: ScriptAnalysisInput) -> Dict[str, Any]:
        """Analyze script into scenes"""
        script = input_data.script

        # Parse script sections (simplified)
        sections = script.split("\n\n")
        scenes = []

        current_time = 0
        for i, section in enumerate(sections):
            if len(section.strip()) < 10:
                continue

            # Estimate duration (roughly 2.2 words per second)
            word_count = len(section.split())
            duration = word_count / 2.2

            # Determine importance
            importance = Importance.MAJOR
            if i == 0:
                importance = Importance.CRITICAL
            elif i == len(sections) - 1:
                importance = Importance.MAJOR

            # Determine emotion
            emotion = "neutral"
            if "achievement" in section.lower() or "success" in section.lower():
                emotion = "triumph"
            elif "challenge" in section.lower() or "difficult" in section.lower():
                emotion = "concern"

            scene = Scene(
                scene_id=f"s{i+1}",
                start_time=current_time,
                end_time=current_time + duration,
                narration=section.strip(),
                emotion=emotion,
                importance=importance,
                entities=self._extract_entities(section),
                location=self._extract_location(section),
                date=self._extract_date(section),
                visual_requirements=self._determine_visual_needs(section),
            )

            scenes.append(scene)
            current_time += duration

        total_duration = sum(s.end_time for s in scenes) if scenes else 0

        return ScriptAnalysisOutput(
            agent_name=self.agent_name,
            status=AgentStatus.PASS,
            scenes=scenes,
            total_duration=total_duration,
            scene_count=len(scenes),
        ).dict()

    def _extract_entities(self, text: str) -> list:
        """Extract entities from text"""
        entities = []
        if "Dangote" in text:
            entities.append("Aliko Dangote")
        if "Nigeria" in text:
            entities.append("Nigeria")
        if "refinery" in text.lower():
            entities.append("Dangote Refinery")
        return entities

    def _extract_location(self, text: str) -> str:
        """Extract location from text"""
        if "Lagos" in text:
            return "Lagos"
        if "Nigeria" in text:
            return "Nigeria"
        return None

    def _extract_date(self, text: str) -> str:
        """Extract date from text"""
        if "2023" in text:
            return "2023"
        if "1980s" in text or "1980" in text:
            return "1980s"
        if "2006" in text:
            return "2006"
        return None

    def _determine_visual_needs(self, text: str) -> list:
        """Determine visual requirements"""
        needs = []
        if "refinery" in text.lower():
            needs.append("facility_footage")
        if any(x in text.lower() for x in ["map", "location", "place"]):
            needs.append("map_required")
        if any(x in text.lower() for x in ["history", "1980", "timeline"]):
            needs.append("timeline_required")
        if any(x in text.lower() for x in ["$", "million", "billion", "%"]):
            needs.append("chart_required")
        return needs
