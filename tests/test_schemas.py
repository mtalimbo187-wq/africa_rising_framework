#!/usr/bin/env python3
"""Unit tests for data contracts and schemas"""

import unittest
from datetime import datetime
from core.schemas import (
    Shot, Asset, Timeline, AgentMessage, QualityScore,
    EmotionType, VisualType, LicenseType, TransitionType
)


class TestShot(unittest.TestCase):
    """Test Shot schema"""

    def test_valid_shot(self):
        shot = Shot(
            shot_id="shot_1",
            shot_number=1,
            text="Documentary narration",
            duration_seconds=5.0,
            emotions=[EmotionType.DOCUMENTARY],
            visual_type=VisualType.STOCK_FOOTAGE
        )
        self.assertEqual(shot.shot_number, 1)
        self.assertEqual(shot.duration_seconds, 5.0)

    def test_shot_invalid_duration(self):
        with self.assertRaises(ValueError):
            Shot(
                shot_id="shot_invalid",
                shot_number=1,
                text="Bad narration",
                duration_seconds=-1  # Invalid
            )

    def test_shot_min_max_duration(self):
        shot = Shot(
            shot_id="shot_2",
            shot_number=2,
            text="Narration",
            duration_seconds=3.0
        )
        self.assertEqual(shot.min_visual_duration, 2.0)
        self.assertEqual(shot.max_visual_duration, 8.0)


class TestAsset(unittest.TestCase):
    """Test Asset schema"""

    def test_valid_asset(self):
        asset = Asset(
            asset_id="asset_1",
            source="pexels",
            url="https://pexels.com/video/123",
            license=LicenseType.CC0,
            search_query="documentary footage"
        )
        self.assertEqual(asset.asset_id, "asset_1")
        self.assertEqual(asset.license, LicenseType.CC0)

    def test_asset_with_dimensions(self):
        asset = Asset(
            asset_id="asset_2",
            source="archive.org",
            url="https://archive.org/123",
            license=LicenseType.PUBLIC_DOMAIN,
            width=1920,
            height=1080,
            search_query="archival footage"
        )
        self.assertEqual(asset.width, 1920)
        self.assertEqual(asset.height, 1080)


class TestTimeline(unittest.TestCase):
    """Test Timeline schema"""

    def test_valid_timeline_clip(self):
        clip = Timeline(
            clip_id="clip_1",
            shot_id="shot_1",
            start_time_seconds=0.0,
            end_time_seconds=5.0,
            asset_ref="asset_1"
        )
        self.assertEqual(clip.clip_id, "clip_1")
        self.assertEqual(clip.end_time_seconds, 5.0)

    def test_timeline_invalid_time_order(self):
        with self.assertRaises(ValueError):
            Timeline(
                clip_id="bad_clip",
                shot_id="shot_1",
                start_time_seconds=5.0,
                end_time_seconds=2.0,  # End before start
                asset_ref="asset_1"
            )

    def test_timeline_transitions(self):
        clip = Timeline(
            clip_id="clip_2",
            shot_id="shot_2",
            start_time_seconds=5.0,
            end_time_seconds=8.0,
            asset_ref="asset_2",
            transition_type=TransitionType.CROSS_FADE,
            transition_duration=0.5
        )
        self.assertEqual(clip.transition_type, TransitionType.CROSS_FADE)


class TestQualityScore(unittest.TestCase):
    """Test QualityScore schema"""

    def test_valid_quality_score(self):
        score = QualityScore(
            overall_score=85.0,
            claims_verified=True,
            visuals_complete=True,
            audio_sync_quality=90.0,
            subtitle_quality=88.0,
            approval_status="approved"
        )
        self.assertEqual(score.overall_score, 85.0)
        self.assertTrue(score.claims_verified)

    def test_quality_score_with_issues(self):
        score = QualityScore(
            overall_score=65.0,
            claims_verified=False,
            visuals_complete=False,
            unsupported_claims=["Claim 1", "Claim 2"],
            missing_visuals=[3, 5],
            pacing_issues=[{"clip_id": "clip_1", "issue": "Too fast"}],
            approval_status="needs_revision"
        )
        self.assertEqual(len(score.unsupported_claims), 2)
        self.assertEqual(len(score.missing_visuals), 2)


class TestAgentMessage(unittest.TestCase):
    """Test inter-agent communication"""

    def test_agent_message(self):
        message = AgentMessage(
            sender="research_agent",
            recipient="visual_planner",
            message_type="response",
            payload={"verified_claims": 10}
        )
        self.assertEqual(message.sender, "research_agent")
        self.assertEqual(message.recipient, "visual_planner")
        self.assertIsNotNone(message.timestamp)


if __name__ == "__main__":
    unittest.main()
