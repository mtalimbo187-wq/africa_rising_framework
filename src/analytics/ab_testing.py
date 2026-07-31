"""A/B testing engine for gate threshold optimization"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from dataclasses import dataclass
import math

logger = logging.getLogger(__name__)


@dataclass
class Variant:
    """A/B test variant"""
    name: str
    gate_threshold: float
    success_count: int = 0
    failure_count: int = 0
    total_trials: int = 0

    @property
    def success_rate(self) -> float:
        if self.total_trials == 0:
            return 0.0
        return self.success_count / self.total_trials

    @property
    def confidence_interval(self) -> tuple[float, float]:
        """Calculate 95% confidence interval"""
        if self.total_trials == 0:
            return (0.0, 0.0)

        p = self.success_rate
        n = self.total_trials
        z = 1.96  # 95% confidence

        margin = z * math.sqrt((p * (1 - p)) / n)

        return (
            max(0, p - margin),
            min(1, p + margin)
        )


class ABTestEngine:
    """A/B testing framework for optimizing gate thresholds"""

    MIN_TRIALS = 30  # Minimum trials before declaring winner
    SIGNIFICANCE_LEVEL = 0.05

    def __init__(self):
        self.tests: Dict[str, List[Variant]] = {}
        self.results: List[Dict[str, Any]] = []

    def create_test(
        self,
        gate_name: str,
        baseline_threshold: float,
        variant_threshold: float
    ):
        """Create A/B test for gate threshold"""
        logger.info(f"Creating A/B test for {gate_name}")
        logger.info(f"  Baseline: {baseline_threshold}")
        logger.info(f"  Variant:  {variant_threshold}")

        self.tests[gate_name] = [
            Variant(name="baseline", gate_threshold=baseline_threshold),
            Variant(name="variant", gate_threshold=variant_threshold),
        ]

    def record_trial(
        self,
        gate_name: str,
        variant_name: str,
        passed: bool
    ):
        """Record test trial result"""
        if gate_name not in self.tests:
            return

        variants = self.tests[gate_name]
        variant = next((v for v in variants if v.name == variant_name), None)

        if not variant:
            return

        variant.total_trials += 1
        if passed:
            variant.success_count += 1
        else:
            variant.failure_count += 1

        logger.debug(f"{gate_name}/{variant_name}: {'PASS' if passed else 'FAIL'} ({variant.success_count}/{variant.total_trials})")

    def is_test_complete(self, gate_name: str) -> bool:
        """Check if test has enough data"""
        if gate_name not in self.tests:
            return False

        variants = self.tests[gate_name]
        return all(v.total_trials >= self.MIN_TRIALS for v in variants)

    def get_winner(self, gate_name: str) -> Dict[str, Any]:
        """Determine test winner with statistical significance"""
        if gate_name not in self.tests:
            return {"status": "no_test"}

        if not self.is_test_complete(gate_name):
            variants = self.tests[gate_name]
            trials_needed = self.MIN_TRIALS - min(v.total_trials for v in variants)
            return {
                "status": "incomplete",
                "trials_needed": trials_needed,
                "current_data": [
                    {
                        "variant": v.name,
                        "success_rate": v.success_rate,
                        "trials": v.total_trials
                    }
                    for v in variants
                ]
            }

        variants = self.tests[gate_name]
        baseline = variants[0]
        variant = variants[1]

        # Chi-squared test for statistical significance
        z_score = self._calculate_z_score(baseline, variant)
        is_significant = abs(z_score) > 1.96  # 95% confidence

        winner = "variant" if variant.success_rate > baseline.success_rate else "baseline"

        result = {
            "status": "complete",
            "gate_name": gate_name,
            "winner": winner,
            "is_significant": is_significant,
            "baseline": {
                "threshold": baseline.gate_threshold,
                "success_rate": baseline.success_rate,
                "trials": baseline.total_trials,
                "confidence_interval": baseline.confidence_interval
            },
            "variant": {
                "threshold": variant.gate_threshold,
                "success_rate": variant.success_rate,
                "trials": variant.total_trials,
                "confidence_interval": variant.confidence_interval
            },
            "improvement": (variant.success_rate - baseline.success_rate) * 100,
            "z_score": z_score
        }

        self.results.append(result)
        logger.info(f"A/B test complete: {gate_name}")
        logger.info(f"  Winner: {winner}")
        logger.info(f"  Improvement: {result['improvement']:.1f}%")

        return result

    def _calculate_z_score(self, variant1: Variant, variant2: Variant) -> float:
        """Calculate z-score for statistical significance"""
        p1 = variant1.success_rate
        p2 = variant2.success_rate
        n1 = variant1.total_trials
        n2 = variant2.total_trials

        if n1 == 0 or n2 == 0:
            return 0.0

        p_pool = (variant1.success_count + variant2.success_count) / (n1 + n2)
        se = math.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2))

        if se == 0:
            return 0.0

        return (p1 - p2) / se

    def get_recommended_threshold(self, gate_name: str) -> Dict[str, Any]:
        """Get recommended threshold based on test results"""
        result = self.get_winner(gate_name)

        if result["status"] != "complete":
            return result

        winner = result["winner"]
        new_threshold = result[winner]["threshold"]

        return {
            "status": "recommended",
            "gate_name": gate_name,
            "recommended_threshold": new_threshold,
            "improvement": result["improvement"],
            "confidence": "high" if result["is_significant"] else "low"
        }

    def apply_recommendation(self, gate_name: str, new_threshold: float):
        """Apply recommended threshold to production"""
        logger.info(f"Applying new threshold for {gate_name}: {new_threshold}")
        # In production, update gate configuration
        return {
            "status": "applied",
            "gate_name": gate_name,
            "new_threshold": new_threshold,
            "applied_at": datetime.utcnow().isoformat()
        }

    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all test results"""
        return self.results

    def export_results(self, filepath: str):
        """Export test results to JSON"""
        import json
        with open(filepath, "w") as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"Exported A/B test results to {filepath}")
