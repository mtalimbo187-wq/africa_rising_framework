#!/usr/bin/env python3
"""
Prompt Engineering Library & Versioning

Centralized management of all agent prompts with versioning,
role templates, constraints, and retry policies.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime


class PromptManager:
    """Manages versioned prompts and role templates"""

    def __init__(self, prompt_dir: str = "prompts"):
        self.prompt_dir = Path(prompt_dir)
        self.prompt_dir.mkdir(exist_ok=True)
        self._load_prompts()
        self._load_changelog()

    def _load_prompts(self):
        """Load all versioned prompts from disk"""
        self.prompts = {}
        for file in self.prompt_dir.glob("*.txt"):
            agent_name = file.stem.rsplit("_v", 1)[0]
            if agent_name not in self.prompts:
                self.prompts[agent_name] = {}
            self.prompts[agent_name][file.stem] = file

    def _load_changelog(self):
        """Load prompt changelog"""
        changelog_file = self.prompt_dir / "PROMPT_CHANGELOG.md"
        if changelog_file.exists():
            with open(changelog_file) as f:
                self.changelog_content = f.read()
        else:
            self.changelog_content = ""

    def get_prompt(self, agent_name: str, version: str = "latest") -> str:
        """Get prompt for agent (latest version if not specified)"""
        if agent_name not in self.prompts:
            raise ValueError(f"No prompts found for agent: {agent_name}")

        if version == "latest":
            versions = sorted(self.prompts[agent_name].keys())
            if not versions:
                raise ValueError(f"No prompt versions for agent: {agent_name}")
            version = versions[-1]

        if version not in self.prompts[agent_name]:
            raise ValueError(f"Version {version} not found for agent {agent_name}")

        with open(self.prompts[agent_name][version]) as f:
            return f.read()

    def save_prompt(self, agent_name: str, version: str, content: str, changelog_entry: str):
        """Save new prompt version with changelog"""
        filename = self.prompt_dir / f"{agent_name}_{version}.txt"
        with open(filename, "w") as f:
            f.write(content)

        self._add_changelog_entry(agent_name, version, changelog_entry)
        self._load_prompts()

    def _add_changelog_entry(self, agent_name: str, version: str, entry: str):
        """Add entry to PROMPT_CHANGELOG.md"""
        changelog_file = self.prompt_dir / "PROMPT_CHANGELOG.md"
        timestamp = datetime.now().isoformat()

        entry_text = f"\n## {agent_name} v{version}\n**Date:** {timestamp}\n**Changes:** {entry}\n"

        if changelog_file.exists():
            with open(changelog_file, "a") as f:
                f.write(entry_text)
        else:
            with open(changelog_file, "w") as f:
                f.write(f"# Prompt Version Changelog\n{entry_text}")

    def interpolate(self, prompt: str, variables: Dict[str, str]) -> str:
        """Fill variables in prompt template"""
        for key, value in variables.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", value)
        return prompt


class RoleTemplate:
    """Pre-built role templates for agents"""

    RESEARCHER = """You are a meticulous documentary researcher with expertise in fact-checking and verification.

Your role:
- Extract and validate claims from the provided text
- Use provided sources to verify each claim
- Identify statistics, quotes, and assertions that require verification
- Mark confidence levels for each verification (0.0-1.0)
- Flag unsupported claims clearly

Constraints:
- ALWAYS cite sources for verifications
- NEVER invent sources or statistics
- MARK claims as "unverified" if sources don't confirm them
- FOCUS on factual accuracy over narrative flow

Output Format:
- For each claim: [VERIFIED | UNVERIFIED | PARTIAL] | Claim Text | Source(s)
- Confidence score for each verification"""

    VISUAL_STRATEGIST = """You are an Emmy-award-winning documentary visual strategist.

Your role:
- Analyze script shots and recommend optimal visual approaches
- Apply Emmy-standard 10-point visual hierarchy:
  1. Archival footage (authentic, highest priority)
  2. Documentary footage
  3. Interview clips
  4. B-roll from major archives (Internet Archive, Library of Congress)
  5. Professional stock footage (Pexels, Pixabay)
  6. Animated maps and data visualization
  7. Infographics and diagrams
  8. AI-generated video (Veo, Runway) - only when nothing else fits
  9. Illustrated sequences
  10. Text/title cards (lowest priority, use sparingly)
- Consider pacing: visual changes every 2-5 seconds
- Suggest color grading per emotion (documentary, investigative, empathetic, etc.)

Constraints:
- ALWAYS prefer authentic sources over AI-generated
- NEVER use AI video for claims that need archival evidence
- MARK confidence level for each suggestion
- CONSIDER Emmy standards for editing pace and composition"""

    SCRIPT_ANALYZER = """You are a precise script analyzer specializing in documentary structure.

Your role:
- Break script into shots (scenes/sections)
- Extract: Person, Place, Date, Emotion, Visual need, Map locations, Timeline events
- Estimate duration based on reading pace (~2.2 words per second)
- Identify entities: people, organizations, places, dates, concepts
- Mark emotional tone for each shot
- Note any special visual needs (maps, infographics, data)

Constraints:
- EXTRACT exactly as written, no paraphrasing
- IDENTIFY all proper nouns and entities
- MARK confidence for each extraction
- PRESERVE original meaning and context"""

    TIMELINE_BUILDER = """You are a precision editor specializing in audio-visual synchronization.

Your role:
- Sync narration timing to visual shots
- Build timeline with precise clip start/end times
- Match visual duration to narration duration
- Plan transitions between clips (fade, cross-fade, wipe)
- Add subtitles synchronized to narration
- Layer audio: narration + music + sound effects

Constraints:
- NEVER exceed shot duration with narration
- MARK any timing conflicts clearly
- ROUND times to nearest frame (0.04s @ 25fps)
- VERIFY audio sync within ±0.1s tolerance"""

    QA_REVIEWER = """You are a rigorous quality assurance reviewer for documentary films.

Your role:
- Verify all claims are fact-checked
- Check visuals are complete and high-resolution (≥1280x720)
- Detect timing issues: scenes too fast (<2s) or too slow (>8s)
- Check subtitle sync with narration
- Identify duplicate shots
- Detect audio clipping (peaks >-3dB)
- Rate overall production quality (0-100)

Constraints:
- FLAG every issue found, no exceptions
- CITE specific timestamps for problems
- SUGGEST fixes for each issue
- PROVIDE overall approval recommendation: APPROVED | NEEDS_REVISION | REJECTED"""

    @classmethod
    def get_template(cls, agent_type: str) -> str:
        """Get role template by agent type"""
        templates = {
            "researcher": cls.RESEARCHER,
            "visual_strategist": cls.VISUAL_STRATEGIST,
            "visual_planner": cls.VISUAL_STRATEGIST,
            "script_analyzer": cls.SCRIPT_ANALYZER,
            "timeline_builder": cls.TIMELINE_BUILDER,
            "quality_review": cls.QA_REVIEWER,
        }
        return templates.get(agent_type, "")


class RetryPolicy:
    """Retry policy for resilient prompt execution"""

    def __init__(self, max_retries: int = 3, backoff_seconds: float = 5):
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.attempt_history = []

    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Decide if should retry based on error type"""
        if attempt >= self.max_retries:
            return False

        retry_errors = [
            "RateLimitError",
            "ConnectionError",
            "TimeoutError",
            "APIError",
        ]

        return any(err in str(type(error)) for err in retry_errors)

    def record_attempt(self, attempt: int, success: bool, error: Optional[Exception] = None):
        """Record attempt history"""
        self.attempt_history.append({
            "attempt": attempt,
            "success": success,
            "error": str(error) if error else None,
            "timestamp": datetime.now().isoformat()
        })

    def get_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay"""
        return self.backoff_seconds * (2 ** (attempt - 1))


def initialize_prompt_library():
    """Initialize standard prompt library on first run"""
    prompt_dir = Path("prompts")
    prompt_dir.mkdir(exist_ok=True)

    # Create initial v1.0 prompts
    prompts = {
        "research_agent_v1.0.txt": RoleTemplate.RESEARCHER,
        "visual_planner_agent_v1.0.txt": RoleTemplate.VISUAL_STRATEGIST,
        "script_analyzer_agent_v1.0.txt": RoleTemplate.SCRIPT_ANALYZER,
        "timeline_builder_agent_v1.0.txt": RoleTemplate.TIMELINE_BUILDER,
        "quality_review_agent_v1.0.txt": RoleTemplate.QA_REVIEWER,
    }

    for filename, content in prompts.items():
        file_path = prompt_dir / filename
        if not file_path.exists():
            with open(file_path, "w") as f:
                f.write(content)

    # Create changelog
    changelog_file = prompt_dir / "PROMPT_CHANGELOG.md"
    if not changelog_file.exists():
        with open(changelog_file, "w") as f:
            f.write("""# Prompt Version Changelog

## Overview
This document tracks all prompt versions and changes.
Each agent maintains backward-compatible versions.

## Initial Release (v1.0)
- research_agent_v1.0: Fact-checking with source verification
- visual_planner_agent_v1.0: Emmy-standard visual hierarchy
- script_analyzer_agent_v1.0: Entity and shot extraction
- timeline_builder_agent_v1.0: Audio-visual synchronization
- quality_review_agent_v1.0: Production QA checklist
""")
