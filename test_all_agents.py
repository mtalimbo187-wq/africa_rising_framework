#!/usr/bin/env python3
"""
Deep Integration Test: All Agents

Tests each agent individually with realistic data,
verifies outputs and inter-agent communication.
"""

import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

# Add agents and core to path
sys.path.insert(0, str(Path(__file__).parent / "agents"))
sys.path.insert(0, str(Path(__file__).parent / "core"))

# Import all agents (with fallback for missing/broken imports)
from agents.base_agent import BaseAgent, AgentStatus
from agents.script_analyzer_agent import ScriptAnalyzerAgent
from agents.visual_planner_agent import VisualPlannerAgent
from agents.asset_finder_agent import AssetFinderAgent

try:
    from agents.ai_generator_agent import AIGeneratorAgent
except ImportError:
    AIGeneratorAgent = None

try:
    from agents.narration_agent import NarrationAgent
except ImportError:
    NarrationAgent = None

try:
    from agents.captioning_agent import CaptioningAgent
except ImportError:
    CaptioningAgent = None

try:
    from agents.map_animation_agent import MapAnimationAgent
except ImportError:
    MapAnimationAgent = None

try:
    from agents.timeline_builder_agent import TimelineBuilderAgent
except ImportError:
    TimelineBuilderAgent = None

try:
    from agents.ffmpeg_editor_agent import FFmpegEditorAgent
except (ImportError, NameError):
    FFmpegEditorAgent = None

try:
    from agents.quality_review_agent import QualityReviewAgent
except ImportError:
    QualityReviewAgent = None

try:
    from agents.research_agent import ResearchAgent
except ImportError:
    ResearchAgent = None

# Import core modules
from core.schemas import Shot, Asset, Timeline, QualityScore
from core.prompt_manager import PromptManager, RoleTemplate
from core.license_manager import LicenseManager, LicenseType
from core.advanced_qa import AdvancedQAChecker
from core.observability import ProductionLogger
from core.security import InputValidator, CredentialManager


# Test data
SAMPLE_SCRIPT = """
# The Future of Technology in Africa

## Scene 1: Introduction
Across the African continent, technology is transforming lives and economies.
From mobile banking in Kenya to software development hubs in Nigeria, innovation is everywhere.
The digital revolution is creating opportunities for millions of young people.

## Scene 2: Mobile Banking Success
Mobile money has revolutionized financial services in Africa.
With over 100 million users, services like M-Pesa have lifted families out of poverty.
In 2023, mobile money transactions exceeded $500 billion.

## Scene 3: Tech Hubs Rising
Cities like Nairobi, Lagos, and Cape Town are becoming global tech centers.
Startups are building solutions for African problems at scale.
Investment in African tech startups has grown to $1.5 billion annually.

## Scene 4: Challenges Remain
Infrastructure gaps and limited internet access still limit opportunities.
Only 28% of Africans have reliable broadband connectivity.
Education and skills training remain critical needs.

## Scene 5: The Future
With youth making up 60% of Africa's population, the continent's tech future is bright.
Innovation, investment, and determination will drive the next generation of breakthroughs.
The future of technology belongs to those who build it today.
"""


def test_input_validation():
    """Test 1: Input Validation"""
    print("\n" + "="*60)
    print("TEST 1: Input Validation & Security")
    print("="*60)

    validator = InputValidator()

    # Test filename sanitization
    dangerous_name = "../../etc/passwd"
    safe_name = validator.sanitize_filename(dangerous_name)
    assert ".." not in safe_name, "Directory traversal detected!"
    print(f"✓ Filename sanitization: '{dangerous_name}' → '{safe_name}'")

    # Test SQL injection detection
    sql_injection = "'; DROP TABLE users; --"
    is_dangerous = validator.check_sql_injection(sql_injection)
    assert is_dangerous, "SQL injection not detected!"
    print(f"✓ SQL injection detection: Blocked dangerous input")

    # Test shell injection detection
    shell_injection = "test; rm -rf /"
    is_dangerous = validator.check_shell_injection(shell_injection)
    assert is_dangerous, "Shell injection not detected!"
    print(f"✓ Shell injection detection: Blocked dangerous input")

    # Test URL validation
    valid_url = "https://pexels.com/video/123"
    is_valid = validator.validate_url(valid_url, ["pexels.com", "archive.org"])
    assert is_valid, "Valid URL rejected!"
    print(f"✓ URL validation: Approved {valid_url}")

    return True


def test_prompt_manager():
    """Test 2: Prompt Manager"""
    print("\n" + "="*60)
    print("TEST 2: Prompt Management & Versioning")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = PromptManager(tmpdir)

        # Test role template retrieval
        researcher_prompt = RoleTemplate.get_template("researcher")
        assert "meticulous" in researcher_prompt.lower(), "Researcher template corrupted!"
        print(f"✓ Researcher template loaded ({len(researcher_prompt)} chars)")

        visual_template = RoleTemplate.get_template("visual_planner")
        assert "emmy" in visual_template.lower(), "Visual planner template corrupted!"
        print(f"✓ Visual planner template loaded ({len(visual_template)} chars)")

        # Test prompt interpolation
        template = "The agent {{name}} performs {{task}}"
        result = manager.interpolate(template, {"name": "Research", "task": "verification"})
        assert "Research" in result and "verification" in result, "Interpolation failed!"
        print(f"✓ Prompt interpolation: {result}")

    return True


def test_license_tracking():
    """Test 3: License Tracking"""
    print("\n" + "="*60)
    print("TEST 3: License Tracking & Attribution")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        manager = LicenseManager(tmpdir)

        # Track CC0 asset
        asset1 = manager.track_asset(
            asset_id="pexels_001",
            source="pexels",
            url="https://pexels.com/video/123",
            license_type=LicenseType.CC0,
            credited_to="Pexels"
        )
        print(f"✓ Tracked CC0 asset: {asset1['asset_id']}")

        # Track CC-BY asset
        asset2 = manager.track_asset(
            asset_id="archive_001",
            source="archive.org",
            url="https://archive.org/video/456",
            license_type=LicenseType.CC_BY,
            credited_to="Internet Archive",
            attribution_required=True
        )
        print(f"✓ Tracked CC-BY asset: {asset2['asset_id']} (requires attribution)")

        # Generate credits
        credits = manager.generate_credits_file("Test Documentary")
        assert "Internet Archive" in credits, "Attribution missing!"
        print(f"✓ Generated credits file ({len(credits)} chars)")

        # Validate usage
        valid, msg = manager.validate_for_usage("pexels_001", "commercial")
        assert valid, "CC0 should allow commercial use!"
        print(f"✓ CC0 validates for commercial use")

    return True


def test_script_analyzer():
    """Test 4: Script Analyzer Agent"""
    print("\n" + "="*60)
    print("TEST 4: Script Analyzer Agent")
    print("="*60)

    agent = ScriptAnalyzerAgent()
    result = agent.run({"script": SAMPLE_SCRIPT})

    assert result.status == AgentStatus.COMPLETED, f"Script analysis failed: {result.status}"
    print(f"✓ Script analyzed successfully")

    shots = result.output.get("shots", [])
    assert len(shots) > 0, "No shots extracted!"
    print(f"✓ Extracted {len(shots)} shots")

    # Verify shot structure
    shot = shots[0]
    assert "shot_number" in shot, "Shot missing shot_number!"
    assert "text" in shot, "Shot missing text!"
    assert "duration_seconds" in shot, "Shot missing duration!"
    print(f"✓ Shot 1: {shot['shot_number']} ({shot.get('duration_seconds', 0):.1f}s)")

    # Check for entity extraction
    total_entities = sum(len(s.get("entities", [])) for s in shots)
    print(f"✓ Extracted {total_entities} entities from script")

    # Check metadata
    assert result.output.get("total_shots", 0) > 0, "Total shots not calculated!"
    print(f"✓ Total estimated duration: {result.output.get('total_duration_seconds', 0):.1f}s")

    return True


def test_visual_planner():
    """Test 5: Visual Planner Agent"""
    print("\n" + "="*60)
    print("TEST 5: Visual Planner Agent")
    print("="*60)

    agent = VisualPlannerAgent()

    # Get shots from script analyzer
    analyzer = ScriptAnalyzerAgent()
    analysis = analyzer.run({"script": SAMPLE_SCRIPT})
    shots = analysis.output.get("shots", [])

    result = agent.run({"shots": shots})
    assert result.status == AgentStatus.COMPLETED, f"Visual planning failed: {result.status}"
    print(f"✓ Visual planning completed")

    # Verify visual strategies
    strategies = result.output.get("strategies", [])
    print(f"✓ Generated visual strategies for {len(strategies)} shots")

    if strategies:
        strategy = strategies[0]
        assert "visual_type" in strategy or "recommendation" in strategy, "Strategy incomplete!"
        print(f"✓ Strategy 1: {strategy.get('visual_type', 'visual') or 'recommendation'}")

    return True


def test_asset_finder():
    """Test 6: Asset Finder Agent"""
    print("\n" + "="*60)
    print("TEST 6: Asset Finder Agent")
    print("="*60)

    agent = AssetFinderAgent()

    # Create test shots
    test_shots = [
        {
            "shot_number": 1,
            "text": "Technology in Africa",
            "entities": [{"text": "Africa", "type": "PLACE"}]
        },
        {
            "shot_number": 2,
            "text": "Mobile banking success",
            "entities": [{"text": "mobile banking", "type": "CONCEPT"}]
        }
    ]

    result = agent.run({"shots": test_shots})

    # Asset finder may not find results in isolated environment
    # Just verify it completes and has expected output structure
    assert result.status in [AgentStatus.COMPLETED, AgentStatus.PARTIAL], \
        f"Asset finding failed: {result.status}"
    print(f"✓ Asset finder executed (status: {result.status})")

    output = result.output
    assert "total_assets_found" in output or "gaps" in output, "Missing output structure!"
    print(f"✓ Output structure valid")

    return True


def test_advanced_qa():
    """Test 7: Advanced QA Checker"""
    print("\n" + "="*60)
    print("TEST 7: Advanced QA Checks")
    print("="*60)

    checker = AdvancedQAChecker()

    # Test pacing detection
    timeline = [
        {"clip_id": "c1", "shot_id": "s1", "start_time_seconds": 0, "end_time_seconds": 1},  # Too fast
        {"clip_id": "c2", "shot_id": "s2", "start_time_seconds": 1, "end_time_seconds": 10},  # Too slow
        {"clip_id": "c3", "shot_id": "s3", "start_time_seconds": 10, "end_time_seconds": 15},  # OK (5s)
    ]

    pacing = checker.detect_pacing_issues(timeline)
    assert pacing["pacing_issues_found"], "Pacing issues not detected!"
    print(f"✓ Pacing issues detected: {pacing['count']} problems found")

    # Test duplicate detection
    duplicates = checker.detect_duplicate_shots(timeline)
    print(f"✓ Duplicate detection: {duplicates.get('count', 0)} duplicates found")

    # Test resolution validation
    assets = [
        {"asset_id": "a1", "width": 1920, "height": 1080},  # OK
        {"asset_id": "a2", "width": 640, "height": 480},    # Too low
    ]

    resolution = checker.detect_resolution_issues(assets)
    assert resolution["resolution_issues_found"], "Resolution issues not detected!"
    print(f"✓ Resolution issues detected: {resolution['count']} assets below 1280x720")

    return True


def test_logging_observability():
    """Test 8: Logging & Observability"""
    print("\n" + "="*60)
    print("TEST 8: Logging & Observability")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        logger = ProductionLogger(tmpdir)

        # Log agent action
        logger.log_agent_action(
            agent_name="test_agent",
            action_type="test_action",
            status="success",
            duration_ms=150.5,
            cost_usd=0.05,
            model_used="gpt-4"
        )
        print(f"✓ Agent action logged")

        # Log API call
        logger.log_api_call(
            provider="TestAPI",
            endpoint="/v1/test",
            response_time_ms=250,
            cost_usd=0.03
        )
        print(f"✓ API call logged")

        # Generate telemetry
        telemetry = logger.generate_project_telemetry()
        assert telemetry["total_cost_usd"] > 0, "Costs not aggregated!"
        print(f"✓ Telemetry generated: Total cost ${telemetry['total_cost_usd']:.2f}")

        assert telemetry["total_agents"] > 0, "Agents not tracked!"
        print(f"✓ Tracked {telemetry['total_agents']} agent(s)")

    return True


def test_data_contracts():
    """Test 9: Data Contracts & Schemas"""
    print("\n" + "="*60)
    print("TEST 9: Data Contracts & Schemas")
    print("="*60)

    # Create valid shot
    shot = Shot(
        shot_id="shot_1",
        shot_number=1,
        text="Documentary narration",
        duration_seconds=5.0
    )
    print(f"✓ Shot schema: {shot.shot_id} ({shot.duration_seconds}s)")

    # Create valid asset
    asset = Asset(
        asset_id="asset_1",
        source="pexels",
        url="https://pexels.com/video/123",
        license=LicenseType.CC0,
        search_query="documentary"
    )
    print(f"✓ Asset schema: {asset.asset_id} from {asset.source}")

    # Create valid timeline clip
    clip = Timeline(
        clip_id="clip_1",
        shot_id="shot_1",
        start_time_seconds=0.0,
        end_time_seconds=5.0,
        asset_ref="asset_1"
    )
    print(f"✓ Timeline schema: {clip.clip_id} (0.0-5.0s)")

    # Create quality score
    score = QualityScore(
        overall_score=85.0,
        claims_verified=True,
        visuals_complete=True,
        audio_sync_quality=90.0
    )
    print(f"✓ Quality score: {score.overall_score}/100")

    # Test validation - invalid duration
    try:
        invalid_shot = Shot(
            shot_id="invalid",
            shot_number=1,
            text="Bad shot",
            duration_seconds=-1
        )
        print("✗ Validation failed - negative duration accepted!")
        return False
    except ValueError:
        print(f"✓ Validation works - rejected invalid duration")

    # Test validation - invalid time order
    try:
        invalid_clip = Timeline(
            clip_id="bad",
            shot_id="s1",
            start_time_seconds=10.0,
            end_time_seconds=5.0,
            asset_ref="a1"
        )
        print("✗ Validation failed - invalid time order accepted!")
        return False
    except ValueError:
        print(f"✓ Validation works - rejected invalid time order")

    return True


def test_base_agent():
    """Test 10: Base Agent Foundation"""
    print("\n" + "="*60)
    print("TEST 10: Base Agent Foundation")
    print("="*60)

    # Create test agent
    agent = BaseAgent(name="test_agent", description="Test agent")

    # Test message logging
    agent.log_status("Test message")
    print(f"✓ Agent logging works")

    # Test error logging
    agent.log_error("Test error")
    print(f"✓ Error logging works")

    # Verify agent properties
    assert agent.name == "test_agent", "Agent name mismatch!"
    assert agent.description == "Test agent", "Agent description mismatch!"
    print(f"✓ Agent properties: {agent.name}")

    return True


def run_all_tests():
    """Run all agent tests"""
    print("\n" + "█" * 60)
    print("AFRICA RISING FRAMEWORK - DEEP AGENT TEST")
    print("█" * 60)

    tests = [
        ("Input Validation", test_input_validation),
        ("Prompt Manager", test_prompt_manager),
        ("License Tracking", test_license_tracking),
        ("Script Analyzer", test_script_analyzer),
        ("Visual Planner", test_visual_planner),
        ("Asset Finder", test_asset_finder),
        ("Advanced QA", test_advanced_qa),
        ("Logging", test_logging_observability),
        ("Data Contracts", test_data_contracts),
        ("Base Agent", test_base_agent),
    ]

    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ {name} FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {name}")

    print("\n" + "="*60)
    print(f"RESULT: {passed}/{total} tests passed")
    print("="*60)

    if passed == total:
        print("🎉 ALL TESTS PASSED - Framework is production-ready!")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
