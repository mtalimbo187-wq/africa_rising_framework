#!/usr/bin/env python3
"""
Africa Rising Video Framework — Visual Generator

Creates missing visuals:
- AI-generated infographics and illustrations (Grok, DALL-E)
- Animated still images (Ken Burns effect, zoom/pan)
- Maps and location visualizations
- Timelines and data visualizations
- Text overlays and graphics
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

class VisualGenerator:
    def __init__(self):
        self.output_dir = Path("/Users/rajab/africa_rising_framework/cache/visuals")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # API Keys
        self.grok_key = "xai-edxHqBNRmIYIoqJQ03Q7A4oiZEtJhO3G0RZKDKLL1HipEdaWWUhTI1A8TfPpEd2Wltg3HfVQPssNMGDz"

        self.prompt_templates = {
            "wage_comparison": "Professional infographic showing wage disparity. Left: $2/HOUR in red. Right: $20/HOUR in green. Bold typography, dark background, gold accents. 1280x720.",
            "map_africa": "World map highlighting Africa and Sub-Saharan region. Countries marked: Nigeria, Kenya, Uganda where content moderation occurs. Professional cartographic style.",
            "timeline": "Historical timeline visualization: 2016 (contractors emerge), 2019 (lawsuits), 2023 (ongoing). Documentary style, clear date markers.",
            "mental_health": "Stat card: '68% PTSD' in large bold text. Psychological impact visualization. Empathetic documentary design.",
            "corporate_hierarchy": "Meta → Sama → Workers flow diagram showing disconnection and wage gap. Professional visualization.",
            "worker_conditions": "Split-screen comparison: Left (poor conditions) vs Right (US benefits). Professional infographic.",
            "global_scale": "Stat card: '5,000+ AFRICAN WORKERS'. Globe background showing global reach. Documentary infographic.",
            "solution_pathway": "Steps from exploitation to fair wages ($15/hour target). Progress visualization with green accents."
        }

    def generate_infographic(self, shot_number: int, topic: str, data: Dict = None) -> Dict[str, Any]:
        """Generate AI infographic for a shot"""

        result = {
            "shot_number": shot_number,
            "type": "ai_infographic",
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "status": "placeholder",
            "path": None,
            "prompt": None
        }

        # Get appropriate prompt template
        prompt = self.prompt_templates.get(
            topic.lower().replace(" ", "_"),
            f"Professional infographic about {topic}. 1280x720 resolution."
        )

        result["prompt"] = prompt

        # Log for manual review or API call
        print(f"Shot {shot_number}: Would generate AI image with Grok")
        print(f"  Prompt: {prompt[:80]}...")

        # Placeholder: can be replaced with actual API call
        # For now, we note what should be generated
        result["status"] = "queued"
        result["note"] = "Ready for generation via Grok Imagine or DALL-E when API available"

        return result

    def generate_animation(self, shot_number: int, image_path: Path, effect: str = "ken_burns") -> Dict[str, Any]:
        """Generate animation for a still image"""

        result = {
            "shot_number": shot_number,
            "type": "animation",
            "source_image": str(image_path),
            "effect": effect,
            "timestamp": datetime.now().isoformat(),
            "status": "configured",
            "output_path": None
        }

        # Common animation effects
        effects = {
            "ken_burns": "Slow zoom/pan across still image",
            "zoom_in": "Zoom in from wide to close-up",
            "pan_left": "Pan left across image",
            "pan_right": "Pan right across image",
            "fade_in": "Fade in from black"
        }

        result["effect_description"] = effects.get(effect, "Custom animation")

        print(f"Shot {shot_number}: Animation configured")
        print(f"  Effect: {effect}")
        print(f"  Source: {image_path.name}")

        return result

    def generate_map(self, shot_number: int, locations: List[str], map_type: str = "world") -> Dict[str, Any]:
        """Generate map visualization"""

        result = {
            "shot_number": shot_number,
            "type": "map",
            "locations": locations,
            "map_type": map_type,
            "timestamp": datetime.now().isoformat(),
            "status": "configured",
            "output_path": None
        }

        print(f"Shot {shot_number}: Map visualization configured")
        print(f"  Type: {map_type}")
        print(f"  Locations: {', '.join(locations)}")

        return result

    def generate_timeline(self, shot_number: int, events: List[Dict]) -> Dict[str, Any]:
        """Generate timeline visualization"""

        result = {
            "shot_number": shot_number,
            "type": "timeline",
            "events": events,
            "timestamp": datetime.now().isoformat(),
            "status": "configured",
            "output_path": None
        }

        print(f"Shot {shot_number}: Timeline configured")
        for event in events:
            print(f"  {event.get('year')}: {event.get('description')}")

        return result

    def generate_text_overlay(self, shot_number: int, text: str, style: str = "stat_card") -> Dict[str, Any]:
        """Generate text overlay graphic"""

        result = {
            "shot_number": shot_number,
            "type": "text_overlay",
            "text": text,
            "style": style,
            "timestamp": datetime.now().isoformat(),
            "status": "configured",
            "output_path": None
        }

        print(f"Shot {shot_number}: Text overlay configured")
        print(f"  Style: {style}")
        print(f"  Text: {text[:50]}...")

        return result

    def generate_batch(self, shots: List[Dict]) -> Dict[str, Any]:
        """Generate all missing visuals for a complete script"""

        print("\n" + "="*80)
        print("🎨 GENERATING VISUALS")
        print("="*80 + "\n")

        results = {
            "timestamp": datetime.now().isoformat(),
            "total_shots": len(shots),
            "generated_visuals": []
        }

        # Examples of what could be generated
        visual_generation_examples = [
            {
                "shot": 1,
                "action": "Generate infographic",
                "topic": "wage_comparison",
                "desc": "$2/hour vs $20/hour stat card"
            },
            {
                "shot": 2,
                "action": "Generate map",
                "locations": ["Nigeria", "Kenya", "Uganda"],
                "desc": "African locations highlighted"
            },
            {
                "shot": 3,
                "action": "Generate stat card",
                "text": "68% PTSD",
                "desc": "Mental health impact"
            },
            {
                "shot": 4,
                "action": "Generate timeline",
                "events": [
                    {"year": 2016, "desc": "Contractors emerge"},
                    {"year": 2019, "desc": "Lawsuits filed"},
                    {"year": 2023, "desc": "Ongoing"}
                ],
                "desc": "Historical timeline"
            }
        ]

        for shot in shots:
            visual_types = shot.get("visual_types", [])

            for visual_type in visual_types:
                if visual_type == "ai_image":
                    topic = shot["text"][:50]  # Use first part of text as topic
                    visual = self.generate_infographic(shot["shot_number"], topic)
                    results["generated_visuals"].append(visual)

                elif visual_type == "map":
                    visual = self.generate_map(shot["shot_number"], ["Africa", "Nigeria", "Kenya"])
                    results["generated_visuals"].append(visual)

                elif visual_type == "timeline":
                    events = [
                        {"year": 2016, "description": "Content moderation outsourcing begins"},
                        {"year": 2019, "description": "Lawsuits and investigations"},
                        {"year": 2023, "description": "Ongoing exploitation"}
                    ]
                    visual = self.generate_timeline(shot["shot_number"], events)
                    results["generated_visuals"].append(visual)

                elif visual_type == "text_overlay":
                    # Extract key numbers/stats from text
                    if "$" in shot["text"] or "%" in shot["text"]:
                        visual = self.generate_text_overlay(shot["shot_number"], shot["text"])
                        results["generated_visuals"].append(visual)

        # Save generation plan
        output_file = self.output_dir / "generation_plan.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"\n✅ Visual generation plan saved to {output_file}\n")
        return results


def main():
    """Example usage"""
    from script_analyzer import ScriptAnalyzer

    sample_script = """
    Facebook content moderators in Africa earn just two dollars an hour.
    In the United States, the same work pays twenty dollars.
    This is a ten-times wage gap.
    Workers in Nigeria, Kenya, and Uganda moderate content daily.
    Studies show 68 percent develop PTSD.
    """

    analyzer = ScriptAnalyzer()
    analysis = analyzer.analyze(sample_script)

    generator = VisualGenerator()
    visuals = generator.generate_batch(analysis["shots"])

    print(f"Generated {len(visuals['generated_visuals'])} visual assets")


if __name__ == "__main__":
    main()
