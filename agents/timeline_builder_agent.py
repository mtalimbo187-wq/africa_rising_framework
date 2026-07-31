#!/usr/bin/env python3
"""
Timeline Builder Agent — Sync visuals to narration

Creates precise timeline:
  0:00–0:05 Map of location
  0:05–0:08 Archival footage
  0:08–0:12 Interview/B-roll
  0:12–0:15 Statistics graphic
"""

from base_agent import BaseAgent, AgentResult, AgentStatus
from typing import Dict, Any, List
from pathlib import Path


class TimelineBuilderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Timeline Builder",
            description="Sync visuals to narration - create precise clip timeline"
        )

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Build synchronized timeline"""

        shots = input_data.get("shots", [])
        narration_dir = input_data.get("narration_dir")

        if not shots:
            self.log_error("No shots provided")
            return AgentResult(self.name, AgentStatus.FAILED, {})

        self.log_status(f"Building timeline for {len(shots)} shots")

        # Load narration durations
        narration_durations = self._get_narration_durations(narration_dir, len(shots))

        timeline = []
        current_time = 0.0

        for i, shot in enumerate(shots):
            # Use actual audio duration if available
            duration = narration_durations.get(i + 1, shot.get("duration", 3.0))

            clip = {
                "clip_number": i + 1,
                "shot_number": shot["shot_number"],
                "text": shot["text"][:60],
                "start_time": self._format_time(current_time),
                "end_time": self._format_time(current_time + duration),
                "duration": duration,
                "visual": shot.get("visual_type", "stock_footage"),
                "assets": shot.get("asset_priority", []),
                "transitions": {
                    "in": "fade" if i == 0 else "cross_fade",
                    "out": "fade" if i == len(shots) - 1 else "cross_fade"
                },
                "audio_file": f"section_{i+1}.mp3",
                "audio_duration": narration_durations.get(i + 1, 0)
            }

            timeline.append(clip)
            current_time += duration

        total_duration = current_time

        self.log_status(f"Timeline created: {self._format_time(total_duration)}")

        output = {
            "total_duration": total_duration,
            "total_clips": len(timeline),
            "timeline": timeline,
            "statistics": {
                "avg_clip_duration": total_duration / len(timeline) if timeline else 0,
                "narration_synced": True,
                "ready_for_editing": True
            }
        }

        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            output=output
        )

    def _get_narration_durations(self, narration_dir: Path, expected_count: int) -> Dict[int, float]:
        """Get duration of each narration file"""

        durations = {}

        if not narration_dir or not Path(narration_dir).exists():
            return durations

        # Try to get MP3 durations
        import subprocess
        from pathlib import Path

        for i in range(1, expected_count + 1):
            mp3_file = Path(narration_dir) / f"section_{i}.mp3"

            if mp3_file.exists():
                try:
                    result = subprocess.run(
                        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1:nokey=1", str(mp3_file)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.stdout:
                        durations[i] = float(result.stdout.strip())
                except:
                    pass

        return durations

    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS"""

        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
