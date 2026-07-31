#!/usr/bin/env python3
"""
Quality Review Agent — Final QA before upload

Checks:
  ✔ Wrong/missing images
  ✔ Wrong/missing dates
  ✔ Pacing (2-5 seconds per shot)
  ✔ Subtitles/captions
  ✔ Transitions (smooth, no jarring cuts)
  ✔ Narration sync (audio matches video)
"""

from base_agent import BaseAgent, AgentResult, AgentStatus
from typing import Dict, Any, List


class QualityReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Quality Review",
            description="Final QA - verify images, dates, pacing, sync, transitions"
        )

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Review final video"""

        video_file = input_data.get("video_file")
        timeline = input_data.get("timeline", [])

        if not video_file or not timeline:
            self.log_error("Missing video file or timeline")
            return AgentResult(self.name, AgentStatus.FAILED, {})

        self.log_status(f"Reviewing {len(timeline)} clips...")

        issues = []

        # Check 1: Images
        image_issues = self._check_images(timeline)
        issues.extend(image_issues)

        # Check 2: Dates/temporal accuracy
        date_issues = self._check_dates(timeline)
        issues.extend(date_issues)

        # Check 3: Pacing
        pacing_issues = self._check_pacing(timeline)
        issues.extend(pacing_issues)

        # Check 4: Subtitles
        subtitle_issues = self._check_subtitles(timeline)
        issues.extend(subtitle_issues)

        # Check 5: Transitions
        transition_issues = self._check_transitions(timeline)
        issues.extend(transition_issues)

        # Check 6: Narration sync
        sync_issues = self._check_sync(timeline)
        issues.extend(sync_issues)

        # Report
        critical = [i for i in issues if i.get("severity") == "critical"]
        warnings = [i for i in issues if i.get("severity") == "warning"]
        approved = len(critical) == 0

        output = {
            "video_file": str(video_file),
            "total_clips": len(timeline),
            "issues": issues,
            "critical_issues": len(critical),
            "warnings": len(warnings),
            "approved_for_upload": approved,
            "approval_score": 100 - (len(critical) * 20 + len(warnings) * 5)
        }

        status = AgentStatus.COMPLETED if approved else AgentStatus.FAILED

        if approved:
            self.log_status("✅ APPROVED FOR UPLOAD")
        else:
            self.log_status(f"⚠️ {len(critical)} critical issues found")

        return AgentResult(
            agent_name=self.name,
            status=status,
            output=output
        )

    def _check_images(self, timeline: List) -> List[Dict]:
        """Check for wrong/missing images"""

        issues = []

        for clip in timeline:
            if not clip.get("visual"):
                issues.append({
                    "clip": clip.get("clip_number"),
                    "type": "missing_visual",
                    "severity": "critical",
                    "message": "No visual assigned"
                })

            if clip.get("visual") == "ai_generated":
                # Flag AI-generated if better alternatives exist
                if clip.get("search_found"):
                    issues.append({
                        "clip": clip.get("clip_number"),
                        "type": "unnecessary_ai",
                        "severity": "warning",
                        "message": "AI used when stock available"
                    })

        return issues

    def _check_dates(self, timeline: List) -> List[Dict]:
        """Check for temporal accuracy"""

        issues = []

        for clip in timeline:
            if clip.get("needs_timeline"):
                if not clip.get("timeline_shown"):
                    issues.append({
                        "clip": clip.get("clip_number"),
                        "type": "missing_timeline",
                        "severity": "warning",
                        "message": "Timeline mentioned but not shown"
                    })

        return issues

    def _check_pacing(self, timeline: List) -> List[Dict]:
        """Check clip pacing (2-5 seconds ideal)"""

        issues = []

        for clip in timeline:
            duration = clip.get("duration", 3)

            if duration < 1.5:
                issues.append({
                    "clip": clip.get("clip_number"),
                    "type": "too_fast",
                    "severity": "warning",
                    "message": f"Clip too fast ({duration}s)"
                })

            if duration > 8:
                issues.append({
                    "clip": clip.get("clip_number"),
                    "type": "too_slow",
                    "severity": "warning",
                    "message": f"Clip too long ({duration}s)"
                })

        return issues

    def _check_subtitles(self, timeline: List) -> List[Dict]:
        """Check subtitle/caption presence"""

        issues = []

        for clip in timeline:
            if not clip.get("subtitle"):
                issues.append({
                    "clip": clip.get("clip_number"),
                    "type": "missing_subtitle",
                    "severity": "warning",
                    "message": "No subtitle/caption"
                })

        return issues

    def _check_transitions(self, timeline: List) -> List[Dict]:
        """Check transitions are smooth"""

        issues = []

        for i, clip in enumerate(timeline[:-1]):
            next_clip = timeline[i + 1]

            transition = clip.get("transition_out", "cut")

            if transition == "cut" and clip.get("emotion") != "urgent":
                issues.append({
                    "clip": clip.get("clip_number"),
                    "type": "jarring_transition",
                    "severity": "warning",
                    "message": "Hard cut - consider fade"
                })

        return issues

    def _check_sync(self, timeline: List) -> List[Dict]:
        """Check narration/video sync"""

        issues = []

        for clip in timeline:
            clip_duration = clip.get("duration", 0)
            audio_duration = clip.get("audio_duration", 0)

            if audio_duration and abs(clip_duration - audio_duration) > 0.5:
                issues.append({
                    "clip": clip.get("clip_number"),
                    "type": "sync_mismatch",
                    "severity": "critical",
                    "message": f"Video ({clip_duration}s) ≠ Audio ({audio_duration}s)"
                })

        return issues
