#!/usr/bin/env python3
"""
Captioning Agent — Auto-generate captions from narration using Whisper

Uses OpenAI Whisper for:
- Automatic speech-to-text transcription
- Timestamp generation
- SRT/VTT subtitle file creation
- Multi-language support
- Speaker identification (optional)
"""

from base_agent import BaseAgent, AgentResult, AgentStatus
from typing import Dict, Any, List
from pathlib import Path
import subprocess
import json
import re


class CaptioningAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Captioning",
            description="Auto-generate captions from audio using OpenAI Whisper"
        )

        # Whisper configuration
        self.api_key = "YOUR_OPENAI_API_KEY"  # Set from config
        self.model = "base"  # Options: tiny, base, small, medium, large
        self.language = "en"

        # Whisper quality levels
        self.models = {
            "tiny": {"size": "39M", "speed": "fastest", "accuracy": "low"},
            "base": {"size": "140M", "speed": "fast", "accuracy": "medium"},
            "small": {"size": "244M", "speed": "medium", "accuracy": "good"},
            "medium": {"size": "769M", "speed": "slow", "accuracy": "very_good"},
            "large": {"size": "1.5GB", "speed": "slowest", "accuracy": "excellent"},
        }

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Generate captions from audio files"""

        narration_dir = Path(input_data.get("narration_dir", "cache/narration"))
        output_dir = Path(input_data.get("output_dir", "cache/captions"))
        format_type = input_data.get("format", "srt")  # srt, vtt, or json

        if not narration_dir.exists():
            self.log_error(f"Narration directory not found: {narration_dir}")
            return AgentResult(self.name, AgentStatus.FAILED, {})

        output_dir.mkdir(parents=True, exist_ok=True)

        # Find all narration files
        audio_files = sorted(narration_dir.glob("section_*.mp3"))

        if not audio_files:
            self.log_error("No audio files found")
            return AgentResult(self.name, AgentStatus.FAILED, {})

        self.log_status(f"Generating captions for {len(audio_files)} audio files (format: {format_type})")

        captions_data = []
        total_duration = 0

        for i, audio_file in enumerate(audio_files, 1):
            self.log_status(f"Transcribing {i}/{len(audio_files)}: {audio_file.name}")

            result = self._transcribe_audio(audio_file, output_dir, format_type)

            if result.get("status") == "success":
                captions_data.append(result)
                total_duration += result.get("duration", 0)
            else:
                self.log_error(f"Failed to transcribe {audio_file.name}: {result.get('error')}")

        self.log_status(f"Generated captions for {len(captions_data)}/{len(audio_files)} files")

        output = {
            "total_files": len(audio_files),
            "captions_generated": len(captions_data),
            "output_dir": str(output_dir),
            "format": format_type,
            "captions": captions_data,
            "total_duration_seconds": total_duration,
            "model_used": self.model,
            "files": {
                "srt": str(output_dir / "captions.srt") if format_type == "srt" else None,
                "vtt": str(output_dir / "captions.vtt") if format_type == "vtt" else None,
                "json": str(output_dir / "captions.json") if format_type == "json" else None,
            }
        }

        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED if len(captions_data) == len(audio_files) else AgentStatus.FAILED,
            output=output
        )

    def _transcribe_audio(self, audio_file: Path, output_dir: Path, format_type: str) -> Dict:
        """Transcribe single audio file using Whisper"""

        try:
            # Use local Whisper (installed via pip install openai-whisper)
            result = self._run_whisper_local(audio_file)

            if not result:
                return {"status": "failed", "error": "Whisper transcription failed"}

            # Parse results and generate captions
            captions = self._generate_captions(result, format_type)

            # Save caption file
            section_num = audio_file.stem.split("_")[1]
            caption_file = output_dir / f"section_{section_num}.{self._get_extension(format_type)}"

            with open(caption_file, "w") as f:
                f.write(captions["content"])

            return {
                "status": "success",
                "section": section_num,
                "audio_file": str(audio_file),
                "caption_file": str(caption_file),
                "format": format_type,
                "duration": result.get("duration", 0),
                "text": result.get("text", ""),
                "segments": result.get("segments", [])
            }

        except Exception as e:
            return {
                "status": "failed",
                "error": str(e)
            }

    def _run_whisper_local(self, audio_file: Path) -> Dict:
        """Run local Whisper transcription"""

        try:
            # Run whisper CLI
            cmd = [
                "whisper",
                str(audio_file),
                "--model", self.model,
                "--language", self.language,
                "--output_format", "json",
                "--output_dir", "/tmp/whisper_output"
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                self.log_error(f"Whisper error: {result.stderr}")
                return None

            # Parse JSON output
            json_file = Path(f"/tmp/whisper_output/{audio_file.stem}.json")
            if json_file.exists():
                with open(json_file) as f:
                    return json.load(f)

        except subprocess.TimeoutExpired:
            self.log_error(f"Whisper transcription timed out for {audio_file.name}")
            return None
        except Exception as e:
            self.log_error(f"Whisper error: {str(e)}")
            return None

        return None

    def _generate_captions(self, whisper_result: Dict, format_type: str) -> Dict:
        """Generate captions in specified format"""

        segments = whisper_result.get("segments", [])
        text = whisper_result.get("text", "")

        if format_type == "srt":
            return self._generate_srt(segments)
        elif format_type == "vtt":
            return self._generate_vtt(segments)
        elif format_type == "json":
            return self._generate_json(segments, text)
        else:
            return self._generate_srt(segments)  # Default to SRT

    def _generate_srt(self, segments: List) -> Dict:
        """Generate SRT subtitle format"""

        lines = []

        for i, segment in enumerate(segments, 1):
            start = self._format_timestamp(segment["start"])
            end = self._format_timestamp(segment["end"])
            text = segment.get("text", "").strip()

            lines.append(f"{i}")
            lines.append(f"{start} --> {end}")
            lines.append(text)
            lines.append("")

        return {
            "format": "srt",
            "content": "\n".join(lines)
        }

    def _generate_vtt(self, segments: List) -> Dict:
        """Generate WebVTT subtitle format"""

        lines = ["WEBVTT", ""]

        for segment in segments:
            start = self._format_timestamp_vtt(segment["start"])
            end = self._format_timestamp_vtt(segment["end"])
            text = segment.get("text", "").strip()

            lines.append(f"{start} --> {end}")
            lines.append(text)
            lines.append("")

        return {
            "format": "vtt",
            "content": "\n".join(lines)
        }

    def _generate_json(self, segments: List, text: str) -> Dict:
        """Generate JSON format"""

        data = {
            "full_text": text,
            "segments": segments
        }

        return {
            "format": "json",
            "content": json.dumps(data, indent=2)
        }

    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp for SRT (HH:MM:SS,mmm)"""

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _format_timestamp_vtt(self, seconds: float) -> str:
        """Format timestamp for VTT (HH:MM:SS.mmm)"""

        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def _get_extension(self, format_type: str) -> str:
        """Get file extension for format"""

        extensions = {
            "srt": "srt",
            "vtt": "vtt",
            "json": "json"
        }

        return extensions.get(format_type, "srt")
