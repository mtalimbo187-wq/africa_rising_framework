#!/usr/bin/env python3
"""
Research Agent — Fact-finding and source verification

Responsibilities:
- Extract claims from script
- Verify facts using Tavily API
- Find authoritative sources
- Identify key statistics
- Create verification checklist
"""

from base_agent import BaseAgent, AgentResult, AgentStatus
from typing import Dict, Any, List
import re
import requests


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Research Agent",
            description="Fact-finding via Tavily, source verification, and reference database"
        )

        # Tavily API configuration (for fact-checking)
        self.tavily_api_key = "YOUR_TAVILY_API_KEY"  # Set from config
        self.tavily_url = "https://api.tavily.com/search"

        self.trusted_sources = {
            "tier_1": [
                "Reuters", "AP", "BBC", "Al Jazeera", "Guardian",
                "NYT", "WSJ", "FT", "Economist", "NPR"
            ],
            "tier_2": [
                "Vice News", "ProPublica", "investigativeReporting.org",
                "academic_databases", "government_records"
            ]
        }

    def execute(self, input_data: Dict[str, Any]) -> AgentResult:
        """Extract and verify facts from script"""

        script_text = input_data.get("script", "")
        if not script_text:
            self.log_error("No script provided")
            return AgentResult(self.name, AgentStatus.FAILED, {})

        self.log_status(f"Analyzing {len(script_text)} characters...")

        # Extract claims (sentences with numbers, assertions, statistics)
        claims = self._extract_claims(script_text)
        self.log_status(f"Found {len(claims)} factual claims")

        # Extract statistics
        statistics = self._extract_statistics(script_text)
        self.log_status(f"Found {len(statistics)} statistics")

        # Extract entities (organizations, people, locations)
        entities = self._extract_entities(script_text)
        self.log_status(f"Found {len(entities)} key entities")

        output = {
            "claims": claims,
            "statistics": statistics,
            "entities": entities,
            "reference_sources": self._get_relevant_sources(entities),
            "verification_checklist": self._create_checklist(claims, statistics),
            "total_items": len(claims) + len(statistics)
        }

        return AgentResult(
            agent_name=self.name,
            status=AgentStatus.COMPLETED,
            output=output
        )

    def _extract_claims(self, text: str) -> List[Dict]:
        """Extract factual claims from text"""

        claims = []

        # Pattern: "X [verb] Y" sentences
        sentences = re.split(r'[.!?]+', text)

        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:
                continue

            # Check if sentence makes an assertion
            has_assertion = any(verb in sentence.lower() for verb in [
                "is", "are", "earn", "paid", "cost", "total", "number",
                "equal", "more", "less", "increase", "decrease", "build",
                "work", "exploit", "provide", "receive"
            ])

            if has_assertion:
                claims.append({
                    "text": sentence[:100],
                    "line_number": i,
                    "requires_verification": self._requires_verification(sentence),
                    "source_type": self._suggest_source_type(sentence)
                })

        return claims

    def _extract_statistics(self, text: str) -> List[Dict]:
        """Extract numbers and statistics"""

        statistics = []

        # Find patterns: "$X", "X%", "X million", "X,XXX"
        patterns = [
            (r'\$\d+(?:,\d{3})*(?:\.\d+)?', 'currency'),
            (r'\d+(?:\.\d+)?%', 'percentage'),
            (r'\d+(?:\s+)?(?:million|billion|thousand|hundred)', 'quantity'),
            (r'\d{4}', 'year'),
        ]

        for pattern, stat_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get context (sentence containing the match)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()

                statistics.append({
                    "value": match.group(),
                    "type": stat_type,
                    "context": context[:80],
                    "requires_source": True
                })

        return statistics

    def _extract_entities(self, text: str) -> Dict[str, List]:
        """Extract key entities (organizations, people, locations)"""

        entities = {
            "organizations": [],
            "people": [],
            "locations": [],
            "countries": []
        }

        # Known entities
        org_patterns = [
            r'\b(?:Meta|Facebook|Google|Twitter|Amazon|Apple|Microsoft|YouTube)\b',
            r'\b(?:Sama|Telecare|DataAnnotation|Scale AI)\b',
        ]

        location_patterns = [
            r'\b(?:Nigeria|Kenya|Uganda|Ghana|Ethiopia|South Africa|Africa)\b',
            r'\b(?:United States|US|America|China|India|Europe)\b',
        ]

        for pattern in org_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group() not in entities["organizations"]:
                    entities["organizations"].append(match.group())

        for pattern in location_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.group() not in entities["locations"]:
                    entities["locations"].append(match.group())

        return entities

    def _requires_verification(self, sentence: str) -> bool:
        """Check if sentence requires fact-checking"""

        critical_terms = [
            "earn", "paid", "wage", "cost", "profit", "percent", "million",
            "exploit", "abuse", "illegal", "violate", "lawsuit", "death"
        ]

        return any(term in sentence.lower() for term in critical_terms)

    def _suggest_source_type(self, sentence: str) -> str:
        """Suggest what type of source would verify this claim"""

        if "wage" in sentence.lower() or "$" in sentence:
            return "financial_database"
        if "lawsuit" in sentence.lower() or "court" in sentence.lower():
            return "legal_records"
        if "study" in sentence.lower() or "research" in sentence.lower():
            return "academic"
        if "said" in sentence.lower() or "according" in sentence.lower():
            return "primary_source"

        return "news_article"

    def _get_relevant_sources(self, entities: Dict) -> List[str]:
        """Recommend trusted sources for verification"""

        sources = []

        # Add tier 1 sources as default
        sources.extend(self.trusted_sources["tier_1"][:5])

        # Add specialized sources based on entities
        if any(org in str(entities) for org in ["Meta", "Facebook", "Google"]):
            sources.append("Official company reports")
            sources.append("SEC filings")

        if any(loc in str(entities) for loc in ["Nigeria", "Kenya", "Africa"]):
            sources.append("African journalism outlets")
            sources.append("International news agencies")

        return sources

    def _create_checklist(self, claims: List, stats: List) -> List[Dict]:
        """Create verification checklist"""

        checklist = []

        for claim in claims[:5]:  # Top 5 claims
            if claim.get("requires_verification"):
                # Try to verify with Tavily
                verification = self._verify_with_tavily(claim["text"])
                checklist.append({
                    "item": claim["text"],
                    "status": "verified" if verification.get("verified") else "pending",
                    "source_type": claim["source_type"],
                    "sources": verification.get("sources", [])
                })

        for stat in stats[:5]:  # Top 5 statistics
            checklist.append({
                "item": f"{stat['value']} ({stat['type']})",
                "status": "pending",
                "context": stat["context"]
            })

        return checklist

    def _verify_with_tavily(self, claim: str) -> Dict[str, Any]:
        """Verify claim using Tavily research API"""

        try:
            response = requests.post(
                self.tavily_url,
                json={
                    "api_key": self.tavily_api_key,
                    "query": claim,
                    "max_results": 3,
                    "include_answer": True
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                sources = [
                    {"title": r.get("title"), "url": r.get("url")}
                    for r in data.get("results", [])
                ]

                return {
                    "verified": len(sources) > 0,
                    "answer": data.get("answer", ""),
                    "sources": sources
                }

        except Exception as e:
            pass

        return {"verified": False, "sources": []}
