"""Cost optimization for API calls"""

import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CostOptimizer:
    """Optimizes costs by dynamically switching between real and mock APIs"""

    API_COSTS = {
        "runway_ml": 0.30,  # per video
        "pexels": 0.00,  # free
        "tavily": 0.01,  # per query
        "elevenlabs": 0.02,  # per minute of audio
    }

    def __init__(self, budget: float = 100.0):
        self.budget = budget
        self.spent = 0.0
        self.cost_log: list[Dict[str, Any]] = []

    def estimate_cost(self, service: str, params: Dict[str, Any]) -> float:
        """Estimate cost for a service call"""
        base_cost = self.API_COSTS.get(service, 0.01)

        # Adjust based on parameters
        if service == "runway_ml":
            duration = params.get("duration_seconds", 10)
            resolution = params.get("resolution", "1080p")
            # Cost increases with duration and resolution
            multiplier = (duration / 10) * (1.0 if resolution == "1080p" else 1.5)
            return base_cost * multiplier

        elif service == "elevenlabs":
            text_length = len(params.get("text", ""))
            # ~5 characters per word, ~2.5 words per second
            estimated_seconds = text_length / 5 / 2.5
            return base_cost * estimated_seconds

        elif service == "tavily":
            # Cost per research query
            return base_cost

        return base_cost

    def can_afford(self, service: str, params: Dict[str, Any]) -> bool:
        """Check if we can afford a service call"""
        cost = self.estimate_cost(service, params)
        remaining = self.budget - self.spent

        can_afford = cost <= remaining
        logger.info(f"Cost check: {service} costs ${cost:.2f}, remaining ${remaining:.2f} - {'OK' if can_afford else 'OVER BUDGET'}")

        return can_afford

    def should_use_mock(self, service: str, params: Dict[str, Any]) -> bool:
        """Determine if we should use mock data instead of real API"""
        # Always use real for critical services
        if service in ["tavily"]:  # Fact checking is critical
            return False

        # Use mock if we can't afford the real service
        if not self.can_afford(service, params):
            logger.warning(f"Switching to mock for {service} due to budget constraints")
            return True

        # Use mock for low-priority services if budget is tight
        remaining = self.budget - self.spent
        if remaining < self.budget * 0.1:  # Less than 10% budget left
            if service in ["runway_ml", "elevenlabs"]:
                logger.warning(f"Switching to mock for {service} to preserve budget")
                return True

        return False

    def log_cost(self, service: str, amount: float, description: str = ""):
        """Log a cost"""
        self.spent += amount
        self.cost_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "service": service,
            "amount": amount,
            "description": description,
            "total_spent": self.spent
        })
        logger.info(f"Cost logged: {service} ${amount:.2f} (Total: ${self.spent:.2f})")

    def get_budget_remaining(self) -> float:
        """Get remaining budget"""
        return self.budget - self.spent

    def get_utilization(self) -> float:
        """Get budget utilization percentage"""
        return (self.spent / self.budget) * 100 if self.budget > 0 else 0.0

    def get_cost_report(self) -> Dict[str, Any]:
        """Get cost summary report"""
        # Group by service
        by_service = {}
        for entry in self.cost_log:
            service = entry["service"]
            if service not in by_service:
                by_service[service] = 0
            by_service[service] += entry["amount"]

        return {
            "budget": self.budget,
            "spent": self.spent,
            "remaining": self.get_budget_remaining(),
            "utilization_percent": self.get_utilization(),
            "by_service": by_service,
            "cost_log": self.cost_log
        }
