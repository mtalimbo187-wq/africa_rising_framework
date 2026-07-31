#!/usr/bin/env python3
"""
Advanced Quality Assurance Checks

Extends Quality Review with:
- Unsupported claims detection
- Subtitle drift detection
- Pacing issue detection
- Duplicate shot detection
- Resolution validation
- Audio clipping detection
"""

from typing import Dict, List, Any, Tuple
from pathlib import Path
import json
import subprocess
from datetime import datetime


class AdvancedQAChecker:
    """Advanced QA checks for production quality"""

    def __init__(self, tolerance_sync: float = 0.1, min_scene_duration: float = 2.0, max_scene_duration: float = 8.0):
        self.tolerance_sync = tolerance_sync  # ±0.1s tolerance for audio sync
        self.min_scene_duration = min_scene_duration
        self.max_scene_duration = max_scene_duration
        self.min_resolution = (1280, 720)
        self.audio_clipping_threshold = -3.0  # dB

    def detect_unsupported_claims(self, narration: List[Dict], research_results: Dict) -> Dict:
        """Compare narration claims vs research verification results"""
        unsupported = []

        for claim in narration:
            claim_text = claim.get("text", "")
            verified = research_results.get(claim_text, {}).get("verified", False)

            if not verified:
                unsupported.append({
                    "claim": claim_text,
                    "timestamp": claim.get("timestamp", "unknown"),
                    "severity": "high",
                    "recommendation": "Add source or revise claim to match verified facts"
                })

        return {
            "unsupported_claims_found": len(unsupported) > 0,
            "count": len(unsupported),
            "issues": unsupported
        }

    def detect_subtitle_drift(self, timeline_clips: List[Dict], subtitles: List[Dict]) -> Dict:
        """Check if subtitles exceed narration duration"""
        drifts = []

        for subtitle in subtitles:
            sub_end = subtitle.get("end_time", 0)
            shot_id = subtitle.get("shot_id")

            clip = next((c for c in timeline_clips if c.get("shot_id") == shot_id), None)
            if not clip:
                continue

            clip_end = clip.get("end_time_seconds", 0)

            if sub_end > clip_end + self.tolerance_sync:
                drift = sub_end - clip_end
                drifts.append({
                    "subtitle": subtitle.get("text", ""),
                    "shot_id": shot_id,
                    "subtitle_end": sub_end,
                    "clip_end": clip_end,
                    "drift_seconds": drift,
                    "severity": "high" if drift > 0.5 else "low",
                    "recommendation": f"Trim subtitle by {drift:.2f}s or extend clip"
                })

        return {
            "subtitle_drift_detected": len(drifts) > 0,
            "count": len(drifts),
            "issues": drifts
        }

    def detect_pacing_issues(self, timeline_clips: List[Dict]) -> Dict:
        """Check for pacing issues: too fast (<2s) or too slow (>8s)"""
        pacing_issues = []

        for clip in timeline_clips:
            start = clip.get("start_time_seconds", 0)
            end = clip.get("end_time_seconds", 0)
            duration = end - start

            if duration < self.min_scene_duration:
                pacing_issues.append({
                    "clip_id": clip.get("clip_id"),
                    "shot_id": clip.get("shot_id"),
                    "duration": duration,
                    "issue": "Too fast (Emmy standard: min 2s)",
                    "severity": "medium",
                    "recommendation": f"Extend scene to {self.min_scene_duration}s or add transition"
                })

            elif duration > self.max_scene_duration:
                pacing_issues.append({
                    "clip_id": clip.get("clip_id"),
                    "shot_id": clip.get("shot_id"),
                    "duration": duration,
                    "issue": "Too slow (Emmy standard: max 8s)",
                    "severity": "medium",
                    "recommendation": f"Trim scene to {self.max_scene_duration}s or add cutaway"
                })

        return {
            "pacing_issues_found": len(pacing_issues) > 0,
            "count": len(pacing_issues),
            "issues": pacing_issues
        }

    def detect_duplicate_shots(self, timeline_clips: List[Dict]) -> Dict:
        """Detect consecutive clips using same asset"""
        duplicates = []
        prev_asset = None
        prev_clip_id = None

        for i, clip in enumerate(timeline_clips):
            asset_ref = clip.get("asset_ref")

            if asset_ref == prev_asset:
                duplicates.append({
                    "first_clip": prev_clip_id,
                    "second_clip": clip.get("clip_id"),
                    "asset_ref": asset_ref,
                    "severity": "medium",
                    "recommendation": "Replace one with different asset or add transition"
                })

            prev_asset = asset_ref
            prev_clip_id = clip.get("clip_id")

        return {
            "duplicate_shots_found": len(duplicates) > 0,
            "count": len(duplicates),
            "issues": duplicates
        }

    def detect_resolution_issues(self, assets: List[Dict]) -> Dict:
        """Check all assets meet minimum resolution"""
        low_res = []

        for asset in assets:
            width = asset.get("width")
            height = asset.get("height")

            if width and height:
                if width < self.min_resolution[0] or height < self.min_resolution[1]:
                    low_res.append({
                        "asset_id": asset.get("asset_id"),
                        "resolution": f"{width}x{height}",
                        "required": f"{self.min_resolution[0]}x{self.min_resolution[1]}",
                        "severity": "high",
                        "recommendation": "Replace with higher resolution asset"
                    })

        return {
            "resolution_issues_found": len(low_res) > 0,
            "count": len(low_res),
            "issues": low_res
        }

    def detect_audio_clipping(self, audio_file: str) -> Dict:
        """Use ffmpeg to detect audio clipping (peaks > -3dB)"""
        try:
            cmd = [
                "ffmpeg",
                "-i", audio_file,
                "-filter:a", "volumedetect",
                "-f", "null",
                "-"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            output = result.stderr

            clipping_detected = False
            max_volume = 0.0

            for line in output.split("\n"):
                if "max_volume" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "dB" in part:
                            try:
                                max_volume = float(parts[i-1])
                            except:
                                pass

            if max_volume > self.audio_clipping_threshold:
                clipping_detected = True

            return {
                "clipping_detected": clipping_detected,
                "max_volume_db": max_volume,
                "threshold_db": self.audio_clipping_threshold,
                "recommendation": "Reduce audio level to prevent distortion" if clipping_detected else "Audio levels acceptable"
            }

        except Exception as e:
            return {
                "clipping_detected": False,
                "error": str(e),
                "recommendation": "Could not analyze audio"
            }

    def run_all_checks(self, project_data: Dict) -> Dict:
        """Run all QA checks and generate comprehensive report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": 6,
            "passed_checks": 0,
            "failed_checks": 0,
            "issues_found": 0
        }

        # Run each check
        checks = [
            ("unsupported_claims", self.detect_unsupported_claims(
                project_data.get("narration", []),
                project_data.get("research_results", {})
            )),
            ("subtitle_drift", self.detect_subtitle_drift(
                project_data.get("timeline", []),
                project_data.get("subtitles", [])
            )),
            ("pacing", self.detect_pacing_issues(
                project_data.get("timeline", [])
            )),
            ("duplicate_shots", self.detect_duplicate_shots(
                project_data.get("timeline", [])
            )),
            ("resolution", self.detect_resolution_issues(
                project_data.get("assets", [])
            )),
        ]

        for check_name, check_result in checks:
            report[check_name] = check_result
            if check_result.get(f"{check_name}_found" if check_name != "unsupported_claims" else "unsupported_claims_found"):
                report["failed_checks"] += 1
                report["issues_found"] += check_result.get("count", 0)
            else:
                report["passed_checks"] += 1

        # Audio clipping check if audio file provided
        if project_data.get("audio_file"):
            audio_check = self.detect_audio_clipping(project_data["audio_file"])
            report["audio_clipping"] = audio_check
            if audio_check.get("clipping_detected"):
                report["failed_checks"] += 1
                report["issues_found"] += 1
            else:
                report["passed_checks"] += 1

        # Overall QA score
        if report["total_checks"] > 0:
            report["qa_score"] = (report["passed_checks"] / report["total_checks"]) * 100
        else:
            report["qa_score"] = 0

        report["approval_status"] = (
            "APPROVED" if report["qa_score"] >= 90 else
            "NEEDS_REVISION" if report["qa_score"] >= 70 else
            "REJECTED"
        )

        return report

    def generate_qa_report(self, project_data: Dict, output_file: str = "qa_report.json"):
        """Generate and save QA report"""
        report = self.run_all_checks(project_data)

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        return report
