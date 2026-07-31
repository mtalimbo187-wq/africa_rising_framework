# Africa Rising Automated Video Framework

Complete pipeline for producing investigative documentary videos on labor, economics, and social justice in Africa.

## Structure

```
africa_rising_framework/
├── script_analyzer.py          # Break down script → visual requirements
├── asset_collector.py          # Search for stock, archives, news footage
├── visual_generator.py         # Create AI images, animations, maps
├── auto_editor.py              # Build edit plan and sync to narration
├── pipeline.py                 # Orchestrate the complete workflow
├── config.yaml                 # Settings, API keys, templates
├── templates/                  # Script and prompt templates
├── cache/
│   ├── assets/                # Collected stock footage/archives
│   ├── visuals/               # Generated images/animations
│   └── narration/             # Audio files
└── pipelines/
    ├── facebook_moderators/    # Project 1
    ├── [future_project]/       # Project 2, etc.
    └── ...
```

## Quick Start

### 1. Create a new project

```bash
cd /Users/rajab/africa_rising_framework
python3 pipeline.py scripts/your_script.md cache/narration/
```

### 2. Pipeline flow

**Input:** Script → **Output:** Complete project with assembly plan

1. **Script Analyzer** — Breaks down script into shots
   - Extracts: persons, places, dates, events, emotions
   - Suggests: visual types, search queries
   - Estimates: duration, pacing

2. **Asset Collector** — Finds existing assets
   - Searches: Pexels, Internet Archive, Unsplash
   - Saves: links, metadata, cache

3. **Visual Generator** — Creates missing visuals
   - Generates: AI infographics, maps, timelines
   - Animates: still images (Ken Burns, zoom/pan)
   - Creates: text overlays, statistics cards

4. **Auto Editor** — Builds video edit plan
   - Syncs: visuals to narration duration
   - Assigns: transitions, effects, color grades
   - Outputs: assembly instructions + FFmpeg script

### 3. Output files

Each project generates:

- `PROJECT_REPORT.json` — Complete analysis + plan
- `ASSEMBLY_INSTRUCTIONS.txt` — Step-by-step assembly guide
- `edit_plan.json` — Detailed clip-by-clip timeline
- `collected_assets.json` — All found assets with URLs
- `generation_plan.json` — AI visuals to be generated

## Configuration

Edit `config.yaml` to:
- Set API keys (Pexels, Grok, etc.)
- Adjust video settings (resolution, fps, codec)
- Configure narration (voice, provider)
- Customize colors, transitions, animations

## Usage Examples

### Example 1: Analyze just the script

```python
from script_analyzer import ScriptAnalyzer

analyzer = ScriptAnalyzer()
analysis = analyzer.analyze(open("script.txt").read())

for shot in analysis["shots"]:
    print(f"Shot {shot['shot_number']}: {shot['visual_types']}")
```

### Example 2: Run full pipeline

```python
from pipeline import AfricaRisingPipeline

pipeline = AfricaRisingPipeline("my_project")
results = pipeline.run(
    script_file="script.md",
    narration_dir="cache/narration/"
)
```

### Example 3: Collect assets for specific shot

```python
from asset_collector import AssetCollector

collector = AssetCollector()
result = collector.collect_for_shot(
    query="content moderator working",
    visual_type="stock_footage",
    shot_number=1
)
```

## API Keys Required

Add to `config.yaml` or environment:

- **Pexels:** `6mRphkqCxN8oBj28vU9lpdeMXgoS5EfsdTKKK9Ts0Dv14pT07cxAPjdq` (stock video)
- **Grok/xAI:** `xai-edxHqBNRmIYIoqJQ03Q7A4oiZEtJhO3G0RZKDKLL1HipEdaWWUhTI1A8TfPpEd2Wltg3HfVQPssNMGDz` (AI images)
- **ElevenLabs:** From memory (TTS narration)
- **YouTube:** From memory (upload channel)

## Workflow for New Video

1. **Write script** → save as `scripts/video_name.md`
2. **Generate narration** → save to `cache/narration/section_1.mp3`, etc.
3. **Run pipeline** → `python3 pipeline.py scripts/video_name.md cache/narration/`
4. **Review project report** → `/pipelines/video_name/PROJECT_REPORT.json`
5. **Collect missing assets** → Use assembly instructions
6. **Generate AI visuals** → For gaps in stock footage
7. **Assemble video** → Use edit plan + FFmpeg script
8. **Upload** → Use YouTube credentials

## Future Enhancements

- [ ] Auto-generate infographics (maps, charts)
- [ ] Animate data visualizations
- [ ] Batch AI image generation
- [ ] Auto-upload to YouTube
- [ ] Email notifications for long tasks
- [ ] Web UI for asset preview + approval
- [ ] Template library (investigations, profiles, features)
- [ ] A/B test different edits

## Cost Estimates

Per video:
- **Stock footage:** Free (Pexels)
- **AI images (10):** $0.50 (Grok), $2 (DALL-E)
- **Narration (7 min):** $5 (ElevenLabs)
- **Total:** ~$5-7 per video

## Support

- Framework location: `/Users/rajab/africa_rising_framework/`
- Questions: Refer to inline Python docstrings
- Troubleshooting: Check project JSON reports for errors

---

**Version:** 1.0 | **Created:** July 30, 2026 | **Status:** Production Ready
