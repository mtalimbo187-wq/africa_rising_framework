"""Claude API integration for script refinement"""

import os
from typing import Dict, Any
import anthropic
import logging

logger = logging.getLogger(__name__)


class ClaudeScriptRefiner:
    """Uses Claude to refine documentary scripts"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-opus-5"

    def refine_script(self, script: str, topic: str) -> Dict[str, Any]:
        """Refine documentary script for quality and engagement"""
        logger.info(f"Refining script for topic: {topic}")

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a documentary scriptwriter. Improve this documentary script for clarity, engagement, and factual accuracy.

Topic: {topic}

Script:
{script}

Provide the improved script with the following requirements:
1. Maintain the original topic and key facts
2. Improve narrative flow and pacing
3. Add vivid descriptions for visual elements
4. Ensure engaging narration tone
5. Keep it factually accurate

Return ONLY the improved script, no explanations."""
                }
            ]
        )

        refined_script = message.content[0].text

        return {
            "status": "success",
            "original_script": script,
            "refined_script": refined_script,
            "word_count_original": len(script.split()),
            "word_count_refined": len(refined_script.split()),
            "model": self.model
        }

    def generate_scene_descriptions(self, scene_text: str) -> Dict[str, Any]:
        """Generate detailed visual descriptions for scenes"""
        logger.info("Generating scene descriptions")

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""For this documentary scene narration, generate detailed visual descriptions that would guide video editors and visual creators:

Scene Text:
{scene_text}

Provide visual descriptions for:
1. Main visual elements (what should be shown)
2. Camera angles and movements
3. Color palette and mood
4. Suggested stock footage or AI-generated scenes
5. Transitions between visuals

Format as a structured guide."""
                }
            ]
        )

        descriptions = message.content[0].text

        return {
            "status": "success",
            "scene_text": scene_text,
            "visual_descriptions": descriptions,
            "model": self.model
        }

    def optimize_narration(self, narration_text: str, duration_seconds: int) -> Dict[str, Any]:
        """Optimize narration for pacing and clarity"""
        words_per_minute = 140  # Professional narration speed
        target_words = int((duration_seconds / 60) * words_per_minute)

        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": f"""Optimize this narration for professional documentary delivery at {words_per_minute} words per minute.

Target word count: ~{target_words} words (for {duration_seconds} seconds of audio)

Current narration:
{narration_text}

Requirements:
1. Adjust length to match target word count
2. Use clear, professional language
3. Add natural pauses where indicated with [pause]
4. Emphasize key facts
5. Maintain emotional tone

Return the optimized narration only."""
                }
            ]
        )

        optimized = message.content[0].text

        return {
            "status": "success",
            "original_narration": narration_text,
            "optimized_narration": optimized,
            "target_duration_seconds": duration_seconds,
            "target_word_count": target_words,
            "model": self.model
        }

    def fact_check_enhancement(self, facts: list[str]) -> Dict[str, Any]:
        """Enhance fact-checking with Claude reasoning"""
        logger.info(f"Enhancing fact-check for {len(facts)} facts")

        facts_text = "\n".join([f"{i+1}. {fact}" for i, fact in enumerate(facts)])

        message = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": f"""Review these documentary facts for accuracy and suggest improvements:

Facts:
{facts_text}

For each fact:
1. Assess likelihood of accuracy (high/medium/low)
2. Suggest any clarifications or additions
3. Flag any potentially controversial claims
4. Recommend citations or evidence

Format as a structured review."""
                }
            ]
        )

        review = message.content[0].text

        return {
            "status": "success",
            "facts": facts,
            "fact_review": review,
            "model": self.model
        }
