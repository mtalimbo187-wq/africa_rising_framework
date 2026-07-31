"""Tests for Phase 2 & 3 components"""

import pytest
from datetime import datetime, timedelta
from src.api.auth import generate_api_key, hash_api_key, verify_api_key
from src.core.cost_optimizer import CostOptimizer
from src.core.advanced_retry import CircuitBreaker, AdvancedRetryManager, FallbackChain
from src.analytics.ab_testing import ABTestEngine, Variant
from src.analytics.ml_predictor import EngagementPredictor, SuccessProbabilityPredictor
from src.webhooks.manager import WebhookManager


class TestAPIAuthentication:
    """Test API key generation and verification"""

    def test_generate_api_key(self):
        key = generate_api_key()
        assert key.startswith("sk_")
        assert len(key) > 20

    def test_hash_api_key(self):
        key = "sk_test123"
        hash1 = hash_api_key(key)
        hash2 = hash_api_key(key)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex

    def test_api_key_different_from_hash(self):
        key = generate_api_key()
        hashed = hash_api_key(key)
        assert key != hashed


class TestCostOptimizer:
    """Test cost optimization engine"""

    def test_estimate_runway_cost(self):
        optimizer = CostOptimizer(budget=100.0)
        cost = optimizer.estimate_cost("runway_ml", {"duration_seconds": 20, "resolution": "1080p"})
        assert cost > 0
        assert cost < 100

    def test_can_afford(self):
        optimizer = CostOptimizer(budget=10.0)
        assert optimizer.can_afford("tavily", {})

        optimizer.log_cost("tavily", 9.5, "test")
        assert not optimizer.can_afford("runway_ml", {"duration_seconds": 20})

    def test_budget_tracking(self):
        optimizer = CostOptimizer(budget=100.0)
        optimizer.log_cost("runway_ml", 30.0, "video")
        optimizer.log_cost("elevenlabs", 5.0, "narration")

        assert optimizer.get_budget_remaining() == 65.0
        assert optimizer.get_utilization() == 35.0

    def test_cost_report(self):
        optimizer = CostOptimizer(budget=100.0)
        optimizer.log_cost("runway_ml", 30.0, "video 1")
        optimizer.log_cost("runway_ml", 20.0, "video 2")
        optimizer.log_cost("elevenlabs", 5.0, "narration")

        report = optimizer.get_cost_report()
        assert report["spent"] == 55.0
        assert report["by_service"]["runway_ml"] == 50.0
        assert report["by_service"]["elevenlabs"] == 5.0

    def test_mock_fallback_decision(self):
        optimizer = CostOptimizer(budget=10.0)
        optimizer.log_cost("runway_ml", 9.0, "test")

        # Should use mock when budget is tight
        assert optimizer.should_use_mock("runway_ml", {"duration_seconds": 20})


class TestCircuitBreaker:
    """Test circuit breaker pattern"""

    def test_circuit_breaker_closed_state(self):
        cb = CircuitBreaker(failure_threshold=3)

        def success():
            return "ok"

        result = cb.call(success)
        assert result == "ok"
        assert str(cb.state.value) == "closed"

    def test_circuit_breaker_opens_after_failures(self):
        cb = CircuitBreaker(failure_threshold=2)

        def fail():
            raise Exception("test error")

        # First failure
        with pytest.raises(Exception):
            cb.call(fail)
        assert cb.failure_count == 1

        # Second failure - circuit opens
        with pytest.raises(Exception):
            cb.call(fail)
        assert str(cb.state.value) == "open"

    def test_circuit_breaker_half_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)

        def fail():
            raise Exception("test")

        # Trigger open state
        with pytest.raises(Exception):
            cb.call(fail)

        # Wait for recovery timeout
        cb.last_failure_time = datetime.utcnow() - timedelta(seconds=2)

        # Should enter half-open
        with pytest.raises(Exception):
            cb.call(fail)
        assert str(cb.state.value) == "half_open"


class TestAdvancedRetryManager:
    """Test advanced retry logic"""

    def test_retry_with_success(self):
        retry_mgr = AdvancedRetryManager("Test Agent")

        def api_call():
            return "success"

        result = retry_mgr.execute_with_retry(api_call)
        assert result == "success"

    def test_retry_with_exponential_backoff(self):
        retry_mgr = AdvancedRetryManager("Asset Finder")
        attempts = [0]

        def flaky_call():
            attempts[0] += 1
            if attempts[0] < 3:
                raise Exception("temporary failure")
            return "success"

        result = retry_mgr.execute_with_retry(flaky_call)
        assert result == "success"
        assert attempts[0] == 3

    def test_retry_max_attempts_exceeded(self):
        retry_mgr = AdvancedRetryManager("Script Analyzer")
        retry_mgr.policy["max_attempts"] = 2

        def always_fail():
            raise Exception("permanent failure")

        with pytest.raises(Exception):
            retry_mgr.execute_with_retry(always_fail)

    def test_get_retry_config(self):
        retry_mgr = AdvancedRetryManager("Fact Checker")
        config = retry_mgr.get_retry_config()

        assert config["agent_name"] == "Fact Checker"
        assert config["policy"]["max_attempts"] == 3
        assert "circuit_breaker" in config


class TestFallbackChain:
    """Test fallback chain execution"""

    def test_fallback_first_success(self):
        chain = FallbackChain([
            (lambda: "success", "primary"),
        ])
        result = chain.execute()
        assert result == "success"

    def test_fallback_second_attempt(self):
        def fail():
            raise Exception("failed")

        def succeed():
            return "fallback success"

        chain = FallbackChain([
            (fail, "primary"),
            (succeed, "fallback"),
        ])
        result = chain.execute()
        assert result == "fallback success"

    def test_fallback_all_exhausted(self):
        def fail():
            raise Exception("failed")

        chain = FallbackChain([
            (fail, "primary"),
            (fail, "fallback"),
        ])

        with pytest.raises(Exception):
            chain.execute()


class TestABTestEngine:
    """Test A/B testing framework"""

    def test_create_test(self):
        engine = ABTestEngine()
        engine.create_test("Fact Verification", 0.95, 0.93)

        assert "Fact Verification" in engine.tests
        variants = engine.tests["Fact Verification"]
        assert len(variants) == 2

    def test_record_trial(self):
        engine = ABTestEngine()
        engine.create_test("Fact Verification", 0.95, 0.93)

        engine.record_trial("Fact Verification", "baseline", True)
        engine.record_trial("Fact Verification", "variant", True)

        variants = engine.tests["Fact Verification"]
        assert variants[0].success_count == 1
        assert variants[1].success_count == 1

    def test_is_test_complete(self):
        engine = ABTestEngine()
        engine.create_test("Fact Verification", 0.95, 0.93)

        # Not complete yet
        assert not engine.is_test_complete("Fact Verification")

        # Add minimum trials
        for i in range(30):
            engine.record_trial("Fact Verification", "baseline", True)
            engine.record_trial("Fact Verification", "variant", True)

        assert engine.is_test_complete("Fact Verification")

    def test_variant_properties(self):
        variant = Variant(name="test", gate_threshold=0.95)
        assert variant.success_rate == 0.0

        variant.total_trials = 10
        variant.success_count = 8
        assert variant.success_rate == 0.8


class TestEngagementPredictor:
    """Test engagement prediction"""

    def test_predict_engagement(self):
        predictor = EngagementPredictor()
        result = predictor.predict_engagement(
            topic="Africa Technology",
            script_quality=0.85,
            visual_complexity=0.75
        )

        assert "predicted_engagement_score" in result
        assert result["predicted_engagement_score"] > 0
        assert result["predicted_engagement_score"] <= 100

    def test_engagement_components(self):
        predictor = EngagementPredictor()
        result = predictor.predict_engagement(topic="documentary")

        assert "predicted_views" in result
        assert "predicted_completion_rate" in result
        assert "predicted_likes" in result
        assert "predicted_shares" in result

    def test_optimal_posting_time(self):
        predictor = EngagementPredictor()
        result = predictor.predict_optimal_posting_time("US/Eastern")

        assert "optimal_posting_time" in result
        assert "expected_engagement_boost" in result


class TestSuccessProbabilityPredictor:
    """Test success probability predictions"""

    def test_predict_gate_success(self):
        predictor = SuccessProbabilityPredictor()
        result = predictor.predict_gate_success(
            topic="documentary",
            production_budget=500.0
        )

        assert "overall_success_probability" in result
        assert result["overall_success_probability"] > 0
        assert result["overall_success_probability"] <= 1

    def test_gate_predictions(self):
        predictor = SuccessProbabilityPredictor()
        result = predictor.predict_gate_success(topic="documentary", production_budget=500)

        gates = result["gate_predictions"]
        assert "fact_verification" in gates
        assert "visual_teaching" in gates
        assert "asset_coverage" in gates
        assert gates["fact_verification"]["pass_probability"] > 0


class TestWebhookManager:
    """Test webhook delivery system"""

    def test_generate_webhook_secret(self):
        secret = WebhookManager.generate_secret()
        assert len(secret) == 64  # hex encoded
        assert secret.isalnum()

    def test_sign_payload(self):
        payload = "test payload"
        secret = "test secret"
        signature = WebhookManager.sign_payload(payload, secret)

        assert len(signature) == 64  # SHA256 hex
        assert signature.isalnum()

    def test_payload_signature_consistent(self):
        payload = "test payload"
        secret = "test secret"

        sig1 = WebhookManager.sign_payload(payload, secret)
        sig2 = WebhookManager.sign_payload(payload, secret)

        assert sig1 == sig2

    def test_different_payloads_different_signatures(self):
        secret = "test secret"
        sig1 = WebhookManager.sign_payload("payload 1", secret)
        sig2 = WebhookManager.sign_payload("payload 2", secret)

        assert sig1 != sig2


class TestIntegrations:
    """Test integration components"""

    def test_claude_refiner_import(self):
        from src.integrations import ClaudeScriptRefiner
        refiner = ClaudeScriptRefiner()
        assert refiner is not None

    def test_youtube_publisher_import(self):
        from src.integrations import YouTubePublisher
        publisher = YouTubePublisher()
        assert publisher is not None

    def test_tiktok_generator_import(self):
        from src.integrations import TikTokGenerator
        generator = TikTokGenerator()
        assert generator is not None


# Performance Tests
class TestPerformance:
    """Test performance characteristics"""

    def test_cost_optimizer_performance(self):
        optimizer = CostOptimizer(budget=10000.0)

        # Log 1000 costs
        for i in range(1000):
            optimizer.log_cost("runway_ml", 0.5, f"test {i}")

        # Should complete quickly
        report = optimizer.get_cost_report()
        assert len(report["cost_log"]) == 1000

    def test_retry_manager_performance(self):
        import time
        retry_mgr = AdvancedRetryManager("Test")

        start = time.time()

        def fast_call():
            return "ok"

        for _ in range(100):
            retry_mgr.execute_with_retry(fast_call)

        elapsed = time.time() - start
        assert elapsed < 1.0  # Should complete in under 1 second

    def test_ab_test_engine_performance(self):
        import time
        engine = ABTestEngine()
        engine.create_test("Gate", 0.95, 0.93)

        start = time.time()

        for i in range(1000):
            engine.record_trial("Gate", "baseline" if i % 2 == 0 else "variant", True)

        elapsed = time.time() - start
        assert elapsed < 0.5  # Should complete quickly


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
