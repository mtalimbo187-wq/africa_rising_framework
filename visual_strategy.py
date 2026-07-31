#!/usr/bin/env python3
"""
Africa Rising Video Framework — Visual Strategy

Emmy-standard visual storytelling: visuals TEACH, not just illustrate.

Philosophy: Each sentence deserves the strongest visual.
- Prefer authentic archival footage over AI
- Use maps for locations and geography
- Use timelines for dates and progression
- Use satellite/historical photos for past events
- Use cinematic B-roll for concepts/feelings
- Use AI-generated content only when real visuals don't exist

Example (from Johnny Harris approach):
Narration: "China built artificial islands in the South China Sea…"
Teaching visual approach:
  1. Zoom into South China Sea on map
  2. Highlight disputed islands
  3. Overlay maritime boundaries
  4. Show satellite imagery (before/after)
  5. Add labels for involved countries
  6. Cut to real footage of islands

Each visual element teaches the viewer something new.
"""

import json
from typing import List, Dict, Any
from pathlib import Path


class VisualStrategy:
    """Determines the strongest visual for each sentence"""

    def __init__(self):
        self.visual_hierarchy = {
            # Tier 1: Authentic, real footage (strongest)
            "archival_footage": 10,
            "satellite_imagery": 9,
            "historical_photos": 9,
            "news_footage": 8,
            "documentary_broll": 7,

            # Tier 2: Maps and location visuals (very strong for teaching)
            "interactive_map": 8,
            "satellite_map": 9,
            "google_earth_flyover": 8,
            "osm_map_animation": 7,

            # Tier 3: Timelines and temporal visuals (excellent for context)
            "timeline_visualization": 8,
            "before_after": 8,
            "progress_bars": 6,

            # Tier 4: Relevant B-roll (good for concepts)
            "stock_footage": 5,
            "cinematic_broll": 6,

            # Tier 5: Generated content (use as last resort)
            "ai_generated_scene": 2,
            "ai_infographic": 3,
            "animation": 4,
            "text_overlay": 3,
        }

        self.emotional_strategy = {
            "critical": ["desaturate", "high_contrast", "documentary_grain"],
            "empathetic": ["warm_tones", "slow_movement", "human_focus"],
            "urgent": ["fast_cuts", "bright_colors", "high_energy"],
            "hopeful": ["bright_tones", "uplifting_music", "forward_motion"],
            "investigative": ["zoom_maps", "before_after", "evidence_overlay"],
            "data_driven": ["clean_graphics", "statistics_overlay", "clear_hierarchy"],
        }

    def analyze_sentence(self, text: str, context: Dict = None) -> Dict[str, Any]:
        """Analyze a sentence and recommend the strongest visuals"""

        analysis = {
            "text": text,
            "primary_visual": None,
            "secondary_visuals": [],
            "teaching_elements": [],
            "asset_priority": [],
            "ai_fallback": None,
            "strength_score": 0
        }

        # Extract key elements
        is_location = self._contains_location(text)
        is_date = self._contains_date(text)
        is_statistic = self._contains_statistic(text)
        is_action = self._contains_action(text)
        is_comparison = self._contains_comparison(text)

        # Build teaching strategy
        if is_location:
            analysis["primary_visual"] = "interactive_map"
            analysis["teaching_elements"].append("Show location on map")
            analysis["teaching_elements"].append("Highlight region/country")
            analysis["teaching_elements"].append("Add relevant labels")
            analysis["strength_score"] = self.visual_hierarchy["interactive_map"]

        if is_date and not analysis["primary_visual"]:
            analysis["primary_visual"] = "timeline_visualization"
            analysis["teaching_elements"].append("Show date on timeline")
            analysis["teaching_elements"].append("Connect to related events")
            analysis["strength_score"] = self.visual_hierarchy["timeline_visualization"]

        if is_comparison:
            analysis["primary_visual"] = "before_after"
            analysis["teaching_elements"].append("Show before state")
            analysis["teaching_elements"].append("Show after state")
            analysis["teaching_elements"].append("Highlight differences")
            analysis["strength_score"] = self.visual_hierarchy["before_after"]

        if is_statistic and "$" in text:
            analysis["primary_visual"] = "ai_infographic"
            analysis["teaching_elements"].append("Display number prominently")
            analysis["teaching_elements"].append("Provide context")
            analysis["teaching_elements"].append("Show comparison if relevant")
            analysis["strength_score"] = self.visual_hierarchy["ai_infographic"]

        if is_action and not analysis["primary_visual"]:
            analysis["primary_visual"] = "archival_footage"
            analysis["teaching_elements"].append("Show actual action")
            analysis["teaching_elements"].append("Provide authentic context")
            analysis["secondary_visuals"] = ["documentary_broll", "news_footage"]
            analysis["strength_score"] = self.visual_hierarchy["archival_footage"]

        # Fallback if nothing matched
        if not analysis["primary_visual"]:
            analysis["primary_visual"] = "stock_footage"
            analysis["teaching_elements"].append("Illustrate concept")
            analysis["strength_score"] = self.visual_hierarchy["stock_footage"]

        # Asset priority (strongest first)
        analysis["asset_priority"] = self._get_asset_priority(analysis["primary_visual"])

        # AI fallback (only if real assets unavailable)
        analysis["ai_fallback"] = self._get_ai_fallback(analysis["primary_visual"])

        return analysis

    def _contains_location(self, text: str) -> bool:
        """Check if sentence mentions a location"""
        locations = [
            "africa", "kenya", "nigeria", "uganda", "ethiopia", "ghana",
            "china", "us", "america", "asia", "europe", "south china sea",
            "continent", "country", "region", "city", "coast", "island",
            "tumwater", "olympia", "washington", "seattle"
        ]
        text_lower = text.lower()
        return any(loc in text_lower for loc in locations)

    def _contains_date(self, text: str) -> bool:
        """Check if sentence mentions a date or era"""
        import re
        date_pattern = r'\b(19|20)\d{2}\b|\b(early|late|mid|beginning|end|during|since|before|after)\b'
        return bool(re.search(date_pattern, text, re.IGNORECASE))

    def _contains_statistic(self, text: str) -> bool:
        """Check if sentence contains numbers or percentages"""
        return any(char.isdigit() for char in text) or "percent" in text.lower() or "%" in text

    def _contains_action(self, text: str) -> bool:
        """Check if sentence describes an action or event"""
        actions = [
            "work", "earning", "paid", "moderate", "content", "earning",
            "exploitation", "abuse", "suffer", "wage", "contract",
            "build", "create", "launch", "operate", "manage"
        ]
        text_lower = text.lower()
        return any(action in text_lower for action in actions)

    def _contains_comparison(self, text: str) -> bool:
        """Check if sentence compares two things"""
        comparison_words = ["vs", "versus", "vs.", "compared", "while", "but", "however", "unlike"]
        text_lower = text.lower()
        return any(word in text_lower for word in comparison_words)

    def _get_asset_priority(self, primary_visual: str) -> List[str]:
        """Return assets in priority order for a visual type"""

        priority_map = {
            "interactive_map": ["satellite_map", "google_earth", "osm"],
            "timeline_visualization": ["archival_photos", "historical_footage"],
            "before_after": ["satellite_imagery", "archival_photos"],
            "archival_footage": ["news_footage", "documentary_broll", "pexels_stock"],
            "ai_infographic": ["stock_photos", "icons", "generated"],
            "stock_footage": ["pexels", "unsplash", "pixabay"],
        }

        return priority_map.get(primary_visual, ["stock_footage", "ai_generated"])

    def _get_ai_fallback(self, primary_visual: str) -> str:
        """Return AI-generated fallback if real assets unavailable"""

        fallback_map = {
            "interactive_map": "ai_map_animation",
            "timeline_visualization": "ai_timeline",
            "before_after": "ai_comparison_graphic",
            "archival_footage": "ai_scene_generation",
            "ai_infographic": "ai_infographic",
            "stock_footage": "ai_cinematic_broll",
        }

        return fallback_map.get(primary_visual, "ai_infographic")

    def create_cutting_strategy(self, shots: List[Dict]) -> Dict[str, Any]:
        """Create a complete cutting strategy for the entire video"""

        strategy = {
            "total_shots": len(shots),
            "shot_sequence": [],
            "visual_variety": {"map": 0, "timeline": 0, "archive": 0, "stock": 0, "ai": 0},
            "teaching_moments": [],
            "estimated_pacing": 0
        }

        for shot in shots:
            shot_strategy = self.analyze_sentence(
                shot["text"],
                context={"emotion": shot.get("emotion")}
            )

            sequence_item = {
                "shot_number": shot["shot_number"],
                "text": shot["text"][:60],
                "duration": shot.get("duration_estimate", 3.0),
                "primary_visual": shot_strategy["primary_visual"],
                "secondary_visuals": shot_strategy["secondary_visuals"],
                "teaching_elements": shot_strategy["teaching_elements"],
                "asset_priority": shot_strategy["asset_priority"],
                "strength_score": shot_strategy["strength_score"]
            }

            strategy["shot_sequence"].append(sequence_item)

            # Track visual variety
            primary = shot_strategy["primary_visual"].split("_")[0]
            if "map" in primary:
                strategy["visual_variety"]["map"] += 1
            elif "timeline" in primary:
                strategy["visual_variety"]["timeline"] += 1
            elif "archive" in primary or "historical" in primary:
                strategy["visual_variety"]["archive"] += 1
            elif "ai" in primary:
                strategy["visual_variety"]["ai"] += 1
            else:
                strategy["visual_variety"]["stock"] += 1

            # Extract teaching moments
            if shot_strategy["teaching_elements"]:
                strategy["teaching_moments"].append({
                    "shot": shot["shot_number"],
                    "elements": shot_strategy["teaching_elements"]
                })

            strategy["estimated_pacing"] += sequence_item["duration"]

        return strategy


def main():
    """Example usage"""

    sample_sentences = [
        "Facebook content moderators in Africa earn just two dollars an hour.",
        "In the United States, the same work pays twenty dollars.",
        "Workers in Nigeria, Kenya, and Uganda moderate content daily.",
        "Since 2016, Meta has contracted out this work to companies like Sama.",
        "The psychological toll is severe compared to work in the developed world.",
    ]

    strategy = VisualStrategy()

    print("\n" + "="*80)
    print("🎬 VISUAL STRATEGY ANALYSIS")
    print("="*80 + "\n")

    for i, sentence in enumerate(sample_sentences, 1):
        analysis = strategy.analyze_sentence(sentence)

        print(f"Shot {i}: {sentence[:60]}...")
        print(f"  Primary visual: {analysis['primary_visual']} (strength: {analysis['strength_score']}/10)")
        print(f"  Teaching elements: {', '.join(analysis['teaching_elements'])}")
        print(f"  Asset priority: {' → '.join(analysis['asset_priority'][:3])}")
        print(f"  AI fallback: {analysis['ai_fallback']}")
        print()

    # Create full cutting strategy
    shots = [{"text": s, "shot_number": i, "emotion": "investigative", "duration_estimate": 3.0}
             for i, s in enumerate(sample_sentences, 1)]

    cutting_strategy = strategy.create_cutting_strategy(shots)

    print("="*80)
    print("CUTTING STRATEGY SUMMARY")
    print("="*80)
    print(f"Total duration: {cutting_strategy['estimated_pacing']:.1f}s")
    print(f"Visual variety: {cutting_strategy['visual_variety']}")
    print(f"Teaching moments: {len(cutting_strategy['teaching_moments'])}")
    print()


if __name__ == "__main__":
    main()
