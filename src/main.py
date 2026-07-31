"""
Main entry point for Documentary Studio.

Demonstrates the complete system with contract enforcement and quality gates.
"""

import logging
import json
from datetime import datetime

from .core.schemas import ProjectPlan
from .producer import Producer
from .agents import (
    ResearchAgent,
    FactCheckAgent,
    ScriptAnalyzerAgent,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_project() -> ProjectPlan:
    """Create test project plan"""
    return ProjectPlan(
        project_name="Dangote Refinery Documentary",
        topic="The Dangote Refinery represents Africa's economic independence through industrial infrastructure.",
        estimated_length_seconds=510,
        scene_count=8,
        estimated_budget=700.40,
        required_agents=[
            "Research Agent",
            "Fact Checker",
            "Script Analyzer",
            "Visual Alignment Agent",
            "Visual Planner",
            "Asset Finder",
            "AI Generator",
            "Timeline Builder",
            "Editor",
            "QA Reviewer",
            "Continuity & Story Flow Agent",
            "Audience Simulation Agent",
            "Re-Edit Agent",
            "Final Approval Agent",
        ],
        quality_thresholds={
            "fact_verification": 0.95,
            "visual_teaching": 0.90,
            "asset_coverage": 0.90,
            "qa_score": 0.90,
            "story_flow": 0.92,
            "audience_satisfaction": 0.92,
        }
    )


def main():
    """Execute documentary production"""
    logger.info("=" * 70)
    logger.info("AI DOCUMENTARY STUDIO - PRODUCTION START")
    logger.info("=" * 70)

    # Create project
    project = create_test_project()
    logger.info(f"Project: {project.project_name}")
    logger.info(f"Budget: ${project.estimated_budget:.2f}")

    # Initialize producer
    producer = Producer()
    logger.info("Producer initialized")

    # Register agents (simplified - only showing first 3)
    producer.register_agent("Research Agent", ResearchAgent())
    producer.register_agent("Fact Checker", FactCheckAgent())
    producer.register_agent("Script Analyzer", ScriptAnalyzerAgent())

    # Execute production
    logger.info("Starting production sequence...")

    result = producer.execute_production(project)

    # Print results
    logger.info("=" * 70)
    logger.info("PRODUCTION RESULT")
    logger.info("=" * 70)
    logger.info(json.dumps(result, indent=2))

    # Generate report
    report = producer.generate_report()
    logger.info("=" * 70)
    logger.info("PRODUCTION REPORT")
    logger.info("=" * 70)
    logger.info(json.dumps(report, indent=2))

    return result


if __name__ == "__main__":
    main()
