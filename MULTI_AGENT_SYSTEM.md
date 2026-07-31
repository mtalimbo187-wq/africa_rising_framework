# Multi-Agent Video Production System

## Complete Architecture

10 specialized agents working in sequence → Fully automated documentary production

```
USER REQUEST
    ↓
┌─────────────────────────────────────────────────────────────┐
│ PRODUCER AGENT (Orchestrator)                               │
│ Coordinates all agents, manages workflow, reports progress  │
└─────────────────────────────────────────────────────────────┘
    ↓
    ├─→ [1] RESEARCH AGENT
    │   └─ Extracts facts, claims, statistics
    │   └─ Suggests trusted sources
    │   └─ Creates verification checklist
    │
    ├─→ [2] SCRIPT ANALYZER AGENT
    │   └─ Breaks script into shots (Person, Place, Date, Emotion, Visual, Map, Timeline)
    │   └─ Estimates duration per shot
    │   └─ Generates asset search queries
    │
    ├─→ [3] VISUAL PLANNER AGENT (Emmy-standard)
    │   └─ Decides STRONGEST visual for each shot
    │   └─ Hierarchy: Archival (10) → AI (1)
    │   └─ Teaching visuals: Maps, timelines, comparisons
    │   └─ Suggests color grading per emotion
    │
    ├─→ [4] ASSET FINDER AGENT (Parallel)
    │   └─ Searches Pexels, Pixabay, Wikimedia, NASA, Internet Archive, LoC
    │   └─ Concurrent searches = fast
    │   └─ Returns URLs, metadata, resolution
    │
    ├─→ [5] AI GENERATOR AGENT
    │   └─ Creates only when real assets unavailable
    │   └─ Generates: Veo/Runway videos, Grok/DALL-E images
    │   └─ Free: Maps (Folium), timelines (Plotly), text (PIL)
    │   └─ Tracks costs
    │
    ├─→ [6] TIMELINE BUILDER AGENT
    │   └─ Syncs visuals to narration duration
    │   └─ Creates precise clip timeline (0:00–0:05 Map, 0:05–0:08 Footage)
    │   └─ Outputs timeline.json for editor
    │
    ├─→ [7] FFMPEG EDITOR AGENT
    │   └─ Assembles video with NO manual editing
    │   └─ Handles: Transitions, zoom/pan, text overlays, audio mix
    │   └─ Outputs 1280×720 MP4 @ 25fps
    │
    └─→ [8] QUALITY REVIEW AGENT
        └─ Final QA checks:
           ✔ Wrong/missing images
           ✔ Wrong/missing dates
           ✔ Pacing (2-5 seconds per shot)
           ✔ Subtitles/captions
           ✔ Smooth transitions
           ✔ Narration/video sync
        └─ Approved for upload or flag for revision
```

---

## Agent Details

### 1. Producer Agent (Orchestrator)
**Responsibility:** Coordinate entire workflow

```python
producer.run({
    "request": "Create a 15-minute documentary on Facebook content moderators",
    "script_file": "script.md",
    "narration_dir": "audio/"
})
```

**Output:** Complete PROJECT_REPORT.json with all stage results

---

### 2. Research Agent
**Responsibility:** Fact-finding and verification

**Extracts:**
- Claims requiring verification
- Statistics (dollar amounts, percentages, years)
- Key entities (organizations, people, locations)
- Trusted sources for verification

**Output:** Verification checklist + source recommendations

---

### 3. Script Analyzer Agent
**Responsibility:** Break script into structured shots

**Per-shot analysis:**
```
Shot 1: "China built artificial islands in the South China Sea"
{
  "person": "government",
  "place": "south-china-sea",
  "date": "present",
  "emotion": "investigative",
  "visual_type": "map",
  "needs_map": true,
  "needs_timeline": false,
  "asset_priority": ["google_maps", "satellite_imagery"],
  "search_queries": ["South China Sea islands", "disputed territories map"]
}
```

**Output:** shots.json with Person, Place, Date, Emotion, Visual, Map, Timeline for each shot

---

### 4. Visual Planner Agent (Emmy-Standard)
**Responsibility:** Emmy-award-winning visual strategy

**Core principle:** Visuals TEACH, not just illustrate

**Hierarchy (10 = strongest):**
```
10: Archival footage (real events)
 9: Satellite imagery (visual truth)
 8: Maps + timelines (teaching)
 7: B-roll + news footage
 6: Animations (Ken Burns)
 5: Stock footage (generic)
 4: AI animations
 3: AI infographics
 2: Text overlays
 1: AI-generated scenes (last resort)
```

**Strategy examples:**
- Location sentence → Interactive map + labels + boundaries
- Date sentence → Timeline + before/after
- Statistic sentence → Infographic + comparison
- Action sentence → Archival footage (real event)

**Output:** Visual plan with teaching elements, asset sources, AI fallbacks

---

### 5. Asset Finder Agent (Parallel)
**Responsibility:** Search for existing assets

**Sources (in order):**
1. Pexels (stock video, free)
2. Pixabay (stock video/photos, free)
3. Wikimedia Commons (historical, free)
4. NASA (satellite/space, free)
5. Internet Archive (historical footage, free)
6. Library of Congress (historical collections, free)

**Parallel execution:** All searches concurrent = 10x faster

**Output:** assets.json with URLs, metadata, resolution, duration

---

### 6. AI Generator Agent
**Responsibility:** Create only when real assets unavailable

**Generates:**
- **Veo 3.1** / **Runway** ($0.10-0.15) → Cinematic video scenes
- **Grok Imagine** / **DALL-E** ($0.05-0.20) → Images, infographics
- **Folium** (free) → Interactive maps
- **Plotly** (free) → Timelines, data viz
- **PIL** (free) → Text overlays

**Smart fallback:** Only generate if better option doesn't exist

**Output:** generation_queue.json with queued tasks + estimated cost

---

### 7. Timeline Builder Agent
**Responsibility:** Sync visuals to narration

**Creates precise timeline:**
```
Clip 1: 0:00–0:05 | Map of Vietnam | cross_fade in
Clip 2: 0:05–0:08 | Helicopter footage | cross_fade
Clip 3: 0:08–0:12 | Soldiers marching | cross_fade
Clip 4: 0:12–0:15 | Newspaper headlines | fade out
```

**Handles:**
- Duration matching (visuals stretch/compress to audio)
- Transitions (fade, cross-fade, wipe, cut)
- Audio sync (extracts MP3 durations)

**Output:** timeline.json with precise clip timings for editor

---

### 8. FFmpeg Editor Agent
**Responsibility:** Assemble final video (NO manual editing)

**Handles:**
- Concatenate video clips
- Apply transitions (0.5s cross-fades)
- Zoom/pan animations (Ken Burns effect)
- Text overlays and lower-thirds
- Audio mixing (concatenate MP3s)
- Final render to 1280×720 MP4 @ 25fps, H.264

**Output:** output.mp4 ready for upload

---

### 9. Quality Review Agent
**Responsibility:** Final QA

**Checks:**
- ✔ Wrong/missing images → Flag if visual doesn't match narration
- ✔ Wrong/missing dates → Flag if timeline mentioned but not shown
- ✔ Pacing → Flag clips < 1.5s (too fast) or > 8s (too slow)
- ✔ Subtitles → Flag missing captions
- ✔ Transitions → Flag jarring cuts
- ✔ Narration sync → Flag audio/video duration mismatches

**Output:** QA report + approval score (0-100)

---

### 10. Producer Agent (Reporting)
**Final output:** PROJECT_REPORT.json with all workflow results

---

## System Prompt for Producer Agent

```
You are the producer of a world-class documentary studio.

Core principles:
1. Never leave narration without a matching visual
2. Every sentence must have the strongest available visual evidence
3. Prefer authentic footage over AI-generated
4. If no footage exists, generate it
5. Use maps for locations, timelines for dates, archival for history
6. Use diagrams for complex ideas
7. Produce videos with pacing, storytelling, and visual quality 
   comparable to leading documentary channels (Netflix, BBC, Vice)

Process:
1. Always verify facts before including in video
2. Source all claims with authoritative references
3. Prioritize teaching over entertainment
4. Ensure every cut, transition, and effect serves the story
5. Maintain consistent pacing and energy
```

---

## Execution Flow

### One-Command Production
```bash
python3 run_pipeline.py \
  --request "Create documentary on Facebook content moderators" \
  --script "script.md" \
  --narration "audio/" \
  --output "facebook_moderators_final.mp4"
```

**Behind the scenes:**
1. Producer orchestrates all 10 agents
2. Each stage feeds into next
3. Parallel searches (Asset Finder)
4. Serial assembly (FFmpeg Editor)
5. Final QA (Quality Review)

**Time estimate:** 30–60 minutes (depends on AI generation)

---

## Phase 1, 2, 3 Roadmap

### Phase 1 (NOW)
- ✅ Claude Code (orchestration)
- ✅ Python (agents)
- ✅ FFmpeg (editing)
- ✅ Pexels API (stock video)
- ✅ Internet Archive (historical)

**Cost:** Very low (~$5-7 per video)

### Phase 2 (PLANNED)
- Tavily (research + fact-checking)
- Veo / Runway (video generation)
- ElevenLabs (TTS narration)
- Google Earth Studio (map flyovers)

**Cost:** $10-15 per video

### Phase 3 (ADVANCED)
- Critique agents that watch finished video
- Auto-detect weak sections
- Self-edit and re-render until quality threshold
- Approaches professional documentary studio workflows

---

## Multi-Agent Advantages

✅ **Specialization** — Each agent focuses on one domain  
✅ **Parallelization** — Asset searches run concurrent  
✅ **Scalability** — Add agents without refactoring others  
✅ **Transparency** — Each agent reports its decisions  
✅ **Fault isolation** — One agent failure doesn't crash pipeline  
✅ **Tool swapping** — Replace Pexels with Getty, Grok with DALL-E  

---

## Cost Estimate (per video)

| Stage | Cost |
|-------|------|
| Stock video (Pexels) | $0 |
| Archival (Internet Archive) | $0 |
| Maps (Folium) | $0 |
| AI infographics (Grok, 5) | $0.25 |
| AI videos (Runway, 2) | $0.20 |
| Narration (ElevenLabs, 10 min) | $5.00 |
| **Total** | **~$5.45** |

---

## Files Created

```
agents/
├── base_agent.py              # Foundation class
├── research_agent.py           # Fact-finding
├── script_analyzer_agent.py    # Script breakdown
├── visual_planner_agent.py     # Emmy-standard visuals
├── asset_finder_agent.py       # Parallel asset search
├── ai_generator_agent.py       # Create missing visuals
├── timeline_builder_agent.py   # Sync to narration
├── ffmpeg_editor_agent.py      # Assemble video
├── producer_agent.py           # Orchestrator
├── quality_review_agent.py     # QA
└── run_pipeline.py             # Main entry point
```

---

**Status:** ✅ Ready for production  
**Version:** 2.0 (Multi-agent)  
**Next:** Test on Facebook Moderators video
