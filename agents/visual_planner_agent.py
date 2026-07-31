#!/usr/bin/env python3
"""
Visual Planner Agent — Emmy-standard visual strategy

Decides STRONGEST visual for each shot
Principle: Visuals TEACH, not just illustrate

Hierarchy (10 = strongest):
  10: Archival footage (real events)
  9:  Satellite imagery (visual truth)
  8:  Maps + timelines (teaching geography/progression)
  7:  B-roll + news footage (professional documentation)
  6:  Animations (motion, Ken Burns effect)
  5:  Stock footage (generic illustration)
  4:  AI animations
  3:  AI infographics
  2:  Text overlays
  1:  AI-generated scenes (last resort)
"""

from base_agent import BaseAgent, AgentResult, AgentStatus
from typing import Dict, Any, List


class VisualPlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Visual Planner",
            description="Emmy-standard visual strategy - visuals TEACH"
        )

        self.hierarchy = {
            "archival_footage": 10,
            "satellite_imagery": 9,
            "historical_photos": 9,
            "interactive_map": 8,
            "timeline": 8,
            "news_footage": 7,
            "documentary_broll": 7,
            "animation": 6,
            "stock_footage": 5,
            "ai_animation": 4,
            "ai_infographic": 3,
            "text_overlay": 2,
            "ai_generated_scene": 1,
        }

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Create visual plan for all shots"""

        shots = input_data.get("shots", [])
        if not shots:
            self.log_error("No shots provided")
            return AgentResult(self.name, AgentStatus.FAILED, {})

        self.log_status(f"Planning visuals for {len(shots)} shots")

        visual_plan = []

        for shot in shots:
            plan = self._plan_shot_visuals(shot)
            visual_plan.append(plan)

        self.log_status(f"Visual plan created")

        # Summary statistics
        primary_visuals = [p["primary_visual"] for p in visual_plan]
        visual_counts = {}
        for v in primary_visuals:
            visual_counts[v] = visual_counts.get(v, 0) + 1

        output = {
            "total_shots": len(visual_plan),
            "visual_plan": visual_plan,
            "visual_breakdown": visual_counts,
            "teaching_moments": sum(1 for p in visual_plan if p.get("teaching_elements")),
            "ai_fallback_needed": sum(1 for p in visual_plan if p.get("ai_fallback") != "none"),
        }

        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            output=output
        )

    def _plan_shot_visuals(self, shot: Dict) -> Dict[str, Any]:
        """Create visual plan for single shot"""

        text = shot.get("text", "")
        needs_map = shot.get("needs_map", False)
        needs_timeline = shot.get("needs_timeline", False)
        needs_comparison = shot.get("needs_comparison", False)

        plan = {
            "shot_number": shot["shot_number"],
            "text": text[:60],
            "primary_visual": None,
            "strength": 0,
            "teaching_elements": [],
            "secondary_visuals": [],
            "asset_sources": [],
            "ai_fallback": "none",
        }

        # STRATEGY 1: Location/Map shots
        if needs_map:
            plan["primary_visual"] = "interactive_map"
            plan["strength"] = self.hierarchy["interactive_map"]
            plan["teaching_elements"] = [
                "Show location on map",
                "Highlight region",
                "Add labels + boundaries",
                "Show scale"
            ]
            plan["asset_sources"] = ["Google Maps", "Satellite imagery", "OpenStreetMap"]
            plan["secondary_visuals"] = ["satellite_imagery", "news_footage_of_location"]
            plan["ai_fallback"] = "animated_map"

        # STRATEGY 2: Timeline/Progression shots
        elif needs_timeline:
            plan["primary_visual"] = "timeline"
            plan["strength"] = self.hierarchy["timeline"]
            plan["teaching_elements"] = [
                "Show date/era on timeline",
                "Connect related events",
                "Show progression",
                "Highlight key moments"
            ]
            plan["asset_sources"] = ["Archival footage", "Historical photos", "News archives"]
            plan["secondary_visuals"] = ["archival_footage", "historical_photos"]
            plan["ai_fallback"] = "timeline_animation"

        # STRATEGY 3: Comparison shots
        elif needs_comparison:
            plan["primary_visual"] = "before_after_split"
            plan["strength"] = self.hierarchy["satellite_imagery"]  # Often uses satellite
            plan["teaching_elements"] = [
                "Show before state",
                "Show after state",
                "Highlight differences",
                "Quantify change"
            ]
            plan["asset_sources"] = ["Satellite imagery", "Archive photos", "News footage"]
            plan["secondary_visuals"] = ["satellite_imagery", "archival_photos"]
            plan["ai_fallback"] = "comparison_graphic"

        # STRATEGY 4: Statistic/Data shots
        elif "$" in text or "%" in text or any(w in text.lower() for w in ["million", "percent"]):
            plan["primary_visual"] = "infographic"
            plan["strength"] = self.hierarchy["ai_infographic"]
            plan["teaching_elements"] = [
                "Display number prominently",
                "Provide context/comparison",
                "Use visual hierarchy",
                "Label clearly"
            ]
            plan["asset_sources"] = ["Generated infographic"]
            plan["secondary_visuals"] = ["text_overlay", "data_visualization"]
            plan["ai_fallback"] = "ai_infographic"

        # STRATEGY 5: Action shots
        else:
            plan["primary_visual"] = "archival_or_stock"
            plan["strength"] = self.hierarchy["archival_footage"]
            plan["teaching_elements"] = [
                "Show authentic action",
                "Provide documentary context",
                "Ensure relevance to narration"
            ]
            plan["asset_sources"] = ["News footage", "Documentary B-roll", "Stock footage"]
            plan["secondary_visuals"] = ["stock_footage", "documentary_broll"]
            plan["ai_fallback"] = "ai_scene"

        return plan

    def _get_teaching_strategy(self, shot_type: str) -> Dict[str, Any]:
        """Get teaching visual strategy based on shot type"""

        strategies = {
            "map": {
                "primary": "interactive_map",
                "teaching": ["Geography", "Context", "Scale"],
                "layers": ["Base map", "Regions", "Labels", "Data overlay"]
            },
            "timeline": {
                "primary": "timeline_visualization",
                "teaching": ["Chronology", "Causality", "Progression"],
                "layers": ["Time axis", "Events", "Connections", "Context"]
            },
            "statistic": {
                "primary": "infographic",
                "teaching": ["Magnitude", "Comparison", "Impact"],
                "layers": ["Number", "Context", "Units", "Visual comparison"]
            },
            "action": {
                "primary": "archival_footage",
                "teaching": ["Reality", "Documentation", "Evidence"],
                "layers": ["Footage", "Caption", "Context", "Impact"]
            }
        }

        return strategies.get(shot_type, {})
