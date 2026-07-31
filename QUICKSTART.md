# Africa Rising Framework — Quick Start

## The System is Ready

You now have a **complete, reusable video production pipeline** that will handle all future Africa Rising videos.

## Files Created

```
/Users/rajab/africa_rising_framework/
├── script_analyzer.py       # Parse scripts into visual shots
├── asset_collector.py       # Find stock footage & archives
├── visual_generator.py      # Create AI images, maps, animations
├── auto_editor.py           # Build edit plans & assembly instructions
├── pipeline.py              # Main orchestrator (run this!)
├── config.yaml              # All settings & API keys
├── README.md                # Full documentation
├── QUICKSTART.md            # This file
└── pipelines/
    └── facebook_moderators/ # First project (template)
```

## One-Command Video Production

```bash
cd /Users/rajab/africa_rising_framework
python3 pipeline.py <script_file> <narration_dir>
```

**Example:**
```bash
python3 pipeline.py /Users/rajab/africa_rising_production/facebook_moderators_script.md /Users/rajab/africa_rising_production/cache/
```

## What It Does (in order)

1. **Script Analysis** — Breaks down script into shots, extracts entities, suggests visuals
2. **Asset Collection** — Searches Pexels, Internet Archive for stock footage
3. **Visual Generation** — Creates AI infographics, maps, animations for gaps
4. **Edit Planning** — Syncs everything to narration, builds assembly instructions

## Output

Each project generates:

- `PROJECT_REPORT.json` — Complete analysis (open to review)
- `ASSEMBLY_INSTRUCTIONS.txt` — Human-readable step-by-step guide
- `edit_plan.json` — Technical clip-by-clip timeline

## For the Facebook Moderators Video

**Current status:** Complete (3:42, 34 MB, high quality)

To test the framework:
```bash
python3 pipeline.py /Users/rajab/africa_rising_production/facebook_moderators_script.md /Users/rajab/africa_rising_production/cache/
```

This will create a fresh analysis in `/pipelines/facebook_moderators/` showing what assets were used and how the video was assembled.

## For Future Videos

1. **Write script** → save as plain text or markdown
2. **Generate narration** → ElevenLabs TTS (George voice), save to section_1.mp3, section_2.mp3, etc.
3. **Run pipeline** → `python3 pipeline.py script.md narration_dir/`
4. **Review output** → Check PROJECT_REPORT.json and ASSEMBLY_INSTRUCTIONS.txt
5. **Follow instructions** → Collect any missing assets, generate AI visuals
6. **Assemble video** → Use edit_plan.json + FFmpeg (or MoviePy)
7. **Upload** → YouTube (credentials already stored)

## Key Features

✅ **Fully automated** — Script → finished assembly plan in one command  
✅ **Free asset sources** — Pexels (stock), Internet Archive (historical)  
✅ **AI generation fallback** — Grok Imagine ($0.05/image) for gaps  
✅ **Emotion-based editing** — Auto color grades based on script tone  
✅ **Narration sync** — Visuals auto-adjust to match audio duration  
✅ **Reusable** — Template for all future Africa Rising videos  

## Configuration

All settings in `config.yaml`:
- API keys (Pexels, Grok, ElevenLabs)
- Video resolution/fps/codec
- Animation types and timing
- Color grading profiles
- Transition defaults

## Cost Per Video

- Stock footage: Free (Pexels)
- AI images: $0.40-0.50 (Grok) or $1.60-2.00 (DALL-E)
- Narration: ~$5 (ElevenLabs pay-per-word)
- **Total: ~$5-7 per video**

## Troubleshooting

**Q: Script parsing errors?**
A: Make sure script is plain text or markdown. One sentence per line helps.

**Q: No assets found for a shot?**
A: Review search queries in PROJECT_REPORT.json, try different keywords manually in Pexels/Archive.

**Q: AI images cost too much?**
A: Prioritize stock footage first. Use AI images only for data visualizations (charts, infographics).

**Q: Want to skip certain shots?**
A: Edit the PROJECT_REPORT.json before assembly, remove shots you don't need.

## Next Steps

1. ✅ Framework is built and saved to memory
2. ⏭️  Test on Facebook Moderators video: `python3 pipeline.py facebook_moderators_script.md cache/`
3. ⏭️  Review output files
4. ⏭️  For next video, repeat with new script + narration

---

**Framework ready for production.** All modules tested with real Pexels API + sample data.

Questions? See README.md or inline Python docstrings.
