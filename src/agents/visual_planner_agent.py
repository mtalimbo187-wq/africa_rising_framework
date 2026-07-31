"""
Visual Planner Agent - Plans visual hierarchy and composition.

Creates Emmy-standard visual hierarchy with 10-point priority system.
"""

from typing import Dict, Any
from pydantic import BaseModel

from .base_agent import BaseAgent
from ..core.schemas import VisualPlan, VisualPlanOutput, AgentStatus


class VisualPlannerInput(BaseModel):
    """Visual Planner Agent input"""
    scenes: list
    visual_alignments: list = []


class VisualPlannerAgent(BaseAgent):
    """Visual Planner Agent implementation"""

    agent_name = "Visual Planner"
    input_schema = VisualPlannerInput
    output_schema = VisualPlanOutput
    timeout_seconds = 300

    success_criteria = {
        "agent_name": ("Visual Planner", "=="),
    }

    def _run(self, input_data: VisualPlannerInput) -> Dict[str, Any]:
        """Plan visual hierarchy"""
        scenes = input_data.scenes
        plans = []

        for i, scene in enumerate(scenes):
            scene_dict = scene if isinstance(scene, dict) else scene.model_dump()

            plan = VisualPlan(
                scene_id=scene_dict.get("scene_id", f"s{i+1}"),
                hierarchy_priority=self._calculate_priority(scene_dict),
                composition_rules=self._determine_composition(scene_dict),
                color_palette=[],
                lighting_notes=self._determine_lighting(scene_dict),
                shot_requirements=self._determine_shots(scene_dict),
            )
            plans.append(plan)

        return VisualPlanOutput(
            agent_name=self.agent_name,
            status=AgentStatus.PASS,
            visual_plans=plans,
            total_plans=len(plans),
            hierarchy_complete=True,
        ).model_dump()

    def _calculate_priority(self, scene: Dict[str, Any]) -> int:
        """Calculate hierarchy priority (1-10, 10 highest)"""
        priority = 5  # Base priority

        # Boost for critical/major importance
        importance = scene.get("importance", "MINOR")
        if importance == "CRITICAL":
            priority = 10
        elif importance == "MAJOR":
            priority = 8
        elif importance == "MINOR":
            priority = 3

        # Boost for emotion
        emotion = scene.get("emotion", "neutral")
        if emotion == "triumph":
            priority = min(10, priority + 2)
        elif emotion == "concern":
            priority = min(10, priority + 1)

        return priority

    def _determine_composition(self, scene: Dict[str, Any]) -> list:
        """Determine composition rules"""
        rules = []

        if "refinery" in scene.get("narration", "").lower():
            rules.append("wide_establishing_shot")
            rules.append("rule_of_thirds")
        else:
            rules.append("center_composition")

        if scene.get("emotion") == "triumph":
            rules.append("upward_angle")
        elif scene.get("emotion") == "concern":
            rules.append("downward_angle")

        return rules

    def _determine_lighting(self, scene: Dict[str, Any]) -> str:
        """Determine lighting approach"""
        if scene.get("emotion") == "triumph":
            return "bright_and_warm"
        elif scene.get("emotion") == "concern":
            return "dramatic_and_moody"
        else:
            return "neutral_and_balanced"

    def _determine_shots(self, scene: Dict[str, Any]) -> list:
        """Determine shot requirements"""
        shots = []

        if any(x in scene.get("visual_requirements", []) for x in ["facility_footage", "refinery"]):
            shots.extend(["establishing_shot", "detail_shot", "wide_shot"])
        else:
            shots.append("medium_shot")

        if "map_required" in scene.get("visual_requirements", []):
            shots.append("map_graphic")

        if "chart_required" in scene.get("visual_requirements", []):
            shots.append("data_visualization")

        return shots
