# Documentary Production Workflow

## Core Principle
**The documentary is the product. GitHub is archive only.**

## Workflow - Strict Order

1. **PRODUCE** → Generate documentary files to `output/`
2. **QA MEASURE** → Run through 6 quality gates
3. **AUDIENCE TEST** → Validate with audience metrics
4. **IF PASS ALL** → Commit to GitHub
5. **IF PASS ALL** → Create release/tag
6. **IF FAIL ANY** → Restart production, do NOT commit

## Output Structure

Every production MUST generate these files in `output/`:

```
output/
├── documentary.mp4           # Actual video file (4K MP4)
├── captions.srt              # Subtitle/caption file
├── research.json             # Research data & verified sources
├── timeline.json             # Editing timeline (clips, transitions)
├── qa_report.json            # QA agent metrics (6 gates)
├── audience_report.json      # Audience satisfaction metrics
└── production_log.json       # Complete production execution log
```

### documentary.mp4
- Actual video file, not metadata
- 4K resolution (3840x2160)
- Duration: 60 seconds (1-min) OR 300 seconds (5-min)
- MP4 container format
- H.264 video codec
- AAC audio codec

#### For 5-Minute Documentaries:
- Generate 12 × 5-second segments (Higgsfield max per segment)
- Each segment: unique prompt tied to narrative progression
- Compile segments sequentially with FFmpeg (seamless transitions)
- Segments 1-2: Opening/hook (10s)
- Segments 3-6: Main content development (20s)
- Segments 7-10: Supporting stories/details (20s)
- Segments 11-12: Conclusion/impact (10s)
- Total: 60 seconds per segment × 5 segments = 300 seconds (5 minutes)

### captions.srt
- SRT subtitle format
- Timestamps synchronized to video
- Full narration text
- Includes speaker cues if applicable

### research.json
```json
{
  "topic": "string",
  "facts": [
    {
      "claim": "string",
      "source": "url",
      "verification_status": "verified|disputed|unknown",
      "confidence": 0.0-1.0
    }
  ],
  "sources": ["url1", "url2", ...],
  "research_date": "ISO timestamp"
}
```

### timeline.json
```json
{
  "duration_seconds": 60,
  "scenes": [
    {
      "start_time": 0.0,
      "end_time": 10.0,
      "visual": "asset_id or description",
      "narration": "text",
      "transition": "fade|cut|dissolve"
    }
  ]
}
```

### qa_report.json
```json
{
  "production_id": "string",
  "qa_timestamp": "ISO timestamp",
  "gates": {
    "fact_verification": {
      "threshold": 0.95,
      "score": 0.972,
      "status": "PASS|FAIL",
      "details": "explanation with metrics only"
    },
    "visual_teaching": {
      "threshold": 0.90,
      "score": 0.980,
      "status": "PASS|FAIL",
      "details": "explanation with metrics only"
    },
    "asset_coverage": {
      "threshold": 0.90,
      "score": 1.0,
      "status": "PASS|FAIL",
      "details": "explanation with metrics only"
    },
    "qa_score": {
      "threshold": 0.90,
      "score": 0.925,
      "status": "PASS|FAIL",
      "details": "explanation with metrics only"
    },
    "story_flow": {
      "threshold": 0.92,
      "score": 0.925,
      "status": "PASS|FAIL",
      "details": "explanation with metrics only"
    },
    "audience_satisfaction": {
      "threshold": 0.92,
      "score": 0.935,
      "status": "PASS|FAIL",
      "details": "explanation with metrics only"
    }
  },
  "all_gates_passed": true,
  "qa_agent_notes": "objective observations only"
}
```

### audience_report.json
```json
{
  "production_id": "string",
  "test_date": "ISO timestamp",
  "sample_size": 50,
  "satisfaction_score": 0.935,
  "completion_rate": 0.92,
  "engagement_metrics": {
    "avg_attention_span": "95%",
    "rewatchability_score": 0.88,
    "sharing_intent": 0.81
  },
  "demographics": {
    "age_groups": {},
    "platforms": ["YouTube", "LinkedIn", "TikTok"]
  },
  "feedback": [
    "quoted user feedback with context"
  ]
}
```

### production_log.json
```json
{
  "production_id": "string",
  "start_time": "ISO timestamp",
  "end_time": "ISO timestamp",
  "duration_minutes": 12.5,
  "stages": [
    {
      "stage": "Script Generation",
      "api": "Claude",
      "status": "SUCCESS",
      "output": "1247 character script",
      "timestamp": "ISO"
    },
    {
      "stage": "Fact Verification",
      "api": "Tavily",
      "status": "SUCCESS",
      "sources_found": 5,
      "verification_rate": 0.972,
      "timestamp": "ISO"
    },
    {
      "stage": "Media Sourcing",
      "api": "Pexels",
      "status": "SUCCESS",
      "assets_found": 5,
      "timestamp": "ISO"
    },
    {
      "stage": "Narration Generation",
      "api": "ElevenLabs",
      "status": "SUCCESS",
      "audio_duration": 55.2,
      "timestamp": "ISO"
    },
    {
      "stage": "Video Generation",
      "api": "Runway ML",
      "status": "SUCCESS",
      "resolution": "4K",
      "timestamp": "ISO"
    }
  ],
  "apis_called": ["Claude", "Tavily", "Pexels", "ElevenLabs", "Runway ML"],
  "total_cost": 3.50,
  "errors": []
}
```

## Language Rules - STRICT

### FORBIDDEN (no exceptions)
These words may ONLY appear WITH objective metrics from QA agents:
- "Production Ready"
- "Emmy-worthy"
- "Professional"
- "Release Candidate"
- "Certified"
- "High quality"
- "Ready for distribution"
- "Verified" (use "verification_status" field instead)

### ALLOWED (no metrics required)
- Objective descriptions: "60-second 4K MP4", "5 Pexels photos", "1247 character script"
- Status statements: "PASS", "FAIL", "COMPLETE", "QUEUED"
- Factual observations: "Script coherence score: 0.95", "Fact verification: 97.2%"

### REQUIRED FORMAT
If claiming quality, format MUST be:
```
"[Metric Name]: [Score], threshold: [Threshold], status: [PASS/FAIL]"
```

Example:
- ❌ "Emmy-worthy script"
- ✅ "Script coherence: 0.95, threshold: 0.92, status: PASS"

## Commit/Release Rules

### NO COMMIT UNTIL:
- ✅ documentary.mp4 exists (real file, not metadata)
- ✅ All 7 output files generated
- ✅ qa_report.json shows all 6 gates PASS
- ✅ audience_report.json shows satisfaction ≥ 0.92

### NO RELEASE UNTIL:
- ✅ All commit conditions met
- ✅ audience_report.json complete
- ✅ production_log.json complete
- ✅ No unresolved QA issues

### COMMIT MESSAGE FORMAT
Only factual, metric-based language:
```
prod: [Documentary Title]

Metrics from QA Pipeline:
- Fact Verification: 0.972 (threshold: 0.95) ✅
- Visual Teaching: 0.980 (threshold: 0.90) ✅
- Asset Coverage: 1.0 (threshold: 0.90) ✅
- QA Score: 0.925 (threshold: 0.90) ✅
- Story Flow: 0.925 (threshold: 0.92) ✅
- Audience Satisfaction: 0.935 (threshold: 0.92) ✅

Production ID: [ID]
Duration: 60 seconds
Format: 4K MP4
Output Files: 7/7 complete
```

## 5-Minute Documentary Production Workflow

### Multi-Segment Video Generation (NEW)

**Problem:** Higgsfield Seedance 2.0 limited to 5-second maximum per generation
**Solution:** Generate 12 × 5-second segments, compile into seamless 5-minute video

**Segment Generation Process:**

1. **Divide Script into 12 segments** (25 seconds each narratively, 5 seconds video)
   - Segment 1-2: Opening hook (background + context)
   - Segment 3-4: First main point (evidence + examples)
   - Segment 5-6: Second main point (data + impact)
   - Segment 7-8: Third main point (innovation + future)
   - Segment 9-10: Supporting details (real-world application)
   - Segment 11-12: Conclusion (vision + call-to-action)

2. **Generate each segment with unique prompt**
   ```
   For each segment:
   - Higgsfield Seedance 2.0
   - Duration: 5 seconds (max allowed)
   - Prompt: narrative-tied (what happens in this 5-second beat)
   - Example: "Segment 1: Wide establishing shot of drone launching at sunrise..."
   ```

3. **Compile segments into final video**
   ```bash
   ffmpeg -f concat -safe 0 -i segment_list.txt -c copy documentary.mp4
   ```
   Where segment_list.txt contains:
   ```
   file 'segment_1.mp4'
   file 'segment_2.mp4'
   ...
   file 'segment_12.mp4'
   ```

4. **Add narration and final audio mix**
   - ElevenLabs narration (5-minute duration)
   - Background music/ambient audio
   - Mix to final output

**Video Segments Output Structure:**
```
output_5min/
├── video_segments/
│   ├── segment_01.mp4 (5s)
│   ├── segment_02.mp4 (5s)
│   ├── segment_03.mp4 (5s)
│   ├── segment_04.mp4 (5s)
│   ├── segment_05.mp4 (5s)
│   ├── segment_06.mp4 (5s)
│   ├── segment_07.mp4 (5s)
│   ├── segment_08.mp4 (5s)
│   ├── segment_09.mp4 (5s)
│   ├── segment_10.mp4 (5s)
│   ├── segment_11.mp4 (5s)
│   └── segment_12.mp4 (5s)
├── segment_prompts.json (all 12 prompts)
├── segment_list.txt (FFmpeg concat file)
└── documentary.mp4 (final 300-second compiled video)
```

**QA for 5-Minute Documentaries:**
- All 6 gates applied equally
- Fact verification: 0.95 minimum
- Visual teaching: 0.90 minimum (across all 12 segments)
- Asset coverage: 0.90 minimum
- Technical QA: 0.90 minimum (video compilation quality)
- Story flow: 0.92 minimum (continuity across segments)
- Audience satisfaction: 0.92 minimum

## Production Checklist

- [ ] Script generated and fact-checked
- [ ] Media sourced and curated
- [ ] Video generated and edited
- [ ] documentary.mp4 file created (verify file size > 0)
- [ ] captions.srt synchronized
- [ ] research.json complete with sources
- [ ] timeline.json accurate
- [ ] QA agents run all 6 gates
- [ ] qa_report.json all PASS
- [ ] Audience testing complete
- [ ] audience_report.json ≥ 0.92 satisfaction
- [ ] production_log.json finalized
- [ ] All 7 output/ files exist
- [ ] Language audit (no forbidden words)
- [ ] Ready for commit
- [ ] Ready for release

## Example: Correct Production Record

```json
{
  "documentary": "African Billionaires: Reshaping the Continent",
  "production_id": "african_billionaires_20260731_131443",
  "status": "qa_passed",
  "output_directory": "output/",
  "files": {
    "video": "documentary.mp4 (245.6 MB)",
    "captions": "captions.srt (8.2 KB)",
    "research": "research.json (12.4 KB)",
    "timeline": "timeline.json (15.7 KB)",
    "qa": "qa_report.json (3.1 KB)",
    "audience": "audience_report.json (5.8 KB)",
    "log": "production_log.json (4.2 KB)"
  },
  "qa_results": {
    "fact_verification": "0.972 (threshold 0.95) PASS",
    "visual_teaching": "0.980 (threshold 0.90) PASS",
    "asset_coverage": "1.0 (threshold 0.90) PASS",
    "qa_score": "0.925 (threshold 0.90) PASS",
    "story_flow": "0.925 (threshold 0.92) PASS",
    "audience_satisfaction": "0.935 (threshold 0.92) PASS"
  },
  "ready_to_commit": true,
  "ready_to_release": true
}
```
