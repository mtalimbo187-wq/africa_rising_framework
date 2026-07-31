#!/usr/bin/env python3
"""Integration tests for the full pipeline"""

import unittest
import tempfile
from pathlib import Path
from core.prompt_manager import PromptManager, RoleTemplate
from core.license_manager import LicenseManager, LicenseType, UsageType
from core.advanced_qa import AdvancedQAChecker
from core.observability import ProductionLogger


class TestPromptManager(unittest.TestCase):
    """Test prompt management"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = PromptManager(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_prompt_initialization(self):
        # Initialize library
        from core.prompt_manager import initialize_prompt_library
        initialize_prompt_library()

    def test_role_templates(self):
        researcher_template = RoleTemplate.get_template("researcher")
        self.assertIn("meticulous", researcher_template.lower())

        visual_template = RoleTemplate.get_template("visual_strategist")
        self.assertIn("emmy", visual_template.lower())

    def test_prompt_interpolation(self):
        manager = self.manager
        template = "The agent is: {agent_type}"
        interpolated = manager.interpolate(template, {"agent_type": "researcher"})
        self.assertEqual(interpolated, "The agent is: researcher")


class TestLicenseManager(unittest.TestCase):
    """Test license tracking and attribution"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.manager = LicenseManager(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_track_asset(self):
        asset = self.manager.track_asset(
            asset_id="asset_1",
            source="pexels",
            url="https://pexels.com/123",
            license_type=LicenseType.CC0,
            credited_to="Pexels Contributor"
        )
        self.assertEqual(asset["asset_id"], "asset_1")
        self.assertEqual(asset["license"], "CC0")

    def test_usage_validation(self):
        self.manager.track_asset(
            asset_id="cc_by_asset",
            source="wikimedia",
            url="https://wikimedia.org/123",
            license_type=LicenseType.CC_BY_NC,
            credited_to="Wikimedia"
        )

        # Should fail for commercial use
        valid, msg = self.manager.validate_for_usage("cc_by_asset", UsageType.COMMERCIAL)
        self.assertFalse(valid)
        self.assertIn("noncommercial", msg.lower())

    def test_credits_generation(self):
        self.manager.track_asset(
            asset_id="asset_1",
            source="pexels",
            url="https://pexels.com/123",
            license_type=LicenseType.CC_BY,
            credited_to="Photographer Name",
            attribution_required=True
        )

        credits = self.manager.generate_credits_file("Test Project")
        self.assertIn("Photographer Name", credits)
        self.assertIn("CC-BY-4.0", credits)


class TestAdvancedQA(unittest.TestCase):
    """Test advanced QA checks"""

    def setUp(self):
        self.checker = AdvancedQAChecker()

    def test_pacing_detection(self):
        timeline = [
            {
                "clip_id": "clip_1",
                "shot_id": "shot_1",
                "start_time_seconds": 0.0,
                "end_time_seconds": 1.0  # Too fast!
            },
            {
                "clip_id": "clip_2",
                "shot_id": "shot_2",
                "start_time_seconds": 1.0,
                "end_time_seconds": 10.0  # Too slow!
            }
        ]

        result = self.checker.detect_pacing_issues(timeline)
        self.assertTrue(result["pacing_issues_found"])
        self.assertEqual(result["count"], 2)

    def test_duplicate_detection(self):
        timeline = [
            {"clip_id": "clip_1", "shot_id": "shot_1", "asset_ref": "asset_1"},
            {"clip_id": "clip_2", "shot_id": "shot_2", "asset_ref": "asset_1"},  # Duplicate!
            {"clip_id": "clip_3", "shot_id": "shot_3", "asset_ref": "asset_2"},
        ]

        result = self.checker.detect_duplicate_shots(timeline)
        self.assertTrue(result["duplicate_shots_found"])
        self.assertEqual(result["count"], 1)

    def test_resolution_validation(self):
        assets = [
            {"asset_id": "asset_1", "width": 1920, "height": 1080},  # OK
            {"asset_id": "asset_2", "width": 640, "height": 480},   # Too low!
        ]

        result = self.checker.detect_resolution_issues(assets)
        self.assertTrue(result["resolution_issues_found"])
        self.assertEqual(result["count"], 1)


class TestObservability(unittest.TestCase):
    """Test logging and observability"""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.logger = ProductionLogger(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_agent_logging(self):
        self.logger.log_agent_action(
            agent_name="research_agent",
            action_type="fact_checking",
            status="success",
            duration_ms=1250.5,
            cost_usd=0.05,
            model_used="gpt-4"
        )

        # Check that log file was created
        production_log = Path(self.temp_dir.name) / "production.jsonl"
        self.assertTrue(production_log.exists())

    def test_api_logging(self):
        self.logger.log_api_call(
            provider="ElevenLabs",
            endpoint="/v1/text-to-speech",
            cost_usd=0.03,
            response_time_ms=250.0
        )

        api_log = Path(self.temp_dir.name) / "api_calls.jsonl"
        self.assertTrue(api_log.exists())

    def test_telemetry_generation(self):
        self.logger.log_agent_action(
            agent_name="agent_1",
            action_type="action_1",
            status="success",
            duration_ms=100,
            cost_usd=0.10
        )

        telemetry = self.logger.generate_project_telemetry()
        self.assertIn("agents", telemetry)
        self.assertGreater(telemetry["total_cost_usd"], 0)


if __name__ == "__main__":
    unittest.main()
