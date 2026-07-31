#!/usr/bin/env python3
"""
Africa Rising Video Framework — Script Analyzer

Breaks down a video script into structured visual requirements:
- Entities (people, places, organizations)
- Temporal markers (dates, eras, timelines)
- Events (actions, phenomena)
- Emotions/tone
- Visual types needed (stock, archive, map, AI image, animation)
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Any

class ScriptAnalyzer:
    def __init__(self):
        self.visual_types = {
            "stock_footage": "General footage (Pexels, Unsplash, YouTube)",
            "archive": "Historical photos/footage (Internet Archive, Google Arts)",
            "satellite": "Satellite imagery or maps (Google Earth, Bing Maps)",
            "map": "Animated map or location visualization",
            "timeline": "Historical timeline or progression",
            "ai_image": "Generated infographic or illustration (DALL-E, Grok)",
            "animation": "Animated still image (Ken Burns, zoom/pan)",
            "text_overlay": "Text graphic or lower-third",
            "news_footage": "News clips or documentary footage"
        }

        self.entity_patterns = {
            "person": r'\b(?:Mr\.|Ms\.|Dr\.|Professor|workers?|moderators?|employees?|contractors?|[A-Z][a-z]+ [A-Z][a-z]+)\b',
            "place": r'\b(?:Africa|US|America|countries?|cities?|regions?|Tumwater|Washington|Nigeria|Kenya|Uganda|Ghana)\b',
            "organization": r'\b(?:Meta|Facebook|Sama|Google|Twitter|X|Reuters|AP|BBC)\b',
            "event": r'\b(?:earning|making|working|moderating|posting|content moderation|exploitation)\b'
        }

    def analyze(self, script_text: str) -> Dict[str, Any]:
        """Analyze a script and return structured visual requirements"""

        sentences = self._split_sentences(script_text)
        shots = []

        for i, sentence in enumerate(sentences):
            shot = {
                "shot_number": i + 1,
                "text": sentence,
                "duration_estimate": self._estimate_duration(sentence),
                "entities": self._extract_entities(sentence),
                "emotion": self._detect_emotion(sentence),
                "visual_types": self._suggest_visuals(sentence),
                "search_queries": self._generate_search_queries(sentence)
            }
            shots.append(shot)

        return {
            "total_shots": len(shots),
            "estimated_duration_seconds": sum(s["duration_estimate"] for s in shots),
            "shots": shots,
            "timeline": self._build_timeline(shots)
        }

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Split on period, but handle cases like "U.S." or "Inc."
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _estimate_duration(self, sentence: str) -> float:
        """Estimate duration in seconds (rough: ~2 words per second)"""
        word_count = len(sentence.split())
        # Average speaking pace: 130-150 words/min = ~2-2.5 words/sec
        return max(2, word_count / 2.2)

    def _extract_entities(self, sentence: str) -> Dict[str, List[str]]:
        """Extract named entities from sentence"""
        entities = {}
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, sentence, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        return entities

    def _detect_emotion(self, sentence: str) -> str:
        """Detect emotional tone (investigative, empathetic, critical, etc.)"""
        sentence_lower = sentence.lower()

        emotions = {
            "critical": ["exploitation", "unfair", "injustice", "abuse", "suffer", "struggle"],
            "empathetic": ["workers", "people", "lives", "struggle", "deserve", "human"],
            "data_driven": ["$", "percent", "number", "rate", "statistics", "data"],
            "urgent": ["crisis", "urgent", "immediate", "alarming", "shocking"],
            "hopeful": ["solution", "change", "action", "progress", "hope", "improve"],
            "investigative": ["reveal", "expose", "discover", "uncover", "show", "investigate"]
        }

        detected = []
        for emotion, keywords in emotions.items():
            if any(kw in sentence_lower for kw in keywords):
                detected.append(emotion)

        return detected[0] if detected else "neutral"

    def _suggest_visuals(self, sentence: str) -> List[str]:
        """Suggest visual types based on sentence content"""
        visuals = []
        sentence_lower = sentence.lower()

        # Heuristics for visual selection
        if any(word in sentence_lower for word in ["$", "earn", "paid", "wage", "rate", "cost"]):
            visuals.append("ai_image")  # Infographic
            visuals.append("text_overlay")

        if any(word in sentence_lower for word in ["africa", "us", "country", "region", "location"]):
            visuals.append("map")
            visuals.append("satellite")

        if any(word in sentence_lower for word in ["2016", "2019", "2023", "history", "evolution", "began", "started"]):
            visuals.append("timeline")
            visuals.append("archive")

        if any(word in sentence_lower for word in ["work", "moderating", "content", "office", "home", "sit"]):
            visuals.append("stock_footage")
            visuals.append("news_footage")

        if any(word in sentence_lower for word in ["mental", "stress", "trauma", "depression", "anxiety"]):
            visuals.append("ai_image")
            visuals.append("animation")

        if not visuals:
            visuals.append("stock_footage")  # Default fallback

        return list(set(visuals))  # Remove duplicates

    def _generate_search_queries(self, sentence: str) -> List[str]:
        """Generate search queries for finding assets"""
        queries = []
        entities = self._extract_entities(sentence)

        # Build queries from entities
        if "organization" in entities:
            for org in entities["organization"]:
                queries.append(f"{org} headquarters office")
                queries.append(f"{org} content moderation")

        if "place" in entities:
            for place in entities["place"]:
                queries.append(f"{place} office work")
                queries.append(f"{place} landscape")

        if "person" in entities:
            for person in entities["person"]:
                queries.append(f"content moderator working")
                queries.append(f"office worker computer")

        # Add generic queries based on emotion/topic
        if "wage" in sentence.lower() or "$" in sentence:
            queries.append("infographic wage comparison")
            queries.append("data visualization money")

        if "mental" in sentence.lower() or "stress" in sentence.lower():
            queries.append("stressed worker mental health")
            queries.append("anxiety depression representation")

        if "africa" in sentence.lower():
            queries.append("Sub-Saharan Africa office")
            queries.append("African workers technology")

        return list(set(queries))  # Remove duplicates

    def _build_timeline(self, shots: List[Dict]) -> Dict[str, Any]:
        """Build timeline structure from shots"""
        return {
            "total_shots": len(shots),
            "estimated_duration": sum(s["duration_estimate"] for s in shots),
            "visual_breakdown": self._count_visual_types(shots)
        }

    def _count_visual_types(self, shots: List[Dict]) -> Dict[str, int]:
        """Count visual types needed across all shots"""
        counts = {vtype: 0 for vtype in self.visual_types.keys()}
        for shot in shots:
            for vtype in shot["visual_types"]:
                if vtype in counts:
                    counts[vtype] += 1
        return {k: v for k, v in counts.items() if v > 0}


def main():
    """Example usage"""
    sample_script = """
    Facebook content moderators in Africa earn just two dollars an hour.
    In the United States, the same work pays twenty dollars.
    This is exploitation at scale.
    Meta, the parent company of Facebook, contracts out this work to companies like Sama.
    Workers in Nigeria, Kenya, and Uganda review violent content for hours each day.
    The psychological toll is severe.
    Studies show 68% of African content moderators develop PTSD.
    Meanwhile, Meta's annual profit exceeds thirty billion dollars.
    """

    analyzer = ScriptAnalyzer()
    analysis = analyzer.analyze(sample_script)

    print("\n" + "="*80)
    print("SCRIPT ANALYSIS REPORT")
    print("="*80 + "\n")

    print(f"Total Shots: {analysis['total_shots']}")
    print(f"Estimated Duration: {analysis['estimated_duration_seconds']:.1f} seconds")
    print(f"Visual Breakdown: {analysis['timeline']['visual_breakdown']}\n")

    for shot in analysis["shots"]:
        print(f"\n--- Shot {shot['shot_number']} ---")
        print(f"Text: {shot['text']}")
        print(f"Duration: {shot['duration_estimate']:.1f}s")
        print(f"Entities: {shot['entities']}")
        print(f"Emotion: {shot['emotion']}")
        print(f"Visuals needed: {', '.join(shot['visual_types'])}")
        print(f"Search queries: {', '.join(shot['search_queries'][:2])}")

    # Save analysis
    output_file = Path("/Users/rajab/africa_rising_framework/output_analysis.json")
    with open(output_file, "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"\n✅ Analysis saved to {output_file}\n")


if __name__ == "__main__":
    main()
