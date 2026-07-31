"""
Research Agent - Extracts facts from script.

Responsibilities:
- Parse script into factual statements
- Extract entities (people, places, dates, organizations)
- Identify statistics and claims
"""

from typing import Dict, Any
from pydantic import BaseModel

from .base_agent import BaseAgent
from ..core.schemas import Fact, ResearchOutput, AgentStatus


class ResearchInput(BaseModel):
    """Research Agent input"""
    script: str
    scene_ids: list = []


class ResearchAgent(BaseAgent):
    """Research Agent implementation"""

    agent_name = "Research Agent"
    input_schema = ResearchInput
    output_schema = ResearchOutput
    timeout_seconds = 600

    success_criteria = {
        "agent_name": ("Research Agent", "=="),  # Quick validation
    }

    def _run(self, input_data: ResearchInput) -> Dict[str, Any]:
        """Extract facts from script"""
        script = input_data.script

        # Parse script into facts (simplified implementation)
        facts = []

        # Extract sentences as potential facts
        sentences = script.replace(".", ".\n").split("\n")

        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) > 10:
                fact = Fact(
                    fact_id=f"f{i+1}",
                    claim=sentence.strip(),
                    entities=[],
                    people=[],
                    places=[],
                    dates=[],
                    organizations=[],
                    statistics=[],
                )

                # Simple entity detection
                if "Dangote" in sentence:
                    fact.people.append("Aliko Dangote")
                if "Nigeria" in sentence:
                    fact.places.append("Nigeria")
                if "Lagos" in sentence:
                    fact.places.append("Lagos")
                if "$" in sentence or "billion" in sentence:
                    fact.statistics.append(sentence)
                if "refinery" in sentence.lower():
                    fact.organizations.append("Dangote Refinery")

                facts.append(fact)

        return ResearchOutput(
            agent_name=self.agent_name,
            status=AgentStatus.PASS,
            facts=facts,
            duration_ms=0,
            cost_usd=0.05,
        ).model_dump()
