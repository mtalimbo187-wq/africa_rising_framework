#!/usr/bin/env python3
"""
Producer Agent — Orchestrator (Master Agent)

Reads user request
Coordinates all other agents
Manages workflow
Reports progress
"""

from base_agent import BaseAgent, AgentResult, AgentStatus
from typing import Dict, Any, List
from pathlib import Path
import json
import time


class ProducerAgent(BaseAgent):
    def __init__(self, project_name: str = "untitled"):
        super().__init__(
            name="Producer",
            description="Master orchestrator - coordinates all agents"
        )

        self.project_name = project_name
        self.project_dir = Path(f"pipelines/{project_name}")
        self.project_dir.mkdir(parents=True, exist_ok=True)

        # Will be set by orchestrator
        self.agents = {}

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Orchestrate complete workflow"""

        user_request = input_data.get("request", "Create a video")
        script_file = input_data.get("script_file")
        narration_dir = input_data.get("narration_dir")

        self.log_status(f"Request: {user_request}")
        self.log_status(f"Project: {self.project_name}")

        if not script_file or not Path(script_file).exists():
            self.log_error("Script file not found")
            return AgentResult(self.name, AgentStatus.FAILED, {})

        # Load script
        with open(script_file) as f:
            script_text = f.read()

        self.log_status(f"Script loaded: {len(script_text)} characters")

        # Workflow
        workflow_results = {
            "script_analyzer": None,
            "research": None,
            "visual_planner": None,
            "asset_finder": None,
            "ai_generator": None,
            "narration": None,
            "captioning": None,
            "map_animation": None,
            "timeline_builder": None,
            "editor": None,
            "quality_review": None,
        }

        # Stage 1: Analysis
        self.log_status("Stage 1: Analyzing script...")
        if "script_analyzer" in self.agents:
            result = self.agents["script_analyzer"].run({"script": script_text})
            workflow_results["script_analyzer"] = result.output
            if result.status == AgentStatus.FAILED:
                self.log_error("Script analysis failed")
                return AgentResult(self.name, AgentStatus.FAILED, workflow_results)

        # Stage 2: Research
        self.log_status("Stage 2: Research & fact-checking...")
        if "research" in self.agents:
            result = self.agents["research"].run({"script": script_text})
            workflow_results["research"] = result.output

        # Stage 3: Visual Planning
        self.log_status("Stage 3: Visual planning...")
        if "visual_planner" in self.agents and workflow_results["script_analyzer"]:
            shots = workflow_results["script_analyzer"]["shots"]
            result = self.agents["visual_planner"].run({"shots": shots})
            workflow_results["visual_planner"] = result.output

        # Stage 4: Asset Finding (parallel)
        self.log_status("Stage 4: Finding assets...")
        if "asset_finder" in self.agents and workflow_results["script_analyzer"]:
            shots = workflow_results["script_analyzer"]["shots"]
            result = self.agents["asset_finder"].run({"shots": shots})
            workflow_results["asset_finder"] = result.output

        # Stage 5: AI Generation (for gaps)
        self.log_status("Stage 5: Generating missing visuals...")
        if "ai_generator" in self.agents:
            gaps = workflow_results.get("asset_finder", {}).get("gaps", [])
            result = self.agents["ai_generator"].run({
                "shots": workflow_results.get("script_analyzer", {}).get("shots", []),
                "gaps": gaps
            })
            workflow_results["ai_generator"] = result.output

        # Stage 6: Narration Generation
        self.log_status("Stage 6: Generating narration...")
        if "narration" in self.agents:
            result = self.agents["narration"].run({
                "sections": workflow_results.get("script_analyzer", {}).get("shots", []),
                "output_dir": narration_dir
            })
            workflow_results["narration"] = result.output

        # Stage 7: Auto-Captioning
        self.log_status("Stage 7: Generating captions...")
        if "captioning" in self.agents:
            result = self.agents["captioning"].run({
                "narration_dir": narration_dir,
                "output_dir": Path("cache/captions"),
                "format": "srt"
            })
            workflow_results["captioning"] = result.output

        # Stage 8: Map Animations
        self.log_status("Stage 8: Creating map animations...")
        if "map_animation" in self.agents:
            result = self.agents["map_animation"].run({
                "shots": workflow_results.get("script_analyzer", {}).get("shots", []),
                "output_dir": Path("cache/visuals/maps")
            })
            workflow_results["map_animation"] = result.output

        # Stage 9: Timeline Building
        self.log_status("Stage 9: Building timeline...")
        if "timeline_builder" in self.agents:
            result = self.agents["timeline_builder"].run({
                "shots": workflow_results.get("script_analyzer", {}).get("shots", []),
                "narration_dir": narration_dir
            })
            workflow_results["timeline_builder"] = result.output

        # Stage 10: Editing
        self.log_status("Stage 10: Assembling video...")
        if "editor" in self.agents:
            result = self.agents["editor"].run(workflow_results["timeline_builder"])
            workflow_results["editor"] = result.output

        # Stage 8: Quality Review
        self.log_status("Stage 8: Quality review...")
        if "quality_review" in self.agents:
            result = self.agents["quality_review"].run(workflow_results["editor"])
            workflow_results["quality_review"] = result.output

        # Save project report
        self._save_project_report(workflow_results)

        output = {
            "project": self.project_name,
            "status": "complete",
            "workflow_results": workflow_results,
            "project_dir": str(self.project_dir)
        }

        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            output=output
        )

    def _save_project_report(self, results: Dict) -> None:
        """Save complete project report"""

        report = {
            "project": self.project_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "workflow_results": results,
            "statistics": {
                "total_shots": len(results.get("script_analyzer", {}).get("shots", [])),
                "assets_found": results.get("asset_finder", {}).get("total_assets_found", 0),
                "visuals_generated": results.get("ai_generator", {}).get("total_generated", 0),
            }
        }

        report_file = self.project_dir / "PROJECT_REPORT.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.log_status(f"Project report saved: {report_file}")
