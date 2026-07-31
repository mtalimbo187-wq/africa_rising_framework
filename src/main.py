"""
Main entry point for Documentary Studio.

Demonstrates the complete system with contract enforcement and quality gates.
"""

import logging
import json
from datetime import datetime

from .core.schemas import ProjectPlan
from .producer import Producer
from .dashboard import ProducerDashboard
from .agents import (
    ResearchAgent,
    FactCheckAgent,
    ScriptAnalyzerAgent,
    VisualAlignmentAgent,
    VisualPlannerAgent,
    AssetFinderAgent,
    AIGeneratorAgent,
    TimelineBuilderAgent,
    EditorAgent,
    QAReviewerAgent,
    ContinuityAgent,
    AudienceSimulatorAgent,
    ReEditAgent,
    FinalApprovalAgent,
    NarrationAgent,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_project(full_length: bool = False) -> ProjectPlan:
    """Create test project plan"""
    if full_length:
        # Full-length documentary script
        topic = """
        The Dangote Refinery represents a transformative chapter in Africa's industrial development. Located in Lagos, Nigeria,
        this state-of-the-art facility processes 650,000 barrels per day, making it one of the world's largest refineries.

        Billionaire Aliko Dangote invested $20 billion in this infrastructure, demonstrating unprecedented confidence in Nigeria's
        industrial potential. The refinery's capacity to process crude oil into refined petroleum products addresses a critical gap
        in Africa's energy independence.

        The facility employs advanced manufacturing techniques and represents the cutting edge of petrochemical technology.
        With its modern production capabilities, the Dangote Refinery reduces Nigeria's dependence on imported refined products,
        strengthening the nation's economic sovereignty.

        This achievement showcases African entrepreneurship and industrial excellence. The refinery's success has inspired
        similar investments across the continent, catalyzing a new wave of industrial development. It stands as a monument to
        the possibilities when vision meets capital and execution.

        From construction to operation, the Dangote Refinery has created thousands of jobs and strengthened Nigeria's position
        as an industrial powerhouse. Its strategic location in Lagos, Africa's commercial hub, positions it as a gateway for
        refined products throughout the continent and beyond.
        """
        return ProjectPlan(
            project_name="Dangote Refinery: Africa's Industrial Renaissance",
            topic=topic,
            estimated_length_seconds=900,  # 15 minutes
            scene_count=5,
            estimated_budget=2500.00,
            required_agents=[
                "Research Agent", "Fact Checker", "Script Analyzer",
                "Visual Alignment Agent", "Visual Planner", "Asset Finder",
                "AI Generator", "Timeline Builder", "Editor",
                "QA Reviewer", "Continuity & Story Flow Agent",
                "Audience Simulation Agent", "Re-Edit Agent", "Final Approval Agent",
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

    # Short test project
    return ProjectPlan(
        project_name="Dangote Refinery Documentary",
        topic="The Dangote Refinery in Lagos, Nigeria processes 650,000 barrels per day. This represents Africa's economic independence through industrial infrastructure. Aliko Dangote built this facility as a $20 billion investment. The refinery demonstrates Nigeria's capacity for advanced manufacturing and petroleum processing.",
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

    # Register all 15 agents
    # Information Layer
    producer.register_agent("Research Agent", ResearchAgent())
    producer.register_agent("Fact Checker", FactCheckAgent())
    producer.register_agent("Script Analyzer", ScriptAnalyzerAgent())

    # Visual Layer
    producer.register_agent("Visual Alignment Agent", VisualAlignmentAgent())
    producer.register_agent("Visual Planner", VisualPlannerAgent())
    producer.register_agent("Asset Finder", AssetFinderAgent())

    # Production Layer
    producer.register_agent("AI Generator", AIGeneratorAgent())
    producer.register_agent("Timeline Builder", TimelineBuilderAgent())
    producer.register_agent("Editor", EditorAgent())

    # Quality Layer
    producer.register_agent("QA Reviewer", QAReviewerAgent())
    producer.register_agent("Continuity & Story Flow Agent", ContinuityAgent())
    producer.register_agent("Audience Simulation Agent", AudienceSimulatorAgent())
    producer.register_agent("Re-Edit Agent", ReEditAgent())

    # Export Layer
    producer.register_agent("Final Approval Agent", FinalApprovalAgent())
    producer.register_agent("Narration Agent", NarrationAgent())

    # Execute production
    logger.info("Starting production sequence...")

    result = producer.execute_production(project)

    # Print results
    logger.info("=" * 70)
    logger.info("PRODUCTION RESULT")
    logger.info("=" * 70)
    logger.info(json.dumps(result, indent=2, default=str))

    # Generate report
    report = producer.generate_report()
    logger.info("=" * 70)
    logger.info("PRODUCTION REPORT")
    logger.info("=" * 70)
    logger.info(json.dumps(report, indent=2, default=str))

    # Generate and save dashboard
    logger.info("=" * 70)
    logger.info("GENERATING DASHBOARD")
    logger.info("=" * 70)
    dashboard = ProducerDashboard(producer)
    dashboard_path = dashboard.save_html_dashboard("dashboard.html")
    logger.info(f"Dashboard saved: {dashboard_path}")
    logger.info("Dashboard available at: file://" + dashboard_path)

    return result


if __name__ == "__main__":
    main()
