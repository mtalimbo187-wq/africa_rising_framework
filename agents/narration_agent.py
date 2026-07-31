#!/usr/bin/env python3
"""
Narration Agent — Generate professional TTS narration

Uses ElevenLabs for high-quality voice generation
- Multiple voices available
- Emotional variation
- Professional quality
- Fast generation
"""

from base_agent import BaseAgent, AgentResult, AgentStatus
from typing import Dict, Any, List
import requests
from pathlib import Path


class NarrationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Narration",
            description="Generate professional TTS narration using ElevenLabs"
        )

        # ElevenLabs configuration
        self.api_key = "YOUR_ELEVENLABS_KEY"  # Set from config
        self.api_url = "https://api.elevenlabs.io/v1"

        self.voices = {
            "george": {
                "voice_id": "JBFqnCBsd6RMkjVDRZzb",
                "name": "George",
                "description": "Deep, authoritative male voice - documentary style"
            },
            "bella": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",
                "name": "Bella",
                "description": "Clear, empathetic female voice"
            },
            "marcus": {
                "voice_id": "EXAVITQu4vr4xnSDxMaL",
                "name": "Marcus",
                "description": "Energetic male voice"
            }
        }

        self.model = "eleven_turbo_v2_5"  # Fast + high quality

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Generate narration from script sections"""

        sections = input_data.get("sections", [])
        output_dir = Path(input_data.get("output_dir", "cache/narration"))
        voice_choice = input_data.get("voice", "george")

        if not sections:
            self.log_error("No sections provided")
            return AgentResult(self.name, AgentStatus.FAILED, {})

        output_dir.mkdir(parents=True, exist_ok=True)
        self.log_status(f"Generating {len(sections)} narration sections with voice: {voice_choice}")

        generated = []
        total_cost = 0

        for i, section in enumerate(sections, 1):
            text = section.get("text", "")
            if not text:
                continue

            self.log_status(f"Section {i}/{len(sections)}: {len(text)} chars")

            result = self._generate_section(text, i, voice_choice, output_dir)

            if result.get("status") == "success":
                generated.append(result)
                # Estimate cost: $0.03 per minute, ~200 words per minute
                word_count = len(text.split())
                estimated_minutes = word_count / 200
                estimated_cost = estimated_minutes * 0.03
                total_cost += estimated_cost
            else:
                self.log_error(f"Section {i} failed: {result.get('error')}")

        self.log_status(f"Generated {len(generated)}/{len(sections)} sections (${total_cost:.2f})")

        output = {
            "total_sections": len(sections),
            "generated": len(generated),
            "output_dir": str(output_dir),
            "audio_files": generated,
            "estimated_cost": total_cost,
            "voice_used": voice_choice,
            "model": self.model
        }

        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED if len(generated) == len(sections) else AgentStatus.FAILED,
            output=output
        )

    def _generate_section(self, text: str, section_num: int, voice: str, output_dir: Path) -> Dict:
        """Generate single narration section"""

        voice_id = self.voices.get(voice, self.voices["george"])["voice_id"]
        output_file = output_dir / f"section_{section_num}.mp3"

        try:
            # Call ElevenLabs API
            headers = {
                "xi-api-key": self.api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "text": text,
                "model_id": self.model,
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }

            response = requests.post(
                f"{self.api_url}/text-to-speech/{voice_id}",
                json=payload,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                # Save audio file
                with open(output_file, "wb") as f:
                    f.write(response.content)

                # Get duration
                import subprocess
                try:
                    result = subprocess.run(
                        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", str(output_file)],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    duration = float(result.stdout.strip()) if result.stdout else 0
                except:
                    duration = 0

                return {
                    "status": "success",
                    "section": section_num,
                    "file": str(output_file),
                    "duration": duration,
                    "voice": voice
                }
            else:
                return {
                    "status": "failed",
                    "section": section_num,
                    "error": f"API error {response.status_code}"
                }

        except Exception as e:
            return {
                "status": "failed",
                "section": section_num,
                "error": str(e)
            }
