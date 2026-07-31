# Operating Procedures

## Production Video Workflow: Start to Finish

### Phase 1: Preparation (30 minutes)

#### 1.1 Setup Environment
```bash
cd /Users/rajab/africa_rising_framework

# Load environment
source .env
source venv/bin/activate

# Verify all systems
python3 -c "from agents.base_agent import BaseAgent; print('✓ Framework ready')"
```

#### 1.2 Prepare Script
- Write or obtain script document (Markdown or text)
- Ensure script is >100 words
- Organize into clear sections (Scene 1, Scene 2, etc.)
- Each section ~100-200 words (3-5 minutes video time)

**Example structure:**
```
# Documentary Title
## Scene 1: Introduction
Narration for opening scene...

## Scene 2: Main Story
Narration for story development...

## Scene 3: Conclusion
Concluding remarks...
```

#### 1.3 Update Configuration
```yaml
# Edit config.yaml
project:
  name: "Your Documentary Title"
  channel: "Africa Rising"

narration:
  voice: "george"  # or "bella", "marcus"

# Verify all API keys are set
research:
  tavily:
    api_key: "your_key_here"
```

#### 1.4 Set Budget Limit
```bash
# Edit deploy/.env or config.yaml
export BUDGET_LIMIT_USD="50.00"
```

### Phase 2: Research & Validation (20 minutes)

#### 2.1 Run Research Agent
```python
python3 << 'EOF'
from agents.research_agent import ResearchAgent
agent = ResearchAgent()
result = agent.run({
    "script": open("script.md").read()
})
print(f"Claims verified: {result.output['verified_count']}")
print(f"Unsupported claims: {result.output['unsupported_claims']}")
EOF
```

**What to look for:**
- ✓ All major claims have sources
- ✓ Statistics are verified
- ⚠️ Flag unverified claims for editing

#### 2.2 Review & Update Script
If claims are unverified:
- Edit script to match verified facts
- Add citations in brackets `[Source: Reuters]`
- Re-run research agent

### Phase 3: Script Analysis (10 minutes)

#### 3.1 Break Script into Shots
```python
python3 << 'EOF'
from agents.script_analyzer_agent import ScriptAnalyzerAgent
agent = ScriptAnalyzerAgent()
result = agent.run({
    "script": open("script.md").read()
})
print(f"Total shots: {len(result.output['shots'])}")
for shot in result.output['shots'][:3]:
    print(f"  Shot {shot['shot_number']}: {shot['duration']:.1f}s")
EOF
```

**Output check:**
- Shot duration 2-8 seconds (per Emmy standards)
- Emotions identified for each shot
- Locations extracted for maps

### Phase 4: Asset Discovery (15 minutes)

#### 4.1 Find Stock Footage
```python
python3 << 'EOF'
from agents.asset_finder_agent import AssetFinderAgent
agent = AssetFinderAgent()
result = agent.run({
    "shots": shots_from_analysis
})
print(f"Assets found: {result.output['total_assets_found']}")
print(f"Coverage: {result.output['coverage_percent']:.1f}%")
EOF
```

**Expected results:**
- >80% coverage with stock assets
- Mix from Pexels, Archive.org, NASA, Library of Congress
- Automatic license tracking

#### 4.2 Check Asset Licenses
```python
from core.license_manager import LicenseManager
manager = LicenseManager()
print(manager.list_assets_needing_attribution())
```

### Phase 5: Visual Generation (30-60 minutes)

#### 5.1 Generate Missing Visuals
For shots without good stock footage:

```python
python3 << 'EOF'
from agents.ai_generator_agent import AIGeneratorAgent
agent = AIGeneratorAgent()
result = agent.run({
    "shots": shots_from_analysis,
    "gaps": [2, 5, 8]  # Shot numbers needing generation
})
print(f"Generated: {result.output['total_generated']}")
print(f"Cost: ${result.output['estimated_cost']:.2f}")
EOF
```

**Cost breakdown:**
- Veo: $0.15/video (most cinematic)
- Runway: $0.10/video (fast)
- Grok: $0.05/image

**Tips:**
- Limit to 3-5 generated videos per project
- Use for specific scenes without good stock alternatives
- Monitor costs in real-time: `tail -f output/logs/costs.jsonl`

### Phase 6: Audio Production (10 minutes)

#### 6.1 Generate Narration
```python
python3 << 'EOF'
from agents.narration_agent import NarrationAgent
agent = NarrationAgent()
result = agent.run({
    "sections": shots_from_analysis,
    "voice": "george",
    "output_dir": "cache/narration/"
})
print(f"Narration generated: {result.output['total_sections']} sections")
print(f"Cost: ${result.output['cost']:.2f}")
EOF
```

**Voice options:**
- `george`: Deep, authoritative (default for documentaries)
- `bella`: Empathetic, clear
- `marcus`: Energetic, dynamic

#### 6.2 Generate Captions
```python
python3 << 'EOF'
from agents.captioning_agent import CaptioningAgent
agent = CaptioningAgent()
result = agent.run({
    "narration_dir": "cache/narration/",
    "output_dir": "cache/captions/",
    "format": "srt"  # or "vtt", "json"
})
print(f"Captions generated: {result.output['captions_generated']}")
EOF
```

**Output:** SRT file with auto-generated subtitles

### Phase 7: Visual Effects (if needed)

#### 7.1 Generate Map Animations
For documentaries with geographic context:

```python
python3 << 'EOF'
from agents.map_animation_agent import MapAnimationAgent
agent = MapAnimationAgent()
result = agent.run({
    "shots": shots_from_analysis,
    "output_dir": "cache/visuals/maps/"
})
print(f"Maps created: {result.output['animations_created']}")
print(f"Cost: ${result.output['cost']:.2f}")
EOF
```

**Cost:** $0.50 per animation

#### 7.2 Apply Color Grading
Handled automatically by FFmpeg Editor based on shot emotions

### Phase 8: Timeline Assembly (20 minutes)

#### 8.1 Build Timeline
```python
python3 << 'EOF'
from agents.timeline_builder_agent import TimelineBuilderAgent
agent = TimelineBuilderAgent()
result = agent.run({
    "shots": shots_from_analysis,
    "narration_dir": "cache/narration/",
    "assets": all_discovered_assets
})
print(f"Timeline clips: {result.output['total_clips']}")
print(f"Total duration: {result.output['duration_seconds']:.1f}s")
EOF
```

**Check:**
- ✓ Narration matches visuals
- ✓ Transitions are smooth
- ✓ Pacing is 2-8s per shot

### Phase 9: Video Editing (20 minutes)

#### 9.1 Assemble Final Video
```python
python3 << 'EOF'
from agents.ffmpeg_editor_agent import FFmpegEditorAgent
agent = FFmpegEditorAgent()
result = agent.run({
    "timeline": timeline_from_builder,
    "output_file": "output/projects/documentary_final.mp4"
})
print(f"Video complete: {result.output['output_file']}")
print(f"Duration: {result.output['duration']:.1f}s")
print(f"File size: {result.output['file_size_mb']:.1f} MB")
EOF
```

**Output settings:**
- Resolution: 1280x720 (HD)
- Frame rate: 25 fps
- Codec: H.264
- Audio: AAC stereo

### Phase 10: Quality Review (15 minutes)

#### 10.1 Run QA Checks
```python
python3 << 'EOF'
from agents.quality_review_agent import QualityReviewAgent
from core.advanced_qa import AdvancedQAChecker

# Standard QA
qa = QualityReviewAgent()
result = qa.run({"video_file": "output/projects/documentary_final.mp4"})
print(f"Quality score: {result.output['quality_score']}/100")

# Advanced checks
checker = AdvancedQAChecker()
report = checker.run_all_checks(project_data)
print(f"\nAdvanced QA Report:")
print(f"  Unsupported claims: {report['unsupported_claims']['count']}")
print(f"  Pacing issues: {report['pacing']['count']}")
print(f"  Duplicate shots: {report['duplicate_shots']['count']}")
EOF
```

**Quality thresholds:**
- ✓ APPROVED: 90+ score
- ⚠️ NEEDS_REVISION: 70-89 score
- ❌ REJECTED: <70 score

#### 10.2 Address Issues
If issues found:
1. Review specific problems (see advanced_qa report)
2. Re-edit timeline or assets
3. Re-run assembly and QA
4. Repeat until APPROVED status

### Phase 11: Final Output & Export

#### 11.1 Generate Credits
```python
python3 << 'EOF'
from core.license_manager import LicenseManager
manager = LicenseManager()
credits = manager.generate_credits_for_description()
print("Paste this in YouTube description:")
print(credits)
EOF
```

#### 11.2 Export Metadata
```bash
# Export project report
cat output/projects/PROJECT_REPORT.json | jq

# Export telemetry
cat output/logs/project_telemetry.json | jq '.total_cost_usd'
```

#### 11.3 Prepare YouTube Upload
```
Video File: output/projects/documentary_final.mp4
Thumbnail: output/projects/thumbnail.jpg (auto-generated at 3s mark)
Title: [Your Documentary Title]
Description: [Paste credits from 11.1]
Tags: labor, technology, Africa, documentary, [your keywords]
Category: Documentary
License: Creative Commons Attribution
```

### Phase 12: Monitoring & Publication

#### 12.1 Monitor Telemetry
```bash
# Watch logs live
tail -f output/logs/application.log

# Check final cost
jq '.total_cost_usd' output/logs/project_telemetry.json

# Review agent performance
jq '.agents' output/logs/project_telemetry.json
```

#### 12.2 Upload to YouTube
```bash
# Manual upload via YouTube Studio:
# 1. Go to youtube.com/upload
# 2. Select video: output/projects/documentary_final.mp4
# 3. Add title, description (with credits), tags
# 4. Set as unlisted/private for review
# 5. Get feedback before publishing
```

## Workflow Automation

### Run Full Pipeline
```bash
python3 pipeline.py \
  --script "script.md" \
  --project "my_documentary" \
  --budget 50.0
```

### Run Specific Stage Only
```bash
# Just research
python3 pipeline.py --script script.md --stage research

# Just asset finding
python3 pipeline.py --stage asset_finder

# Just video assembly
python3 pipeline.py --stage editing
```

## Cost Optimization

### Minimize Costs (Target: $15-25/video)
1. Maximize stock footage coverage (aim >85%)
2. Use Grok for images only ($0.05 each)
3. Use Runway (not Veo) for video ($0.10 vs $0.15)
4. Limit maps to 1-2 per video ($0.50 each)
5. Use "bella" voice (same cost as "george", better for some content)

### Premium Quality (Target: $40-50/video)
1. Use Veo for hero shots ($0.15 per video)
2. Create 3-4 AI videos
3. Use multiple map animations
4. Higher resolution narration model

## Incident Response

### If budget is exceeded:
1. **STOP** - Stop generating visuals immediately
2. **ASSESS** - Check total costs: `jq '.total_cost_usd' output/logs/project_telemetry.json`
3. **NOTIFY** - Review what was generated
4. **DECIDE** - Continue with existing assets or restart with lower budget

### If quality score is low:
1. **REVIEW** - Check specific issues in QA report
2. **PRIORITIZE** - Fix critical issues first (unsupported claims)
3. **RE-EDIT** - Update timeline or assets
4. **TEST** - Re-run QA after changes

### If video encoding fails:
1. **CHECK SPACE** - Ensure 2GB+ free disk space
2. **CHECK PERMISSIONS** - Run `chmod 755 output`
3. **CHECK FFMPEG** - Run `ffmpeg -version`
4. **RESTART** - Delete failed output and retry

## Standard Operating Procedure Summary

| Phase | Duration | Key Output |
|-------|----------|-----------|
| Preparation | 30m | Script ready, config updated |
| Research | 20m | Verified claims, sources |
| Analysis | 10m | Shots with metadata |
| Asset Discovery | 15m | 80%+ coverage |
| Visual Generation | 30-60m | Missing visuals created |
| Audio | 10m | Narration + captions |
| Timeline | 20m | Synchronized clips |
| Editing | 20m | Final video file |
| QA Review | 15m | Quality score, fixes |
| Export | 10m | Credits, metadata |
| Upload | 5m | Video published |

**Total Time: 3-4 hours per video**
**Typical Cost: $15-50 (depending on premium features)**
