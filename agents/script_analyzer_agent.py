#!/usr/bin/env python3
"""
Script Analyzer Agent — Break down script into shots with metadata

Input: Raw script text
Output: Shot-by-shot analysis with entities, timing, and visual requirements

Format per shot:
  Person: Entity type
  Place: Location
  Date: Temporal marker
  Emotion: Tone
  Visual: Suggested asset type
  Map: Geographic context needed?
  Timeline: Temporal progression needed?
"""

from base_agent import BaseAgent, AgentResult, AgentStatus
from typing import Dict, Any, List
import re


class ScriptAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Script Analyzer",
            description="Break script into shots with metadata (Person, Place, Date, Emotion, Visual, Map, Timeline)"
        )

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Analyze script and return structured shots"""

        script_text = input_data.get("script", "")
        if not script_text:
            self.log_error("No script provided")
            return AgentResult(self.name, AgentStatus.FAILED, {})

        # Split into sentences
        sentences = self._split_sentences(script_text)
        self.log_status(f"Split into {len(sentences)} sentences")

        # Analyze each sentence
        shots = []
        for i, sentence in enumerate(sentences, 1):
            shot = self._analyze_sentence(sentence, i)
            shots.append(shot)

        self.log_status(f"Analyzed {len(shots)} shots")

        # Calculate totals
        total_duration = sum(s.get("duration", 0) for s in shots)
        visual_breakdown = self._count_visuals(shots)

        output = {
            "total_shots": len(shots),
            "estimated_duration_seconds": total_duration,
            "visual_breakdown": visual_breakdown,
            "shots": shots,
            "statistics": {
                "avg_duration_per_shot": total_duration / len(shots) if shots else 0,
                "shots_needing_map": sum(1 for s in shots if s.get("needs_map")),
                "shots_needing_timeline": sum(1 for s in shots if s.get("needs_timeline")),
            }
        }

        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            output=output
        )

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""

        # Split on period/exclamation/question, but handle abbreviations
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _analyze_sentence(self, sentence: str, shot_number: int) -> Dict[str, Any]:
        """Analyze individual sentence"""

        shot = {
            "shot_number": shot_number,
            "text": sentence,
            "duration": self._estimate_duration(sentence),

            # Core analysis
            "person": self._extract_person(sentence),
            "place": self._extract_place(sentence),
            "date": self._extract_date(sentence),
            "emotion": self._detect_emotion(sentence),
            "visual_type": self._suggest_visual(sentence),

            # Context flags
            "needs_map": self._needs_map(sentence),
            "needs_timeline": self._needs_timeline(sentence),
            "needs_comparison": self._needs_comparison(sentence),
            "needs_statistic": self._needs_statistic(sentence),

            # Asset priorities
            "asset_priority": self._get_asset_priority(sentence),
            "search_queries": self._generate_queries(sentence),
        }

        return shot

    def _estimate_duration(self, sentence: str) -> float:
        """Estimate duration in seconds (~2.2 words/sec)"""

        word_count = len(sentence.split())
        return max(2.0, word_count / 2.2)

    def _extract_person(self, sentence: str) -> str:
        """Extract person/entity type"""

        roles = {
            "worker": ["worker", "employee", "moderator", "contractor", "laborer"],
            "organization": ["meta", "facebook", "google", "company", "firm"],
            "government": ["president", "minister", "government", "official"],
            "group": ["team", "crew", "group", "people"],
        }

        sentence_lower = sentence.lower()

        for role, keywords in roles.items():
            if any(kw in sentence_lower for kw in keywords):
                return role

        return "unknown"

    def _extract_place(self, sentence: str) -> str:
        """Extract location"""

        locations = {
            "africa": ["africa", "nigeria", "kenya", "uganda", "ghana", "ethiopia"],
            "us": ["us", "united states", "america", "american"],
            "asia": ["asia", "china", "india", "vietnam", "philippines"],
            "other": ["country", "region", "location", "place"]
        }

        sentence_lower = sentence.lower()

        for place, keywords in locations.items():
            if any(kw in sentence_lower for kw in keywords):
                return place

        return "unspecified"

    def _extract_date(self, sentence: str) -> str:
        """Extract temporal marker"""

        # Look for years
        years = re.findall(r'\b(19|20)\d{2}\b', sentence)
        if years:
            return f"Year {years[0]}"

        # Look for temporal words
        temporal = {
            "past": ["was", "were", "had", "since", "ago", "2016", "2019", "2020"],
            "present": ["is", "are", "currently", "now", "today", "continues"],
            "future": ["will", "is going to", "plans to", "by 2030"],
        }

        sentence_lower = sentence.lower()

        for period, keywords in temporal.items():
            if any(kw in sentence_lower for kw in keywords):
                return period

        return "unspecified"

    def _detect_emotion(self, sentence: str) -> str:
        """Detect emotional tone"""

        emotions = {
            "critical": ["exploitation", "abuse", "unfair", "injustice", "suffering"],
            "empathetic": ["worker", "people", "family", "deserve", "human"],
            "urgent": ["crisis", "urgent", "alarming", "shocking", "immediate"],
            "hopeful": ["solution", "progress", "change", "hope", "improve"],
            "investigative": ["reveal", "expose", "discover", "investigate", "show"],
            "data_driven": ["$", "%", "number", "statistics", "data", "research"],
        }

        sentence_lower = sentence.lower()

        for emotion, keywords in emotions.items():
            if any(kw in sentence_lower for kw in keywords):
                return emotion

        return "neutral"

    def _suggest_visual(self, sentence: str) -> str:
        """Suggest visual asset type"""

        sentence_lower = sentence.lower()

        if "$" in sentence or any(w in sentence_lower for w in ["wage", "pay", "earn", "cost", "percent"]):
            return "infographic"

        if any(w in sentence_lower for w in ["map", "location", "country", "africa", "region"]):
            return "map"

        if any(w in sentence_lower for w in ["2016", "2019", "2023", "history", "before", "after"]):
            return "timeline"

        if any(w in sentence_lower for w in ["work", "office", "computer", "moderate"]):
            return "stock_footage"

        if any(w in sentence_lower for w in ["mental", "stress", "trauma", "ptsd"]):
            return "documentary_broll"

        return "stock_footage"

    def _needs_map(self, sentence: str) -> bool:
        """Check if shot needs geographic map"""

        return any(w in sentence.lower() for w in [
            "location", "country", "africa", "region", "place", "map",
            "nigeria", "kenya", "uganda", "asia", "us"
        ])

    def _needs_timeline(self, sentence: str) -> bool:
        """Check if shot needs temporal timeline"""

        return any(w in sentence.lower() for w in [
            "2016", "2019", "2023", "since", "before", "after", "timeline",
            "evolution", "progression", "history", "began", "started"
        ])

    def _needs_comparison(self, sentence: str) -> bool:
        """Check if shot needs before/after or comparison"""

        return any(w in sentence.lower() for w in [
            "vs", "versus", "compared", "compared to", "while", "but", "unlike",
            "different", "contrast", "gap", "between"
        ])

    def _needs_statistic(self, sentence: str) -> bool:
        """Check if shot needs statistic graphic"""

        return any(w in sentence.lower() for w in ["$", "%", "million", "thousand"]) or \
               re.search(r'\d+', sentence) is not None

    def _get_asset_priority(self, sentence: str) -> List[str]:
        """Get asset search priority for this shot"""

        if self._needs_map(sentence):
            return ["google_maps", "satellite_imagery", "osm"]

        if self._needs_timeline(sentence):
            return ["archive_footage", "historical_photos", "news_footage"]

        if any(w in sentence.lower() for w in ["work", "office", "moderator"]):
            return ["pexels_stock", "news_footage", "documentary"]

        return ["pexels_stock", "unsplash", "pixabay"]

    def _generate_queries(self, sentence: str) -> List[str]:
        """Generate asset search queries"""

        queries = []

        # Extract key nouns/concepts
        keywords = []

        if "work" in sentence.lower():
            keywords.append("office worker")

        if "moderate" in sentence.lower():
            keywords.append("content moderation")

        if "africa" in sentence.lower():
            keywords.append("Africa")

        if "$" in sentence or "wage" in sentence.lower():
            keywords.append("wage comparison infographic")

        if not keywords:
            keywords = [sentence[:20]]

        queries.extend(keywords)

        return queries

    def _count_visuals(self, shots: List[Dict]) -> Dict[str, int]:
        """Count visual types needed"""

        counts = {}

        for shot in shots:
            visual = shot.get("visual_type", "stock_footage")
            counts[visual] = counts.get(visual, 0) + 1

        return counts
