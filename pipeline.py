#!/usr/bin/env python3
"""
Africa Rising Video Framework — Main Pipeline

Orchestrates the complete workflow:
1. Parse script
2. Analyze content
3. Collect assets
4. Generate missing visuals
5. Create edit plan
6. Assemble video
"""

import json
import sys
from pathlib import Path
from script_analyzer import ScriptAnalyzer
from asset_collector import AssetCollector
from visual_generator import VisualGenerator
from auto_editor import AutoEditor


class AfricaRisingPipeline:
    def __init__(self, project_name: str = "untitled"):
        self.project_name = project_name
        self.project_dir = Path(f"/Users/rajab/africa_rising_framework/pipelines/{project_name}")
        self.project_dir.mkdir(parents=True, exist_ok=True)

        self.analyzer = ScriptAnalyzer()
        self.collector = AssetCollector()
        self.generator = VisualGenerator()
        self.editor = AutoEditor()

        self.results = {}

    def run(self, script_file: Path, narration_dir: Path = None) -> Dict:
        """Run the complete pipeline"""

        print("\n" + "="*80)
        print("🚀 AFRICA RISING VIDEO FRAMEWORK")
        print("="*80)
        print(f"Project: {self.project_name}\n")

        # Load script
        if not script_file.exists():
            print(f"❌ Script file not found: {script_file}")
            return {}

        with open(script_file) as f:
            script_text = f.read()

        print(f"📝 Loaded script: {script_file.name}")
        print(f"   Length: {len(script_text)} characters\n")

        # Step 1: Analyze script
        print("Step 1: Analyzing script...")
        analysis = self.analyzer.analyze(script_text)
        self.results["analysis"] = analysis
        print(f"  ✓ {analysis['total_shots']} shots identified")
        print(f"  ✓ Estimated duration: {analysis['estimated_duration_seconds']:.1f}s\n")

        # Step 2: Collect assets
        print("Step 2: Collecting assets...")
        assets = self.collector.collect_batch(analysis["shots"])
        self.results["assets"] = assets
        print(f"  ✓ Assets collected for all shots\n")

        # Step 3: Generate visuals
        print("Step 3: Generating visuals...")
        visuals = self.generator.generate_batch(analysis["shots"])
        self.results["visuals"] = visuals
        print(f"  ✓ {len(visuals['generated_visuals'])} visuals configured\n")

        # Step 4: Build edit plan
        print("Step 4: Building edit plan...")
        narration_paths = self._get_narration_files(narration_dir, len(analysis["shots"]))
        edit_result = self.editor.generate_all(analysis["shots"], assets, narration_paths)
        self.results["edit_plan"] = edit_result["plan"]
        print(f"  ✓ Edit plan created\n")

        # Save complete project report
        self._save_project_report()

        print("="*80)
        print("✅ PIPELINE COMPLETE")
        print("="*80)
        print(f"\nProject directory: {self.project_dir}")
        print("\nNext steps:")
        print("  1. Review assembly instructions")
        print("  2. Confirm asset searches or use alternatives")
        print("  3. Generate AI visuals for gaps")
        print("  4. Run video assembly\n")

        return self.results

    def _get_narration_files(self, narration_dir: Path, expected_count: int) -> list:
        """Find narration files in order"""

        if not narration_dir or not narration_dir.exists():
            return [None] * expected_count

        narration_files = sorted(narration_dir.glob("section_*.mp3"))
        return narration_files + [None] * (expected_count - len(narration_files))

    def _save_project_report(self):
        """Save complete project report"""

        report = {
            "project": self.project_name,
            "timestamp": self.results.get("analysis", {}).get("shots", [{}])[0].get("text", ""),
            "summary": {
                "total_shots": self.results["analysis"].get("total_shots", 0),
                "estimated_duration": self.results["analysis"].get("estimated_duration_seconds", 0),
                "visual_breakdown": self.results["analysis"].get("timeline", {}).get("visual_breakdown", {}),
                "assets_collected": len(self.results["assets"].get("shots", [])),
                "visuals_generated": len(self.results["visuals"].get("generated_visuals", []))
            },
            "analysis": self.results["analysis"],
            "assets": self.results["assets"],
            "visuals": self.results["visuals"],
            "edit_plan": self.results["edit_plan"]
        }

        report_file = self.project_dir / "PROJECT_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Project report saved: {report_file}")


def main():
    """Example usage"""

    # Example: Run pipeline on Facebook moderators video
    script_file = Path("/Users/rajab/africa_rising_production/facebook_moderators_script.md")
    narration_dir = Path("/Users/rajab/africa_rising_production/cache")

    if script_file.exists():
        pipeline = AfricaRisingPipeline("facebook_moderators")
        results = pipeline.run(script_file, narration_dir)
    else:
        print(f"Script file not found: {script_file}")
        print("\nUsage: python3 pipeline.py <script_file> [narration_dir]")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        script_file = Path(sys.argv[1])
        narration_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        pipeline = AfricaRisingPipeline(script_file.stem)
        pipeline.run(script_file, narration_dir)
    else:
        main()
