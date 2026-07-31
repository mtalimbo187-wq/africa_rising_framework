#!/usr/bin/env python3
"""
Africa Rising Video Framework — Auto Editor

Automatically assembles video from:
- Narration (audio)
- Stock footage
- Generated visuals
- Maps, timelines, overlays

Handles:
- Syncing visuals to narration duration
- Transitions and pacing
- Color grading and effects
- MP4 generation
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

class AutoEditor:
    def __init__(self):
        self.output_dir = Path("/Users/rajab/africa_rising_framework/output")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.video_settings = {
            "resolution": "1280x720",
            "fps": 25,
            "codec": "libx264",
            "audio_codec": "aac",
            "bitrate": "5000k"
        }

        self.transition_types = [
            "fade",
            "cross_fade",
            "wipe_right",
            "wipe_left",
            "cut"
        ]

    def build_edit_plan(self, shots: List[Dict], assets: Dict, narration_paths: List[Path]) -> Dict[str, Any]:
        """Build an editing plan that syncs assets to narration"""

        print("\n" + "="*80)
        print("✂️  BUILDING EDIT PLAN")
        print("="*80 + "\n")

        plan = {
            "timestamp": datetime.now().isoformat(),
            "total_shots": len(shots),
            "estimated_duration": 0,
            "clips": [],
            "timeline": [],
            "settings": self.video_settings
        }

        current_time = 0.0  # In seconds

        for i, shot in enumerate(shots):
            shot_duration = shot.get("duration_estimate", 3.0)
            narration_file = narration_paths[i] if i < len(narration_paths) else None

            # Get assets for this shot
            shot_assets = self._get_assets_for_shot(shot, assets)

            # Build clip
            clip = {
                "clip_number": i + 1,
                "shot_number": shot["shot_number"],
                "text": shot["text"],
                "duration": shot_duration,
                "start_time": current_time,
                "end_time": current_time + shot_duration,
                "narration": str(narration_file) if narration_file else None,
                "visuals": shot_assets,
                "transitions": {
                    "in": "fade" if i == 0 else "cross_fade",
                    "out": "fade" if i == len(shots) - 1 else "cross_fade",
                    "duration": 0.5
                },
                "effects": self._suggest_effects(shot)
            }

            plan["clips"].append(clip)

            # Build timeline entry
            timeline_entry = {
                "time": f"{int(current_time // 60)}:{int(current_time % 60):02d}",
                "shot": shot["shot_number"],
                "content": shot["text"][:50],
                "visuals": shot.get("visual_types", [])
            }
            plan["timeline"].append(timeline_entry)

            current_time += shot_duration

        plan["estimated_duration"] = current_time

        # Save plan
        output_file = self.output_dir / "edit_plan.json"
        with open(output_file, "w") as f:
            json.dump(plan, f, indent=2)

        print(f"Edit plan created: {output_file}")
        print(f"Estimated duration: {int(current_time // 60)}:{int(current_time % 60):02d}")
        print(f"Total clips: {len(plan['clips'])}\n")

        return plan

    def _get_assets_for_shot(self, shot: Dict, assets: Dict) -> Dict[str, List]:
        """Get assets for a shot from collected assets"""

        visual_assets = {}

        # Try to match shot number with collected assets
        for collected_shot in assets.get("shots", []):
            if collected_shot.get("shot_number") == shot.get("shot_number"):
                visual_assets = collected_shot.get("assets_by_type", {})
                break

        return visual_assets

    def _suggest_effects(self, shot: Dict) -> List[str]:
        """Suggest effects based on shot emotion/content"""

        effects = []
        emotion = shot.get("emotion", "neutral")
        text_lower = shot.get("text", "").lower()

        # Emotional effects
        if emotion == "critical":
            effects.append("desaturate_slightly")  # Slightly muted colors
            effects.append("increase_contrast")  # Dramatic

        if emotion == "empathetic":
            effects.append("warm_color_grade")  # Warm, human feeling

        if emotion == "data_driven":
            effects.append("sharp_contrast")  # Clean, clear
            effects.append("statistics_overlay")

        # Content-based effects
        if "africa" in text_lower or "country" in text_lower:
            effects.append("subtle_vignette")  # Draw attention

        if "mental" in text_lower or "stress" in text_lower:
            effects.append("slight_grain")  # Documentary feel

        return effects

    def generate_script(self, plan: Dict) -> str:
        """Generate an FFmpeg script for video assembly"""

        script = "#!/bin/bash\n"
        script += "# Auto-generated video assembly script\n"
        script += "# Generated by Africa Rising Framework\n\n"

        script += "ffmpeg \\\n"

        # Add all input files
        for i, clip in enumerate(plan["clips"]):
            narration = clip.get("narration")
            if narration:
                script += f"  -i \"{narration}\" \\\n"

        script += "  -filter_complex \"\\\n"
        script += "    concat=n={}:v=0:a=1 [a]\\\n".format(len(plan["clips"]))
        script += "  \" \\\n"

        script += "  -map [a] \\\n"
        script += f"  -c:a {plan['settings']['audio_codec']} \\\n"
        script += f"  output_audio.mp3\n"

        return script

    def generate_assembly_instructions(self, plan: Dict) -> str:
        """Generate human-readable assembly instructions"""

        instructions = []
        instructions.append("=" * 80)
        instructions.append("AFRICA RISING VIDEO — ASSEMBLY INSTRUCTIONS")
        instructions.append("=" * 80)
        instructions.append("")

        instructions.append(f"Total Duration: {int(plan['estimated_duration'] // 60)}:{int(plan['estimated_duration'] % 60):02d}")
        instructions.append(f"Resolution: {plan['settings']['resolution']}")
        instructions.append(f"Frame rate: {plan['settings']['fps']} fps")
        instructions.append("")

        instructions.append("ASSEMBLY STEPS:")
        instructions.append("")

        for clip in plan["clips"]:
            start_time = clip["start_time"]
            duration = clip["duration"]
            shot_num = clip["shot_number"]

            instructions.append(f"CLIP {clip['clip_number']} (Shot {shot_num})")
            instructions.append(f"  Time: {int(start_time // 60)}:{int(start_time % 60):02d} → {int(clip['end_time'] // 60)}:{int(clip['end_time'] % 60):02d}")
            instructions.append(f"  Duration: {duration:.1f}s")
            instructions.append(f"  Narration: {Path(clip['narration']).name if clip['narration'] else 'None'}")
            instructions.append(f"  Visuals needed: {', '.join(clip['visuals'].keys())}")
            instructions.append(f"  Transitions: {clip['transitions']['in']} → {clip['transitions']['out']}")
            instructions.append(f"  Effects: {', '.join(clip['effects']) if clip['effects'] else 'None'}")
            instructions.append(f"  Text: {clip['text'][:60]}...")
            instructions.append("")

        instructions.append("=" * 80)
        instructions.append("ASSET CHECKLIST:")
        instructions.append("=" * 80)

        visual_types = {}
        for clip in plan["clips"]:
            for vtype in clip["visuals"].keys():
                visual_types[vtype] = visual_types.get(vtype, 0) + 1

        for vtype, count in visual_types.items():
            instructions.append(f"☐ {vtype.replace('_', ' ').title()}: {count} needed")

        return "\n".join(instructions)

    def generate_all(self, shots: List[Dict], assets: Dict, narration_paths: List[Path]) -> Dict[str, Any]:
        """Generate complete assembly plan and instructions"""

        # Build edit plan
        plan = self.build_edit_plan(shots, assets, narration_paths)

        # Generate assembly instructions
        instructions = self.generate_assembly_instructions(plan)

        # Save instructions
        instructions_file = self.output_dir / "ASSEMBLY_INSTRUCTIONS.txt"
        with open(instructions_file, "w") as f:
            f.write(instructions)

        print(f"\n✅ Assembly instructions saved to {instructions_file}\n")

        return {
            "plan": plan,
            "instructions": instructions,
            "instructions_file": str(instructions_file)
        }


def main():
    """Example usage"""
    from script_analyzer import ScriptAnalyzer
    from asset_collector import AssetCollector

    sample_script = """
    Facebook content moderators in Africa earn just two dollars an hour.
    In the United States, the same work pays twenty dollars.
    """

    # Analyze script
    analyzer = ScriptAnalyzer()
    analysis = analyzer.analyze(sample_script)

    # Collect assets (simulated)
    assets = {
        "shots": [
            {
                "shot_number": 1,
                "assets_by_type": {
                    "stock_footage": [],
                    "text_overlay": []
                }
            }
        ]
    }

    # Create narration paths (simulated)
    narration_paths = [Path(f"/cache/section_{i+1}.mp3") for i in range(len(analysis["shots"]))]

    # Generate edit plan
    editor = AutoEditor()
    result = editor.generate_all(analysis["shots"], assets, narration_paths)

    print("Edit plan generated successfully")


if __name__ == "__main__":
    main()
