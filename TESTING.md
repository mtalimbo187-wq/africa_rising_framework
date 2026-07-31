# Testing Guide

## Running Tests

### Unit Tests

```bash
# Run all unit tests
python3 -m pytest tests/test_schemas.py -v

# Run specific test
python3 -m pytest tests/test_schemas.py::TestShot::test_valid_shot -v

# With coverage
python3 -m pytest tests/test_schemas.py --cov=core --cov-report=html
```

### Integration Tests

```bash
# Run integration tests
python3 -m pytest tests/test_integration.py -v

# Run with logging
python3 -m pytest tests/test_integration.py -v -s
```

### Full Test Suite

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run with coverage report
python3 -m pytest tests/ --cov=. --cov-report=html
```

## Test Categories

### 1. Schema Validation Tests
**File:** `tests/test_schemas.py`

Tests data contracts and schemas:
- ✓ Valid Shot creation
- ✓ Invalid duration handling
- ✓ Asset metadata
- ✓ Timeline clip ordering
- ✓ Quality score calculations

**Run:**
```bash
pytest tests/test_schemas.py::TestShot -v
pytest tests/test_schemas.py::TestAsset -v
pytest tests/test_schemas.py::TestTimeline -v
pytest tests/test_schemas.py::TestQualityScore -v
```

### 2. Prompt Management Tests
**File:** `tests/test_integration.py::TestPromptManager`

Tests prompt versioning and templates:
- ✓ Prompt initialization
- ✓ Role template retrieval
- ✓ Prompt interpolation

**Run:**
```bash
pytest tests/test_integration.py::TestPromptManager -v
```

### 3. License Tracking Tests
**File:** `tests/test_integration.py::TestLicenseManager`

Tests license compliance:
- ✓ Asset tracking
- ✓ Usage validation
- ✓ Credit generation

**Run:**
```bash
pytest tests/test_integration.py::TestLicenseManager -v
```

### 4. Quality Assurance Tests
**File:** `tests/test_integration.py::TestAdvancedQA`

Tests QA checks:
- ✓ Pacing detection
- ✓ Duplicate shots
- ✓ Resolution validation

**Run:**
```bash
pytest tests/test_integration.py::TestAdvancedQA -v
```

### 5. Observability Tests
**File:** `tests/test_integration.py::TestObservability`

Tests logging and telemetry:
- ✓ Agent action logging
- ✓ API call logging
- ✓ Telemetry generation

**Run:**
```bash
pytest tests/test_integration.py::TestObservability -v
```

## Regression Tests

### Reference Project Test

```bash
# Create reference project
python3 << 'EOF'
import json
from pathlib import Path

reference = {
    "script": "Sample documentary script about Africa Rising...",
    "expected_shots": 8,
    "expected_duration": 25.0,
    "quality_score_min": 85,
}

with open("tests/regression/reference_1.json", "w") as f:
    json.dump(reference, f)
EOF

# Run test
python3 << 'EOF'
import json
from agents.script_analyzer_agent import ScriptAnalyzerAgent

reference = json.load(open("tests/regression/reference_1.json"))
agent = ScriptAnalyzerAgent()
result = agent.run({"script": reference["script"]})

# Compare
assert len(result.output['shots']) >= reference['expected_shots'], "Fewer shots than expected"
assert result.output['total_duration'] >= reference['expected_duration'], "Shorter duration than expected"
print("✓ Regression test passed")
EOF
```

### Save Reference Output

```bash
# After successful production run
cp output/projects/PROJECT_REPORT.json tests/regression/expected_output.json
cp output/logs/project_telemetry.json tests/regression/expected_telemetry.json
```

## Performance Tests

### Memory Usage Test

```bash
python3 << 'EOF'
import psutil
from agents.asset_finder_agent import AssetFinderAgent

process = psutil.Process()
initial_memory = process.memory_info().rss / 1024 / 1024  # MB

agent = AssetFinderAgent()
# Run 100 searches
for i in range(100):
    agent.run({"shots": [{"text": f"Search query {i}"}]})

final_memory = process.memory_info().rss / 1024 / 1024
increase = final_memory - initial_memory

print(f"Memory increase: {increase:.1f} MB")
assert increase < 500, "Memory leak detected"
EOF
```

### Speed Test

```bash
python3 << 'EOF'
import time
from agents.script_analyzer_agent import ScriptAnalyzerAgent

script = "Large script text..." * 100

start = time.time()
agent = ScriptAnalyzerAgent()
result = agent.run({"script": script})
duration = time.time() - start

print(f"Script analysis: {duration:.2f}s")
assert duration < 30, "Script analysis too slow"
EOF
```

## Integration Test Scenario

### Full Pipeline Test

```bash
python3 << 'EOF'
import tempfile
from pathlib import Path
from agents.producer_agent import ProducerAgent

# Setup
with tempfile.TemporaryDirectory() as tmpdir:
    # Create test script
    script_file = Path(tmpdir) / "test_script.md"
    script_file.write_text("""
# Test Documentary
## Scene 1
This is a test scene about technology in Africa.

## Scene 2
More content about innovation and development.
""")

    # Run producer
    producer = ProducerAgent("test_project")
    result = producer.execute({
        "request": "Create test documentary",
        "script_file": str(script_file),
        "narration_dir": str(Path(tmpdir) / "narration")
    })

    # Verify
    assert result.status == "COMPLETED"
    print("✓ Full pipeline test passed")
EOF
```

## Continuous Integration

### CI Configuration (`.github/workflows/test.yml`)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: pytest tests/ --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Test Coverage Goals

| Module | Current | Target |
|--------|---------|--------|
| core/schemas.py | 85% | 95% |
| core/prompt_manager.py | 70% | 85% |
| core/license_manager.py | 80% | 90% |
| core/advanced_qa.py | 75% | 85% |
| core/observability.py | 80% | 90% |
| core/security.py | 70% | 85% |
| agents/base_agent.py | 85% | 95% |

## Running Coverage Analysis

```bash
# Generate coverage report
python3 -m pytest tests/ --cov=. --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Debugging Tests

### Verbose Output

```bash
pytest tests/ -vv -s
```

### Stop on First Failure

```bash
pytest tests/ -x
```

### Debug with PDB

```bash
pytest tests/ --pdb
```

### Show Local Variables

```bash
pytest tests/ -l
```

## Test Best Practices

1. **Isolate Tests** - Use temporary directories, don't touch filesystem
2. **Mock External APIs** - Use `unittest.mock` for API calls
3. **Clear Assertions** - Each test should have 1-3 assertions
4. **Descriptive Names** - Test name should explain what it tests
5. **Setup/Teardown** - Use `setUp` and `tearDown` for cleanup
6. **Document Expectations** - Add docstrings explaining test purpose

## Example: Writing a New Test

```python
import unittest
from core.schemas import Shot, EmotionType

class TestShotMetadata(unittest.TestCase):
    """Test Shot metadata extraction"""
    
    def setUp(self):
        """Create test fixtures"""
        self.valid_shot = Shot(
            shot_id="test_1",
            shot_number=1,
            text="Test narration",
            duration_seconds=5.0
        )
    
    def test_shot_with_emotions(self):
        """Test that emotions are properly tracked"""
        shot = Shot(
            shot_id="test_2",
            shot_number=2,
            text="Dramatic scene",
            duration_seconds=3.0,
            emotions=[EmotionType.DRAMATIC, EmotionType.DOCUMENTARY]
        )
        self.assertEqual(len(shot.emotions), 2)
        self.assertIn(EmotionType.DRAMATIC, shot.emotions)
    
    def tearDown(self):
        """Cleanup"""
        pass

if __name__ == "__main__":
    unittest.main()
```

## Troubleshooting Test Failures

### Import Errors
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/path/to/africa_rising_framework
pytest tests/
```

### Missing Dependencies
```bash
# Install test dependencies
pip install pytest pytest-cov
```

### File Not Found
```bash
# Tests must run from project root
cd /Users/rajab/africa_rising_framework
pytest tests/
```

### Assertion Errors
- Check test expected values
- Verify test fixtures are correct
- Review error message for details
